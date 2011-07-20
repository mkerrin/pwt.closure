import os.path
import urlparse
import re
import shutil
import string
import subprocess
import sys
import tempfile

import paste.reloader

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


_FILE_REGEX = re.compile(r"^.+\.(js|soy)$")

DEFAULT_SOY_JAR = os.path.join(
    os.path.dirname(__file__), "jars", "SoyToJsSrcCompiler.jar")

class PathSource(source.Source):

    def __init__(self, path):
        super(PathSource, self).__init__(source.GetFileContents(path))

        self._path = path

    def GetPath(self):
        return self._path


class SoySource(source.Source):

    def __init__(self, path):
        # XXX - missing attributes, set later.
        self.provides = set()
        self.requires = set()

        self._path = None
        self._src = path

    def GetPath(self):
        return self._path


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


class Tree(object):

    def __init__(self, roots):
        self.roots = roots

        sources = set()
        path_info = {}
        basefile = None

        soyes = set()
        for root in roots:
            root = os.path.abspath(root)

            for jsfile in treescan.ScanTree(root, _FILE_REGEX):
                if jsfile.endswith("soy"): # template
                    # We need to collect all templates and generate them
                    # all at once so that we only call a java subprocess once
                    src = SoySource(jsfile)
                    soyes.add(src)
                elif jsfile.endswith("js"):
                    src = PathSource(jsfile)
                    if closurebuilder._IsClosureBaseFile(src):
                        basefile = src
                else:
                    raise ValueError("Unknown file extension")

                # Save the path_info so that we can map path_info to a source
                # object and back.
                path = jsfile[len(root):]
                path_info[path] = src
                src.path_info = path

                # watch file for changes. This reloads the whole server
                # compiling any templates that need to changed.
                # This does nothing if we are not running under the PasteScript
                # server that stops and reloads whenever any changes are found.
                paste.reloader.watch_file(jsfile)

                sources.add(src)

        if soyes:
            # XXX - we could have multiple files with the same filename but
            # located in a different patch that will override each other here.
            tmpdir = tempfile.mkdtemp()
            outputPathFormat = "%s/{INPUT_FILE_NAME_NO_EXT}.js" % tmpdir
            args = [
                "java", "-jar", DEFAULT_SOY_JAR,
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
                soy._ScanSource()

            # Cleanup
            shutil.rmtree(tmpdir)

        self.tree = depstree.DepsTree(sources)

        if basefile is None:
            raise ValueError("No Closure base.js found")
        self.base = basefile

        self.path_info = path_info

    def getDeps(self, inputs):
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

    def getCompiledSource(self, inputs, compiler_jar, compiler_flags):
        deps = self.getDeps(inputs)

        args = ["java", "-jar", compiler_jar]
        for src in deps:
            path = src.GetPath()
            if path is None:
                # tp - tempfile that gets cleared out when the pointer goes
                # out of scope
                fp = tempfile.NamedTemporaryFile(suffix = ".js")
                fp.write(src.GetSource())
                fp.flush()
                path = fp.name
            args += ["--js", path]

        if compiler_flags:
            args += compiler_flags

        proc = subprocess.Popen(args, stdout = subprocess.PIPE)
        stdoutdata, unused_stderrdata = proc.communicate()

        if proc.returncode != 0:
            raise ValueError("Compilation failed")

        return stdoutdata

    def getSource(self, path_info):
        # Note: get the Java Script source
        return self.path_info[path_info]
