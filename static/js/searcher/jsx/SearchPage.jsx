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

    this.setState({errorMessage: data.error, recap: data.recap, rows: data.rows, showLoading: false});

    // TODO do not scroll if data.rows.length == 0
    Utils.scrollToTop(ReactDOM.findDOMNode(this.refs.search_result_table));
  },

  onSearchFail: function(jqxhr, textStatus, error) {
    this.setState({showLoading: false});
    console.log('FAIL', jqxhr, textStatus, error);
  },

  beforeSend: function() {
    this.setState({showLoading: true, errorMessage: undefined, recap: null, rows: null});
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

  getTableOrErrorOrNull: function () {
    console.log(this.state);

    if (this.state.errorMessage !== undefined && this.state.errorMessage !== null) {
      return <ErrorBlock message={this.state.errorMessage} />;
    }

    if (this.state.rows === undefined || this.state.rows === null) {
      return null;
    }

    if (this.state.rows.length == 0) {
      return <span>No results were found.</span>;
    }

    var rows = [];
    $(this.state.rows).each((i, row) => {
      rows.push(<SearchResultRow key={i} {...row} />);
    });

    return <SearchResultTable {...this.state.recap} ref="search_result_table">{rows}</SearchResultTable>;
  }

});

module.exports = SearchPage;