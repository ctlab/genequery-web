'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */
var Loader = require('react-loader');
var React = require('react');
var ReactDOM = require('react-dom');
var RequestForm = require('./RequestForm');
var SearchResultTable = require('./SearchResultTable');
var SearchResultRow = require('./SearchResultRow');
var ErrorBlock = require('./ErrorBlock');

var Utils = require('../../utils');

var SearchPage = React.createClass({displayName: "SearchPage",

  getInitialState: function() {
    return {
      showLoading: false,
      rows: undefined,
      recap: undefined,
      errorMessage: undefined
    };
  },

  // TODO move validation checks to separate method
  onSearchSuccess: function(data) {
    console.log('OK', data);

    this.setState({errorMessage: data.error, recap: data.recap, rows: data.rows, showLoading: false});

    // TODO do not scroll if data.rows.length == 0
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.search_result_table));
  },

  onSearchFail: function(jqxhr, textStatus, error) {
    this.setState({showLoading: false});
    console.log('FAIL', jqxhr, textStatus, error);
  },

  beforeSend: function() {
    this.setState({showLoading: true, errorMessage: undefined, recap: null, rows: null});
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.loader));
  },

  onSearchComplete: function() {
    //this.setState({showLoading: false});
  },

  render: function () {
    return (
      React.createElement("div", null, 
        React.createElement("div", {className: "row"}, 
          React.createElement("div", {className: "col-md-6"}, 
            React.createElement(RequestForm, {
              onSuccess: this.onSearchSuccess, 
              onFail: this.onSearchFail, 
              beforeSend: this.beforeSend, 
              onComplete: this.onSearchComplete, 
              ref: "request_form"}
            )
          )
        ), 
        React.createElement("div", {className: "search-results"}, 
          React.createElement("div", {className: "loader-wrap", ref: "loader"}, 
            React.createElement(Loader, {loaded: !this.state.showLoading, 
                    lines: 17, length: 31, width: 10, radius: 38, 
                    color: "#777", speed: 1.5, 
                    trail: 79, className: "spinner", 
                    zIndex: 2e9, left: "50%", scale: 0.75}, 
              this.getTableOrErrorOrNull()
            )
          )
        )
      )
    );
  },

  getTableOrErrorOrNull: function () {
    console.log(this.state);

    if (this.state.errorMessage !== undefined && this.state.errorMessage !== null) {
      return React.createElement(ErrorBlock, {message: this.state.errorMessage});
    }

    if (this.state.rows === undefined || this.state.rows === null) {
      return null;
    }

    if (this.state.rows.length == 0) {
      return React.createElement("span", null, "No results were found.");
    }

    var rows = [];
    $(this.state.rows).each((i, row) => {
      rows.push(React.createElement(SearchResultRow, React.__spread({key: i},  row)));
    });

    return React.createElement(SearchResultTable, React.__spread({},  this.state.recap, {ref: "search_result_table"}), rows);
  }

});

module.exports = SearchPage;