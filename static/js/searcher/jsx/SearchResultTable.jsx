'use strict';
var React = require('react');
var ReactDOM = require('react-dom');
var Utils = require('../../utils');
var Eventbus = require('../../eventbus');

var _ = require('underscore');

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
      Eventbus.removeListener('download-as-csv', this.downloadAsCSV);
    }
  },

  componentDidMount: function() {
    if (!this.props.fake) {
      $(window).scroll(this.onTableHeaderVisibilityChanged);
      Eventbus.addListener('download-as-csv', this.downloadAsCSV);
    }
  },

  shouldToggleStickyHeader: function() {
    return $(ReactDOM.findDOMNode(this.refs.table)).offset().top - $(window).scrollTop() < -300;
  },

  onTableHeaderVisibilityChanged: function() {
    var showFakeHeader = this.shouldToggleStickyHeader();
    $('.search-result').toggleClass('toggle-sticky-header', showFakeHeader);
    // TODO bad solution
    if (showFakeHeader) {
      var $real_header = $('.result-table th');
      var $fake_header = $('.fake-result-table th');
      for (var i = 0; i < $real_header.length; ++i) {
        $($fake_header[i]).css({'min-width': $real_header[i].offsetWidth + "px"});
      }
    }
  },

  render: function () {
    return (
      <table className={"table table-bordered table-hover " + (this.props.fake ? "fake-result-table" : "result-table")}
             ref="table">
        {this.getColGroup()}
        {this.getHeader()}
        <tbody>
          {this.props.children}
        </tbody>
      </table>
    );
  },

  downloadAsCSV: function() {
    var delimeter = ',';
    var columns = ['rank', 'log_p_value', 'series', 'platform',
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

  getHeader: function () {
    return (
      <thead>
        <tr>
          <th>#</th>
          <th>Experiment title</th>
          <th>Module</th>
          <th>log<sub>10</sub>(p<sub>value</sub>)</th>
          <th>Overlap</th>
          <th>GSE</th>
          <th>GMT</th>
        </tr>
      </thead>
    );
  },

  getColGroup: function () {
    return (
      <colgroup>
        <col className="result-table-col-num" />
        <col className="result-table-col-title" />
        <col className="result-table-col-module" />
        <col className="result-table-col-p-value" />
        <col className="result-table-col-overlap" />
        <col className="result-table-col-gse" />
        <col className="result-table-col-gmt" />
      </colgroup>
    );
  }

});

module.exports = ResultTable;