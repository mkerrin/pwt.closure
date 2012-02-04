import json
import os
import urlparse
import datetime

import webob.dec
import webob.datetime_utils
import paste.urlmap

RAW = "RAW"
SIMPLE = "SIMPLE"
ADVANCED = "ADVANCED"

import files

JS_CONTENT_TYPE = "application/javascript"

class Input(object):

    def __init__(self, tree, **kwargs):
        self.tree = tree

    @webob.dec.wsgify
    def __call__(self, request):
        try:
            src = self.tree.getSource(request.path_info)
        except KeyError:
            return webob.Response(
                status = 404,
                content_type = None)
        else:
            # Use the file stats to see if we need to send the contents of the
            # file back to the client.
            last_modified = datetime.datetime.fromtimestamp(
                int(src.mtime), webob.datetime_utils.UTC)
            if request.if_modified_since and \
                   last_modified <= request.if_modified_since:
                return webob.Response(
                    status = 304,
                    content_type = JS_CONTENT_TYPE,
                    last_modified = src.mtime)

            return webob.Response(
                body = src.GetSource(), # May call external programs
                status = 200,
                content_type = JS_CONTENT_TYPE,
                last_modified = src.mtime)


class Raw(object):

    def __init__(self, tree, **kwargs):
        self.tree = tree

    @webob.dec.wsgify
    def __call__(self, request):
        deps = self.tree.getDeps(request.GET.getall("input"))
        path = "/compile"

        base_url = urlparse.urljoin(request.url, "input/")
        # remove starting '/'
        jsfiles = [
            urlparse.urljoin(base_url, js_source.path_info[1:])
            for js_source in deps
            ]

        # Simple small Java Script snippet that checks to see if it is included
        # on this page and then inserts all the dependencies on the inputs.
        output = """(function() {
    CLOSURE_NO_DEPS = true;

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
""" %(json.dumps(jsfiles), path)

        return webob.Response(
            body = output, content_type = "application/javascript")


class Compile(object):

    def __init__(self, tree, **kwargs):
        self.tree = tree

    @webob.dec.wsgify
    def __call__(self, request):
        output = self.tree.getCompiledSource(request.GET.getall("input"))

        return webob.Response(
            body = output, content_type = "application/javascript")


class Deps(object):

    def __init__(self, tree, **kwargs):
        self.tree = tree

    @webob.dec.wsgify
    def __call__(self, request):
        # XXX - generate an unique ID on start up and use this as a Etag
        # to perform caching on this file.
        base_path = urlparse.urljoin(request.path, "input/")
        output = files.MakeDepsFile(self.tree, base_path)

        return webob.Response(
            body = output, content_type = "application/javascript")


class Combined(object):

    def __init__(self, **local_conf):
        self.app = paste.urlmap.URLMap()
        self.app["/compile"] = Raw(**local_conf)
        self.app["/input"] = Input(**local_conf)
        self.app["/deps"] = Deps(**local_conf)

    def __call__(self, environ, start_response):
        return self.app(environ, start_response)


def get_input_arguments(local_conf):
    # local_conf is a dictionary of unparsed configuration from an ini file.
    # We need to split some values up into lists where appropriate.
    inputs = local_conf.get("inputs", "")
    if inputs:
        inputs = inputs.split()
    else:
        inputs = ()
    local_conf["inputs"] = inputs

    # need to configure Jinja2 environment if appropriate
    try:
        local_conf["jinja2.environment"] = files.parse_environment(local_conf)
    except (KeyError, ValueError), err:
        pass

    local_conf["paths"] = local_conf["paths"].split()

    local_conf["tree"] = files.Tree(**local_conf)

    return local_conf

def paste_combined_closure(global_conf, **local_conf):
    conf = get_input_arguments(local_conf)

    return Combined(tree = conf["tree"])
