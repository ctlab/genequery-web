function paintOverlap(canvas, overlap_size, module_size) {
    var overlap = overlap_size / module_size;
    var ctx = canvas.getContext("2d");
    ctx.fillStyle='#d0e2f2';
    ctx.fillRect(0, 0, Math.ceil(overlap * 100), 20);
    ctx.strokeStyle = '#d0e2f2';
    ctx.strokeRect(0, 0, 100, 20);
    ctx.font="12px Arial";
    ctx.fillStyle = "#337ab7";
    ctx.fillText(overlap_size + "/" + module_size, 10, 15);
}

function ResultTable(data) {
    var headInfo = [
        {
            'width': 2,
            'title': '#'
        },
        {
            'width': 70,
            'title': 'Experiment title'
        },
        {
            'width': 2,
            'title': 'Module'
        },
        {
            'width': 6,
            'title': 'p-value'
        },
        {
            'width': 10,
            'title': 'Overlap'
        },
        {
            'width': 5,
            'title': 'GSE'
        },
        {
            'width': 5,
            'title': 'GMT'
        }
    ];

    var makeColumnWidthProportions = function() {
        var result = [];
        $.each(headInfo, function(index, value) {
            result.push($('<col />', {'width': value.width + '%'}));
        });
        return result;
    };

    var makeTHead = function(rc) {
        var $thead = $('<thead>');
        var recap = 'Entered ' + rc['genes_entered'] + ' genes in ' + rc['id_format'] +
            ' format, where ' + rc['unique_entrez'] + ' unique Entrez IDs. Found ' + rc['total'] +
            ' modules in ' + rc['time'] + ' sec.';
        var recapTh = $('<th>', {colspan: 4, class: 'no-right-border'}).text(recap);
        var toTop = $('<th>', {colspan: 1, class: 'no-right-border no-left-border'})
            .append($('<a>', {id: "toTop", cursor: 'pointer'}).text('On top'));
        var csvTh = $('<th>', {colspan: 2, class: 'no-left-border'})
            .append('<input type="submit" value="Download as CSV" id="csv-download" class="btn btn-primary btn-xs"></th>');
        $('<tr>', {class: 'search-result-recap'}).appendTo($thead).append(recapTh).append(toTop).append(csvTh);
        var columnTr = $('<tr>').appendTo($thead);
        $.each(headInfo, function(index, value) {
           $('<th>').text(value['title']).appendTo(columnTr);
        });
        return $thead;
    };

    var makeRow = function(row) {
        var mn = row['module_number'],
            sr = row['series'],
            pl = row['platform'];
        var $tr = $('<tr>');
        // rank
        $('<td>', {class: 'text-right'}).text(row['rank']).appendTo($tr);

        // title
        $('<td>').text(row['title']).appendTo($tr);

        // module
        $('<td>').append($('<a>', {
            'href': row['series_url'],
            'data-lightbox': 'image-' + sr + '-' + pl,
            'data-title': sr + ', module ' + mn}).text(mn)).appendTo($tr);

        // p-value
        $('<td>').text(row['adjusted_score']).appendTo($tr);

        // overlap
        var overlap_length = parseFloat(row['overlap_size']),
            module_length = parseInt(row['module_size']);
        var $canvas = $('<canvas>').attr("width", "100").attr("height", "20");
        paintOverlap($canvas[0], overlap_length, module_length);
        $('<td>', {align: "center", valign: "middle"}).append($canvas).appendTo($tr);

        // series
        $('<td>').append($('<a>', {
            target: '_blank',
            href: 'http://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=' + sr
        }).text(sr)).appendTo($tr);

        // gmt
        $('<td>', {class: 'text-center'}).append($('<a>', {href: row['gmt_url']}).append($('<span>').addClass('glyphicon glyphicon-download')))
            .appendTo($tr);
        return $tr;
    };

    var makeTBody = function(data) {
        var $tbody = $('<tbody>');
        $.each(data, function(index, row){
            $tbody.append(makeRow(row));
        });
        return $tbody;
    };

    this.init = function() {
        var $table = $('<table>').addClass('table table-bordered table-hover');
        $table.append(makeColumnWidthProportions());
        $table.append(makeTHead(data['recap']));
        $table.append(makeTBody(data['data']));
        return $table;
    };

    this.table = this.init();
}

