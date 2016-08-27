'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');
var Utils = require('../../utils');
var Eventbus = require('../../eventbus');

var GSE_ADDRESS_PREF = 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=';

var SearchResultRow = React.createClass({

  // NOTE: in case of renaming of the properties watch out for the CSV building!
  // NOTE: use underscore-style of naming in order to pass all the props as-is using ellipsis syntax `{...data}`
  propTypes: {
    title: React.PropTypes.string.isRequired,
    rank: React.PropTypes.number.isRequired,
    series: React.PropTypes.string.isRequired,
    platform: React.PropTypes.string.isRequired,
    module_number: React.PropTypes.number.isRequired,
    overlap_size: React.PropTypes.number.isRequired,
    module_size: React.PropTypes.number.isRequired,
    series_url: React.PropTypes.string,
    log_adj_p_value: React.PropTypes.number.isRequired,
    gmt_url: React.PropTypes.string
  },

  overlapOnClick: function() {
    this.props.overlapOnClick(this.props.series, this.props.platform, this.props.module_number);
  },

  render: function () {
    return (
      <tr>
        <td className="text-right">{this.props.rank}</td>
        <td>{this.props.title}</td>
        <td>{this.getHeatmapWithMaybeLink()}</td>
        <td>{this.props.log_adj_p_value >= -325 ? this.props.log_adj_p_value.toFixed(2) : "≤ -325"}</td>
        <td align="center" valign="middle">{this.getOverlapLink()}</td>
        <td>
          <a href={GSE_ADDRESS_PREF + this.props.series} target="_blank">{this.props.series}</a>
        </td>
        <td>{this.getGmtDowloadActiveOrIdleIcon()}</td>
      </tr>
    );
  },

  heatmapOnClick: function(e) {
    e.preventDefault();
    Utils.showPopupImage(
      this.props.series_url,
      <p>
        {this.props.series}, module #{this.props.module_number}.{' '}
        <a href={this.props.series_url} target="_blank" className="full-heatmap-link">
          Open full picture on new tab
        </a>.
      </p>
    );
  },

  getHeatmapWithMaybeLink: function() {
    if (this.props.series_url !== null) {
      return (
        <a className="module-heatmap-img"
           data-gse={this.props.series}
           data-module={this.props.module_number}
           href={this.props.series_url}
           onClick={this.heatmapOnClick}>
          {this.props.module_number}
        </a>
      );
    }
    return this.props.module_number;
  },

  getGmtDowloadActiveOrIdleIcon: function() {
    if (this.props.gmt_url !== null) {
      return (
        <a href={this.props.gmt_url} target="_blank">
          <span className="glyphicon glyphicon-download" />
        </a>
      );
    }
    return 'N/A';
  },

  getOverlapLink: function() {
    return (
      <a onClick={() => Eventbus.emit(Utils.Event.SHOW_GENES_OVERLAP, this.props.series, this.props.platform, this.props.module_number)}>
        {this.props.overlap_size + '/' + this.props.module_size}
      </a>
    );
  }
});

module.exports = SearchResultRow;