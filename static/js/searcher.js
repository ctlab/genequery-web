/**
 * Created by smolcoder on 06/02/15.
 */
$(document).ready(function () {
    var lastScrollTop = 0;
    var firstNotReadmore = 0;
    var totalResults = 0;
    var minDistanceBeforeReadmore = $(window).height();
    var readmoreLoadChunkSize = 20;
    var runExampleTimeout = 250;

    var example_gene_set = "Cd274\nNos2\nIrg1\nGbp2\nCxcl9\nPtgs2\nSaa3\nGbp5\nIigp1\nGbp4\nGbp3\nIl1rn\nIl1b\nOasl1" +
        "\nGbp6\nCd86\nRsad2\nCcl5\nTgtp2\nClic5\nZbp1\nGbp7\nSocs3\nSerpina3g\nProcr\nIgtp\nSlco3a1\nLy6a\nSlc7a2\nC3" +
        "\nCd40\nIfit1\nFam26f\nClec4e\nBst1\nIsg15\nIrf1\nAcsl1\nCd38\nIfit2\nThbs1\nIfi47\nIfi44\nIrgm2\nIl15ra\nAss1\\" +
        "nSlfn1\nNod\nIl18bp\nSerpinb9";

    function runExample() {
        $('#mm').prop('checked', true);
        $('#genes').text(example_gene_set).trigger('autosize.resize');
        $('#search-form').submit();
    }

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

    $('#gene-list-label').popover();

    if (getUrlParameter('example') == 'true') {
        setTimeout(function () {
            runExample();
        }, runExampleTimeout);
    }

    $('#example-btn').click(runExample);

    $('#search-form').on('submit', function (event) {
        event.preventDefault();
        scrollToResults();
        send_search_query();
    });

    function scrollToResults() {
        $('html, body').animate({
            scrollTop: $("#search-btn").offset().top
        }, 500);
    }

    function scrollToRecap() {
        $('html, body').animate({
            scrollTop: $(".search-results-recap").offset().top - 10
        }, 500);
    }

    $('#genes').autosize();

    $('.module-description').readmore({
        moreLink: '<a href="#">more</a>',
        lessLink: '<a href="#">less</a>'
    });

    $('body').scrollToTop({
        distance: $("#search-btn").offset().top,
        easing: 'easeOutExpo',
        animation: 'fade', // fade, slide, none
        animationSpeed: 500,
        text: 'To Top', // Text for element, can contain HTML
        throttle: 250,
        namespace: 'scrollToTop'
    });

    function clearResults() {
        $('.search-results').html('');
        lastScrollTop = 0;
        firstNotReadmore = 0;
        totalResults = 0;
    }

    function hideLoader() {
        $('.loader').fadeOut('fast');
    }

    function showLoader() {
        $('.loader').fadeIn('slow');
    }

    function getFormData() {
        return $('#search-form').serialize()
    }

    function setError(message) {
        var error = '<div class="alert alert-danger search-form" role="alert">' +
            '<span class="sr-only">Error:</span>' + message + '</div>';
        $('.search-results').append(error);
    }

    function fillSearchResults(recap, results) {
        var results_div = $('.search-results');
        results_div.append(recap);
        for (var i = 0; i < results.length; ++i) {
            results_div.append(results[i])
        }
        totalResults = results.length;
    }

    function getFormDataInJson() {
        var form = $('#search-form').serializeArray();
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
    }

    function validateForm() {
        var data = getFormDataInJson();
        var messages = [];
        if (data['species'] == null || data['species'] == '') {
            messages.push('Species not specified.');
        }
        if (data['genes'] == '') {
            messages.push('Gene list is empty.');
        }
        return messages.join(' ');
    }

    function setReadmore(to) {
        if (totalResults == 0 || firstNotReadmore >= totalResults) return;
        to = Math.min(totalResults, to);
        var $descriptions = $('.module-description').slice(firstNotReadmore, to);
        $descriptions.readmore({
            moreLink: '<a href="#">more</a>',
            lessLink: '<a href="#">less</a>'
        });
        lastScrollTop = $descriptions.last().offset().top;
        firstNotReadmore = to;
        console.log(lastScrollTop, firstNotReadmore, to);
    }

    $(window).scroll(function (event) {
        var st = $(this).scrollTop();
        if (st > lastScrollTop - minDistanceBeforeReadmore) {
            setReadmore(firstNotReadmore + readmoreLoadChunkSize);
        }

    });

    function asyncReadmore(to) {
        setTimeout(function () {
            setReadmore(to);
        }, 100);
    }

    function ajaxSuccess(json) {
        hideLoader();
        if (json['error']) {
            setError(json['error']);
            console.log('error', json['error']);
        } else {
            fillSearchResults(json['recap'], json['data']);
            scrollToRecap();
            asyncReadmore(25);
            console.log('ok');
        }
    }

    function ajaxError(xhr, errmsg, err) {
        hideLoader();
        setError("Server error.");
    }

    function send_search_query() {
        clearResults();
        var errorMessage = validateForm();
        if (errorMessage != '') {
            setError(errorMessage);
        } else {
            $.ajax({
                type: "GET",
                url: "/searcher/search/",
                data: getFormData(),

                beforeSend: function () {
                    showLoader();
                },
                success: ajaxSuccess,
                error: ajaxError
            });
        }

    }
});
