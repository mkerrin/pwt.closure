import json
import os
import sys
import webob.dec

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

RAW = "RAW"
SIMPLE = "SIMPLE"
ADVANCED = "ADVANCED"

class Input(object):

    def __init__(self, paths, inputs = None):
        self.paths = [os.path.abspath(path) for path in paths]

    @webob.dec.wsgify
    def __call__(self, request):
        path_info = request.path_info[1:] # remove '/'
        for path in self.paths:
            abspath = os.path.join(path, path_info)
            if os.path.exists(abspath):
                output = open(abspath).read()
                status = 200
                break
        else:
            output = ""
            status = 404

        return webob.Response(
            body = output,
            status = status,
            content_type = "application/javascript")


class Raw(object):

    def __init__(self, paths, default_mode = RAW, inputs = None):
        self.paths = paths
        self.default_mode = default_mode
        self.inputs = inputs

    def getHref(self, src, root):
        return src.GetPath()[len(root):]

    def getFiles(self):
        sources = set()
        for path in self.paths:
            path = os.path.abspath(path)

            for jsfile in treescan.ScanTreeForJsFiles(path):
                src = closurebuilder._PathSource(jsfile)
                src.href = self.getHref(src, path)
                sources.add(src)

        tree = depstree.DepsTree(sources)

        input_namespaces = set()
        for input_path in self.inputs:
            js_input = closurebuilder._PathSource(input_path)
            input_namespaces.update(js_input.provides)
        if not input_namespaces:
            raise ValueError("")

        base = closurebuilder._GetClosureBaseFile(sources)
        deps = [base] + tree.GetDependencies(input_namespaces)

        files = [js_source.href for js_source in deps]

        return files

    @webob.dec.wsgify
    def __call__(self, request):
        files = self.getFiles()
        path = "/compile"
        
        output = """(function() {
    var files = %s;
    var path = '%s';

    var scriptEl;
    var doc = document;
    var scripts = doc.getElementsByTagName('script');
    for (var i = scripts.length - 1; i >= 0; --i) {
        var candidateScriptEl = scripts[i];
        var src = candidateScriptEl.src;
        if (src.indexOf(path) >= 0) {
            scriptEl = candidateScriptEl;
            break;
        }
    }

    if (!scriptEl) {
        return;
    }

    for (var i = 0; i < files.length; i++) {
        doc.write('<script type="text/javascript" src="' + files[i] + '"><\/script>');
    }
}
""" %(json.dumps(files), path)
        
        return webob.Response(
            body = output, content_type = "application/javascript")
