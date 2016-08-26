var React = require('react');
var ReactDOM = require('react-dom');
var SearchPage = require('./ui/SearchPage');

$(document).ready(function() {
  ReactDOM.render(
    React.createElement(SearchPage),
    document.getElementById('search-page')
  );
});