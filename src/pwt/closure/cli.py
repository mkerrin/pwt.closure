import hashlib
import optparse
import sys

import files

def main(args = None, output = None):
    if output is None:
        output = sys.stdout

    parser = optparse.OptionParser()

    parser.add_option(
        "--outputdir", dest = "outputdir", default = None,
        metavar = "OUTPUTDIR")

    parser.add_option(
        "--input", dest = "inputs", action = "append", default = [],
        metavar = "INPUTS",
        )

    parser.add_option(
        "--root", dest = "paths", action = "append", default = [],
        metavar = "ROOTS",
        )

    options, inputs = parser.parse_args(args)

    # Directory to save the comiled Java Script to
    if not options.outputdir:
        raise ValueError("Missing outputdir")

    # We can list our inputs on the command line without the --input option
    options.inputs.extend(inputs)

    # need to configure Jinja2 environment if appropriate
    try:
        options["jinja2.environment"] = files.parse_environment(options)
    except (KeyError, ValueError), err:
        pass

    tree = files.Tree(**options)
    compiled_code = tree.getCompiledSource(options.inputs)

    md5 = haslib.md5()
    md5.update(compiled_code)

    open(
        os.path.join(options.outputdir, md5.hexdigest() + ".js"),
        "w").\
        write(compiled_code)


if __name__ == "__main__":
    main(sys.argv[1:])
