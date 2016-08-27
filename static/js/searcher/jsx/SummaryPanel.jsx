'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var IdMappingTable = require('./IdMappingTable');
var Eventbus = require('../../eventbus');
var PopupLayout = require('./PopupLayout');

var Utils = require('../../utils');
var _ = require('underscore');

var SummaryPanel = React.createClass({
  propTypes: {
    allEnrichedModules: React.PropTypes.object.isRequired,
    numberOfGroups: React.PropTypes.number,
    inputGenes: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,
    identifiedGeneFormat: React.PropTypes.string.isRequired,
    isOrthologyUsed: React.PropTypes.bool.isRequired,
    inputGenesToFinalEntrez: React.PropTypes.object.isRequired,
    handleGroupingCheckbox: React.PropTypes.func.isRequired
  },

  getDefaultProps: function() {
    return {
      numberOfGroups: 0
    }
  },

  resultIsEmpty: function() {
    return _.isEmpty(this.props.allEnrichedModules);
  },

  render: function() {
    return (
      <div className="panel summary-panel">
        <div className="panel-body">
          {this.getModuleSummary()}
          {this.getGenesSummary()}
        </div>
        {!this.resultIsEmpty() ? this.getFooter() : null}
      </div>
    );
  },

  getModuleSummary: function() {
    var min_p_value = _.min(_.map(this.props.allEnrichedModules, (data, name) => data.log_adj_p_value));
    return (
      <div className="summary-description">
        <dl className="dl-horizontal">
          <dt>Modules</dt>
          <dd>{_.size(this.props.allEnrichedModules)}</dd>
          <dt>Detected groups</dt>
          <dd>{this.props.numberOfGroups}</dd>
          <dt>Min log<sub>10</sub>(adj.p<sub>value</sub>)</dt>
          <dd>{this.resultIsEmpty() ? "–" : min_p_value.toFixed(2)}</dd>
        </dl>
      </div>
    );
  },

  getGenesSummary: function() {
    var unique_entrez_ids = _.size(_.without(_.uniq(_.values(this.props.inputGenesToFinalEntrez)), null));
    return (
      <div className="summary-description">
        <dl className="dl-horizontal">
          <dt>Detected gene format</dt>
          <dd className="text-uppercase">{this.props.identifiedGeneFormat}</dd>
          <dt>Genes entered</dt>
          <dd>{this.props.inputGenes.length}</dd>
          <dt>Unique entrez IDs</dt>
          <dd>{unique_entrez_ids}</dd>
          <dd>
            <button className="btn btn-default btn-xs" onClick={this.showConversionTable}>
              show gene conversion table
            </button>
          </dd>
          <dt>Apply orthology</dt>
          <dd>{this.props.isOrthologyUsed ? "yes" : "no"}</dd>
        </dl>
      </div>
    );
  },


  showConversionTable: function() {
    Utils.showPopupInlineReactElement(
      <PopupLayout>
        <IdMappingTable inputGenesToFinalEntrez={this.props.inputGenesToFinalEntrez}
                        inputGenes={this.props.inputGenes} />
      </PopupLayout>
    );
  },
  
  getFooter: function() {
    return (
      <div className="with-line-on-top panel-footer">
        <div className="download-btn">
          <button className="btn btn-primary btn-xs"
                  onClick={() => Eventbus.emit(Utils.Event.DOWNLOAD_ALL_AS_CSV_EVENT)}>Download results as CSV</button>
        </div>
        <div className="group-result-checkbox">
          <label>
            <input type="checkbox"
                   name="grouping-checkbox"
                   onChange={this.props.handleGroupingCheckbox} /> Group results
          </label>
        </div>
      </div>
    );
  }
});

module.exports = SummaryPanel;