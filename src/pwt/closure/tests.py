import os.path
import shutil
import tempfile
import unittest

import paste.urlmap
import webtest
import zc.buildout.buildout
import zc.buildout.testing

import wsgi
import files

BODIES = {
    "test1": """(function() {
    CLOSURE_NO_DEPS = true;

    var files = ["http://localhost/input/closure/goog/base.js", "http://localhost/input/closure/goog/string/stringbuffer.js", "http://localhost/input/closure/goog/i18n/bidi.js", "http://localhost/input/closure/goog/debug/error.js", "http://localhost/input/closure/goog/string/string.js", "http://localhost/input/closure/goog/asserts/asserts.js", "http://localhost/input/closure/goog/array/array.js", "http://localhost/input/closure/goog/dom/classes.js", "http://localhost/input/closure/goog/object/object.js", "http://localhost/input/closure/goog/dom/tagname.js", "http://localhost/input/closure/goog/useragent/useragent.js", "http://localhost/input/closure/goog/math/size.js", "http://localhost/input/closure/goog/dom/browserfeature.js", "http://localhost/input/closure/goog/math/math.js", "http://localhost/input/closure/goog/math/coordinate.js", "http://localhost/input/closure/goog/dom/dom.js", "http://localhost/input/closure/goog/structs/inversionmap.js", "http://localhost/input/closure/goog/i18n/graphemebreak.js", "http://localhost/input/closure/goog/format/format.js", "http://localhost/input/closure/goog/i18n/bidiformatter.js", "http://localhost/input/soyutils_usegoog.js", "http://localhost/input/test1.soy", "http://localhost/input/test1.js"];
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

    "test2": """(function() {
    CLOSURE_NO_DEPS = true;

    var files = ["http://localhost/input/closure/goog/base.js", "http://localhost/input/closure/goog/string/stringbuffer.js", "http://localhost/input/closure/goog/i18n/bidi.js", "http://localhost/input/closure/goog/debug/error.js", "http://localhost/input/closure/goog/string/string.js", "http://localhost/input/closure/goog/asserts/asserts.js", "http://localhost/input/closure/goog/array/array.js", "http://localhost/input/closure/goog/dom/classes.js", "http://localhost/input/closure/goog/object/object.js", "http://localhost/input/closure/goog/dom/tagname.js", "http://localhost/input/closure/goog/useragent/useragent.js", "http://localhost/input/closure/goog/math/size.js", "http://localhost/input/closure/goog/dom/browserfeature.js", "http://localhost/input/closure/goog/math/math.js", "http://localhost/input/closure/goog/math/coordinate.js", "http://localhost/input/closure/goog/dom/dom.js", "http://localhost/input/closure/goog/structs/inversionmap.js", "http://localhost/input/closure/goog/i18n/graphemebreak.js", "http://localhost/input/closure/goog/format/format.js", "http://localhost/input/closure/goog/i18n/bidiformatter.js", "http://localhost/input/soyutils_usegoog.js", "http://localhost/input/test1.soy", "http://localhost/input/test2.js", "http://localhost/input/test1.js"];
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
    CLOSURE_NO_DEPS = true;

    var files = ["http://localhost/js/input/closure/goog/base.js", "http://localhost/js/input/closure/goog/string/stringbuffer.js", "http://localhost/js/input/closure/goog/i18n/bidi.js", "http://localhost/js/input/closure/goog/debug/error.js", "http://localhost/js/input/closure/goog/string/string.js", "http://localhost/js/input/closure/goog/asserts/asserts.js", "http://localhost/js/input/closure/goog/array/array.js", "http://localhost/js/input/closure/goog/dom/classes.js", "http://localhost/js/input/closure/goog/object/object.js", "http://localhost/js/input/closure/goog/dom/tagname.js", "http://localhost/js/input/closure/goog/useragent/useragent.js", "http://localhost/js/input/closure/goog/math/size.js", "http://localhost/js/input/closure/goog/dom/browserfeature.js", "http://localhost/js/input/closure/goog/math/math.js", "http://localhost/js/input/closure/goog/math/coordinate.js", "http://localhost/js/input/closure/goog/dom/dom.js", "http://localhost/js/input/closure/goog/structs/inversionmap.js", "http://localhost/js/input/closure/goog/i18n/graphemebreak.js", "http://localhost/js/input/closure/goog/format/format.js", "http://localhost/js/input/closure/goog/i18n/bidiformatter.js", "http://localhost/js/input/soyutils_usegoog.js", "http://localhost/js/input/test1.soy", "http://localhost/js/input/test1.js"];
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
                "..", "..", "..", "checkouts", "closure"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(
            wsgi.Raw(tree = files.Tree(paths = paths, inputs = inputs)))

    def get_inputApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(
            wsgi.Input(tree = files.Tree(paths = paths, inputs = inputs)))

    def test_secure_input_app(self):
        app = self.get_inputApp(["test1.js"])
        resp = app.get("/etc/password", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

    def test_compile_raw1(self):
        app = self.get_app(["test1.js"])
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1"])

    def test_compile_raw2(self):
        app = self.get_app(["test1.js"])
        resp = app.get("/?input=test1.js&input=test2.js")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test2"])

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
                "..", "..", "..", "checkouts", "closure"),
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Combined(
            tree = files.Tree(paths = paths, inputs = inputs)))

    def test_combined1(self):
        app = self.get_combined(["test1.js"])
        resp = app.get("/", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

    def test_combined2(self):
        app = self.get_combined(["test1.js"])
        resp = app.get("/compile")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1"])

    def test_combined3(self):
        app = self.get_combined(["test1.js"])
        resp = app.get("/input", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

    def test_combined3(self):
        app = self.get_combined(["test1.js"])
        resp = app.get("/input/closure/goog/base.js")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")

    def get_subApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"
                ),
            os.path.join(os.path.dirname(__file__)),
            ]
        urlmap = paste.urlmap.URLMap()
        urlmap["/js"] = wsgi.Combined(
            tree = files.Tree(paths = paths, inputs = inputs))
        return webtest.TestApp(urlmap)

    def test_sub_combined1(self):
        app = self.get_subApp(["test1.js"])
        resp = app.get("/js/compile")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assertEqual(resp.body, BODIES["test1_js"])

    def get_compileApp(self, inputs):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"),
            os.path.join(os.path.dirname(__file__)),
            ]
        app = wsgi.Compile(
            tree = files.Tree(paths = paths, inputs = inputs))
        return webtest.TestApp(app)

    def test_compile1(self):
        app = self.get_compileApp(["test1.js"])
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assert_(resp.content_length > 0)

    def test_compile2(self):
        # XXX - update test to make sure that we pull in the extra Java Script
        # source specified
        app = self.get_compileApp(["test1.js"])
        resp = app.get("/?input=test1.js&input=test2.js")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        self.assert_(resp.content_length > 0)

    def test_paste_integration1(self):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"),
            os.path.join(os.path.dirname(__file__)),
            ]
        app = webtest.TestApp(
            wsgi.paste_combined_closure(
                {},
                inputs = "",
                paths = "\n".join(paths),
                )
            )

        resp = app.get("/", expect_errors = True)
        self.assertEqual(resp.status_int, 404)

        resp = app.get("/input/test1.js")
        self.assertEqual(resp.status_int, 200)


