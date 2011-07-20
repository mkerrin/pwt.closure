import os.path
import paste.urlmap
import shutil
import tempfile
import unittest
import webtest

import wsgi
import files

BODIES = {
    "test1": """(function() {
    var files = ["http://localhost/input/closure/goog/base.js", "http://localhost/input/closure/goog/string/string.js", "http://localhost/input/closure/goog/useragent/jscript.js", "http://localhost/input/closure/goog/string/stringbuffer.js", "http://localhost/input/closure/goog/i18n/bidi.js", "http://localhost/input/closure/goog/debug/error.js", "http://localhost/input/closure/goog/asserts/asserts.js", "http://localhost/input/closure/goog/array/array.js", "http://localhost/input/closure/goog/dom/classes.js", "http://localhost/input/closure/goog/object/object.js", "http://localhost/input/closure/goog/dom/tagname.js", "http://localhost/input/closure/goog/useragent/useragent.js", "http://localhost/input/closure/goog/math/size.js", "http://localhost/input/closure/goog/dom/browserfeature.js", "http://localhost/input/closure/goog/math/coordinate.js", "http://localhost/input/closure/goog/dom/dom.js", "http://localhost/input/closure/goog/structs/inversionmap.js", "http://localhost/input/closure/goog/i18n/graphemebreak.js", "http://localhost/input/closure/goog/format/format.js", "http://localhost/input/closure/goog/i18n/bidiformatter.js", "http://localhost/input/soyutils_usegoog.js", "http://localhost/input/test1.soy", "http://localhost/input/test1.js"];
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
    var files = ["http://localhost/js/input/closure/goog/base.js", "http://localhost/js/input/closure/goog/string/string.js", "http://localhost/js/input/closure/goog/useragent/jscript.js", "http://localhost/js/input/closure/goog/string/stringbuffer.js", "http://localhost/js/input/closure/goog/i18n/bidi.js", "http://localhost/js/input/closure/goog/debug/error.js", "http://localhost/js/input/closure/goog/asserts/asserts.js", "http://localhost/js/input/closure/goog/array/array.js", "http://localhost/js/input/closure/goog/dom/classes.js", "http://localhost/js/input/closure/goog/object/object.js", "http://localhost/js/input/closure/goog/dom/tagname.js", "http://localhost/js/input/closure/goog/useragent/useragent.js", "http://localhost/js/input/closure/goog/math/size.js", "http://localhost/js/input/closure/goog/dom/browserfeature.js", "http://localhost/js/input/closure/goog/math/coordinate.js", "http://localhost/js/input/closure/goog/dom/dom.js", "http://localhost/js/input/closure/goog/structs/inversionmap.js", "http://localhost/js/input/closure/goog/i18n/graphemebreak.js", "http://localhost/js/input/closure/goog/format/format.js", "http://localhost/js/input/closure/goog/i18n/bidiformatter.js", "http://localhost/js/input/soyutils_usegoog.js", "http://localhost/js/input/test1.soy", "http://localhost/js/input/test1.js"];
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

DEFAULT_COMPILER_JAR = os.path.join(
    os.path.dirname(__file__),
    "jars",
    "compiler.jar")

class WSGICompile(unittest.TestCase):

    def get_app(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(
            wsgi.Raw(files = files.Tree(paths), inputs = inputs))

    def get_inputApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library/"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(
            wsgi.Input(files = files.Tree(paths), inputs = inputs))

    def test_secure_input_app(self):
        app = self.get_inputApp(
            [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/etc/password", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

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
            files = files.Tree(paths), inputs = inputs))

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
            files = files.Tree(paths), inputs = inputs)
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
            files = files.Tree(paths), inputs = inputs,
            compiler_jar = DEFAULT_COMPILER_JAR)
        return webtest.TestApp(app)

    def test_compile1(self):
        app = self.get_compileApp(
            inputs = [os.path.join(os.path.dirname(__file__), "test1.js")])
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assert_(resp.content_length > 0)


class TestFiles(unittest.TestCase):

    def setUp(self):
        self.root1 = tempfile.mkdtemp()
        # 
        self.writefile1("base.js", "goog.provide('goog');\n")

    def tearDown(self):
        shutil.rmtree(self.root1)

    def writefile1(self, name, contents):
        filename = os.path.join(self.root1, name)
        open(filename, "w").write(contents)
        return filename

    def test_tree1(self):
        tree = files.Tree([self.root1])
        info = dict(
            [(key, val.GetPath()) for key, val in tree.path_info.items()])
        self.assertEqual(info, {"/base.js": "%s/base.js" % self.root1})

    def test_deps1(self):
        tree = files.Tree([self.root1])
        self.assertRaises(ValueError, tree.getDeps, "")

    def test_deps2(self):
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree([self.root1])
        deps = tree.getDeps([filename])
        self.assertEqual(len(deps), 2)
        self.assertEqual(
            [d.GetPath() for d in deps],
            ["%s/base.js" % self.root1, "%s/app.js" % self.root1])

    def test_source1(self):
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree([self.root1])
        src = tree.getSource("/base.js")
        self.assertEqual(src.GetSource(), "goog.provide('goog');\n")
