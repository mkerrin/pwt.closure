import unittest
import webtest
import os.path

import wsgi

class WSGICompile(unittest.TestCase):

    def get_app(self):
        paths = [
            os.path.join(
                os.path.dirname(__file__),
                "..", "..", "..",
                "parts", "closure-library", "closure-library")
            ]
        return webtest.TestApp(wsgi.Compile(paths = paths))

    def test1(self):
        app = self.get_app()
        resp = app.get("/")
