var Eventbus = require('../../eventbus');
var React = require('react');
var Utils = require('../../utils');
var TextareaAutosize = require('react-textarea-autosize');

var $ = require('jquery');
var _ = require('underscore');


var SYMBOL_GENES_EXAMPLE = (
  "Col5a1 Tgm2 Gpc1 Phkg1 Efna1 Ampd3 Tktl1 Pnrc1 Plaur Glrx Maff Serpine1 Cited2 Gapdh Errfi1 Ets1 Aldoa Tmem45a Pdk1" +
  " Pgam2 Atf3 Aldoc Gcnt2 Pgf Gpc4 Nr3c1 Fbp1 Pgm1 Igfbp3 Tpd52 Ppfia4 Prkcdbp Ldha Rbpj Pkp1 Plac8 Dcn Igfbp1 Cdkn1c" +
  " Slc37a4 Ppargc1a Ugp2 Csrp2 Bhlhe40 Hmox1 Grhpr Hk1 Jmjd6 Ndst2 Dpysl4 Hs3st1 Slc2a5 Tiparp Siah2 P4ha2 Ptrf Adm" +
  " Hspa5 Pfkp Pfkfb3 Hk2 Sdc3 Gpc3 Eno2 Ddit4 Mxi1 Gys1 Cav1 Srpx Plin2 Gbe1 Ier3 Slc6a6 Ankzf1 Aldob Has1 Kdelr3" +
  " Anxa2 Bcan Brs3 Btg1 Irs2 Selenbp1 Cxcr4 Klhl24 Cdkn1a Sap30 Vhl Mif Dtna Lox Lxn Cdkn1b Map3k1 Ero1l Myh9 Pdk3" +
  " S100a4 Cp Casp6 Il6 Tnfaip3 Vldlr Pam Nedd4l Adora2b Cyr61 Noct Bnip3l Tpi1 Scarb1 Nagk Tpbg Isg20 Hoxb9 Pfkl" +
  " Zfp36 Ids Klf6 Wsb1 Xpnpep1 Bcl2 Ddit3 Ldhc Pck1 Ndst1 Ppp1r15a B3galt6 Pgm2 Vegfa Sult2b1 Stc1 Kif5a Pgk1 Sdc2" +
  " Slc25a1 Rragd Jun Fos Tgfb3 Ilvbl Ctgf Gapdhs Ccng2 Dusp1 Tpst2 Lalba Ncan Ndrg1 Inha F3 Akap12 Tes Galk1 Pdgfb" +
  " Slc2a3 Fosl2 Hexa Sdc4 Fam162a Wisp2 Ak4 Chst3 Egfr Eno1 Rora Ppp1r3c Efna3 Car12 Gck Large Nfil3 Tgfbi Kdm3a" +
  " Edn2 Bgn Pygm Foxo3 Pklr P4ha1 Gaa Stbd1 Prkca Hdlbp Eno3")
    .replace(/\s/g, '\n');

