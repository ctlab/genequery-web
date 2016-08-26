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

  getInitialState: function() {
    return {
      showAllGenes: false
    }
  },

  render: function () {
    var module_id = this.props.series + this.props.platform + this.props.moduleNumber;

    return (
      <PopupLayout>
        <div className="overlap-genes-caption">
          <p>Overlap of input genes with module {this.props.moduleNumber} of {this.props.series}.</p>
        </div>
        <div className="overlap-genes-controls">
          <label>
            <input type="checkbox"
                   onChange={this.handleShowAllGenes} /> show other genes of the module
          </label>
          <a data-clipboard-target={'#' + module_id}
             className="copy-to-clipboard">Copy genes to clipboard</a>
        </div>
        <div className="overlap-genes-list">
          {
            this.state.showAllGenes
            ? <pre id={module_id}>
                <b>
                  {this.props.responseData.result['overlap_genes'].join(' ')}
                </b>{' '}
                {this.props.responseData.result['other_module_genes'].join(' ')}
              </pre>
            : <pre id={module_id}>
                {this.props.responseData.result['overlap_genes'].join(' ')}
              </pre>
          }

        </div>
      </PopupLayout>
    );
  },

  handleShowAllGenes: function(event) {
    this.setState({showAllGenes: event.target.checked});
  }
});

module.exports = OverlapLayout;