import os.path

import jinja2.visitor
import jinja2.compiler
import jinja2.environment

import pwt.jinja2js.jscompiler
import pwt.jinja2js.environment

import files

class Source(jinja2.visitor.NodeVisitor):
    """
    Source object for Jinja2 templates that we can compile to Java Script

    We require a Jinja2 environment in order to start to compile the templates.

    
    """

    def __init__(self, tree, path):
        self._tree = tree
        self.env = tree.config["jinja2.environment"]

        self.source = files.source.GetFileContents(path).decode("utf-8")
        self.node = self.env._parse(
            self.source,
            os.path.basename(path),
            path)

        self._path = path

        self.provides = set([])
        # Manually added
        self.requires = set(["goog.string", "goog.string.StringBuffer"])
        self.visit(self.node)

    def GetSource(self):
        return pwt.jinja2js.jscompiler.generateClosure(
            self.node,
            self.env,
            os.path.basename(self._path),
            self._path)

    def GetPath(self):
        # I want files.py to call GetSource when compiling Java Script templates
        return None

    def visit_NamespaceNode(self, node):
        self.provides.add(node.namespace.encode("utf-8"))

    def visit_Import(self, node):
        name = node.template.value
        source, filename, uptodate = self.env.loader.get_source(self.env, name)
        fromnode = self.env._parse(source, name, filename)

        # Need to find the namespace
        namespace = list(fromnode.find_all(nodes.NamespaceNode))
        if len(namespace) != 1:
            raise jinja2.compiler.TemplateAssertionError(
                "You must supply one namespace for your template",
                0,
                name,
                filename)
        namespace = namespace[0].namespace

        self.requires.add(namespace.encode("utf-8"))
