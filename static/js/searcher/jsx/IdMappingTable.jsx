'use strict';
/**
 * Created by smolcoder on 30/11/15.
 */

var React = require('react');

var _ = require('underscore');

var NOT_ANNOTATED_MSG = '(not annotated)';

var IdMappingTable = React.createClass({
  propTypes: {
    inputGenesToFinalEntrez: React.PropTypes.objectOf(React.PropTypes.number).isRequired,
    inputGenes: React.PropTypes.array.isRequired
  },

  render: function () {
    return (
      <div className="id-mapping-table-wrapper">
        <table className="table table-hover id-mapping-table">
          {this.getColgroup}
          <thead>
            {this.getTheadContent()}
          </thead>
          <tbody>
            {this.getRows()}
          </tbody>
        </table>
      </div>
    );
  },

  // TODO move this to CSS
  getColgroup: function() {
    return (
      <colgroup>
        <col style={{width: "10%"}}/>
        <col style={{width: "45%"}}/>
        <col style={{width: "45%"}}/>
      </colgroup>
    );
  },

  getTheadContent: function() {
    return (
      <tr>
        <th>#</th>
        <th>Input gene</th>
        <th>Entrez</th>
      </tr>
    );
  },

  getRows: function() {
    var to_entrez = this.props.inputGenesToFinalEntrez;

    return  _.chain(this.props.inputGenes)
      .map((gene, i) => {
        return (
          <tr key={i} className={gene in to_entrez ? "": "danger"}>
            <td>{i + 1}</td>
            <td>{gene}</td>
            <td>{to_entrez[gene] || NOT_ANNOTATED_MSG}</td>
          </tr>
        );
      })
      .value();
  }
});

module.exports = IdMappingTable;