ResultTable.prototype = {
    show: function() {
        var $results = $('.search-results');
        $results.empty().append(this.table);
        this.table.stickyTableHeaders();
        $('html, body').animate({
            scrollTop: $results.offset().top
        }, 500);
        $('#toTop').on('click', function() {
            $(window).scrollTop($results.offset().top);
        });
    },
    destroy: function() {
        this.table.remove();
    }
};

function SearchForm() {
    this.init = function() {
        this.mm = $('#mm');
        this.hs = $('#hs');
        this.genesInput = $('#genes');
        this.form = $('#search-form');

        $('#gene-list-label').popover();
    };

    this.init();
}

SearchForm.prototype = {
    getFormDataInJson: function() {
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

    getData: function() {
        return this.form.serialize();
    },

    validate: function() {
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

function SearchPage() {
    this.init = function() {
        this.searchResults = $('.search-results');
        this.runExampleTimeout = 250; // in milliseconds

        this.searchForm = new SearchForm();
        var $this = this;
        this.searchForm.form.submit(function(event) {
            event.preventDefault();
            (function scrollToResults() {
                $('html, body').animate({
                    scrollTop: $("#search-btn").offset().top
                }, 500);
            })();
            $this.sendSearchQuery();
        });
    };
    this.init();
}

SearchPage.prototype = {
    resultData: null,
    runExample: function() {
        var example_genes = ("Cd274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86 " +
            "Rsad2 Ccl5 Tgtp2 Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f " +
            "Clec4e Bst1 Isg15 Irf1 Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9")
            .replace(/\s/g, '\n');

        this.searchForm.mm.prop('checked', true);
        this.searchForm.genesInput.val(example_genes).trigger('autosize.resize');
        this.searchForm.form.submit();
    },

    clearResults: function() {
        this.searchResults.html('');
    },

    showLoader: function() {
        $('.loader').fadeIn('slow');
    },

    hideLoader: function() {
        $('.loader').fadeOut('fast');
    },


    setError: function(message) {
        // TODO
        var error = '<div class="alert alert-danger search-form" role="alert">' +
                    '<span class="sr-only">Error:</span>' + message + '</div>';
        this.searchResults.append(error);
    },

    noResult: function() {
        $('.search-results').text('No result found.');
    },

    ajaxSuccess: function(json) {
        var $this = this;
        $('.loader').fadeOut("fast", function() {
            if (json['error']) {
                $this.resultData = null;
                $this.setError(json['error']);
            } else {
                $this.resultData = json; // todo clone?
                if (json['data'].length > 0) {
                    var table = new ResultTable(json);
                    table.show();
                } else {
                    $this.noResult();
                }
            }
        });
    },

    ajaxError: function() {
        var $this = this;
        $this.resultData = null;
        $('.loader').fadeOut("fast", function() {
            $this.setError("Server error.");
        });
    },

    sendSearchQuery: function() {
        this.clearResults();
        var errorMessage = this.searchForm.validate();
        if (errorMessage != '') {
            this.setError(errorMessage);
        } else {
            var $this = this;
            $.ajax({
                type: "GET",
                url: "search/",
                data: $this.searchForm.getData(),

                beforeSend: function () {
                    $this.showLoader();
                },
                success: function(data) {$this.ajaxSuccess(data)},
                error: function() {$this.ajaxError()}
            });
        }
    },

    csv_fields: ['rank', 'adjusted_score', 'series', 'platform', 'module_number', 'overlap_size', 'module_size', 'title'],

    getCSV: function() {
        var $this = this;
        var data = $this.resultData['data'];
        var delimiter = ',';
        var csvContent = SearchPage.prototype.csv_fields.join(delimiter) + "\n";
        $.each(data, function(index, value){
            var row = '';
            $.each($this.csv_fields, function(i, v) {
                if (i > 0) row += delimiter;
                if (v == "title") {
                    row += "\"" + value[v] + "\"" + 3 * delimiter;
                } else {
                    row += value[v];
                }
            });
            csvContent += index < data.length ? row + "\n" : row;
        });
        return csvContent;
    }

};

$(document).ready(function () {
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

    $('#example-btn').click(function() {
        searchPage.runExample();
    });

    $('#genes').autosize();


    $('.search-results').on('click', '#csv-download', function () {
        var filename = 'search_results.csv';
        var blob = new Blob([searchPage.getCSV()], { type: 'text/csv;charset=utf-8;' });
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
