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

var Utils = require('../../utils');
var _ = require('underscore');

var Clipboard = require('clipboard');


var SearchPage = React.createClass({

  componentWillMount: function() {
    new Clipboard('.copy-to-clipboard');

    if (Utils.getUrlParameter('example') === 'true') {
      setTimeout(
        () => Eventbus.emit('example-run'),
        250
      )
    }
  },

  getInitialState: function() {
    return {
      showLoading: false,
      rows: undefined,
      total: undefined,
      idConversion: undefined,
      errorMessage: undefined
    };
  },

  // TODO move validation checks to separate method
  onSearchSuccess: function(data) {
    console.log('OK', data);

    var state = {showLoading: false, lastRequestData: this.state.lastRequestData};

    if (_.has(data, 'error')) {
      state.errorMessage = data.error;
    } else if (_.isArray(data.rows) && _.isObject(data.id_conversion)) {
      state.total = data.total_found;
      state.rows = data.rows;
      state.idConversion = data.id_conversion;
    } else {
      state.errorMessage = "Seems like server error. Wrong response format.";
    }

    this.replaceState(state);

    if (_.isArray(data.rows) && !_.isEmpty(data.rows)) {
      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.search_result_table));
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
      rows: undefined,
      total: undefined,
      lastRequestData: {dbSpecies: db_species, querySpecies: query_species, genes: genes}
    });
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.loader));
  },

  onSearchComplete: function() {
    //this.setState({showLoading: false});
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
    var module_id = series + platform + module_number;
    Utils.showPopupAjax(
      'search/get_overlap/',
      data,
      response_data => (
        <div className="white-popup-block row">
          <div className="overlap-genes-list col-md-4">
            <pre id={module_id}>{response_data.genes.join('\n')}</pre>
          </div>
          <div className="overlap-genes-caption col-md-8">
            <p>Overlap of genes from request and from module {module_number} of {series}.</p>
            <a data-clipboard-target={'#' + module_id} className="copy-to-clipboard">Copy genes to clipboard.</a>
          </div>
        </div>
      )
    );
  },

  getIdConvertionTableOrNull: function() {
    if (_.isUndefined(this.state.idConversion)) {
      return null;
    }

    return (
      <div className="row row-margin">
        <div className="col-md-3">
          <IdMappingTable totalFound={this.state.total}
                          idConversion={this.state.idConversion}
                          inputGenes={this.state.lastRequestData.genes} />
        </div>
      </div>
    );
  },

  getTableOrErrorOrNull: function () {
    if (!_.isUndefined(this.state.errorMessage)) {
      return <ErrorBlock message={this.state.errorMessage} />;
    }

    if (_.isUndefined(this.state.rows)) {
      return null;
    }

    if (_.isArray(this.state.rows) && _.isEmpty(this.state.rows)) {
      return <span>No modules were found.</span>;
    }

    var rows = [];
    $(this.state.rows).each((i, row) => {
      rows.push(<SearchResultRow key={i} overlapOnClick={this.overlapOnClick} {...row} />);
    });

    return (
      <div className="row">
        <div className="col-md-12">
          <SearchResultTable ref="search_result_table">
            {rows}
          </SearchResultTable>
        </div>
      </div>
    );
  }

});

module.exports = SearchPage;