import hashlib
import os.path

import files

class CompileRecipe(object):

    def __init__(self, buildout, name, options):
        self.buildout = buildout
        self.name = name
        self.options = options

        config = options.copy()
        config["inputs"] = options["inputs"].split()
        tree = files.Tree(options["roots"].split(), config)
        self.compiled_code = tree.getCompiledSource()

        md5name = hashlib.md5()
        md5name.update(self.compiled_code)
        self.options["filename"] = self.filename = md5name.hexdigest() + ".js"

    def install(self):
        open(
            os.path.join(self.options["outputdir"], self.filename),
            "w"). \
            write(self.compiled_code)
        return (self.filename,)

    def update(self):
        return self.install()
