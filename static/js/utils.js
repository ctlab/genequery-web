/**
 * Created by smolcoder on 09/11/15.
 */

var ReactDOMServer = require('react-dom/server');

var Utils = {

  getCookie: function(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = $.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) == (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  },

  getCSRFToken: function() {
    return this.getCookie('csrftoken');
  },


  scrollToTop: function(node, speed) {
    if (node === null) {
      return;
    }
    var element = $(node);
    $('html, body').animate({scrollTop: element.offset().top}, speed == undefined ? 750 : speed);
  },

  reactElementToString: function(element) {
    return ReactDOMServer.renderToStaticMarkup(element);
  },

  /**
   * Show popup with data received via AJAX (e.g. genes from overlap with module).
   *
   * @param url url to send ajax request to
   * @param data ajax request data
   * @param getElementByData function: Object -> ReactElement, transform response to element
   * @param getErrorElement function: Object -> ReactElement, show error
   */
  showPopupAjax: function(url, data, getElementByData, getErrorElement) {
    $.magnificPopup.open({
      items: {
        type: 'ajax'
      },
      alignTop: true,
      ajax: {
        settings: {
          url: url,
          data: data
        }
      },
      callbacks: {
        parseAjax: function (response) {
          var element;
          try {
            console.log('Got data for popup', response.data);
            element = getElementByData(response.data);
          } catch (e) {
            console.error(e);
            element = getErrorElement(e);
          }
          response.data = Utils.reactElementToString(element);
        }
      }
    }, 0);
  },

  /**
   * Show image popup (e.g. heatmap).
   *
   * @param src image url
   * @param title_element title ReactElement
   */
  showPopupImage: function(src, title_element) {
    $.magnificPopup.open({
      items: {
        src: src
      },
      type: 'image',
      alignTop: true,
      overflowY: 'scroll',
      image: {
        verticalFit: false,
        titleSrc: _ => Utils.reactElementToString(title_element)
      }
    });
  },

  /**
   * Initiates downloading of the CSV content as a file.
   *
   * @param filename name of the result CSV file
   * @param content CSV string to be places in the file
   */
  downloadDataAsCSV: function(filename, content) {
    var blob = new Blob([content], {type: 'text/csv;charset=utf-8;'});
    if (navigator.msSaveBlob) { // IE 10+
      navigator.msSaveBlob(blob, filename);
    } else {
      var link = document.createElement("a");
      if (link.download !== undefined) {
        var url = URL.createObjectURL(blob);
        link.setAttribute("href", url);
        link.setAttribute("download", filename);
        link.setAttribute('style', 'visibility:hidden;');
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
      }
    }
  },

  /**
   * Extracts parameter from url and returns it (or null if absents).
   *
   * @param key parameter name
   * @returns string | null
   */
  getUrlParameter: function(key) {
    var page_url = window.location.search.substring(1);
    var url_variables = page_url.split('&');
    for (var i = 0; i < url_variables.length; i++) {
      var param_name = url_variables[i].split('=');
      if (param_name[0] == key) {
        return param_name[1];
      }
    }
    return null;
  },

  /**
   * Remove version from gene string:
   * ENSG000123.4 --> ENSG000123
   * XM_1234.5 --> XM_1234
   *
   * @param gene string representation of the gene.
   * @returns string
   */
  removeGeneVersion: function(gene) {
    if (gene.indexOf('.') >= 0) {
      return gene.substr(0, gene.indexOf('.'));
    }
    return gene;
  }

};

module.exports = Utils;