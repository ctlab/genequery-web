'use strict';
/**
 * Created by smolcoder on 19/08/16.
 */

var React = require('react');
var GroupPanelSet = require('./GroupPanelSet');
var SummaryPanel = require('./SummaryPanel');
var OverlapLayout = require('./OverlapLayout');

var Utils = require('../../utils');
var Eventbus = require('../../eventbus');

var _ = require('underscore');


var LoadedSearchResultPanel = React.createClass({
  propTypes: {
    speciesFrom: React.PropTypes.oneOf([Utils.Species.HUMAN, Utils.Species.MOUSE, Utils.Species.RAT]).isRequired,
    speciesTo: React.PropTypes.oneOf([Utils.Species.HUMAN, Utils.Species.MOUSE, Utils.Species.RAT]).isRequired,
    inputGenes: React.PropTypes.arrayOf(React.PropTypes.string).isRequired,

    enrichedModules: React.PropTypes.object.isRequired,
    idConversionInfo: React.PropTypes.object.isRequired,
    networkClustering: React.PropTypes.object
  },

  componentWillUnmount: function() {
    Eventbus.removeListener(Utils.Event.DOWNLOAD_ALL_AS_CSV_EVENT, this.downloadAsCSV);
    Eventbus.removeListener(Utils.Event.SHOW_GENES_OVERLAP, this.showGenesOverlap);
  },

  componentDidMount: function() {
    Eventbus.addListener(Utils.Event.DOWNLOAD_ALL_AS_CSV_EVENT, this.downloadAsCSV);
    Eventbus.addListener(Utils.Event.SHOW_GENES_OVERLAP, this.showGenesOverlap);
  },

  render: function () {
    return (
      <div>
        { this.getSummaryPanel() }
        { this.getGroupPanelSet() }
      </div>
    );
  },

  getSummaryPanel: function() {
    return <SummaryPanel inputGenes={this.props.inputGenes}
                         numberOfModulesFound={_.size(this.props.enrichedModules)}
                         identifiedGeneFormat={this.props.idConversionInfo['identified_gene_format']}
                         isOrthologyUsed={this.props.idConversionInfo['orthology_used']}
                         inputGenesToFinalEntrez={this.props.idConversionInfo['input_genes_to_final_entrez']} />;
  },

  getGroupPanelSet: function() {
    return <GroupPanelSet freeGroup={this.props.networkClustering['free_group']}
                          otherGroups={this.props.networkClustering['other_groups']}
                          allEnrichedModules={this.props.enrichedModules} />;
  },

  downloadAsCSV: function() {
    var sortedEnrichedModules = _.sortBy(_.values(this.props.enrichedModules),'rank');
    var delimiter = ',';
    var columns = ['rank', 'log_p_value', 'log_adj_p_value', 'series', 'platform',
      'module_number', 'overlap_size', 'module_size', 'title'];
    var content = [columns.join(delimiter)];
    console.log(sortedEnrichedModules);
    _.each(sortedEnrichedModules, module => {
      var csv_row = _.map(columns, field => {
        if (field === 'title') {
          return '"' + module[field] + '"';
        }
        return module[field];
      });
      content.push(csv_row.join(delimiter))
    });

    var now = new Date();
    var dateString = now.getHours() + "-" + now.getMinutes() + "_"
      + now.getMonth() + "-" + (now.getDay() + 1) + "-" + now.getFullYear();
    var filename = 'genequery_search_result_' + dateString + '.csv';

    Utils.downloadDataAsCSV(filename, content.join('\n'));
  },

  showGenesOverlap: function(series, platform, module_number) {
    var data = {
      module: series + '_' + platform + '#' + module_number,
      genes: this.props.inputGenes.join(' '),
      db_species: this.props.speciesTo,
      query_species: this.props.speciesFrom
    };
    Utils.showPopupAjaxPost(
      'search/get_overlap/',
      data,
      response_data => (
        <OverlapLayout series={series}
                       platform={platform}
                       moduleNumber={module_number}
                       responseData={response_data} />
      ),
      error => <PopupLayout>Error while parsing data.</PopupLayout>
    );
  }

});

module.exports = LoadedSearchResultPanel;