'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */
var Eventbus = require('../../eventbus');
var Loader = require('react-loader');
var React = require('react');
var ReactDOM = require('react-dom');
var RequestForm = require('./RequestForm');
var SearchResultTable = require('./SearchResultTable');
var SearchResultRow = require('./SearchResultRow');
var ErrorBlock = require('./ErrorBlock');
var IdMappingTable = require('./IdMappingTable');
var OverlapLayout = require('./OverlapLayout');
var PopupLayout = require('./PopupLayout');

var Utils = require('../../utils');
var _ = require('underscore');

var Clipboard = require('clipboard');


var SearchPage = React.createClass({

  componentWillMount: function() {
    new Clipboard('.copy-to-clipboard');

    var example = Utils.getUrlParameter('example');
    if (example === 'symbol' || example === 'entrez' || example === 'refseq' || example === 'ensembl') {
      setTimeout(
        () => Eventbus.emit('example-run', {'notation': example}),
        250
      )
    }
  },

  getInitialState: function() {
    return {
      showLoading: false,
      enrichedModules: undefined,
      total: undefined,
      idConversion: undefined,
      errorMessage: undefined
    };
  },

  // TODO move validation checks to separate method
  onSearchSuccess: function(payload) {
    console.log('OK', payload);

    var state = {showLoading: false, lastRequestData: this.state.lastRequestData};

    try {
      var success = payload['success'];
      var data = payload['result'];
      var errors = payload['errors'];
    } catch (e) {
      console.log('fail to parse payload', e);
      state.errorMessage = "Seems like server error. Wrong response format.";
    }

    if (success === true) {
      state.enrichedModules = data['enriched_modules'];
      state.total = state.enrichedModules.length;
      state.idConversion = data['id_conversion'];

      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.idMappingTable));
    } else {
      state.errorMessage = errors.join('\n');
    }

    this.replaceState(state);

    if (_.isArray(state.enrichedModules) && !_.isEmpty(state.enrichedModules)) {
      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.idMappingTable));
    }
  },

  onSearchFail: function(jqxhr, textStatus, error) {
    this.replaceState({showLoading: false, errorMessage: "Server error."});
    console.log('FAIL', jqxhr, textStatus, error);
  },

  beforeSend: function(db_species, query_species, genes) {
    this.setState({
      // Todo can we just replaceState({showLoading: true}, lastRequestData:...)?
      showLoading: true,
      errorMessage: undefined,
      idConversion: undefined,
      enrichedModules: undefined,
      total: undefined,
      lastRequestData: {dbSpecies: db_species, querySpecies: query_species, genes: genes}
    });
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.loader));
  },

  onSearchComplete: function() {
    this.setState({showLoading: false});
  },

  render: function () {
    return (
      <div>
        <div className="row">
          <div className="col-md-6">
            <RequestForm
              onSuccess={this.onSearchSuccess}
              onFail={this.onSearchFail}
              beforeSend={this.beforeSend}
              onComplete={this.onSearchComplete}
              ref="request_form"
            />
          </div>
        </div>
        <div className="search-result">
          <div className={this.state.showLoading ? "loader-wrap" : ""}
               ref="loader">
            <Loader loaded={!this.state.showLoading}
                    lines={17} length={31} width={10} radius={38}
                    color="#777" speed={1.5}
                    trail={79} className="load-spinner"
                    zIndex={2e9} left="50%" scale={0.75}>
              {this.getIdConvertionTableOrNull()}
              {this.getTableOrErrorOrNull()}
            </Loader>
          </div>
        </div>
      </div>
    );
  },

  overlapOnClick: function(series, platform, module_number) {
    var data = {
      module: series + '_' + platform + '#' + module_number,
      genes: this.state.lastRequestData.genes.join(' '),
      db_species: this.state.lastRequestData.dbSpecies,
      query_species: this.state.lastRequestData.querySpecies
    };
    Utils.showPopupAjax(
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
  },

  getIdConvertionTableOrNull: function() {
    if (_.isUndefined(this.state.idConversion)) {
      return null;
    }

    return (
      <div className="row row-margin">
        <div className="col-md-6">
          <IdMappingTable totalFound={this.state.total}
                          idConversion={this.state.idConversion}
                          inputGenes={this.state.lastRequestData.genes}
                          ref="idMappingTable" />
        </div>
      </div>
    );
  },

  getTableOrErrorOrNull: function () {
    if (!_.isUndefined(this.state.errorMessage)) {
      return <ErrorBlock message={this.state.errorMessage} />;
    }

    if (_.isUndefined(this.state.enrichedModules)) {
      return null;
    }

    if (_.isArray(this.state.enrichedModules) && _.isEmpty(this.state.enrichedModules)) {
      return <span>No modules were found.</span>;
    }

    var enrichedModules = [];
    $(this.state.enrichedModules).each((i, row) => {
      enrichedModules.push(<SearchResultRow key={i} overlapOnClick={this.overlapOnClick} {...row} />);
    });

    return (
      <div>
        <div className="row sticky-result-table-header">
          <div className="col-md-12">
            <SearchResultTable fake={true}/>
          </div>
        </div>
        <div className="row">
          <div className="col-md-12">
            <SearchResultTable ref="searchResultTable">
              {enrichedModules}
            </SearchResultTable>
          </div>
        </div>
      </div>
    );
  }

});

module.exports = SearchPage;