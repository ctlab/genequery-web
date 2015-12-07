'use strict';
/**
 * Created by smolcoder on 03/12/15.
 */

var React = require('react');
var PopupLayout = require('./PopupLayout');


var OverlapLayout = React.createClass({
  propTypes: {
    series: React.PropTypes.string.isRequired,
    platform: React.PropTypes.string.isRequired,
    moduleNumber: React.PropTypes.number.isRequired,
    responseData: React.PropTypes.object.isRequired
  },

  render: function () {
    var module_id = this.props.series + this.props.platform + this.props.module_number;

    var failed = null;
    if (this.props.responseData.failed.length > 0) {
      failed = (
        <div>
          <br/>
          <p>
            Following Entrez IDs couldn't be converted to symbol format
            (see detailed conversion table above for original genes):
          </p>
          <pre>
            {this.props.responseData.failed.join('\n')}
          </pre>
        </div>
      );
    }

    return (
      <PopupLayout>
        <div className="row">
          <div className="overlap-genes-list col-md-4">
            <pre id={module_id}>{this.props.responseData.genes.join('\n')}</pre>
          </div>
          <div className="overlap-genes-caption col-md-8">
            <p>Overlap of genes from request and from module {this.props.moduleNumber} of {this.props.series}.</p>
            <a data-clipboard-target={'#' + module_id} className="copy-to-clipboard">Copy genes to clipboard.</a>
            {failed}
          </div>
        </div>
      </PopupLayout>
    );
  }
});

module.exports = OverlapLayout;