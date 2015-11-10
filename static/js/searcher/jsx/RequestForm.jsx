
var React = require('react');
var ReactDOM = require('react-dom');
var Utils = require('../../utils');
var TextareaAutosize = require('react-textarea-autosize');

var GENES_EXAMPLE = ("Cd274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86 " +
"Rsad2 Ccl5 Tgtp2 Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f " +
"Clec4e Bst1 Isg15 Irf1 Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9")
  .replace(/\s/g, '\n');
var SPECIES_EXAMPLE = 'mm';

/**
 * Returns URL send request to. We can't cache it since variables out of
 * class scope cat initialize before DOM is ready.
 *
 * @returns {string}
 */
function getURL() {
  return document.getElementById('request-url').textContent;
}

var RequestForm = React.createClass({
  propTypes: {
    beforeSend: React.PropTypes.func,
    onSuccess: React.PropTypes.func,
    onFail: React.PropTypes.func,
    onComplete: React.PropTypes.func
  },

  getInitialState: function() {
    return {species: '', genes: ''};
  },

  onSubmit: function(event) {
    event.preventDefault();

    if (this.props.beforeSend) {
      this.props.beforeSend();
    }

    $.get(getURL(), this.state)
      .done(data => {
        if (this.props.onSuccess){
          this.props.onSuccess(data)
        }
      })
      .fail((qxhr, textStatus, error) => {
        if (this.props.onFail){
          this.props.onFail(qxhr, textStatus, error)
        }
      })
      .always(() => {
        if (this.props.onComplete) {
          this.props.onComplete();
        }
      });
  },

  handleSpeciesChange: function(event) {
    this.setState({species: event.currentTarget.value});
  },

  handleGenesChange: function(event) {
    this.setState({genes: event.currentTarget.value});
  },

  runExample: function(e) {
    this.setState({species: SPECIES_EXAMPLE, genes: GENES_EXAMPLE});
    this.forceUpdate();
    setTimeout(() => this.refs.submitBtn.click(), 200);
  },


  render: function () {
    return (
      <form role="form" className="search-form" method="GET" onSubmit={this.onSubmit}>
        <div className="form-group form-inline">
          <div className="radio">
            <label>
              <input type="radio" name="species" value="hs" checked={this.state.species === 'hs'}
                onChange={this.handleSpeciesChange} />
              Homo Sapiens
            </label>
          </div>
          <div className="radio">
            <label>
              <input type="radio" name="species" value="mm" checked={this.state.species === 'mm'}
                onChange={this.handleSpeciesChange} />
              Mus Musculus
            </label>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="form-genes">Gene list</label> {" "}
          <small>(separated by newline/whitespace/tab)</small>
          <TextareaAutosize id="genes" name="genes" className="form-control" maxRows={40} minRows={2}
            onChange={this.handleGenesChange} value={this.state.genes} />
        </div>

        <div className="form-group form-inline" id="search-btn">
          <input type="submit" value="Search" className="btn btn-default" ref="submitBtn" />
          <button type="button" className="btn btn-link" id="example-btn" onClick={this.runExample}>
            Run example
          </button>
        </div>
      </form>
    );
  }

});

module.exports = RequestForm;