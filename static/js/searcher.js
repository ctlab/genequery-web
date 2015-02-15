/**
 * Created by smolcoder on 06/02/15.
 */
$(document).ready(function() {
    var lastScrollTop = 0;
    var firstNotReadmore = 0;
    var totalResults = 0;
    var minDistanceBeforeReadmore = $(window).height();
    var readmoreLoadChunkSize = 20;

    var example_gene_set = "Cd274\nNos2\nIrg1\nGbp2\nCxcl9\nPtgs2\nSaa3\nGbp5\nIigp1\nGbp4\nGbp3\nIl1rn\nIl1b\nAW112010" +
        "\nOasl1\nGbp6\nCd86\nRsad2\nAA467197\nCcl5\nTgtp2\nClic5\nZbp1\nGbp7\nSocs3\nSerpina3g\nProcr\nIgtp\nSlco3a1" +
        "\nLy6a\nSlc7a2\nC3\nCd40\nIfit1\nFam26f\nClec4e\nBst1\nIsg15\nIrf1\nAcsl1\nCd38\nIfit2\nThbs1\nGm4951\nIfi47" +
        "\nIfi44\nGm12250\nIrgm2\nIl15ra\nAss1\nSlfn1\nNod1\nIl18bp\nSerpinb9\nSocs1\nSod2\nGm12185\nCnn3\nHerc6\nCcrl2" +
        "\nTnf\nSlamf8\nPla2g4a\nTrim30c\nUsp18\nIrf7\nGbp8\nFpr1\nTap1\nH2-Q6\nTgm2\nIrgm1\nTraf1\nMx1\nAoah\nBatf2" +
        "\nF830016B08Rik\nPfkfb3\nUpp1\nFpr2\nItga6\nTapbpl\nH2-Q7\nPhf11d\nMmp14\nMs4a6d\nLtf\nNlrc5\nPla2g16\nIl6" +
        "\nSlc31a2\nRasgrp1\nJdp2\n1600014C10Rik\nLrrc8c\nStat1\nGbp9\nTma16\nSlc2a6\nSerpina3f";

    function setExampleData() {
        $('#mm').prop('checked', true);
        $('#genes').text(example_gene_set).trigger('autosize.resize');
        $('#search-form').submit();
    }

    $('#example-btn').click(setExampleData);

    $('#search-form').on('submit', function(event){
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

    function setError (message) {
        var error = '<div class="alert alert-danger search-form" role="alert">' +
        '<span class="sr-only">Error:</span>' + message + '</div>';
        $('.search-results').append(error);
    }

    function fillSearchResults(recap, results) {
        var results_div = $('.search-results');
        results_div.append(recap);
        for(var i = 0; i < results.length; ++i) {
            results_div.append(results[i])
        }
        totalResults = results.length;
    }

    function getFormDataInJson() {
        var form = $('#search-form').serializeArray();
        var data ={};
        $.each(form, function() {
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

    $(window).scroll(function(event){
        var st = $(this).scrollTop();
        if (st > lastScrollTop - minDistanceBeforeReadmore){
            setReadmore(firstNotReadmore + readmoreLoadChunkSize);
        }

    });

    function asyncReadmore(to) {
        setTimeout(function() {
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
                type : "GET",
                url: "/searcher/search/",
                data : getFormData(),

                beforeSend : function() {
                    showLoader();
                },
                success : ajaxSuccess,
                error : ajaxError
            });
        }

    }
});
