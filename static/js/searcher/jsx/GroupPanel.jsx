'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var SearchResultRow = require('./SearchResultRow');
var SearchResultTable = require('./SearchResultTable');

var _ = require('underscore');

var GroupPanel = React.createClass({
  propTypes: {
    isGroupFree: React.PropTypes.bool,
    annotation: React.PropTypes.string,
    score: React.PropTypes.number.isRequired,
    groupId: React.PropTypes.number.isRequired,
    moduleNames: React.PropTypes.array.isRequired,
    allEnrichedModules: React.PropTypes.object.isRequired
  },

  getDefaultProps: function() {
    return {
      isGroupFree: false,
      annotation: null
    };
  },

  getInitialState: function() {
    return this.props;
  },

  getGroupHTMLId: function() {
    return "group_id_" + this.state.groupId;
  },

  render: function() {
    var enrichedModules = [];
    $(this.state.moduleNames).each((i, module_name) => {
      enrichedModules.push(
        <SearchResultRow key={this.state.groupId + "_" + i} {...this.state.allEnrichedModules[module_name]} />
      );
    });
    enrichedModules = _.sortBy(enrichedModules, (element) => element.props.log_adj_p_value);
    var bestScore = enrichedModules[0].props.log_adj_p_value.toFixed(2);

    return (
      <div className="panel">
        <div className="panel-heading collapsed" data-target={"#" + this.getGroupHTMLId()} data-toggle="collapse" data-parent="#result-groups-accordion">
          <div className="panel-title flexible-title">
            <div className="title-group-id">
              <a>{"#" + this.state.groupId}</a>
              <span>group ID</span>
            </div>
            <div className="title-modules-found">
              <a>{this.state.moduleNames.length}</a>
              <span>{this.state.moduleNames.length > 1 ? "modules" : "module"}</span>
            </div>
            <div className="title-min-pv">
              <a>{bestScore}</a>
              <span>min.adj.p-value</span>
            </div>
            <div className="title-group-annotation">
              <a>{this.props.isGroupFree ? "Modules that didn't fall in any group." : this.state.annotation}</a>
              <span>group annotation</span>
            </div>
          </div>
        </div>
        <div className="panel-collapse collapse" id={this.getGroupHTMLId()}>
          <div className="panel-body">
            <p><strong>Results found: </strong>{this.state.moduleNames.length}</p>
            <p>
              <strong>Group key-words: </strong>
              {this.state.annotation}
            </p>

          </div>
          <SearchResultTable>
            {enrichedModules}
          </SearchResultTable>
        </div>
      </div>
    );
  }
});

module.exports = GroupPanel;