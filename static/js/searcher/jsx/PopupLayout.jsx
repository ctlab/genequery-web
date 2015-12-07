'use strict';
/**
 * Created by smolcoder on 03/12/15.
 */

var React = require('react');


var PopupLayout = React.createClass({

  render: function () {
    return (
      <div className="white-popup-block">
        {this.props.children}
      </div>
    );
  }
});

module.exports = PopupLayout;