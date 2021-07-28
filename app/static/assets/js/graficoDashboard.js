"use strict";
!function (NioApp, $) {
    var TrafficChannelDoughnutData = {
        labels: nombreCuenta,
        dataUnit: '',
        legend: false,
        datasets: [{
          borderColor: "#fff",
          background: ["#798bff", "#b8acff", "#ffa9ce", "#f9db7b"],
          data: totalGastos
        }]
      };
    function analyticsDoughnut(selector, set_data) {
        var $selector = selector ? $(selector) : $('.analytics-doughnut');
        $selector.each(function () {
          var $self = $(this),
              _self_id = $self.attr('id'),
              _get_data = typeof set_data === 'undefined' ? eval(_self_id) : set_data;

          var selectCanvas = document.getElementById(_self_id).getContext("2d");
          var chart_data = [];

          for (var i = 0; i < _get_data.datasets.length; i++) {
            chart_data.push({
              backgroundColor: _get_data.datasets[i].background,
              borderWidth: 2,
              borderColor: _get_data.datasets[i].borderColor,
              hoverBorderColor: _get_data.datasets[i].borderColor,
              data: _get_data.datasets[i].data
            });
          }

          var chart = new Chart(selectCanvas, {
            type: 'doughnut',
            data: {
              labels: _get_data.labels,
              datasets: chart_data
            },
            options: {
              legend: {
                display: _get_data.legend ? _get_data.legend : false,
                labels: {
                  boxWidth: 12,
                  padding: 20,
                  fontColor: '#6783b8'
                }
              },
              rotation: -1.5,
              cutoutPercentage: 70,
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
                backgroundColor: '#fff',
                borderColor: '#eff6ff',
                borderWidth: 2,
                titleFontSize: 16,
                titleFontColor: '#6783b8',
                titleMarginBottom: 6,
                bodyFontColor: '#121315',
                bodyFontSize: 16,
                bodySpacing: 4,
                yPadding: 10,
                xPadding: 10,
                footerMarginTop: 0,
                displayColors: false,

                headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
                pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                    '<td style="padding:0"><b>{point.y:.1f} m</b></td></tr>',
                footerFormat: '</table>',
                shared: true,
                useHTML: true

              }
            }
          });
        });
    } // init chart
      NioApp.coms.docReady.push(function () {
        analyticsDoughnut();
      });
}(NioApp, jQuery);
