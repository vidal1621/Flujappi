"use strict";

!function (NioApp, $) {

    function barChart(selector, set_data) {
        var $selector = selector ? $(selector) : $('.bar-chart');
        $selector.each(function () {
          var $self = $(this),
              _self_id = $self.attr('id'),
              _get_data = typeof set_data === 'undefined' ? eval(_self_id) : set_data,
              _d_legend = typeof _get_data.legend === 'undefined' ? false : _get_data.legend;

          var selectCanvas = document.getElementById(_self_id).getContext("2d");
          var chart_data = [];

          for (var i = 0; i < _get_data.datasets.length; i++) {
            chart_data.push({
              label: _get_data.datasets[i].label,
              data: _get_data.datasets[i].data,
              // Styles
              backgroundColor: _get_data.datasets[i].color,
              borderWidth: 2,
              borderColor: 'transparent',
              hoverBorderColor: 'transparent',
              borderSkipped: 'bottom',
              barPercentage: .6,
              categoryPercentage: .7
            });
          }

          var chart = new Chart(selectCanvas, {
            type: 'bar',
            data: {
              labels: _get_data.labels,
              datasets: chart_data
            },
            options: {
              legend: {
                display: _get_data.legend ? _get_data.legend : true,
                rtl: NioApp.State.isRTL,
                labels: {
                  boxWidth: 30,
                  padding: 20,
                  fontColor: '#6783b8'
                }
              },
              maintainAspectRatio: false,
              tooltips: {
                enabled: true,
                rtl: NioApp.State.isRTL,
                callbacks: {
                  title: function title(tooltipItem, data) {
                    return data.datasets[tooltipItem[0].datasetIndex].label;
                  },
                  label: function label(tooltipItem, data) {
                    return separadorMiles(data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem['index']]) + ' ' + _get_data.dataUnit;
                  },
                },
                /*propiedades de la información flotante*/
                backgroundColor: '#eff6ff',
                titleFontSize: 16,
                titleFontColor: '#6783b8',
                titleMarginBottom: 6,
                bodyFontColor: '#111215',
                bodyFontSize: 12,
                bodySpacing: 4,
                yPadding: 10,
                xPadding: 10,
                footerMarginTop: 0,
                displayColors: false
              },
              scales: {
                yAxes: [{
                  display: true,
                  stacked: _get_data.stacked ? _get_data.stacked : false,
                  position: NioApp.State.isRTL ? "right" : "left",
                  ticks: {
                    beginAtZero: true,
                    fontSize: 12,
                    fontColor: '#9eaecf',
                    padding: 5,
                    callback: function(value, index, values) {
                        return '' + separadorMiles(value);
                    }
                  },
                  gridLines: {
                    color: NioApp.hexRGB("#526484", .2),
                    tickMarkLength: 0,
                    zeroLineColor: NioApp.hexRGB("#526484", .2)
                  }
                }],
                xAxes: [{
                  display: true,
                  stacked: _get_data.stacked ? _get_data.stacked : false,
                  ticks: {
                    fontSize: 14,
                    fontColor: '#9eaecf',
                    source: 'auto',
                    padding: 5,
                    reverse: NioApp.State.isRTL
                  },
                  gridLines: {
                    color: "transparent",
                    tickMarkLength: 10,
                    zeroLineColor: 'transparent'
                  }
                }]
              }
            }
          });
        });
    }
    barChart();

    function lineChart(selector, set_data) {
        var $selector = selector ? $(selector) : $('.line-chart');
        $selector.each(function () {
          var $self = $(this),
              _self_id = $self.attr('id'),
              _get_data = typeof set_data === 'undefined' ? eval(_self_id) : set_data;

          var selectCanvas = document.getElementById(_self_id).getContext("2d");
          var chart_data = [];

          for (var i = 0; i < _get_data.datasets.length; i++) {
            chart_data.push({
              label: _get_data.datasets[i].label,
              tension: _get_data.lineTension,
              backgroundColor: _get_data.datasets[i].background,
              borderWidth: 2,
              borderColor: _get_data.datasets[i].color,
              pointBorderColor: _get_data.datasets[i].color,
              pointBackgroundColor: '#fff',
              pointHoverBackgroundColor: "#fff",
              pointHoverBorderColor: _get_data.datasets[i].color,
              pointBorderWidth: 2,
              pointHoverRadius: 4,
              pointHoverBorderWidth: 2,
              pointRadius: 4,
              pointHitRadius: 4,
              data: _get_data.datasets[i].data
            });
          }

          var chart = new Chart(selectCanvas, {
            type: 'line',
            data: {
              labels: _get_data.labels,
              datasets: chart_data
            },
            options: {
              legend: {
                display: _get_data.legend ? _get_data.legend : false,
                rtl: NioApp.State.isRTL,
                labels: {
                  boxWidth: 12,
                  padding: 20,
                  fontColor: '#6783b8'
                }
              },
              maintainAspectRatio: false,
              tooltips: {
                enabled: true,
                rtl: NioApp.State.isRTL,
                callbacks: {
                  title: function title(tooltipItem, data) {
                    return data['labels'][tooltipItem[0]['index']];
                  },
                  label: function label(tooltipItem, data) {
                    return separadorMiles(data.datasets[tooltipItem.datasetIndex]['data'][tooltipItem['index']]) + ' ' + _get_data.dataUnit;
                  }
                },
                backgroundColor: '#eff6ff',
                titleFontSize: 13,
                titleFontColor: '#6783b8',
                titleMarginBottom: 6,
                bodyFontColor: '#030405',
                bodyFontSize: 16,
                bodySpacing: 4,
                yPadding: 10,
                xPadding: 10,
                footerMarginTop: 0,
                displayColors: false
              },
              scales: {
                yAxes: [{
                  display: true,
                  position: NioApp.State.isRTL ? "right" : "left",
                  ticks: {
                    beginAtZero: false,
                    fontSize: 12,
                    fontColor: '#9eaecf',
                    padding: 10,
                    callback: function(value, index, values) {
                        return '' + separadorMiles(value);
                    }
                  },
                  gridLines: {
                    color: NioApp.hexRGB("#526484", .2),
                    tickMarkLength: 0,
                    zeroLineColor: NioApp.hexRGB("#526484", .2)
                  }
                }],
                xAxes: [{
                  display: true,
                  ticks: {
                    fontSize: 12,
                    fontColor: '#9eaecf',
                    source: 'auto',
                    padding: 5,
                    reverse: NioApp.State.isRTL
                  },
                  gridLines: {
                    color: "transparent",
                    tickMarkLength: 10,
                    zeroLineColor: NioApp.hexRGB("#526484", .2),
                    offsetGridLines: true
                  }
                }]
              }
            }
          });
        });
    } // init line chart
    lineChart();
}(NioApp, jQuery);
