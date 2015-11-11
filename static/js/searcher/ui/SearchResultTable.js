'use strict';
var React = require('react');
var ReactDOM = require('react-dom');
var SearchResultRow = require('./SearchResultRow');

require('floatthead');


// TODO how to implement this using CSS only?
var TABLE_HEADER_CONFIG = [
  {'width': 2, 'title': '#'},
  {'width': 70, 'title': 'Experiment title'},
  {'width': 2, 'title': 'Module'},
  {'width': 6, 'title': 'p-value'},
  {'width': 7, 'title': 'Overlap'},
  {'width': 5, 'title': 'GSE'},
  {'width': 5, 'title': 'GMT'}
];

var ResultTable = React.createClass({displayName: "ResultTable",

  // TODO describe PropTypes

  componentWillUnmount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead('destroy');
  },

  componentDidMount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead();
  },

  render: function () {
    return (
      React.createElement("table", {className: "table table-bordered table-hover", ref: "table"}, 
        React.createElement("colgroup", null, this.getColConfig()), 
        React.createElement("thead", {className: "tableFloatingHeaderOriginal"}, 
          this.getHeaderRecap(), 
          this.getHeaderTitles()
        ), 
        React.createElement("tbody", null, 
          this.props.children
        )
      )
    );
  },

  getHeaderRecap: function() {
    var recap = this.props;
    return (
      React.createElement("tr", {className: "search-result-recap"}, 
        React.createElement("th", {colSpan: "4", className: "no-right-border"}, 
          "Entered ", recap.genes_entered, " genes in ", recap.id_format, " format," + ' ' +
          "where ", recap.unique_entez, " unique Entrez IDs." + ' ' +
          "Found ", recap.total, " modules in ", recap.time, " sec."
        ), 
        React.createElement("th", {colSpan: "1", className: "no-right-border no-left-border"}, React.createElement("a", null, "To top")), 
        React.createElement("th", {colSpan: "2", className: "no-left-border"}, 
          React.createElement("input", {type: "submit", value: "Download as CSV", id: "csv-download", className: "btn btn-primary btn-xs"})
        )
      )
    );
  },

  getHeaderTitles: function () {
    return (
      React.createElement("tr", null, 
        TABLE_HEADER_CONFIG.map((config, i) => React.createElement("th", {key: i}, config.title))
      )
    );
  },

  getColConfig: function () {
    return TABLE_HEADER_CONFIG.map((config, i) => {
      var style = {width: config.width + '%'};
      return React.createElement("col", {key: i, style: style});
    });
  }

});

module.exports = ResultTable;