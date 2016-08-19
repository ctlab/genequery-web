'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');


var ErrorBlock = React.createClass({
  propTypes: {
    messages: React.PropTypes.arrayOf(React.PropTypes.string).isRequired
  },

  render: function () {
    return (
      <div className="row">
        <div className="col-md-6">
          <div className="alert alert-danger error-alert-block" role="alert">
            {this.props.messages.join('\n')}
          </div>
        </div>
      </div>
    );
  }
});

module.exports = ErrorBlock;