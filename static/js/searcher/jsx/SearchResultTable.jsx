'use strict';
var React = require('react');
var ReactDOM = require('react-dom');

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
  },

  componentDidMount: function() {
    if (!this.props.fake) {
      $(window).scroll(this.onTableHeaderVisibilityChanged);
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
      <table className={"table table-hover " + (this.props.fake ? "fake-result-table" : "result-table")}
             ref="table">
        {this.getColGroup()}
        {this.getHeader()}
        <tbody>
          {this.props.children}
        </tbody>
      </table>
    );
  },

  getHeader: function () {
    return (
      <thead>
        <tr>
          <th>#</th>
          <th>Experiment title</th>
          <th>Module</th>
          <th>log<sub>10</sub>(adj.p<sub>value</sub>)</th>
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
        <col className="result-table-col-adj-p-value" />
        <col className="result-table-col-overlap" />
        <col className="result-table-col-gse" />
        <col className="result-table-col-gmt" />
      </colgroup>
    );
  }

});

module.exports = ResultTable;