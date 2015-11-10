(function e(t,n,r){function s(o,u){if(!n[o]){if(!t[o]){var a=typeof require=="function"&&require;if(!u&&a)return a(o,!0);if(i)return i(o,!0);var f=new Error("Cannot find module '"+o+"'");throw f.code="MODULE_NOT_FOUND",f}var l=n[o]={exports:{}};t[o][0].call(l.exports,function(e){var n=t[o][1][e];return s(n?n:e)},l,l.exports,e,t,n,r)}return n[o].exports}var i=typeof require=="function"&&require;for(var o=0;o<r.length;o++)s(r[o]);return s})({1:[function(require,module,exports){
// ugly code :(
(function ($, window, document) {
  var ResultTable = (function () {
    var headInfo = [
      {'width': 2, 'title': '#'},
      {'width': 70, 'title': 'Experiment title'},
      {'width': 2, 'title': 'Module'},
      {'width': 6, 'title': 'p-value'},
      {'width': 7, 'title': 'Overlap'},
      {'width': 5, 'title': 'GSE'},
      {'width': 5, 'title': 'GMT'}
    ];

    var chunkSize = 50;

    function makeColumnWidthProportions() {
      var result = [];
      $.each(headInfo, function (index, value) {
        result.push($('<col />', {'width': value.width + '%'}));
      });
      return result;
    }

    function makeTHead(rc) {
      var $thead = $('<thead>');
      var recap = ['Entered', rc['genes_entered'], 'genes in', rc['id_format'], 'format, where',
        rc['unique_entrez'], 'unique Entrez IDs. Found', rc['total'], 'modules in', rc['time'], 'sec.'].join(' ');
      var recapTh = $('<th>', {colspan: 4, class: 'no-right-border'}).text(recap);
      var toTop = $('<th>', {colspan: 1, class: 'no-right-border no-left-border'})
        .append($('<a>', {id: "toTop"}).text('To top'));
      var csvTh = $('<th>', {colspan: 2, class: 'no-left-border'})
        .append('<input type="submit" value="Download as CSV" id="csv-download" class="btn btn-primary btn-xs"></th>');
      $('<tr>', {class: 'search-result-recap'}).appendTo($thead).append(recapTh).append(toTop).append(csvTh);
      var columnTr = $('<tr>').appendTo($thead);
      $.each(headInfo, function (index, value) {
        $('<th>').text(value['title']).appendTo(columnTr);
      });
      return $thead;
    }

    function makeRow(row) {
      var mn = row['module_number'],
        sr = row['series'],
        pl = row['platform'];
      var $tr = $('<tr>');
      // rank
      $('<td>', {class: 'text-right'}).text(row['rank']).appendTo($tr);

      // title
      $('<td>').text(row['title']).appendTo($tr);

      // module
      if (row['series_url']) {
        $('<td>').append($('<a>', {
          'href': row['series_url'],
          'data-lightbox': 'image-' + sr + '-' + pl,
          'data-title': sr + ', module ' + mn
        }).text(mn)).appendTo($tr);
      } else {
        $('<td>').text(mn).appendTo($tr);
      }

      // p-value
      $('<td>').text(row['adjusted_score']).appendTo($tr);

      // overlap
      var overlap_length = parseFloat(row['overlap_size']);
      var module_length = parseInt(row['module_size']);
      $('<td>', {align: "center", valign: "middle"})
        .append($('<a>', {'class': 'overlap', 'data-module': sr + '_' + pl + '#' + mn})
          .text(overlap_length + '/' + module_length))
        .appendTo($tr);

      // series
      $('<td>').append($('<a>', {
        target: '_blank',
        href: 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + sr
      }).text(sr)).appendTo($tr);

      // gmt
      $('<td>', {class: 'text-center'})
        .append($('<a>', {href: row['gmt_url']})
          .append($('<span>')
            .addClass('glyphicon glyphicon-download')))
        .appendTo($tr);
      return $tr;
    }

    function ResultTable(jsonData) {
      this.recap = jsonData['recap'];
      this.data = jsonData['data'];
      this.rowsLoaded = 0;

      this.innerTable = $('<table>').addClass('table table-bordered table-hover');
      this.innerTable.append(makeColumnWidthProportions());
      this.innerTable.append(makeTHead(this.recap));
      this.tbody = $('<tbody>');
      this.innerTable.append(this.tbody);
    }

    ResultTable.prototype = {
      loadNextChunk: function () {
        if (this.rowsLoaded >= this.data.length) {
          return 0;
        }
        var upper = Math.min(this.data.length, this.rowsLoaded + chunkSize);
        for (var i = this.rowsLoaded; i < upper; i++) {
          this.tbody.append(makeRow(this.data[i]))
        }
        this.rowsLoaded = upper;
        return upper;
      },

      show: function () {
        var $this = this;
        var w = $(window);
        var $results = $('.search-results');

        while ($this.loadNextChunk() > 0) {
        }

        $results.empty().append(this.innerTable);
        $this.innerTable.stickyTableHeaders();
        $('html, body').animate({
          scrollTop: $results.offset().top
        }, 500);
        $('#toTop').on('click', function () {
          w.scrollTop($results.offset().top);
        });
        //w.scroll(function() {
        //    if ($(document).height() - (w.scrollTop() - w.height()) < 2000) {
        //        $this.loadNextChunk();
        //    }
        //})
      }
    };
    return ResultTable;
  }());

  var SearchForm = (function () {
    function SearchForm() {
      this.init = function () {
        this.mm = $('#mm');
        this.hs = $('#hs');
        this.genesInput = $('#genes');
        this.form = $('#search-form');

        $('#gene-list-label').popover();
      };

      this.init();
    }

    SearchForm.prototype = {
      getFormDataInJson: function () {
        var form = this.form.serializeArray();
        var data = {};
        $.each(form, function () {
          if (data[this.name] !== undefined) {
            if (!data[this.name].push) {
              data[this.name] = [data[this.name]];
            }
            data[this.name].push(this.value || '');
          } else {
            data[this.name] = this.value || '';
          }
        });
        return data;
      },

      getDataAsUrl: function () {
        return this.form.serialize();
      },

      getDataAsObj: function () {
        var paramObj = {};
        $.each(this.form.serializeArray(), function (_, kv) {
          if (paramObj.hasOwnProperty(kv.name)) {
            paramObj[kv.name] = $.makeArray(paramObj[kv.name]);
            paramObj[kv.name].push(kv.value);
          }
          else {
            paramObj[kv.name] = kv.value;
          }
        });
        return paramObj;
      },

      validate: function () {
        var data = this.getFormDataInJson();
        var messages = [];
        if (data['species'] == null || data['species'] == '') {
          messages.push('Species not specified.');
        }
        if (data['genes'] == '') {
          messages.push('Gene list is empty.');
        }
        return messages.join(' ');
      }
    };
    return SearchForm;
  }());

  var SearchPage = (function () {
    var example_genes = ("Cd274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86 " +
    "Rsad2 Ccl5 Tgtp2 Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f " +
    "Clec4e Bst1 Isg15 Irf1 Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9")
      .replace(/\s/g, '\n');

    var csv_fields = ['rank', 'adjusted_score', 'series', 'platform',
      'module_number', 'overlap_size', 'module_size', 'title'];

    function SearchPage() {
      var $this = this;

      $this.resultData = null;
      $this.searchResults = $('.search-results');
      $this.runExampleTimeout = 250; // in milliseconds

      $this.searchForm = new SearchForm();
      $this.searchForm.form.submit(function (event) {
        event.preventDefault();
        (function scrollToResults() {
          $('html, body').animate({
            scrollTop: $("#search-btn").offset().top
          }, 500);
        })();
        $this.clearResults();
        $this.sendSearchQuery();
      });
    }

    SearchPage.prototype = {

      runExample: function () {
        this.searchForm.mm.prop('checked', true);
        this.searchForm.genesInput.val(example_genes).trigger('autosize.resize');
        this.searchForm.form.submit();
      },

      clearResults: function () {
        this.searchResults.html('');
      },

      showLoader: function () {
        $('.loader').fadeIn('slow');
      },

      hideLoader: function () {
        $('.loader').fadeOut('fast');
      },


      setError: function (message) {
        this.searchResults.append('<div class="alert alert-danger search-form" role="alert">' +
        '<span class="sr-only">Error:</span>' + message + '</div>');
      },

      noResult: function () {
        $('.search-results').text('No result found.');
      },

      ajaxSuccess: function (json) {
        var $this = this;
        $('.loader').fadeOut("fast", function () {
          if (json['error']) {
            $this.resultData = null;
            $this.setError(json['error']);
          } else {
            $this.resultData = json; // todo clone?
            if (json['data'].length > 0) {
              console.time('create');
              var table = new ResultTable(json);
              console.timeEnd('create');
              console.time('show');
              table.show();
              console.timeEnd('show');
            } else {
              $this.noResult();
            }
          }
        });
      },

      ajaxError: function () {
        var $this = this;
        $this.resultData = null;
        $('.loader').fadeOut("fast", function () {
          $this.setError("Server error.");
        });
      },

      sendSearchQuery: function () {
        var errorMessage = this.searchForm.validate();
        if (errorMessage != '') {
          this.setError(errorMessage);
        } else {
          var $this = this;
          $.ajax({
            type: "GET",
            url: "search/",
            data: $this.searchForm.getDataAsUrl(),

            beforeSend: function () {
              $this.showLoader();
            },
            success: function (data) {
              $this.ajaxSuccess(data)
            },
            error: function (xhr, status, error) {
              console.log(xhr, status, error);
              $this.ajaxError()
            }
          });
        }
      },

      getCSV: function () {
        var data = this.resultData['data'];
        var delimiter = ',';
        var csvContent = csv_fields.join(delimiter) + "\n";
        $.each(data, function (index, value) {
          var row = '';
          $.each(csv_fields, function (i, v) {
            if (i > 0) row += delimiter;
            if (v === "title") {
              row += "\"" + value[v] + "\"";
            } else {
              row += value[v];
            }
          });
          csvContent += index < data.length ? row + "\n" : row;
        });
        return csvContent;
      }
    };
    return SearchPage;
  }());

  // do on document ready
  $(function () {
    var searchPage = new SearchPage();

    function getUrlParameter(sParam) {
      var sPageURL = window.location.search.substring(1);
      var sURLVariables = sPageURL.split('&');
      for (var i = 0; i < sURLVariables.length; i++) {
        var sParameterName = sURLVariables[i].split('=');
        if (sParameterName[0] == sParam) {
          return sParameterName[1];
        }
      }
      return null;
    }

    if (getUrlParameter('example') == 'true') {
      setTimeout(function () {
        searchPage.runExample();
      }, searchPage.runExampleTimeout);
    }

    $('#example-btn').click(function () {
      searchPage.runExample();
    });

    $('#genes').autosize();

    // TODO refactor this monkey code!
    $(document).on('click', '.overlap', function () {
      var formData = searchPage.searchForm.getDataAsObj();
      $.ajax({
        type: "GET",
        url: "search/get_overlap/",
        data: {
          species: formData['species'],
          genes: formData['genes'],
          module: this.getAttribute('data-module')
        },

        success: function (data) {
          $.featherlight($('<div>', {style: 'white-space: pre;'})
            .text(data['genes'].join('\n')));
        }
      });
    });


    $('.search-results').on('click', '#csv-download', function () {
      var formData = searchPage.searchForm.getDataAsObj();
      var now = new Date();
      var dateString = now.getHours() + "-" + now.getMinutes() + "_"
        + now.getMonth() + "-" + (now.getDay() + 1) + "-" + now.getFullYear();
      var filename = 'genequery_search_result_' + formData['species'] + "_" + dateString + '.csv';

      var blob = new Blob([searchPage.getCSV()], {type: 'text/csv;charset=utf-8;'});
      if (navigator.msSaveBlob) { // IE 10+
        navigator.msSaveBlob(blob, filename);
      } else {
        var link = document.createElement("a");
        if (link.download !== undefined) {
          var url = URL.createObjectURL(blob);
          link.setAttribute("href", url);
          link.setAttribute("download", filename);
          link.style = "visibility:hidden";
          document.body.appendChild(link);
          link.click();
          document.body.removeChild(link);
        }
      }
    });
  });
})(window.jQuery, window, document);
},{}]},{},[1]);
