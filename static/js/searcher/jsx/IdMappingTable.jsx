'use strict';
/**
 * Created by smolcoder on 30/11/15.
 */

var React = require('react');

var _ = require('underscore');

var NOT_ANNOTATED_MSG = '(not annotated)';
var GENECARDS_URL_PREF = 'http://www.genecards.org/cgi-bin/carddisp.pl?gene=';

var IdMappingTable = React.createClass({
  propTypes: {
    inputGenesToFinalEntrez: React.PropTypes.objectOf(React.PropTypes.number).isRequired,
    inputGenes: React.PropTypes.array.isRequired
  },

  render: function () {
    return (
      <table className="table table-bordered table-hover id-mapping-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Input gene</th>
            <th>Entrez</th>
          </tr>
        </thead>
        <tbody>
          {this.getRows()}
        </tbody>
      </table>
    );
  },

  getRows: function() {
    var to_entrez = this.props.inputGenesToFinalEntrez;

    return  _.chain(this.props.inputGenes).map((gene, i) => {
        return (
          <tr key={i} className={to_entrez[gene] ? "": "danger"}>
            <td>{i + 1}</td>
            <td><a href={GENECARDS_URL_PREF + gene} target="_blank">{gene}</a></td>
            <td>{to_entrez[gene] || NOT_ANNOTATED_MSG}</td>
          </tr>
        );
      }).value();
  }
});

module.exports = IdMappingTable;