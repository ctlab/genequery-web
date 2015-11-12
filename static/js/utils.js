/**
 * Created by smolcoder on 09/11/15.
 */

var ReactDOM = require('react-dom');
var ReactDOMServer = require('react-dom/server');

var Utils = {

  getCookie: function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = $.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },

  getCSRFToken: function() {
    return this.getCookie('csrftoken');
  },


  scrollToTop: function(node, speed) {
    if (node === null) {
      return;
    }
    var element = $(node);
    $('html, body').animate({scrollTop: element.offset().top}, speed == undefined ? 750 : speed);
  },

  reactElementToString: function(element) {
    return ReactDOMServer.renderToStaticMarkup(element);
  },

};

module.exports = Utils;