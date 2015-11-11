'use strict';
/**
 * Created by smolcoder on 10/11/15.
 */

var React = require('react');


var ErrorBlock = React.createClass({displayName: "ErrorBlock",
  propTypes: {
    message: React.PropTypes.string.isRequired
  },

  getInitialState: function() {
    return this.props;
  },

  render: function () {
    return (
      React.createElement("div", {className: "row"}, 
        React.createElement("div", {className: "col-md-6"}, 
          React.createElement("div", {className: "alert alert-danger search-form", role: "alert"}, 
            React.createElement("span", {className: "sr-only"}, "Error:"), " ", this.state.message
          )
        )
      )
    );
  }
});

module.exports = ErrorBlock;