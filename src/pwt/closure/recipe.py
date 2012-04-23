import hashlib
import os.path

import files

def getTree(options):
    config = options.copy()
    config["inputs"] = options.get("inputs", "").split()
    config["paths"] = options["paths"].split()
    compiler_jar = options.get("compiler_jar", None)
    if compiler_jar:
        config["compiler_jar"] = compiler_jar
    config["compiler_flags"] = options.get("compiler_flags", "").split()
    # need to configure Jinja2 environment if appropriate
    try:
        config["jinja2.environment"] = files.parse_environment(options)
    except (KeyError, ValueError), err:
        pass

    return files.Tree(**config)


class CompileRecipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        tree = getTree(options)

        self.compiled_code = tree.getCompiledSource()

        md5name = hashlib.md5()
        md5name.update(self.compiled_code)
        self.options["filename"] = self.filename = md5name.hexdigest() + ".js"

    def install(self):
        filename = os.path.join(self.options["outputdir"], self.filename)
        open(filename, "w").write(self.compiled_code)
        return (filename,)

    def update(self):
        return self.install()


class DepsRecipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        tree = getTree(options)

        self.compiled_code = files.MakeDepsFile(tree)

    def install(self):
        open(self.options["deps_js"], "w").write(self.compiled_code)
        return (self.options["deps_js"],)

    def update(self):
        return self.install()
