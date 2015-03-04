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
    runExample: function() {
        var example_genes = ("Cd274 Nos2 Irg1 Gbp2 Cxcl9 Ptgs2 Saa3 Gbp5 Iigp1 Gbp4 Gbp3 Il1rn Il1b Oasl1 Gbp6 Cd86" +
            "Rsad2 Ccl5 Tgtp2 Clic5 Zbp1 Gbp7 Socs3 Serpina3g Procr Igtp Slco3a1 Ly6a Slc7a2 C3 Cd40 Ifit1 Fam26f" +
            "Clec4e Bst1 Isg15 Irf1 Acsl1 Cd38 Ifit2 Thbs1 Ifi47 Ifi44 Irgm2 Il15ra Ass1 Slfn1 Nod Il18bp Serpinb9").replace(/\s/g, '\n');

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

    fillSearchResults: function(recap, results) {
        this.searchResults.append(recap);
        for (var i = 0; i < results.length; ++i) {
            this.searchResults.append(results[i])
        }
    },

    scrollToRecap: function() {
        $('html, body').animate({
            scrollTop: $(".search-results-recap").offset().top - 10
        }, 500);
    },

    setError: function(message) {
        var error = '<div class="alert alert-danger search-form" role="alert">' +
                    '<span class="sr-only">Error:</span>' + message + '</div>';
        this.searchResults.append(error);
    },

    ajaxSuccess: function(json) {
        this.hideLoader();
        if (json['error']) {
            this.setError(json['error']);
        } else {
            this.fillSearchResults(json['recap'], json['data']);
            this.scrollToRecap();
        }
    },

    ajaxError: function() {
        this.hideLoader();
        this.setError("Server error.");
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

    csv_fields: ['rank', 'score', 'series', 'platform', 'module-number', 'overlap-size', 'module-size'],

    collectData: function() {
        var data = [];
        $('.search-result').each(function () {
            var info = $(this).find('.search-result-info');
            var row = [];
            $.each(SearchPage.prototype.csv_fields, function(index, value) {
                row.push(info.attr('data-' + value));
            });
            row.push($(this).find('.data-title').text());
            data.push(row);
        });
        return data;
    },

    getCSV: function() {
        var data = this.collectData();
        var csvContent = SearchPage.prototype.csv_fields.join(";") + ";title\n";
        data.forEach(function(infoArray, index){
            var dataString = infoArray.join(";");
            csvContent += index < data.length ? dataString + "\n" : dataString;
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

    $('body').scrollToTop({
        distance: $("#search-btn").offset().top,
        easing: 'easeOutExpo',
        animation: 'fade',
        animationSpeed: 500,
        text: 'To Top',
        throttle: 250,
        namespace: 'scrollToTop'
    });

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
                searchPage.collectData();
                document.body.removeChild(link);
            }
        }
    });

});
