var chartdata1 = [];
var chartname1 = '';
var series2 = [];
var chart_test;
var highchart_object_list = [];
const urlParamsInitial = window.location.href;
const chartDictionary = {};

// by clicking on the 'Add chart', the request sent through the 'modal' is processed by this function
$(function () {
    $(document).ready(function () {
        $("#add_chart_submit").click(function () {
            $.ajax({
                'async': true,
                'type': "POST",
                'global': false,
                'dataType': 'html',
                'url': $SCRIPT_ROOT + "/add_chart",
                'data': {
                    chart_name: $('input[name="chart_name"]').val(),
                    chart_config: $('input[name="chart_config"]').val(),
                    urlParamsInitial: urlParamsInitial, // Include urlParams_initial here
                    param1: $('input[name="chart_param1"]').val(),
                    param2: $('input[name="chart_param2"]').val(),
                    //username: $('input[name="username"]').val(),
                    //password: $('input[name="password"]').val(),
                    //title: $('input[name="title"]').val(),
                    //customer: $('input[name="customer"]').val(),
                    //version: $('input[name="version"]').val()
                },
                'success': function (data) {
                    $("#result_add_chart").html(data);
                    $("#wait_add_chart").css("display", "none");
                },
                'beforeSend': function (x) {
                    $("#wait_add_chart").css("display", "inline");
                    $("#result_add_chart").html('Waiting for the result...');
                },
            });
        });
    });
});



// $(document).ready(function () {
//     // chart 1
//     const chart1 = Highcharts.chart('chart-div1', {
//         time: {
//             useUTC: false
//         },

//         xAxis: {
//             type: 'datetime',
//             dateTimeLabelFormats: {
//                 minute: '%H:%M',
//                 hour: '%H:%M',
//                 day: '%e. %b',
//                 week: '%e. %b',
//                 month: '%b \'%y',
//                 year: '%Y'
//             }
//         },

//         series: [{
//             name: 'CPU usage - chart1',
//             data: []
//         }],
//         title: {
//             text: 'CPU - chart1'
//         }
//     });


//     // chart 2
//     const chart2 = Highcharts.chart('chart-div2', {
//         time: {
//             useUTC: false
//         },

//         xAxis: {
//             type: 'datetime',
//             dateTimeLabelFormats: {
//                 minute: '%H:%M',
//                 hour: '%H:%M',
//                 day: '%e. %b',
//                 week: '%e. %b',
//                 month: '%b \'%y',
//                 year: '%Y'
//             }
//         },

//         series: [{
//             name: 'Memory usage - chart 2',
//             data: []
//         }],
//         title: {
//             text: 'Memory - chart 2'
//         }
//     });

//     request_params = {
//         //client_name: client_name_from_flask,
//     };




// to retrieve the configured charts from the database. The next function 'fetch_chart_data', will fill these charts.
function fetchAndRenderCharts() {
    $.get('/get_charts', { urlParamsInitial: urlParamsInitial }, function (chart_list) {
        chart_list.forEach(function (chart) {
            const chartDiv = document.createElement('div');
            chartDiv.id = chart.chart_name;
            document.getElementById('chartContainer').appendChild(chartDiv);

            // Convert the JSON string back to a JavaScript object for the chart configuration
            const chartConfig = JSON.parse(chart.chart_config);

            // Create a Highcharts chart and store it in the dictionary using the unique ID as the key
            const highchart = Highcharts.chart(chart.chart_name, chartConfig);
            chartDictionary[chart.chart_unique_id] = highchart;
        });
        console.log('chartDictionary');
        console.log(chartDictionary);

        // After rendering the charts, fetch chart data for all unique IDs
        //fetchChartDataForAllCharts();
    });
}

fetchAndRenderCharts();








function updateChartWithData(chart, chartData) {
    if (chartData && chartData.length > 0) {
        // Create an object to store data by parameter name
        const dataByParameter = {};

        // Group data by parameter name
        chartData.forEach(item => {
            for (const parameter in item.param_subtree) {
                if (!dataByParameter[parameter]) {
                    dataByParameter[parameter] = [];
                }
                dataByParameter[parameter].push({
                    x: new Date(item.timestamp).getTime(),
                    y: parseFloat(item.param_subtree[parameter]),
                });
            }
        });

        // Update series data in the chart
        chart.series.forEach(series => {
            const parameterName = series.name;
            const data = dataByParameter[parameterName];
            if (data) {
                series.setData(data);
            }
        });
    }
}

function fetch_chart_data() {
    const chart_unique_ids = Object.keys(chartDictionary);
    console.log('chart_unique_ids:');
    console.log(chart_unique_ids);

    // Send the list of chart_unique_id values to the backend
    $.getJSON('/fetch_chart_data', { 'urlParamsInitial': urlParamsInitial, 'chart_unique_ids': chart_unique_ids }, function (data_received) {
        if (data_received.ts_data) {
            // Loop through the received data
            for (const chartUniqueID in data_received.ts_data) {
                const chartData = data_received.ts_data[chartUniqueID];
                const chart = chartDictionary[chartUniqueID];

                console.log('###############################################################');
                console.log('chartUniqueID:'+ chartUniqueID);
                console.log('chartData:', chartData);
                console.log('chartDictionary:', chartDictionary);
                console.log('chart:', chart);



                if (chart) {
                    updateChartWithData(chart, chartData);
                }
            }

            // Update other elements as needed
            document.getElementById('cli_result').innerHTML = data_received.meta_data.last_cli_response;
            document.getElementById('ts_lastmessage').innerHTML = data_received.meta_data.ts_last_message;
        }
    });
}

fetch_chart_data();
setInterval(fetch_chart_data, 1000);













// about CLI commands and PII change, device remote controls
document.addEventListener("DOMContentLoaded", function () {

    // Buttons
    const buttonCliSend = document.getElementById("button_cli_send");
    const buttonIntervalSend = document.getElementById("button_interval_send");

    // Inputs
    const inputContentCli = document.getElementById("input_cli");
    const inputContentInterval = document.getElementById("input_interval");

    // Result element
    const resultDiv = document.getElementById("cli_result");

    // Function to send a message
    function sendMessage(inputType) {

        let message_body, message_type;

        if (inputType === 'cli') {
            message_body = inputContentCli.value;
            message_type = 'cli_request';
        } else if (inputType === 'interval') {
            message_body = inputContentInterval.value;
            message_type = 'interval_update';
        }

        //const urlParamsInitial = window.location.href;

        // Send the message to the Flask backend
        fetch("/send_to_device", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ message_body, message_type, urlParamsInitial })
        })
            .then(response => response.json())
            //.then(data => {
            //    resultDiv.textContent = data.result;
            //})
            .catch(error => {
                console.error("Error:", error);
                resultDiv.textContent = "An error occurred.";
            });
    }

    buttonCliSend.addEventListener("click", function () {
        sendMessage('cli'); // Pass 'cli' as the input type
    });

    buttonIntervalSend.addEventListener("click", function () {
        sendMessage('interval'); // Pass 'interval' as the input type
    });

    // Listen for Enter key press in the input fields
    inputContentCli.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            sendMessage('cli'); // Pass 'cli' as the input type
        }
    });

    inputContentInterval.addEventListener("keyup", function (event) {
        if (event.key === "Enter") {
            sendMessage('interval'); // Pass 'interval' as the input type
        }
    });
});


