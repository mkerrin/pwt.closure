goog.provide('testApplication');

goog.require('testapp')

soy.renderElement(goog.dom.getElement('output'), testapp.hello);