class WSGICompile2(unittest.TestCase):
    # We need to fix the closure tree when generating deps.js files as
    # otherwise we will get different output based on the version
    # of the closure library that we are using.

    def setUp(self):
        self.root = tempfile.mkdtemp()

        self.writefile("base.js", "goog.provide('goog');\n")

    def tearDown(self):
        shutil.rmtree(self.root)

    def writefile(self, name, contents):
        filename = os.path.join(self.root, name)
        open(filename, "w").write(contents)
        return filename

    def get_DepsApp(self):
        paths = [
            self.root,
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(
            wsgi.Deps(tree = files.Tree(paths = paths)))

    def test_deps1(self):
        app = self.get_DepsApp()
        resp = app.get("/")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        expectedBody = open(
            os.path.join(os.path.dirname(__file__), "test_deps1.js")).read()
        self.assertEqual(resp.body, expectedBody)

    def get_combined(self, inputs):
        paths = [
            self.root,
            os.path.join(os.path.dirname(__file__)),
            ]
        return webtest.TestApp(wsgi.Combined(
            tree = files.Tree(paths = paths, inputs = inputs)))

    def test_combined_deps1(self):
        app = self.get_combined(["test1.js"])
        resp = app.get("/deps")
        self.assertEqual(resp.status_int, 200)
        self.assertEqual(resp.content_type, "application/javascript")
        expectedBody = open(
            os.path.join(
                os.path.dirname(__file__), "test_deps1.js"
                )
            ).read()
        self.assertEqual(resp.body, expectedBody)


class TestFiles(unittest.TestCase):

    def setUp(self):
        self.root1 = tempfile.mkdtemp()
        self.writefile1("base.js", "goog.provide('goog');\n")

    def tearDown(self):
        shutil.rmtree(self.root1)

    def writefile1(self, name, contents):
        filename = os.path.join(self.root1, name)
        open(filename, "w").write(contents)
        return filename

    def test_tree1(self):
        # If we don't update the tree we don't have access to the path_info
        tree = files.Tree(paths = [self.root1])
        # tree.update()
        self.assertEqual(tree.path_info, None)
        tree.update()
        self.assertNotEqual(tree.path_info, None)

    def test_tree2(self):
        # We need to update the tree
        tree = files.Tree(paths = [self.root1])
        tree.update()
        info = dict(
            [(key, val.GetPath()) for key, val in tree.path_info.items()])
        self.assertEqual(info, {"/base.js": "%s/base.js" % self.root1})

    def test_deps1(self):
        tree = files.Tree(paths = [self.root1])
        self.assertRaises(ValueError, tree.getDeps, "")

    def test_deps2(self):
        # test getDeps with full filename
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree(paths = [self.root1])
        deps = tree.getDeps([filename])
        self.assertEqual(len(deps), 2)
        self.assertEqual(
            [d.GetPath() for d in deps],
            ["%s/base.js" % self.root1, "%s/app.js" % self.root1])

    def test_deps3(self):
        # test getDeps with just the path info
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree(paths = [self.root1])
        deps = tree.getDeps(["app.js"])
        self.assertEqual(len(deps), 2)
        self.assertEqual(
            [d.GetPath() for d in deps],
            ["%s/base.js" % self.root1, "%s/app.js" % self.root1])

    def test_deps4(self):
        # default inputs
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree(paths = [self.root1], inputs = ["app.js"])
        deps = tree.getDeps()
        self.assertEqual(len(deps), 2)
        self.assertEqual(
            [d.GetPath() for d in deps],
            ["%s/base.js" % self.root1, "%s/app.js" % self.root1])

    def test_source1(self):
        filename = self.writefile1("app.js", """goog.provide('app');\n""")
        tree = files.Tree(paths = [self.root1])
        src = tree.getSource("/base.js")
        self.assertEqual(src.GetSource(), "goog.provide('goog');\n")


class ClosureTemplatesTestCase(unittest.TestCase):

    def setUp(self):
        self.root1 = tempfile.mkdtemp()
        self.writefile1("base.js", "goog.provide('goog');\n")
        self.writefile1("soy.js", """goog.provide('soy.StringBuilder');
goog.provide('soy');""")

    def tearDown(self):
        shutil.rmtree(self.root1)

    def writefile1(self, name, contents):
        filename = os.path.join(self.root1, name)
        open(filename, "w").write(contents)
        return filename

    def test_source_scan1(self):
        filename = self.writefile1("test.soy", """{namespace examples.soy}

{template .helloWorld}Hello{/template}""")

        source = files.SoySource(files.Tree(paths = [self.root1]), filename)
        self.assertEqual(source.provides, set(["examples.soy"]))
        self.assertEqual(source.requires, set(["soy", "soy.StringBuilder"]))

    def test_source_scan2(self):
        filename = self.writefile1("test.soy", """{namespace examples.soy2}

{template .helloWorld}Hello{/template}""")

        source = files.SoySource(files.Tree(paths = [self.root1]), filename)
        self.assertEqual(source.provides, set(["examples.soy2"]))
        self.assertEqual(source.requires, set(["soy", "soy.StringBuilder"]))

    def test_source_scan3(self):
        filename = self.writefile1("test.soy", """{namespace examples.soy}
{namespace examples.soy2}

{template .helloWorld}Hello{/template}""")

        class DummyTree(object):
            pass

        source = files.SoySource(DummyTree(), filename)
        self.assertEqual(
            source.provides, set(["examples.soy", "examples.soy2"]))
        self.assertEqual(source.requires, set(["soy", "soy.StringBuilder"]))

    def test_files1(self):
        filename = self.writefile1("test.soy", """{namespace examples.soy}
/** */
{template .helloWorld}
Hello
{/template}
""")

        tree = files.Tree(paths = [self.root1])
        source = tree.getSource("/test.soy")
        self.assertEqual(source.GetSource(), """// This file was automatically generated from test.soy.
// Please don't edit this file by hand.

goog.provide('examples.soy');

goog.require('soy');
goog.require('soy.StringBuilder');


examples.soy.helloWorld = function(opt_data, opt_sb) {
  var output = opt_sb || new soy.StringBuilder();
  output.append('Hello');
  if (!opt_sb) return output.toString();
};
""")


class RecipeTestCase(unittest.TestCase):

    def setUp(self):
        base = tempfile.mkdtemp("buildoutSetUp")
        self.base = os.path.realpath(base)

        self.cwd = os.getcwd()

        # XXX - when we run the recipe in the test buildout upgrades itself and
        # installs a new version of setuptools and zc.buildout but never
        # reuses the ones installed by the buildout to generate the test
        # scripts.
        self.builddir = os.path.join(self.base, "_TEST_")
        os.mkdir(self.builddir)
        self.media = os.path.join(self.builddir, "media")
        os.mkdir(self.media)

        # Nothing so far
        compiled = os.listdir(self.media)
        self.assertEqual(len(compiled), 0)

        deggs = os.path.join(self.builddir, "develop-eggs")
        os.mkdir(deggs)

        zc.buildout.testing.install_develop("setuptools", deggs)
        zc.buildout.testing.install_develop("zc.buildout", deggs)
        zc.buildout.testing.install_develop("pwt.closure", deggs)
        zc.buildout.testing.install_develop("Paste", deggs)
        zc.buildout.testing.install_develop("WebOb", deggs)

    def tearDown(self):
        shutil.rmtree(self.base)
        os.chdir(self.cwd)

    def test_compiled_recipe(self):
        closure_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"
                )
            )

        open(os.path.join(self.builddir, "buildout.cfg"), "w").write("""
[buildout]
parts = compiled.js

[compiled.js]
recipe = pwt.closure:compile
paths =
    %(closure)s
    %(pwt.closure)s

inputs = %(inputs)s

outputdir = %(media)s
""" % {"closure": closure_path,
       "pwt.closure": os.path.dirname(__file__),
       "inputs": os.path.join(os.path.dirname(__file__), "test1.js"),
       "media": self.media,
       })

        os.chdir(self.builddir)
        config = [
            ("buildout", "log-level", "WARNING"),
            ("buildout", "offline", "true"),
            ("buildout", "newest", "false"),
            ]
        zc.buildout.buildout.Buildout(
            "buildout.cfg", config, user_defaults = False,
            ).bootstrap([])

        buildout = os.path.join(self.builddir, "bin", "buildout")
        os.system(buildout)

        compiled = os.listdir(self.media)
        self.assertEqual(len(compiled), 1)
        self.assert_(compiled[0].endswith(".js"))

    def test_deps_recipe(self):
        closure_path = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..", "checkouts", "closure"
                )
            )

        open(os.path.join(self.builddir, "buildout.cfg"), "w").write("""
[buildout]
parts = deps.js

[deps.js]
recipe = pwt.closure:deps
paths =
    %(closure)s
    %(pwt.closure)s

deps_js = %(media)s/deps.js
""" % {"closure": closure_path,
       "pwt.closure": os.path.dirname(__file__),
       "inputs": os.path.join(os.path.dirname(__file__), "test1.js"),
       "media": self.media,
       })

        os.chdir(self.builddir)
        config = [
            ("buildout", "log-level", "WARNING"),
            ("buildout", "offline", "true"),
            ("buildout", "newest", "false"),
            ]
        zc.buildout.buildout.Buildout(
            "buildout.cfg", config, user_defaults = False,
            ).bootstrap([])

        buildout = os.path.join(self.builddir, "bin", "buildout")
        os.system(buildout)

        deps = os.listdir(self.media)
        self.assertEqual(len(deps), 1)
        self.assertEqual(deps[0], "deps.js")
