import json
import os
import urlparse
import sys

import webob.dec
import paste.urlmap

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

    def __init__(self, paths, default_mode = None, inputs = None):
        self.paths = [os.path.abspath(path) for path in paths]

    @webob.dec.wsgify
    def __call__(self, request):
        path_info = request.path_info[1:] # remove '/'
        for path in self.paths:
            abspath = os.path.join(path, path_info)
            if os.path.isfile(abspath):
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
        self.paths = [os.path.abspath(path) for path in paths]
        self.default_mode = default_mode
        self.inputs = inputs

    def getDeps(self, request):
        base_url = urlparse.urljoin(request.url, "input/")

        sources = set()
        for path in self.paths:
            path = os.path.abspath(path)

            for jsfile in treescan.ScanTreeForJsFiles(path):
                src = closurebuilder._PathSource(jsfile)
                src.href = urlparse.urljoin(
                    base_url,
                    src.GetPath()[len(path) + 1:]) # remove starting '/'
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

        return deps

    @webob.dec.wsgify
    def __call__(self, request):
        deps = self.getDeps(request)
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
})();
""" %(json.dumps([js_source.href for js_source in deps]), path)
        
        return webob.Response(
            body = output, content_type = "application/javascript")


class Compile(Raw):

    def __init__(self, paths, default_mode = None, inputs = None):
        super(Compile, self).__init__(paths, default_mode, inputs)

        self.compiler_jar = "/home/michael/deri/javascript/closure-compiler-read-only/build/compiler.jar"
        self.compiler_flags = []

    @webob.dec.wsgify
    def __call__(self, request):
        deps = self.getDeps(request)

        output = jscompiler.Compile(
            self.compiler_jar,
            [src.GetPath() for src in deps],
            self.compiler_flags)

        return webob.Response(
            body = output, content_type = "application/javascript")


class Combined(object):

    def __init__(self, **local_conf):
        self.app = paste.urlmap.URLMap()
        self.app["/compile"] = Raw(**local_conf)
        self.app["/input"] = Input(**local_conf)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


def get_input_arguments(local_conf):
    paths = local_conf.get("paths", "")
    if paths:
        paths = [os.path.abspath(path) for path in paths.split()]
    else:
        paths = ()

    inputs = local_conf.get("inputs", "")
    if inputs:
        inputs = inputs.split()
    else:
        inputs = ()

    return {"paths": paths, "default_mode": RAW, "inputs": inputs}

def paste_combined_closure(global_conf, **local_conf):
    conf = get_input_arguments(local_conf)

    return Combined(**conf)
