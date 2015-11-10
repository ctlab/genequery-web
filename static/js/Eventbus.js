/**
 * Created by smolcoder on 09/11/15.
 */

var Eventbus;

define(['eventEmitter'], function (eventEmitter) {
  if (Eventbus === undefined) {
    Eventbus = new eventEmitter();
  }
  return Eventbus;
});