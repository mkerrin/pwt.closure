goog.provide('testApplication');

goog.require('testapp')

goog.require('goog.events.EventTarget');

soy.renderElement(goog.dom.getElement('output'), testapp.hello);
