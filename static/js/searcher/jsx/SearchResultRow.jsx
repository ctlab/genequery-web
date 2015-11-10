'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');


var SearchResultRow = React.createClass({
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
      <tr>
        <td className="text-right">{this.state.rank}</td>
        <td>{this.state.title}</td>
        <td>{this.state.module_number}</td>
        <td>{this.state.adjusted_score}</td>
        <td align="center" valign="middle">{this.state.overlap_size}{" / "}{this.state.module_size}</td>
        <td>{this.state.series}</td>
        <td className="text-center">
          <a href="#">
            <span className="glyphicon glyphicon-download" />
          </a>
        </td>
      </tr>
    );
  }
});

module.exports = SearchResultRow;