var ENSEMBL_GENES_EXAMPLE = (
  "ENSMUSG00000028494 ENSMUSG00000030790 ENSMUSG00000018500 ENSMUSG00000028527 ENSMUSG00000030695 ENSMUSG00000017390" +
  " ENSMUSG00000005686 ENSMUSG00000026628 ENSMUSG00000004892 ENSMUSG00000057329 ENSMUSG00000031375 ENSMUSG00000022051" +
  " ENSMUSG00000031130 ENSMUSG00000036478 ENSMUSG00000032231 ENSMUSG00000027997 ENSMUSG00000007655 ENSMUSG00000029385" +
  " ENSMUSG00000023087 ENSMUSG00000023067 ENSMUSG00000003031 ENSMUSG00000037664 ENSMUSG00000045382 ENSMUSG00000026837" +
  " ENSMUSG00000003617 ENSMUSG00000002341 ENSMUSG00000020186 ENSMUSG00000019929 ENSMUSG00000025408 ENSMUSG00000003528" +
  " ENSMUSG00000024302 ENSMUSG00000028635 ENSMUSG00000027954 ENSMUSG00000028039 ENSMUSG00000020122 ENSMUSG00000063524" +
  " ENSMUSG00000004267 ENSMUSG00000060600 ENSMUSG00000028128 ENSMUSG00000069805 ENSMUSG00000019997 ENSMUSG00000021250" +
  " ENSMUSG00000029135 ENSMUSG00000032114 ENSMUSG00000025579 ENSMUSG00000057666 ENSMUSG00000061099 ENSMUSG00000021360" +
  " ENSMUSG00000020766 ENSMUSG00000034220 ENSMUSG00000055653 ENSMUSG00000031119 ENSMUSG00000024431 ENSMUSG00000026864" +
  " ENSMUSG00000003865 ENSMUSG00000003665 ENSMUSG00000025232 ENSMUSG00000037012 ENSMUSG00000000628 ENSMUSG00000005413" +
  " ENSMUSG00000020875 ENSMUSG00000051022 ENSMUSG00000022261 ENSMUSG00000054008 ENSMUSG00000035847 ENSMUSG00000003541" +
  " ENSMUSG00000020429 ENSMUSG00000028195 ENSMUSG00000020427 ENSMUSG00000025746 ENSMUSG00000032968 ENSMUSG00000052684" +
  " ENSMUSG00000074657 ENSMUSG00000022991 ENSMUSG00000004383 ENSMUSG00000063229 ENSMUSG00000030851 ENSMUSG00000024529" +
  " ENSMUSG00000047557 ENSMUSG00000042622 ENSMUSG00000033307 ENSMUSG00000039308 ENSMUSG00000039910 ENSMUSG00000025025" +
  " ENSMUSG00000040435 ENSMUSG00000022443 ENSMUSG00000005125 ENSMUSG00000056749 ENSMUSG00000019916 ENSMUSG00000018906" +
  " ENSMUSG00000026335 ENSMUSG00000027513 ENSMUSG00000000489 ENSMUSG00000020277 ENSMUSG00000004791 ENSMUSG00000062070" +
  " ENSMUSG00000025537 ENSMUSG00000050965 ENSMUSG00000041237 ENSMUSG00000026413 ENSMUSG00000037411 ENSMUSG00000046223" +
  " ENSMUSG00000029167 ENSMUSG00000024190 ENSMUSG00000004044 ENSMUSG00000032648 ENSMUSG00000039191 ENSMUSG00000032238" +
  " ENSMUSG00000001020 ENSMUSG00000068874 ENSMUSG00000036432 ENSMUSG00000003153 ENSMUSG00000037936 ENSMUSG00000014813" +
  " ENSMUSG00000030103 ENSMUSG00000025743 ENSMUSG00000017009 ENSMUSG00000030096 ENSMUSG00000029552 ENSMUSG00000021253" +
  " ENSMUSG00000035493 ENSMUSG00000037820 ENSMUSG00000019850 ENSMUSG00000035274 ENSMUSG00000027506 ENSMUSG00000023456" +
  " ENSMUSG00000029344 ENSMUSG00000023951 ENSMUSG00000033933 ENSMUSG00000024924 ENSMUSG00000027656 ENSMUSG00000044786" +
  " ENSMUSG00000000078 ENSMUSG00000032035 ENSMUSG00000021754 ENSMUSG00000025478 ENSMUSG00000021831 ENSMUSG00000090084" +
  " ENSMUSG00000028278 ENSMUSG00000026199 ENSMUSG00000047963 ENSMUSG00000057337 ENSMUSG00000067279 ENSMUSG00000003271" +
  " ENSMUSG00000020475 ENSMUSG00000034744 ENSMUSG00000022754 ENSMUSG00000021196 ENSMUSG00000048756 ENSMUSG00000028976" +
  " ENSMUSG00000039236 ENSMUSG00000031609 ENSMUSG00000029171 ENSMUSG00000026458 ENSMUSG00000003955 ENSMUSG00000025791" +
  " ENSMUSG00000028967 ENSMUSG00000022707 ENSMUSG00000020108 ENSMUSG00000062901 ENSMUSG00000035637 ENSMUSG00000032373" +
  " ENSMUSG00000017677 ENSMUSG00000038587 ENSMUSG00000031397 ENSMUSG00000024589 ENSMUSG00000021591 ENSMUSG00000034640" +
  " ENSMUSG00000041798 ENSMUSG00000053470 ENSMUSG00000010830 ENSMUSG00000056962 ENSMUSG00000040128 ENSMUSG00000037060" +
  " ENSMUSG00000034088 ENSMUSG00000050796 ENSMUSG00000025027 ENSMUSG00000026773 ENSMUSG00000032763 ENSMUSG00000001891" +
  " ENSMUSG00000006494 ENSMUSG00000028307 ENSMUSG00000029322 ENSMUSG00000035232 ENSMUSG00000038894")
  .replace(/\s/g, '\n');

