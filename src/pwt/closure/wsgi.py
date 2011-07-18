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

import files

class Input(object):

    def __init__(self, files, **kwargs):
        self.files = files

    @webob.dec.wsgify
    def __call__(self, request):
        try:
            src = self.files.getSource(request.path_info)
        except KeyError:
            status = 404
            content_type = None
            output = ""
        else:
            status = 200
            content_type = "application/javascript"
            output = src.GetSource()

        return webob.Response(
            body = output,
            status = status,
            content_type = content_type)


class Raw(object):

    def __init__(self, files, inputs = None, **kwargs):
        self.files = files
        self.inputs = inputs

    @webob.dec.wsgify
    def __call__(self, request):
        deps = self.files.getDeps(self.inputs)
        path = "/compile"

        base_url = urlparse.urljoin(request.url, "input/")
        # remove starting '/'
        files = [
            urlparse.urljoin(base_url, js_source.path_info[1:])
            for js_source in deps
            ]

        # Simple small Java Script snippet that checks to see if it is included
        # on this page and then inserts all the dependencies on the inputs.
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
""" %(json.dumps(files), path)
        
        return webob.Response(
            body = output, content_type = "application/javascript")


class Compile(Raw):

    def __init__(self, files, inputs = None, compiler_jar = None, compiler_flags = []):
        super(Compile, self).__init__(files, inputs)

        self.compiler_jar = compiler_jar
        self.compiler_flags = compiler_flags

    @webob.dec.wsgify
    def __call__(self, request):
        deps = self.files.getDeps(self.inputs)

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
    local_conf["files"] = files.Tree(local_conf["paths"])

    inputs = local_conf.get("inputs", "")
    if inputs:
        inputs = inputs.split()
    else:
        inputs = ()
    local_conf["inputs"] = inputs

    return local_conf

def paste_combined_closure(global_conf, **local_conf):
    conf = get_input_arguments(local_conf)

    return Combined(**conf)
