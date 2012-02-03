import logging
import os.path
import urlparse
import re
import shutil
import string
import subprocess
import sys
import tempfile

# We need to reload the server whenever any of our files change. We need
# to support multiple monitors here.
_reloaders = []
try:
    import paste.reloader
except ImportError:
    pass
else:
    _reloaders.append(paste.reloader.watch_file)

try:
    import pyramid.scripts.pserve
except ImportError:
    pass
else:
    _reloaders.append(pyramid.scripts.pserve.watch_file)


# Import the depswrite and source from closure-library checkout
old_path = sys.path
sys.path.append(os.path.join(os.path.dirname(__file__), "build"))
import depswriter
import depstree
import source
import treescan
import closurebuilder
import jscompiler
# reset the path
sys.path = sys.path[:-1]


_FILE_REGEX = re.compile(r"^.+\.(js|soy|jinja2)$")

DEFAULT_SOY_JAR = os.path.join(
    os.path.dirname(__file__), "jars", "SoyToJsSrcCompiler.jar")

DEFAULT_COMPILER_JAR = os.path.join(
    os.path.dirname(__file__), "jars", "compiler.jar")


class PathSource(source.Source):
    """
    Source object of ordinary Java Script file
    """

    def __init__(self, tree, path):
        super(PathSource, self).__init__(source.GetFileContents(path))

        self._path = path

    def GetPath(self):
        return self._path


_SOY_NAMESPACE = re.compile(r"{namespace\s+([a-zA-Z0-9_\.]+)\s*}")

class SoySource(source.Source):
    """
    Source object of Closure Template file. GetSource converts template
    to Java Script
    """

    def __init__(self, tree, path):
        self.provides = set()
        self.requires = set()

        self._tree = tree

        self._path = None
        self._src = path
        self._ScanSource()

        # We need to collect all templates and generate them
        # all at once so that we only call a java subprocess once
        soyes = getattr(tree, "_soyes", None)
        if soyes is None:
            tree._soyes = set()
            tree._soyes_built = False
        tree._soyes.add(self)

    def GetPath(self):
        return self._path

    def GetSource(self):
        self._update()
        return self._source

    def _update(self):
        if not self._tree._soyes_built and self._tree._soyes:
            self._build_soyes()

    def _build_soyes(self):
        soyes = self._tree._soyes

        # XXX - we could have multiple files with the same filename but
        # located in a different patch that will override each other here.
        # XXX - Also we need to be able to handle multiple languages
        tmpdir = tempfile.mkdtemp()
        outputPathFormat = "%s/{INPUT_FILE_NAME_NO_EXT}.js" % tmpdir
        args = [
            "java", "-jar", self._tree.config["soy_jar"],
            "--shouldProvideRequireSoyNamespaces",
            "--outputPathFormat", outputPathFormat,
            ]
        for soy in soyes:
            args.append(soy._src)

        proc = subprocess.Popen(args, stdout = subprocess.PIPE)
        stdoutdata, unused_stderrdata = proc.communicate()

        if proc.returncode != 0:
            raise ValueError("Failed to generate templates")

        for soy in soyes:
            # Patch up the source
            _path = get_output_filename(outputPathFormat, soy._src)
            soy._source = source.GetFileContents(_path)

        # Cleanup
        shutil.rmtree(tmpdir)

        self._tree._soyes_built = True

    def _ScanSource(self):
        src = source.GetFileContents(self._src)

        self.requires.add("soy")
        self.requires.add("soy.StringBuilder")

        src_lines = src.splitlines()
        for line in src_lines:
            match = _SOY_NAMESPACE.match(line)
            if match:
                self.provides.add(match.group(1))

            # XXX - need to implement a RE for any {call}...{/call} blocks
            # that would define a goog.require for us


def get_output_filename(output_format, filename):
    filename_template = string.Template(output_format)

    data = {
        "{INPUT_FILE_NAME}": os.path.basename(filename),
        "{INPUT_FILE_NAME_NO_EXT}": os.path.splitext(os.path.basename(filename))[0],
        "{INPUT_DIRECTORY}": os.path.dirname(filename),
        # "{INPUT_PREFIX}": 
        }

    for key, val in data.items():
        output_format = output_format.replace(key, val)

    return output_format