var REFSEQ_GENES_EXAMPLE = (
  "XM_011249907 XM_006513247 XR_389265 XM_011238697 NM_010442 XR_875857 XR_874326 NM_080445 XM_006510796 XM_006529077" +
  " XM_006532452 XM_006497644 XM_006512806 XM_006534517 NM_027342 NM_153150 XM_011241268 XM_006510016 NM_008064" +
  " NM_010728 XR_879520 XM_006527846 NM_133662 NM_008681 XM_011249655 NM_031379 XM_011243401 XM_006503779 NM_009811" +
  " NM_016911 NM_030678 NM_178892 NM_009627 NM_010591 XM_006516490 XM_011241214 XM_006541030 XM_006504976 NM_011044" +
  " NM_175096 XM_011244379 XM_011250435 XR_380369 NM_010474 XM_006541429 XM_006504058 XM_011243513 XM_006536195" +
  " NM_007498 NM_010516 XM_011243665 NM_016753 XM_011238675 XM_006520592 NM_007635 XM_006539076 NM_011756 NM_008304" +
  " XM_011247939 XM_006511549 NM_028803 XM_011239446 NM_008447 NM_031185 XM_011244664 NM_018870 XR_873272 NM_009285" +
  " XM_006509543 XM_006503799 NM_008826 XM_011246838 XM_011244016 NM_008828 NM_007792 XM_006501178 XM_011245484" +
  " NM_010171 XM_011244488 NM_207176 XM_011240871 XM_011247160 XM_006500937 NM_177410 XM_011246309 NM_001081212" +
  " XR_865927 NM_144903 XM_006512576 NM_007413 XM_006539210 NM_007669 NM_009875 XM_006508471 NM_008341 NM_011803" +
  " XM_006504286 NM_016905 NM_007902 NM_009368 NM_009369 NM_013642 XM_006514444 NM_001033225 NM_011101 XM_006510269" +
  " NM_031168 NM_009505 NM_010107 XM_006500988 XM_011241109 NM_009507 XM_006527758 NM_207655 XM_006501135" +
  " XM_006529251 XM_011248817 XR_386457 NM_021788 NM_009373 NM_015774 NM_008871 NM_145630 XR_877142 XM_006539641" +
  " XR_379397 NM_011224 XM_006506410 NM_009150 XR_377434 XM_006502685 NM_007833 XM_006520517 XM_006499169 NM_010217" +
  " XM_011247925 XM_006513197 XM_011250978 XM_011244936 XM_006538525 XR_869642 XR_878325 NM_009657 NM_011498" +
  " XM_011248318 NM_010798 XM_006512702 XM_011242682 NM_013820 XM_006527759 XM_006529114 XM_006541000 NR_102727" +
  " XM_006540681 NM_007569 XM_006526742 XR_378209 NM_010234 NM_008037 XR_390349 NM_008654 XM_006522396 NM_009174" +
  " NM_016854 NM_027491 NM_028132 NM_022410 NM_011627 XM_011248145 XM_011245393 NM_009415 XM_006538688 NM_011521" +
  " NM_022310 NM_139297 XM_006505504 XM_006537130 NM_028444 XM_011249430 XM_011246846 XM_006525666 XM_006500956" +
  " NM_029083 XM_006517477 XR_879502")
  .replace(/\s/g, '\n');

