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
      text: "show details"
    }
  },

  fireMappingTableToggleEvent: function(e) {
    var $table = $('.id-mapping-table-wrapper');
    $table.toggle();
    this.setState({text: $table.is(':visible') ? "hide details" : "show details"});
    Eventbus.emit('id-mapping-toggle');
  },

  render: function () {
    var orthologyInfo = this.isOrthology() ? "Orthology was applied." : null;

    return (
      <div>
        <p>
          Entered: {this.props.inputGenes.length} genes.<br/>
          Parsed annotation format: {this.props.idConversion['original_notation']}.<br/>
          {orthologyInfo} {orthologyInfo !== null ? <br/> : null}
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
    if (this.isOrthology()) {
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
    if (this.isOrthology()) {
      return (
        <tr>
          <th>#</th>
          <th>Input gene</th>
          <th>Input symbol</th>
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

  isOrthology: function() {
    return this.props.idConversion['orthology'];
  },

  onDownloadClick: function() {
    Eventbus.emit('download-as-csv');
  },

  getRows: function() {
    var not_annotated = '(not annotated)';
    var notation = this.props.idConversion['original_notation'];
    var removeVersion = notation === 'ensembl' || notation === 'refseq';
    var to_entrez = this.props.idConversion['to_entrez_conversion'];
    var to_symbol = this.isOrthology() ? this.props.idConversion['to_symbol_conversion'] : null;

    return  _.chain(this.props.inputGenes)
      .map(gene => {
        if (removeVersion) {
          return Utils.removeGeneVersion(gene);
        }
        return gene;
      })
      .map((gene, i) => {
        var entrez_ids = '';
        var symbol_ids = '';

        if (gene in to_entrez) {
          entrez_ids = to_entrez[gene].join(',');
        }
        if (to_symbol !== null && gene in to_symbol) {
          symbol_ids = to_symbol[gene].join(',');
        }

        return (
          <tr key={i} className={entrez_ids === '' ? "danger" : ""}>
            <td>{i + 1}</td>
            <td>{gene}</td>
            {to_symbol !== null ? <td>{symbol_ids || not_annotated}</td> : null}
            <td>{entrez_ids || not_annotated}</td>
          </tr>
        );
      })
      .value();
  }
});

module.exports = IdMappingTable;