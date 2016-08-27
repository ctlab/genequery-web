'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
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

  getGroupHTMLId: function() {
    return "group_id_" + this.props.groupId;
  },

  render: function() {
    var listOfEnrichedModuleData = [];
    _.each(this.props.moduleNames, (module_name) => {
      listOfEnrichedModuleData.push(this.props.allEnrichedModules[module_name]);
    });
    var bestScore = _.min(_.pluck(listOfEnrichedModuleData, 'log_adj_p_value')).toFixed(2);

    return (
      <div className="panel">
        <div className="panel-heading collapsed"
             data-target={'#' + this.getGroupHTMLId()}
             data-toggle="collapse"
             data-parent="#result-groups-accordion">
          <div className="panel-title flexible-title">
            <div className="title-group-id">
              <a>{"#" + this.props.groupId}</a>
              <span>group ID</span>
            </div>
            <div className="title-modules-found">
              <a>{this.props.moduleNames.length}</a>
              <span>{this.props.moduleNames.length > 1 ? "modules" : "module"}</span>
            </div>
            <div className="title-min-pv">
              <a>{bestScore}</a>
              <span>min.adj.p-value</span>
            </div>
            <div className="title-group-annotation">
              <a>{this.props.isGroupFree ? "Modules that didn't fall in any group." : this.props.annotation}</a>
              <span>group annotation</span>
            </div>
          </div>
        </div>
        <div className="panel-collapse collapse" id={this.getGroupHTMLId()}>
          <div className="panel-body">
            {
              _.isEmpty(this.props.annotation)
              ? null
              : <p>
                  <strong>Group key-words: </strong>
                  {this.props.annotation}
                </p>
            }
          </div>
          <SearchResultTable listOfModuleDataObjects={listOfEnrichedModuleData} />
        </div>
      </div>
    );
  }
});

module.exports = GroupPanel;