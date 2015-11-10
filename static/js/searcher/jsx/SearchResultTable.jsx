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

var ResultTable = React.createClass({

  // TODO describe PropTypes

  componentWillUnmount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead('destroy');
  },

  componentDidMount: function() {
    $(ReactDOM.findDOMNode(this.refs.table)).floatThead();
  },

  render: function () {
    return (
      <table className="table table-bordered table-hover" ref="table">
        <colgroup>{this.getColConfig()}</colgroup>
        <thead className="tableFloatingHeaderOriginal">
          {this.getHeaderRecap()}
          {this.getHeaderTitles()}
        </thead>
        <tbody>
          {this.props.children}
        </tbody>
      </table>
    );
  },

  getHeaderRecap: function() {
    var recap = this.props;
    return (
      <tr className="search-result-recap">
        <th colSpan="4" className="no-right-border">
          Entered {recap.genes_entered} genes in {recap.id_format} format,
          where {recap.unique_entez} unique Entrez IDs.
          Found {recap.total} modules in {recap.time} sec.
        </th>
        <th colSpan="1" className="no-right-border no-left-border"><a>To top</a></th>
        <th colSpan="2" className="no-left-border">
          <input type="submit" value="Download as CSV" id="csv-download" className="btn btn-primary btn-xs" />
        </th>
      </tr>
    );
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