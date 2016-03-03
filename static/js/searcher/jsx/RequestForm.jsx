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
  "ENSMUSG00000076441 ENSMUSG00000031596 ENSMUSG00000029082 ENSMUSG00000024164 ENSMUSG00000029084 " +
  "ENSMUSG00000022901 ENSMUSG00000053113 ENSMUSG00000018796 ENSMUSG00000028270 ENSMUSG00000078920 " +
  "ENSMUSG00000034459 ENSMUSG00000045932 ENSMUSG00000070427 ENSMUSG00000078853 ENSMUSG00000023206 " +
  "ENSMUSG00000027398 ENSMUSG00000026981 ENSMUSG00000018899 ENSMUSG00000022126 ENSMUSG00000029417 " +
  "ENSMUSG00000079363 ENSMUSG00000020826 ENSMUSG00000027611 ENSMUSG00000032487 ENSMUSG00000040026 " +
  "ENSMUSG00000035042 ENSMUSG00000078763 ENSMUSG00000045827 ENSMUSG00000040152 ENSMUSG00000017652 " +
  "ENSMUSG00000069874 ENSMUSG00000028268 ENSMUSG00000030142 ENSMUSG00000020641 ENSMUSG00000027514 " +
  "ENSMUSG00000054072 ENSMUSG00000028037 ENSMUSG00000038058 ENSMUSG00000025790 ENSMUSG00000075602 " +
  "ENSMUSG00000046031 ENSMUSG00000023959 ENSMUSG00000040264 ENSMUSG00000105504 ENSMUSG00000040253 " +
  "ENSMUSG00000041827 ENSMUSG00000035692 ENSMUSG00000078921").replace(/\s/g, '\n');

var REFSEQ_GENES_EXAMPLE = (
  "XM_006509266 NM_010260 NM_212440 NM_145545 NM_018738 XM_006503706 XM_011246980 NM_011198 XM_006524135 XM_011248707 " +
  "XR_865926 XM_011241415 XM_006498795 NM_008599 XM_006499155 XM_006498955 XM_006497727 XM_006502486 XM_011249411 " +
  "XM_006499152 XM_006507382 XM_011243886 NM_011407 NM_007646 NM_013653 NM_008330 XM_006509253 NM_008331 XR_386444 " +
  "XR_377400 NM_021394 NM_175449 XM_011249387 XM_006532446 NM_015783 XM_006530295 XM_006501724 NM_008390 " +
  "XM_006543030 XR_384517 XM_006518582 NM_011315 XM_006516629 XM_011251340 NM_010738 NM_023908 NM_007494 NM_019440 " +
  "XM_011246258").replace(/\s/g, '\n');

var ENTREZ_GENES_EXAMPLE = (
  "14081 14469 229898 229900 16145 12182 60440 19225 224796 12702 16169 56619 16176 17329 21939 19124 16181 99899 " +
  "17472 21825 16068 58185 20555 18126 20304 15953 108116 12494 15958 107607 58203 215900 100702 100038882 231655 " +
  "55932 16362 20715 12524 16365 20210 20723 100039796 110454 11988 11898 54396 12266 15957")
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
              <label>Database species:</label>
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
              <label>Query species:</label>
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