'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var IdMappingTable = require('./IdMappingTable');
var Eventbus = require('../../eventbus');

var Utils = require('../../utils');
var _ = require('underscore');

var SummaryPanel = React.createClass({
  propTypes: {
    numberOfModulesFound: React.PropTypes.number,
    inputGenes: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
    identifiedGeneFormat: React.PropTypes.string.isRequired,
    isOrthologyUsed: React.PropTypes.bool.isRequired,
    inputGenesToFinalEntrez: React.PropTypes.object.isRequired,
    handleGroupingCheckbox: React.PropTypes.func.isRequired
  },

  getDefaultProps: function() {
    return {
      numberOfModulesFound: 0
    }
  },

  render: function() {
    return (
      <div className="panel summary-panel">
        <div className="panel-body">
          {this.getBasicInfo()}
          {this.getConversionPanel()}
          {this.getGropingCheckbox()}
          {this.getDownloadButton()}
        </div>
      </div>
    );
  },

  getGropingCheckbox: function() {
    return (
      <div className="group-result-checkbox">
        <label>
          <input type="checkbox"
                 name="grouping-checkbox"
                 onChange={this.props.handleGroupingCheckbox} /> group results
        </label>
      </div>
    );
  },

  getBasicInfo: function() {
    return (
      <p>
        Entered: {this.props.inputGenes.length} genes. {' '}
        Identified gene format: {this.props.identifiedGeneFormat}. {' '}
        {this.props.isOrthologyUsed ? "Orthology was applied." : ""} {' '}
        Unique Entrez IDs: {_.size(_.without(_.uniq(_.values(this.props.inputGenesToFinalEntrez)), null))}.
      </p>
    );
  },

  getConversionPanel: function() {
    return (
      <div className="panel gene-conversion-panel">
        <div className="panel-heading">
          <div className="panel-title">
            <a data-toggle="collapse" data-target="#conversion-table-wrapper">Gene Conversion Table</a>
          </div>
        </div>
        <div className="panel-body panel-collapse collapse" id="conversion-table-wrapper">
          <IdMappingTable inputGenesToFinalEntrez={this.props.inputGenesToFinalEntrez}
                          inputGenes={this.props.inputGenes} />
        </div>
      </div>
    );
  },

  getDownloadButton: function() {
    return this.props.numberOfModulesFound > 0
      ? <button className="btn btn-primary btn-xs"
                onClick={() => Eventbus.emit(Utils.Event.DOWNLOAD_ALL_AS_CSV_EVENT)}>Download results as CSV</button>
      : null;
  }

});

module.exports = SummaryPanel;