
var chartdata2 = [];
var chartname2 = '';
function processData2(data_received) {
    var data = data_received.data;
    for (var i = 0; i < data.length; i++) {
        chartdata2.push([
            Date.parse(data[i][1]), data[i][2]
        ])
    }
    chartname2 = data_received.name;
};

function plotCharts2() {
    Highcharts.chart('chart-div2', {

        chart: {
            events: {
                load: function () {
                    var series = this.series[0];
                    setInterval(function () {
                        fetch_newdata2(series);
                    }, 1000);
                }
            }
        },

        time: {
            useUTC: false
        },

        xAxis: {
            type: 'datetime',
            dateTimeLabelFormats: {
                minute: '%H:%M',
                hour: '%H:%M',
                day: '%e. %b',
                week: '%e. %b',
                month: '%b \'%y',
                year: '%Y'
            }
        },

        series: [{
            name: chartname2,
            data: chartdata2
        }]
    });
};


function fetchdata2() {
    request_params = {
        client_name: 'cpe1',
        param_name: 'param1',
        table_name: 'table1',
        ts_start: '',
        ts_end: '',
    };

    $.getJSON('/fetchdata', request_params, function (data_received) {
        //console.log('received from be', data_received);
        processData2(data_received);
        plotCharts2();
    });
};


function fetch_newdata2(series) {
    $.ajax({
        url: "/fetchdata",
        data: {
            client_name: 'cpe1',
            param_name: 'param1',
            table_name: 'table1',
            single_data: true,
            ts_start: '',
            ts_end: '',
        },
        dataType: 'json',
        success: function (response) {
            //temp = parseFloat(((raw.main.temp) - 273.15).toPrecision(4))
            date = Date.now()
            //data_.push([date, temp])
            //response=JSON.parse(response);
            console.log('response is: ', response.data)
            //var datax = response.data;
            x = Date.parse(response.data[0][1])
            y = response.data[0][2]
            console.log('data member is: ', response.data[0][2])

            //plot_chart()
            var index = series.xData.indexOf(x)
            console.log('# index', index)
            if (y != null && index == -1) {
                series.addPoint([x, y], true, true, false);
            }
        }
    })
};


$(document).ready(function () {
    fetchdata2();
});

