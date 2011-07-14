import unittest
import webtest
import os.path

import wsgi

BODIES = {
    "test1": """(function() {
    var files = ["/closure/goog/base.js", "/closure/goog/debug/errorhandlerweakdep.js", "/closure/goog/string/string.js", "/closure/goog/useragent/useragent.js", "/closure/goog/object/object.js", "/closure/goog/debug/error.js", "/closure/goog/asserts/asserts.js", "/closure/goog/array/array.js", "/closure/goog/debug/entrypointregistry.js", "/closure/goog/events/eventwrapper.js", "/closure/goog/events/eventtype.js", "/closure/goog/events/browserfeature.js", "/closure/goog/disposable/idisposable.js", "/closure/goog/disposable/disposable.js", "/closure/goog/events/event.js", "/closure/goog/reflect/reflect.js", "/closure/goog/events/browserevent.js", "/closure/goog/events/listener.js", "/closure/goog/useragent/jscript.js", "/closure/goog/structs/simplepool.js", "/closure/goog/events/pools.js", "/closure/goog/events/events.js", "/closure/goog/events/eventtarget.js", "/test1.js"];
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
}
"""
    }

class WSGICompile(unittest.TestCase):

    def get_app(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Raw(paths = paths, inputs = inputs))

    def get_inputApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Input(paths = paths, inputs = inputs))

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
                "parts", "closure-library", "closure-library"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Combined(
            paths = paths, default_mode = wsgi.RAW, inputs = inputs))

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
