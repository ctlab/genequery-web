var Eventbus = require('../../eventbus');
var React = require('react');
var Utils = require('../../utils');
var TextareaAutosize = require('react-textarea-autosize');

var $ = require('jquery');
var _ = require('underscore');


var SYMBOL_GENES_EXAMPLE = (
  "CD274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86 " +
  "Rsad2 Ccl5 Tgtp2 Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f " +
  "Clec4e Bst1 Isg15 Irf1 Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9")
    .replace(/\s/g, '\n');

var ENSEMBL_GENES_EXAMPLE = (
  "ENSMUSG00000031617 ENSMUSG00000001670 ENSMUSG00000066687 ENSMUSG00000053716 ENSMUSG00000023249 ENSMUSG00000053398" +
  " ENSMUSG00000029298 ENSMUSG00000069793 ENSMUSG00000073555 ENSMUSG00000037253 ENSMUSG00000073678 ENSMUSG00000038507" +
  " ENSMUSG00000030471 ENSMUSG00000053338 ENSMUSG00000022651 ENSMUSG00000069892 ENSMUSG00000050982 ENSMUSG00000059089" +
  " ENSMUSG00000032661 ENSMUSG00000032690 ENSMUSG00000052776 ENSMUSG00000034826 ENSMUSG00000032640 ENSMUSG00000033192" +
  " ENSMUSG00000033777 ENSMUSG00000071478 ENSMUSG00000055415 ENSMUSG00000022696 ENSMUSG00000031562 ENSMUSG00000040483")
  .replace(/\s/g, '\n');

var REFSEQ_GENES_EXAMPLE = (
  "NM_001081957.1 NR_028566.2 NM_145599 XM_006530853 NM_146214 NM_001033324 XM_006510258 NM_153459 XR_379763 NM_001311150" +
  " NM_145619 XM_006511717 XM_006511718 XM_006511719 XM_006511720 NM_016966 NM_172777 XM_006534924 XM_006534925" +
  " XM_006534926 NM_172796 XM_006533235 NM_001033767 XM_006525925 XM_006537473 XM_006537474 XM_006537475 XM_011246928" +
  " XM_011246929 XM_011251341")
  .replace(/\s/g, '\n');

var ENTREZ_GENES_EXAMPLE = (
  "234463 234724 235320 235584 235587 236539 236573 237886 240327 240396 241062 243771 243983 245126 245195 245240" +
  " 245282 246256 246727 246728 246730 269113 269941 270084 279572 319165 319767 320007 320685 327959")
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

  componentDidMount: function() {
    Eventbus.once('example-run', this.runExample)
  },

  componentWillUnmount: function() {
    Eventbus.removeListener('example-run', this.runExample)
  },

  onSubmit: function(event) {
    event.preventDefault();
    // TODO form validation
    // TODO use Underscore to check if it function
    if (this.props.beforeSend) {
      this.props.beforeSend(
        this.state.db_species,
        this.state.query_species,
        this.state.genes.trim().split(/[\s]+/)
      );
    }
    var post_data = {'csrfmiddlewaretoken': Utils.getCSRFToken()};
    _.extend(post_data, this.state);

    $.post(getURL(), post_data)
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

  handleDBSpeciesChange: function(event) {
    this.setState({db_species: event.currentTarget.value});
  },

  handleQuerySpeciesChange: function(event) {
    this.setState({query_species: event.currentTarget.value});
  },

  handleGenesChange: function(event) {
    this.setState({genes: event.currentTarget.value});
  },

  runExample: function(data) {
    var genes;
    if (data.notation === 'ensembl') {
      genes = ENSEMBL_GENES_EXAMPLE;
    } else if (data.notation === 'refseq') {
      genes = REFSEQ_GENES_EXAMPLE;
    } else if (data.notation === 'entrez') {
      genes = ENTREZ_GENES_EXAMPLE;
    } else {
      genes = SYMBOL_GENES_EXAMPLE;
    }

    this.setState({db_species: SPECIES_EXAMPLE, query_species: SPECIES_EXAMPLE, genes: genes});
    this.forceUpdate();
    setTimeout(() => this.refs.submitBtn.click(), 200);
  },


  render: function () {
    return (
      <form role="form" className="search-form" method="GET" onSubmit={this.onSubmit}>
        <div className="form-group form-inline radio-inline-with-title">
          <div className="row">
            <div className="col-md-4">
              <label>Data base species:</label>
            </div>
            <div className="col-md-8">
              <div className="radio">
                <label>
                  <input type="radio" name="db_species" value="hs" checked={this.state.db_species === 'hs'}
                         onChange={this.handleDBSpeciesChange} />
                  Homo Sapiens
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="db_species" value="mm" checked={this.state.db_species === 'mm'}
                         onChange={this.handleDBSpeciesChange} />
                  Mus Musculus
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="db_species" value="rt" checked={this.state.db_species === 'rt'}
                         onChange={this.handleDBSpeciesChange} />
                  Rattus Norvegicus
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="form-group form-inline radio-inline-with-title">
          <div className="row">
            <div className="col-md-4">
              <label>Query genes species:</label>
            </div>
            <div className="col-md-8">
              <div className="radio">
                <label>
                  <input type="radio" name="query_species" value="hs" checked={this.state.query_species === 'hs'}
                         onChange={this.handleQuerySpeciesChange} />
                  Homo Sapiens
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="query_species" value="mm" checked={this.state.query_species === 'mm'}
                         onChange={this.handleQuerySpeciesChange} />
                  Mus Musculus
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="query_species" value="rt" checked={this.state.query_species === 'rt'}
                         onChange={this.handleQuerySpeciesChange} />
                  Rattus Norvegicus
                </label>
              </div>
            </div>
          </div>
        </div>

        <div className="form-group">
          <label htmlFor="genes">Gene list</label> {" "}
          <small>(separated by newline/whitespace/tab)</small>
          <TextareaAutosize id="genes" name="genes" className="form-control" maxRows={40} minRows={2}
            onChange={this.handleGenesChange} value={this.state.genes} />
        </div>

        <div className="form-group inline-group" id="search-btn">
          <input type="submit" value="Search" className="btn btn-primary" ref="submitBtn" />
          <div className="btn-group pull-right">
            <button id="exampleButtonId"
                    className="btn btn-default dropdown-toggle"
                    type="button"
                    data-toggle="dropdown"
                    aria-haspopup="true"
                    aria-expanded="true">
              Run example{' '}
              <span className="caret" />
            </button>
            <ul className="dropdown-menu" aria-labelledby="exampleButtonId">
              <li><a onClick={() => this.runExample({notation: 'symbol'})}>with Symbol</a></li>
              <li><a onClick={() => this.runExample({notation: 'ensembl'})}>with Ensembl</a></li>
              <li><a onClick={() => this.runExample({notation: 'refseq'})}> with RefSeq</a></li>
              <li><a onClick={() => this.runExample({notation: 'entrez'})}> with Entrez</a></li>
            </ul>
          </div>
        </div>
      </form>
    );
  }

});

module.exports = RequestForm;