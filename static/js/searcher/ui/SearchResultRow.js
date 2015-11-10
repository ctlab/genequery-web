'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');


var SearchResultRow = React.createClass({displayName: "SearchResultRow",
  propTypes: {
    title: React.PropTypes.string.isRequired,
    series: React.PropTypes.string.isRequired,
    module_number: React.PropTypes.number.isRequired,
    overlap_size: React.PropTypes.number.isRequired,
    module_size: React.PropTypes.number.isRequired,
    adjusted_score: React.PropTypes.number.isRequired
  },

  getInitialState: function() {
    return this.props;
  },

  render: function () {
    return (
      React.createElement("tr", null, 
        React.createElement("td", {className: "text-right"}, this.state.rank), 
        React.createElement("td", null, this.state.title), 
        React.createElement("td", null, this.state.module_number), 
        React.createElement("td", null, this.state.adjusted_score), 
        React.createElement("td", {align: "center", valign: "middle"}, this.state.overlap_size, " / ", this.state.module_size), 
        React.createElement("td", null, this.state.series), 
        React.createElement("td", {className: "text-center"}, 
          React.createElement("a", {href: "#"}, 
            React.createElement("span", {className: "glyphicon glyphicon-download"})
          )
        )
      )
    );
  }
});

module.exports = SearchResultRow;