_default_config = {
    # SoyToJsSrcCompiler.jar
    "soy_jar": DEFAULT_SOY_JAR,
    # compiler.jar
    "compiler_jar": DEFAULT_COMPILER_JAR,
    "compiler_flags": [],
    # default inputs
    "inputs": [],
    }

_default_config["plugins_extensions"] = {
    ".js": PathSource,
    ".soy": SoySource,
    }
try:
    import jinja
    import pwt.jinja2js.environment
except ImportError: # pwt.jinja2js not installed, probable
    def parse_environment(settings):
        raise ValueError("pwt.jinja2js is not installed")
else:
    _default_config["plugins_extensions"][".jinja2"] = jinja.Source

    def parse_environment(settings):
        return pwt.jinja2js.environment.parse_environment(settings)


class Tree(object):

    def __init__(self, **config):
        self.roots = config["paths"]
        # Extend the default configuration but don't change it
        self.config = _default_config.copy()
        self.config.update(config)

        self.tree = self.base = self.path_info = None

    def update(self):
        if self.tree is not None:
            return

        sources = set()
        path_info = {}
        basefile = None

        for root in self.roots:
            root = os.path.abspath(root)

            for jsfile in treescan.ScanTree(root, _FILE_REGEX):
                ext = os.path.splitext(jsfile)[1]
                # throws KeyError if we don't understand the file extension
                src = _default_config["plugins_extensions"][ext](self, jsfile)

                if basefile is None and closurebuilder._IsClosureBaseFile(src):
                    basefile = src

                # Save the path_info so that we can map path_info to a source
                # object and back.
                path = jsfile[len(root):]
                path_info[path] = src
                src.path_info = path
                # Rememmber the last modified time so that we can before some
                # sort of caching of resources.
                src.mtime = os.stat(jsfile).st_mtime

                # watch file for changes. This reloads the whole server
                # compiling any templates that need to changed.
                # This does nothing if we are not running under the PasteScript
                # server that stops and reloads whenever any changes are found.
                [watch_file(jsfile) for watch_file in _reloaders]

                sources.add(src)

        if basefile is None:
            raise ValueError("No Closure base.js found")

        self.tree = depstree.DepsTree(sources)

        self.base = basefile

        self.path_info = path_info

    def getDeps(self, inputs = None):
        # Returns a list of Source objects.
        self.update()
        inputs = inputs or self.config["inputs"]

        input_namespaces = set()
        for input_path in inputs:
            src = None
            try:
                js_input = source.Source(source.GetFileContents(input_path))
            except IOError:
                # All path_info attributes start with a slash. So put in
                # the slash to make sure we find the file
                js_input = self.getSource(os.path.join("/", input_path))
            
            input_namespaces.update(js_input.provides)
        if not input_namespaces:
            raise ValueError("Input namespaces must be specified")

        deps = [self.base] + self.tree.GetDependencies(input_namespaces)

        return deps

    def getCompiledSource(self, inputs = None):
        deps = self.getDeps(inputs)

        # Collect all the temporary files and remove them at the end in a
        # finally statement.
        alltempfiles = []

        try:
            args = ["java", "-jar", self.config["compiler_jar"]]
            for src in deps:
                path = src.GetPath()
                if path is None:
                    # Soy Source files create tempfiles so we need to recreate
                    # them now so that we don't leave loads of tempfiles on the
                    # system
                    # tp - tempfile that gets cleared out when the pointer goes
                    # out of scope
                    fp = tempfile.NamedTemporaryFile(
                        suffix = ".js", delete = False)
                    fp.write(src.GetSource())
                    fp.close()
                    path = fp.name

                    alltempfiles.append(path)

                args += ["--js", path]

            args += self.config["compiler_flags"]

            logging.info(
                "Compiling with the following command: %s", " ".join(args))

            proc = subprocess.Popen(args, stdout = subprocess.PIPE)
            stdoutdata, unused_stderrdata = proc.communicate()

            if proc.returncode != 0:
                raise ValueError("Compilation failed")

            return stdoutdata
        finally:
            for tmp in alltempfiles:
                os.remove(tmp)

    def getSource(self, path_info):
        self.update()
        # Note: get the Java Script source
        return self.path_info[path_info]


def MakeDepsFile(tree):
    """
    Convert the Tree object into a deps.js file. Returns the contents of
    such a file.
    """
    tree.update()

    source_map = dict([
        (src.path_info, src) for src in tree.tree._sources
        ])

    return depswriter.MakeDepsFile(source_map)
