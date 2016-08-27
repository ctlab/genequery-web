'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */
var Eventbus = require('../../eventbus');
var Loader = require('react-loader');
var React = require('react');
var ReactDOM = require('react-dom');
var RequestForm = require('./RequestForm');
var ErrorBlock = require('./ErrorBlock');
var LoadedSearchResultPanel = require('./LoadedSearchResultPanel');

var Utils = require('../../utils');
var _ = require('underscore');

var Clipboard = require('clipboard');


var SearchPage = React.createClass({

  componentWillMount: function() {
    // TODO don't work on Safari browser
    new Clipboard('.copy-to-clipboard');
    this.initExampleRunner();
  },

  initExampleRunner: function() {
    var exampleGeneFormat = Utils.getUrlParameter('example');
    if (_.contains(['symbol', 'entrez', 'refseq', 'ensembl'], exampleGeneFormat)) {
      setTimeout(() => Eventbus.emit(Utils.Event.RUN_EXAMPLE, exampleGeneFormat), 250)
    }
  },

  getInitialState: function() {
    return {
      showLoading: false,
      resultPayload: null,
      success: false,
      errors: null,
      lastRequestData: undefined
    };
  },

  onSearchSuccess: function(payload) {
    console.log('PAYLOAD', payload);

    var new_state = this.getInitialState();
    new_state.lastRequestData = this.state.lastRequestData;
    new_state.showLoading = false;
    try {
      new_state.success = payload['success'];
      new_state.resultPayload = payload['result'];
      new_state.errors = payload['errors'];
      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.searchResultPanel));
    } catch (e) {
      console.log('fail to parse payload', e);
      new_state.errors = "Seems like server error. Wrong response format.";
    } finally {
      this.setState(new_state);
    }
  },

  onSearchFail: function(jqxhr, textStatus, error) {
    this.replaceState({showLoading: false, errors: ["Server error."]});
    console.log('FAIL', jqxhr, textStatus, error);
  },

  beforeSend: function(species_from, species_to, input_genes) {
    var new_state = this.getInitialState();
    new_state.lastRequestData = {dbSpecies: species_to, querySpecies: species_from, genes: input_genes};
    new_state.showLoading = true;
    this.setState(new_state);
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.loader));
  },

  onSearchComplete: function() {
    this.setState({showLoading: false});
  },

  componentDidUpdate: function() {
    if (this.state.success) {
      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.searchResultPanel));
    }
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
            />
          </div>
        </div>
        <div className="search-result">
          <div className={this.state.showLoading ? "loader-wrap" : ""} ref="loader">
            <Loader loaded={!this.state.showLoading}
                    lines={17} length={31} width={10} radius={38}
                    color="#777" speed={1.5}
                    trail={79} className="load-spinner"
                    zIndex={2e9} left="50%" scale={0.75}>
              { this.getLoadedResultOrErrorOrNull() }
            </Loader>
          </div>
        </div>
      </div>
    );
  },

  getLoadedResultOrErrorOrNull: function () {
    if (!this.atLeastOneRequestMade()) return null;
    if (this.lastRequestHasErrors()) {
      return <ErrorBlock messages={this.state.errors} />;
    }
    if (_.isNull(this.state.resultPayload)) {
      return null;
    }
    return <LoadedSearchResultPanel speciesFrom={this.state.lastRequestData.querySpecies}
                                    speciesTo={this.state.lastRequestData.dbSpecies}
                                    inputGenes={this.state.lastRequestData.genes}
                                    enrichedModules={this.state.resultPayload['enriched_modules']}
                                    idConversionInfo={this.state.resultPayload['id_conversion']}
                                    networkClustering={this.state.resultPayload['network_clustering']}
                                    ref="searchResultPanel"/>;
  },

  atLeastOneRequestMade: function() {
    return !_.isUndefined(this.state.lastRequestData)
  },
  lastRequestHasErrors: function() {
    return !_.isNull(this.state.errors) && _.isArray(this.state.errors) && !_.isEmpty(this.state.errors);
  }
});

module.exports = SearchPage;