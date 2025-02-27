$(document).ready(function() {
    const urlParamsInitial = window.location.href;
    var socket = io({
        transports: ["websocket"],
        query: { page_data: urlParamsInitial }
        });

    socket.on('connect', function() {
        const urlParams_connect = window.location.href;
        socket.emit('my_event', {data: urlParams_connect});  // my_event triggers the my_event method in backend
    });

    socket.on('my_response', function(msg, cb) {
        document.getElementById('ts_last_message').innerHTML = msg.user_specific_info;
    });

}
)