var ENTREZ_GENES_EXAMPLE = (
  "15368 93692 104263 99929 15417 16770 15275 12576 66681 13358 17133 16948 12111 21366 17859 21753 14735 56174" +
  " 11535 11541 15937 21985 52231 74747 19252 11674 12831 14387 17684 14121 19017 12457 12209 12177 21983 17886" +
  " 17035 15211 17319 68507 20527 12575 12767 13636 15116 60406 170750 13638 16833 19309 20198 14828 16476 17988" +
  " 23849 12452 21929 12389 14433 14219 12306 109042 236900 15277 16007 14635 18654 22022 16006 14734 57444 26401" +
  " 56012 14936 18534 18655 22346 11676 18591 20778 110611 13008 170768 384783 18750 13649 54200 11717 14815 13808" +
  " 56484 12226 13806 14538 21810 56421 20439 53412 75785 51795 228026 12577 231507 12043 76459 18772 18451 20855" +
  " 11639 19883 13179 15531 22359 230163 13198 18484 117592 16009 20893 105785 72157 14284 83814 12368 56277 83553" +
  " 216136 18793 50527 108767 14733 74155 12870 21991 20341 20970 26757 16828 14066 18641 52187 76238 15529 16193" +
  " 13615 83397 11910 56485 16322 18682 21809 17872 18787 19285 78889 23871 16572 11520 18770 21817 22339 53374" +
  " 52331 15476 14281 107817 22695 17423 216558 15931 18452 14385 16795 20971 74185 13004 70186 14447 18030 13527" +
  " 13807 19664 103988 12032 22403")
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
    return {db_species: '', query_species: '', genes: ''};
  },

  componentDidMount: function() {
    Eventbus.once(Utils.Event.RUN_EXAMPLE, this.runExample)
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
        this.state.query_species,
        this.state.db_species,
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

  runExample: function(geneFormat) {
    var genes;
    if (geneFormat === 'ensembl') {
      genes = ENSEMBL_GENES_EXAMPLE;
    } else if (geneFormat === 'refseq') {
      genes = REFSEQ_GENES_EXAMPLE;
    } else if (geneFormat === 'entrez') {
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
                  <input type="radio" name="db_species" value="hs" checked={this.state.db_species === Utils.Species.HUMAN}
                         onChange={this.handleDBSpeciesChange} />
                  Homo Sapiens
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="db_species" value="mm" checked={this.state.db_species === Utils.Species.MOUSE}
                         onChange={this.handleDBSpeciesChange} />
                  Mus Musculus
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="db_species" value="rt" checked={this.state.db_species === Utils.Species.RAT}
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
                  <input type="radio" name="query_species" value="hs" checked={this.state.query_species === Utils.Species.HUMAN}
                         onChange={this.handleQuerySpeciesChange} />
                  Homo Sapiens
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="query_species" value="mm" checked={this.state.query_species === Utils.Species.MOUSE}
                         onChange={this.handleQuerySpeciesChange} />
                  Mus Musculus
                </label>
              </div>
              <div className="radio">
                <label>
                  <input type="radio" name="query_species" value="rt" checked={this.state.query_species === Utils.Species.RAT}
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
              <li><a onClick={() => this.runExample('symbol')}>with Symbol</a></li>
              <li><a onClick={() => this.runExample('ensembl')}>with Ensembl</a></li>
              <li><a onClick={() => this.runExample('refseq')}> with RefSeq</a></li>
              <li><a onClick={() => this.runExample('entrez')}> with Entrez</a></li>
            </ul>
          </div>
        </div>
      </form>
    );
  }

});

module.exports = RequestForm;