'use strict';
var React = require('react');
var ReactDOM = require('react-dom');
var Utils = require('../../utils');

var _ = require('underscore');

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

  propTypes: {
    recap: React.PropTypes.object.isRequired
  },

  componentWillUnmount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead('destroy');
  },

  componentDidMount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead();
  },

  render: function () {
    console.log(this.props.children[0]);
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
    var recap = this.props.recap;
    return (
      React.createElement("tr", {className: "search-result-recap"}, 
        React.createElement("th", {colSpan: "4", className: "no-right-border"}, 
          "Entered ", recap.genes_entered, " genes in ", recap.id_format, " format," + ' ' +
          "where ", recap.unique_entez, " unique Entrez IDs." + ' ' +
          "Found ", recap.total, " modules in ", recap.time, " sec."
        ), 
        React.createElement("th", {colSpan: "1", className: "no-right-border no-left-border"}, React.createElement("a", null, "To top")), 
        React.createElement("th", {colSpan: "2", className: "no-left-border"}, 
          React.createElement("button", {className: "btn btn-primary btn-xs", onClick: this.downloadAsCSV}, "Download as CSV")
        )
      )
    );
  },

  downloadAsCSV: function() {
    var delimeter = ',';
    var columns = ['rank', 'adjusted_score', 'series', 'platform',
                   'module_number', 'overlap_size', 'module_size', 'title'];
    var content = [columns.join(delimeter)];
    _.each(this.props.children, row => {
      var csv_row = _.map(columns, field => {
        if (field === 'title') {
          return '"' + row.props[field] + '"';
        }
        return row.props[field];
      });
      content.push(csv_row.join(delimeter))
    });

    var now = new Date();
    var dateString = now.getHours() + "-" + now.getMinutes() + "_"
      + now.getMonth() + "-" + (now.getDay() + 1) + "-" + now.getFullYear();
    var filename = 'genequery_search_result_' + dateString + '.csv';

    Utils.downloadDataAsCSV(filename, content.join('\n'));
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