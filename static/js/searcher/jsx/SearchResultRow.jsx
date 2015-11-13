'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');
var Utils = require('../../utils');

var GSE_ADDRESS_PREF = 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=';

var SearchResultRow = React.createClass({

  // In case of renaming of the properties watch out the CSV building!
  propTypes: {
    title: React.PropTypes.string.isRequired,
    rank: React.PropTypes.number.isRequired,
    series: React.PropTypes.string.isRequired,
    platform: React.PropTypes.string.isRequired,
    module_number: React.PropTypes.number.isRequired,
    overlap_size: React.PropTypes.number.isRequired,
    module_size: React.PropTypes.number.isRequired,
    series_url: React.PropTypes.string,
    adjusted_score: React.PropTypes.number.isRequired,
    gmt_url: React.PropTypes.string,
    overlapOnClick: React.PropTypes.func.isRequired
  },

  overlapOnClick: function() {
    this.props.overlapOnClick(this.state.series, this.state.platform, this.state.module_number);
  },

  getInitialState: function() {
    return this.props;
  },

  render: function () {
    return (
      <tr>
        <td className="text-right">{this.state.rank}</td>
        <td>{this.state.title}</td>
        <td>{this.getHeatmapWithMaybeLink()}</td>
        <td>{this.state.adjusted_score}</td>
        <td align="center" valign="middle">{this.getOverlapLink()}</td>
        <td>
          <a href={GSE_ADDRESS_PREF + this.state.series} target="_blank">{this.state.series}</a>
        </td>
        <td className="text-center">
          <a href={this.state.gmt_url} target="_blank">
            <span className="glyphicon glyphicon-download" />
          </a>
        </td>
      </tr>
    );
  },

  heatmapOnClick: function(e) {
    e.preventDefault();
    Utils.showPopupImage(
      this.state.series_url,
      <p>
        {this.state.series}, module #{this.state.module_number}.{' '}
        <a href={this.state.series_url} target="_blank" className="full-heatmap-link">
          Open full picture on new tab
        </a>.
      </p>
    );
  },

  getHeatmapWithMaybeLink: function() {
    if (this.state.series_url !== null) {
      return (
        <a className="module-heatmap-img"
           data-gse={this.state.series}
           data-module={this.state.module_number}
           href={this.state.series_url}
           onClick={this.heatmapOnClick}>
          {this.state.module_number}
        </a>
      );
    }
    return this.state.module_number;
  },

  getOverlapLink: function() {
    return (
      <a className="overlap-genes-link" onClick={this.overlapOnClick}>
        {this.state.overlap_size + '/' + this.state.module_size}
      </a>
    );
  }
});

module.exports = SearchResultRow;