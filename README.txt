pwt.closure is Python package that provides the tools to compile and manage
JavaScript files. It is optimized to be used with the Closure Library to find
your web application JavaScript dependencies. It then uses the Closure
Compiler to concatenate and compile all your JavaScript to JavaScript that
is optimized for production.

pwt.closure contains a command line tool, a WSGI application and integration
with zc.buildout. All are configured through the same .ini file. The WSGI
application is suited for developing JavaScript heavy applications and is
used manly for development. Once development is finished you can use the
command line tool to optimize the application by compiling all your JavaScript
into one optimized file. Or you can integrate the process with zc.buildout.
