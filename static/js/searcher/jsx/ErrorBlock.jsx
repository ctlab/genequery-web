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
      <div className="row">
        <div className="col-md-6">
          <div className="alert alert-danger error-alert-block" role="alert">
            <span className="sr-only">Error:</span> {this.state.message}
          </div>
        </div>
      </div>
    );
  }
});

module.exports = ErrorBlock;