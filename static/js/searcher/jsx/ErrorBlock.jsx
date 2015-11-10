'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');


var ErrorBlock = React.createClass({
  propTypes: {
    message: React.PropTypes.string.isRequired
  },

  getInitialState: function() {
    return this.props;
  },

  render: function () {
    return (
      <div className="alert alert-danger search-form" role="alert">
        <span className="sr-only">Error:</span> {this.state.message}
      </div>
    );
  }
});

module.exports = ErrorBlock;