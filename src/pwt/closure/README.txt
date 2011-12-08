WSGI integration
================

/compile

 * 

/input

 * /input/closure/goog/base.js
 * /input/relief/auth/auth_manager.js

This also works with Closure Templates and it will return JavaScript

 * /input/relief/handlers/handlers.soy

reload
------

pwt.closure integrates with paste servers reload functionality. So if you
change any Java Script file then the server will restart, refreshing the
internal Java Script tree.


zc.buildout integration
=======================


cli integration
===============


TODO
====

 * Need common configuration between cli, buildout, and wsgi

 * Need default configuration that works out of the box

 * Internationalization needs to be considered in the generation of templates
   and in the compilation stages.

 * Need to be able to configure a mapping from file extensions to a callable
   that will compile any templates to javascript
