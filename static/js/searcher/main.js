var React = require('react');
var ReactDOM = require('react-dom');
var SearchPage = require('./ui/SearchPage');

//var Clipboard = require('clipboard');

$(document).ready(function() {
  //new Clipboard('.copy-to-clipboard');
  ReactDOM.render(
    React.createElement(SearchPage),
    document.getElementById('search-page')
  )
});
