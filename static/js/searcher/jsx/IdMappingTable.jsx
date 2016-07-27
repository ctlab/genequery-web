'use strict';
/**
 * Created by smolcoder on 30/11/15.
 */

var React = require('react');
var Eventbus = require('../../eventbus');
var Utils = require('../../utils');

var _ = require('underscore');


var IdMappingTable = React.createClass({
  propTypes: {
    idConversion: React.PropTypes.object.isRequired,
    inputGenes: React.PropTypes.array.isRequired,
    totalFound: React.PropTypes.number.isRequired
  },

  getInitialState: function() {
    return {
      text: "show conversion table"
    }
  },

  fireMappingTableToggleEvent: function(e) {
    var $table = $('.id-mapping-table-wrapper');
    $table.toggle();
    this.setState({text: $table.is(':visible') ? "hide conversion table" : "show conversion table"});
  },

  render: function () {
    var orthologyInfo = this.props.idConversion['orthology_used'] ? "Orthology was applied." : null;

    return (
      <div>
        <p>
          Entered: {this.props.inputGenes.length} genes. {' '}
          Parsed annotation format: {this.props.idConversion['identified_gene_format']}. {' '}
          {orthologyInfo} {orthologyInfo !== null ? ' ' : null}
          Unique Entrez IDs: {this.props.idConversion['unique_entrez_count']}{' '}
          (<a onClick={this.fireMappingTableToggleEvent}>
            {this.state.text}
          </a>)
        </p>
        <div className="id-mapping-table-wrapper" hidden="true">
          <table className="table table-bordered table-hover id-mapping-table">
            {this.getColgroup}
            <thead>
              {this.getTheadContent()}
            </thead>
            <tbody>
              {this.getRows()}
            </tbody>
          </table>
        </div>
        {this.props.totalFound > 0
          ? <button className="btn btn-primary btn-xs" onClick={this.onDownloadClick}>Download results as CSV</button>
          : null}
      </div>
    );
  },

  getColgroup: function() {
    if (this.showProxyColumn()) {
      return (
        <colgroup>
          <col style={{width: "7%"}}/>
          <col style={{width: "31%"}}/>
          <col style={{width: "31%"}}/>
          <col style={{width: "31%"}}/>
        </colgroup>
      );
    }
    return (
      <colgroup>
        <col style={{width: "10%"}}/>
        <col style={{width: "45%"}}/>
        <col style={{width: "45%"}}/>
      </colgroup>
    );
  },

  getTheadContent: function() {
    if (this.showProxyColumn()) {
      return (
        <tr>
          <th>#</th>
          <th>Input gene</th>
          <th>Input Entrez</th>
          <th>Entrez (DB)</th>
        </tr>
      );
    }
    return (
      <tr>
        <th>#</th>
        <th>Input gene</th>
        <th>Entrez</th>
      </tr>
    );
  },

  showProxyColumn: function() {
    //return this.props.idConversion['showProxyColumn'];
    return false;
  },

  onDownloadClick: function() {
    // TODO make all event names constants
    Eventbus.emit('download-as-csv');
  },

  getRows: function() {
    var not_annotated_msg = '(not annotated)';
    var to_entrez = this.props.idConversion['input_genes_to_final_entrez'];

    return  _.chain(this.props.inputGenes)
      .map((gene, i) => {
        return (
          <tr key={i} className={gene in to_entrez ? "": "danger"}>
            <td>{i + 1}</td>
            <td>{gene}</td>
            <td>{to_entrez[gene] || not_annotated_msg}</td>
          </tr>
        );
      })
      .value();
  }
});

module.exports = IdMappingTable;