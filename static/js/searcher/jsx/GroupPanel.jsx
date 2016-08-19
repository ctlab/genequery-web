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
        <div className="panel-heading" data-target={"#" + this.getGroupHTMLId()} data-toggle="collapse" data-parent="#result-groups-accordion">
          <div className="panel-title">
            <a>{this.props.isGroupFree ? "FREE GROUP" : "Group #" + this.state.groupId} {" "}</a>
            <small>{"Best p-value: " + bestScore + ", " + this.state.annotation}</small>
          </div>
        </div>
        <div className="panel-collapse collapse with-line-on-top" id={this.getGroupHTMLId()}>
          <div className="panel-body">
            <p><strong>Results found: </strong>{this.state.moduleNames.length}</p>
            <p>
              <strong>Group key-words: </strong>
              {this.state.annotation}
            </p>

          </div>
          <div className="panel-body pad-no mar-no">
            <SearchResultTable ref="searchResultTable">
              {enrichedModules}
            </SearchResultTable>
          </div>
        </div>
      </div>
    );
  }
});

module.exports = GroupPanel;