'use strict';
var React = require('react');
var SearchResultRow = require('./SearchResultRow');

var _ = require('underscore');

/**
 * Table with enrichment result. Rows are to be sorted before rendering.
 */
var ResultTable = React.createClass({
  propTypes: {
    listOfModuleDataObjects: React.PropTypes.arrayOf(React.PropTypes.object).isRequired
  },

  render: function () {
    var enrichedModules = [];
    _.each(this.props.listOfModuleDataObjects, (data) => {
      enrichedModules.push(
        <SearchResultRow key={data.series + data.platform + data.module_number} {...data} />
      );
    });
    enrichedModules = _.sortBy(enrichedModules, (element) => element.props.log_adj_p_value);

    return (
      <table className="table table-hover result-table">
        <colgroup>
          <col className="result-table-col-num" />
          <col className="result-table-col-title" />
          <col className="result-table-col-module" />
          <col className="result-table-col-adj-p-value" />
          <col className="result-table-col-overlap" />
          <col className="result-table-col-gse" />
          <col className="result-table-col-gmt" />
        </colgroup>
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
        <tbody>
          {enrichedModules}
        </tbody>
      </table>
    );
  }
});

module.exports = ResultTable;