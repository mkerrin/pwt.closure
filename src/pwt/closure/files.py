import os.path
import urlparse
import re
import subprocess
import sys
import tempfile

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

    def GetSourcePath(self):
        return self._source, self._path


class SoySource(source.Source):

    def __init__(self, path):
        self.tmp = tempfile.NamedTemporaryFile(delete = False, suffix = ".js")
        args = [
            "java", "-jar", DEFAULT_SOY_JAR,
            "--shouldProvideRequireSoyNamespaces",
            "--outputPathFormat", self.tmp.name,
            path]

        proc = subprocess.Popen(args, stdout = subprocess.PIPE)
        stdoutdata, unused_stderrdata = proc.communicate() # XXX - check output

        super(SoySource, self).__init__(source.GetFileContents(self.tmp.name))

        self._path = self.tmp.name

    def GetPath(self):
        return self._path

    def __del__(self):
        if self.tmp:
            os.remove(self.tmp.name)


class Tree(object):

    def __init__(self, roots):
        self._get_files(roots)

    def _get_files(self, roots):
        sources = set()
        path_info = {}
        for root in roots:
            root = os.path.abspath(root)

            for jsfile in treescan.ScanTree(root, _FILE_REGEX):
                if jsfile.endswith("soy"): # template
                    src = SoySource(jsfile)
                elif jsfile.endswith("js"):
                    src = PathSource(jsfile)
                else:
                    raise ValueError("Unknown file extension")

                path = jsfile[len(root):]
                path_info[path] = src
                src.path_info = path

                sources.add(src)

        self.tree = depstree.DepsTree(sources)

        self.base = closurebuilder._GetClosureBaseFile(sources)

        self.path_info = path_info

    def getDeps(self, inputs):
        input_namespaces = set()
        for input_path in inputs:
            js_input = source.Source(source.GetFileContents(input_path))
            input_namespaces.update(js_input.provides)
        if not input_namespaces:
            raise ValueError("Input namespaces must be specified")

        deps = [self.base] + self.tree.GetDependencies(input_namespaces)

        return deps

    def getSource(self, path_info):
        # Note: get the Java Script source
        return self.path_info[path_info]
