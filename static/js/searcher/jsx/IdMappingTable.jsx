'use strict';
/**
 * Created by smolcoder on 30/11/15.
 */

var React = require('react');
var Eventbus = require('../../eventbus');

var _ = require('underscore');


var IdMappingTable = React.createClass({
  propTypes: {
    idConversion: React.PropTypes.object.isRequired,
    inputGenes: React.PropTypes.array.isRequired
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
    return (
      <div>
        <p>
          Entered: {this.props.inputGenes.length} genes.<br/>
          Parsed annotation format: {this.props.idConversion['original_notation']}.<br/>
          Unique Entrez IDs: {this.props.idConversion['unique_entrez_count']}{' '}
          (<a onClick={this.fireMappingTableToggleEvent}>
            {this.state.text}
          </a>)
        </p>
        <div className="id-mapping-table-wrapper" hidden="true">
          <table className="table table-bordered table-hover id-mapping-table">
            <colgroup>
              <col style={{width: "10%"}}/>
              <col style={{width: "45%"}}/>
              <col style={{width: "45%"}}/>
            </colgroup>
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
        </div>
        <button className="btn btn-primary btn-xs" onClick={this.onDownloadClick}>Download results as CSV</button>
      </div>
    );
  },

  onDownloadClick: function() {
    Eventbus.emit('download-as-csv');
  },

  getRows: function() {
    var rows = [];
    _.each(this.props.inputGenes, (input_gene, i) => {
      var input_gene_data = this.props.idConversion['original_to_entrez'][input_gene];
      var entrez_ids = input_gene_data['entrez'].join(',');
      var inDB = input_gene_data['in_db'];
      var color = entrez_ids === '' && !inDB ? "danger" : !inDB ? "warning" : "";
      rows.push(
        <tr key={i} className={color}>
          <td>{i + 1}</td>
          <td>{input_gene}</td>
          <td>{entrez_ids || '(not annotated)'}</td>
        </tr>
      );
    });
    return rows;
  }

});

module.exports = IdMappingTable;