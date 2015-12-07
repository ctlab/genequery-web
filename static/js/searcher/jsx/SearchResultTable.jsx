'use strict';
var React = require('react');
var ReactDOM = require('react-dom');
var Utils = require('../../utils');
var Eventbus = require('../../eventbus');

var _ = require('underscore');

// TODO how to implement this using CSS only?
// TODO inline this
var TABLE_HEADER_CONFIG = [
  {'width': 2, 'title': '#'},
  {'width': 70, 'title': 'Experiment title'},
  {'width': 2, 'title': 'Module'},
  {'width': 6, 'title': 'p-value'},
  {'width': 7, 'title': 'Overlap'},
  {'width': 5, 'title': 'GSE'},
  {'width': 5, 'title': 'GMT'}
];

var ResultTable = React.createClass({

  propTypes: {
    fake: React.PropTypes.bool
  },

  getDefaultProps: function() {
    return {
      fake: false
    };
  },

  componentWillUnmount: function() {
    if (!this.props.fake) {
      $(window).off('scroll', this.onTableHeaderVisibilityChanged);
    }
    Eventbus.removeListener('download-as-csv', this.downloadAsCSV);
  },

  componentDidMount: function() {
    if (!this.props.fake) {
      $(window).scroll(this.onTableHeaderVisibilityChanged);
    }
    Eventbus.addListener('download-as-csv', this.downloadAsCSV);
  },

  shouldToggleStickyHeader: function() {
    return $(ReactDOM.findDOMNode(this.refs.table)).offset().top - $(window).scrollTop() < -400;
  },

  onTableHeaderVisibilityChanged: function() {
    $('.search-result').toggleClass('toggle-sticky-header', this.shouldToggleStickyHeader());
  },

  render: function () {
    return (
      <table className="table table-bordered table-hover" ref="table">
        <colgroup>{this.getColConfig()}</colgroup>
        <thead className="tableFloatingHeaderOriginal">
          {this.getHeaderTitles()}
        </thead>
        <tbody>
          {this.props.children}
        </tbody>
      </table>
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
      <tr>
        {TABLE_HEADER_CONFIG.map((config, i) => <th key={i}>{config.title}</th>)}
      </tr>
    );
  },

  getColConfig: function () {
    return TABLE_HEADER_CONFIG.map((config, i) => {
      var style = {width: config.width + '%'};
      return <col key={i} style={style} />;
    });
  }

});

module.exports = ResultTable;