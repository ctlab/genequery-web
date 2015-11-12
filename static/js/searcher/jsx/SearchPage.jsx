'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */
var Loader = require('react-loader');
var React = require('react');
var ReactDOM = require('react-dom');
var RequestForm = require('./RequestForm');
var SearchResultTable = require('./SearchResultTable');
var SearchResultRow = require('./SearchResultRow');
var ErrorBlock = require('./ErrorBlock');

var Utils = require('../../utils');
var _ = require('underscore');


var SearchPage = React.createClass({

  getInitialState: function() {
    return {
      showLoading: false,
      rows: undefined,
      recap: undefined,
      errorMessage: undefined
    };
  },

  // TODO move validation checks to separate method
  onSearchSuccess: function(data) {
    console.log('OK', data);

    var state = {showLoading: false, lastRequestData: this.state.lastRequestData};

    if (_.has(data, 'error')) {
      state.errorMessage = data.error;
    } else if (_.isObject(data.recap) && _.isArray(data.rows)) {
      state.recap = data.recap;
      state.rows = data.rows;
    } else {
      state.errorMessage = "Seems like server error. Wrong response format.";
    }

    this.replaceState(state);

    if (_.isArray(data.rows) && !_.isEmpty(data.rows)) {
      Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.search_result_table));
    }
  },

  onSearchFail: function(jqxhr, textStatus, error) {
    this.setState({showLoading: false, errorMessage: "Server error."});
    console.log('FAIL', jqxhr, textStatus, error);
  },

  beforeSend: function(species, genes) {
    this.setState({
      showLoading: true,
      errorMessage: undefined,
      recap: undefined,
      rows: undefined,
      lastRequestData: {species: species, genes: genes}
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
        <div className="search-results">
          <div className="loader-wrap" ref="loader">
            <Loader loaded={!this.state.showLoading}
                    lines={17} length={31} width={10} radius={38}
                    color="#777" speed={1.5}
                    trail={79} className="spinner"
                    zIndex={2e9} left="50%" scale={0.75}>
              {this.getTableOrErrorOrNull()}
            </Loader>
          </div>
        </div>
      </div>
    );
  },

  overlapOnClick: function(series, platform, module_number) {
    //console.log('from page', this.state.lastRequestData, series, platform, module_number);
    //var data = {
    //  genes: this.state.lastRequestData.genes,
    //  species: this.state.lastRequestData.species,
    //  module: series + '_' + platform + '#' + module_number
    //};
    //$.get('search/get_overlap/', data)
    //  .done(data => {
    //    console.log('OK overlap', data)
    //  })
    //  .fail((qxhr, textStatus, error) => {
    //    console.log('FAIL overlap', data)
    //  })
    //  .always(() => {
    //
    //  });
  },

  getTableOrErrorOrNull: function () {
    if (!_.isUndefined(this.state.errorMessage)) {
      return <ErrorBlock message={this.state.errorMessage} />;
    }

    if (_.isUndefined(this.state.recap) && _.isUndefined(this.state.rows)) {
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
      <SearchResultTable recap={this.state.recap} ref="search_result_table">
        {rows}
      </SearchResultTable>
    );
  }

});

module.exports = SearchPage;