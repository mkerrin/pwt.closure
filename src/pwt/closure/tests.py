import paste.urlmap
import unittest
import webtest
import os.path

import wsgi

BODIES = {
    "test1": """(function() {
    var files = ["http://localhost/input/closure/goog/base.js", "http://localhost/input/closure/goog/debug/errorhandlerweakdep.js", "http://localhost/input/closure/goog/string/string.js", "http://localhost/input/closure/goog/useragent/useragent.js", "http://localhost/input/closure/goog/object/object.js", "http://localhost/input/closure/goog/debug/error.js", "http://localhost/input/closure/goog/asserts/asserts.js", "http://localhost/input/closure/goog/array/array.js", "http://localhost/input/closure/goog/debug/entrypointregistry.js", "http://localhost/input/closure/goog/events/eventwrapper.js", "http://localhost/input/closure/goog/events/eventtype.js", "http://localhost/input/closure/goog/events/browserfeature.js", "http://localhost/input/closure/goog/disposable/idisposable.js", "http://localhost/input/closure/goog/disposable/disposable.js", "http://localhost/input/closure/goog/events/event.js", "http://localhost/input/closure/goog/reflect/reflect.js", "http://localhost/input/closure/goog/events/browserevent.js", "http://localhost/input/closure/goog/events/listener.js", "http://localhost/input/closure/goog/useragent/jscript.js", "http://localhost/input/closure/goog/structs/simplepool.js", "http://localhost/input/closure/goog/events/pools.js", "http://localhost/input/closure/goog/events/events.js", "http://localhost/input/closure/goog/events/eventtarget.js", "http://localhost/input/test1.js"];
    var path = '/compile';

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
""",
    "test1_js": """(function() {
    var files = ["http://localhost/js/input/closure/goog/base.js", "http://localhost/js/input/closure/goog/debug/errorhandlerweakdep.js", "http://localhost/js/input/closure/goog/string/string.js", "http://localhost/js/input/closure/goog/useragent/useragent.js", "http://localhost/js/input/closure/goog/object/object.js", "http://localhost/js/input/closure/goog/debug/error.js", "http://localhost/js/input/closure/goog/asserts/asserts.js", "http://localhost/js/input/closure/goog/array/array.js", "http://localhost/js/input/closure/goog/debug/entrypointregistry.js", "http://localhost/js/input/closure/goog/events/eventwrapper.js", "http://localhost/js/input/closure/goog/events/eventtype.js", "http://localhost/js/input/closure/goog/events/browserfeature.js", "http://localhost/js/input/closure/goog/disposable/idisposable.js", "http://localhost/js/input/closure/goog/disposable/disposable.js", "http://localhost/js/input/closure/goog/events/event.js", "http://localhost/js/input/closure/goog/reflect/reflect.js", "http://localhost/js/input/closure/goog/events/browserevent.js", "http://localhost/js/input/closure/goog/events/listener.js", "http://localhost/js/input/closure/goog/useragent/jscript.js", "http://localhost/js/input/closure/goog/structs/simplepool.js", "http://localhost/js/input/closure/goog/events/pools.js", "http://localhost/js/input/closure/goog/events/events.js", "http://localhost/js/input/closure/goog/events/eventtarget.js", "http://localhost/js/input/test1.js"];
    var path = '/compile';

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
"""
    }

class WSGICompile(unittest.TestCase):

    def get_app(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Raw(paths = paths, inputs = inputs))

    def test_getapp(self):
        # Note that the trailing '/' is removed :-)
        app = self.get_app("test1.js")
        self.assertEqual(app.app.paths, [
            "/home/michael/deri/javascript/pwt.closure/parts/closure-library/closure-library",
            "/home/michael/deri/javascript/pwt.closure/src/pwt/closure"])

    def get_inputApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Input(paths = paths, inputs = inputs))

    def test_inputApp(self):
        # Note that the trailing '/' is removed :-)
        app = self.get_inputApp("test1.js")
        self.assertEqual(app.app.paths, [
            "/home/michael/deri/javascript/pwt.closure/parts/closure-library/closure-library",
            "/home/michael/deri/javascript/pwt.closure/src/pwt/closure"])

    def test_compile_raw1(self):
        app = self.get_app(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")]
            )
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1"])

    def test_input1(self):
        app = self.get_inputApp(None)
        resp = app.get("/closure/goog/base.js")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")

    def test_input2(self):
        app = self.get_inputApp(None)
        resp = app.get("/missing.js", expect_errors = True)
        self.assertEqual(resp.status_int, 404)
        self.assertEqual(resp.body, "")

    def get_combined(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Combined(
            paths = paths, default_mode = wsgi.RAW, inputs = inputs))

    def test_combinedApp(self):
        # Note that the trailing '/' is removed :-)
        app = self.get_combined("test1.js")
        self.assertEqual(app.app.app[(None, "/compile")].paths, [
            "/home/michael/deri/javascript/pwt.closure/parts/closure-library/closure-library",
            "/home/michael/deri/javascript/pwt.closure/src/pwt/closure"])
        self.assertEqual(app.app.app[(None, "/input")].paths, [
            "/home/michael/deri/javascript/pwt.closure/parts/closure-library/closure-library",
            "/home/michael/deri/javascript/pwt.closure/src/pwt/closure"])

    def test_combined1(self):
        app = self.get_combined(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

    def test_combined2(self):
        app = self.get_combined(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/compile")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1"])

    def test_combined3(self):
        app = self.get_combined(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/input", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

    def test_combined3(self):
        app = self.get_combined(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/input/closure/goog/base.js")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")

    def get_subApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        urlmap = paste.urlmap.URLMap()
        urlmap["/js"] = wsgi.Combined(
            paths = paths, default_mode = wsgi.RAW, inputs = inputs)
        return webtest.TestApp(urlmap)

    def test_sub_combined1(self):
        app = self.get_subApp(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/js/compile")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1_js"])

    def get_compileApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        app = wsgi.Compile(
            paths = paths, default_mode = wsgi.RAW, inputs = inputs)
        return webtest.TestApp(app)

    def test_compile1(self):
        app = self.get_compileApp(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assert_(resp.content_length > 0)
