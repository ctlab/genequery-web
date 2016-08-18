'use strict';
/**
 * Created by smolcoder on 18/08/16.
 */
var React = require('react');
var Eventbus = require('../../eventbus');
var Utils = require('../../utils');

var _ = require('underscore');

var SummaryPanel = React.createClass({
  render: function() {
    return (
      <div className="panel summary-panel">
        <div className="panel-heading">
          <div className="panel-title">SUMMARY</div>
        </div>
        <div className="panel-body">
          <p>Entered: 185 genes. Parsed annotation format: symbol. Orthology was applied. Unique Entrez IDs: 33</p>

          <div className="panel id-mapping-table-wrapper gene-conversion-panel">
            <div className="panel-heading">
              <div className="panel-title"><a>Gene Conversion Table</a></div>
            </div>
          </div>
        </div>
      </div>
    );
  }
});

module.exports = SummaryPanel;