$(document).ready(function () {
    var time = Intl.DateTimeFormat().resolvedOptions().timeZone;
    var i = document.createElement("img");
    i.src = "/getTime?browsertz=" + time;
});
