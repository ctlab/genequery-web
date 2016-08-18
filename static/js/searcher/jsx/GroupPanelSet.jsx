'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var Eventbus = require('../../eventbus');
var Utils = require('../../utils');
var SearchResultRow = require('./SearchResultRow');
var GroupPanel = require('./GroupPanel');

var _ = require('underscore');

var GroupPanelSet = React.createClass({
  propTypes: {
    freeGroup: React.PropTypes.object.isRequired,
    otherGroups: React.PropTypes.array.isRequired,
    allEnrichedModules: React.PropTypes.object.isRequired
  },

  getInitialState: function() {
    return this.props;
  },

  render: function() {
    console.log(this.state);

    var groups = [<GroupPanel
      key={this.state.freeGroup['group_id']}
      isFreeGroup={true}
      score={this.state.freeGroup['score']}
      groupId={this.state.freeGroup['group_id']}
      moduleNames={this.state.freeGroup['module_names']}
      allEnrichedModules={this.state.allEnrichedModules}
    />];

    $(this.state.otherGroups).each((i, group_data) => {
      groups.push(<GroupPanel
        key={group_data['group_id']}
        annotation={group_data['annotation']}
        score={group_data['score']}
        groupId={group_data['group_id']}
        moduleNames={group_data['module_names']}
        allEnrichedModules={this.state.allEnrichedModules}/>);
    });
    groups = _.sortBy(groups, (element) => element.props.score);

    return (
      <div className="panel-group result-groups" id="result-groups-accordion">
        {groups}
      </div>
    );
  }
});

module.exports = GroupPanelSet;