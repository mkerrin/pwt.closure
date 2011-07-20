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
        "--root", dest = "roots", action = "append", default = [],
        metavar = "ROOTS",
        )

    options, inputs = parser.parse_args(args)

    #
    if not options.outputdir:
        raise ValueError("Missing outputdir")

    # 
    options.inputs.extend(inputs)

    tree = files.Tree(options.roots)
    compiled_code = tree.getCompiledSource(options.inputs)

    md5 = haslib.md5()
    md5.update(compiled_code)

    open(
        os.path.join(options.outputdir, md5.hexdigest() + ".js"),
        "w").\
        write(compiled_code)


if __name__ == "__main__":
    main(sys.argv[1:])
