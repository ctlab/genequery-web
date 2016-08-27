'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var GroupPanel = require('./GroupPanel');

var _ = require('underscore');

/**
 * Sorted by score set of groups.
 */
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
    var groups = [
      <GroupPanel key={this.props.freeGroup['group_id']}
                  isGroupFree={true}
                  score={this.props.freeGroup['score']}
                  groupId={this.props.freeGroup['group_id']}
                  moduleNames={this.props.freeGroup['module_names']}
                  allEnrichedModules={this.props.allEnrichedModules} />
    ];

    _.each(this.props.otherGroups, (group_data) => {
      groups.push(<GroupPanel
        key={group_data['group_id']}
        annotation={group_data['annotation']}
        score={group_data['score']}
        groupId={group_data['group_id']}
        moduleNames={group_data['module_names']}
        allEnrichedModules={this.props.allEnrichedModules}/>);
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