'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var SearchResultTable = require('./SearchResultTable');

var _ = require('underscore');

var UngroupedResultPanel = React.createClass({
  propTypes: {
    allEnrichedModules: React.PropTypes.object.isRequired
  },

  getInitialState: function() {
    return this.props;
  },

  render: function() {
    return (
      <div className="panel">
        <SearchResultTable listOfModuleDataObjects={_.values(this.props.allEnrichedModules)} />
      </div>
    );
  }
});

module.exports = UngroupedResultPanel;