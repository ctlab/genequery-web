'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var SearchResultRow = require('./SearchResultRow');
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
    var enrichedModules = [];
    _.each(this.props.allEnrichedModules, (data, module_name) => {
      enrichedModules.push(
        <SearchResultRow key={module_name + "_table_key"} {...data} />
      );
    });
    enrichedModules = _.sortBy(enrichedModules, (element) => element.props.log_adj_p_value);

    return (
      <div className="panel">
        <SearchResultTable>
          {enrichedModules}
        </SearchResultTable>
      </div>
    );
  }
});

module.exports = UngroupedResultPanel;