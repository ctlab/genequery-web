'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');
var Utils = require('../../utils');

var GSE_ADDRESS_PREF = 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=';

var SearchResultRow = React.createClass({displayName: "SearchResultRow",

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
      React.createElement("tr", null, 
        React.createElement("td", {className: "text-right"}, this.state.rank), 
        React.createElement("td", null, this.state.title), 
        React.createElement("td", null, this.getHeatmapWithMaybeLink()), 
        React.createElement("td", null, this.state.adjusted_score), 
        React.createElement("td", {align: "center", valign: "middle"}, this.getOverlapLink()), 
        React.createElement("td", null, 
          React.createElement("a", {href: GSE_ADDRESS_PREF + this.state.series, target: "_blank"}, this.state.series)
        ), 
        React.createElement("td", {className: "text-center"}, 
          React.createElement("a", {href: this.state.gmt_url, target: "_blank"}, 
            React.createElement("span", {className: "glyphicon glyphicon-download"})
          )
        )
      )
    );
  },

  heatmapOnClick: function(e) {
    e.preventDefault();
    Utils.showPopupImage(
      this.state.series_url,
      React.createElement("p", null, 
        this.state.series, ", module #", this.state.module_number, ".", ' ', 
        React.createElement("a", {href: this.state.series_url, target: "_blank", className: "full-heatmap-link"}, 
          "Open full picture on new tab"
        ), "."
      )
    );
  },

  getHeatmapWithMaybeLink: function() {
    if (this.state.series_url !== null) {
      return (
        React.createElement("a", {className: "module-heatmap-img", 
           "data-gse": this.state.series, 
           "data-module": this.state.module_number, 
           href: this.state.series_url, 
           onClick: this.heatmapOnClick}, 
          this.state.module_number
        )
      );
    }
    return this.state.module_number;
  },

  getOverlapLink: function() {
    return (
      React.createElement("a", {className: "overlap-genes-link", onClick: this.overlapOnClick}, 
        this.state.overlap_size + '/' + this.state.module_size
      )
    );
  }
});

module.exports = SearchResultRow;