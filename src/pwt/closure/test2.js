goog.provide('testApplication2');

goog.require('testapp')

soy.renderElement(goog.dom.getElement('output'), testapp.hello);
