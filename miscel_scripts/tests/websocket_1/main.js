window.addEventListener("DOMContentLoaded", () => {

  const websocket = new WebSocket("ws://localhost:8001/");
  websocket.addEventListener("message", ({ data }) => {
    const event = JSON.parse(data);
    switch (event.type) {

      case "field_update":
        document.getElementById('my_dynamic_field').innerHTML = event.value;
        break;

      default:
        throw new Error(`Some error for event type: ${event.type}.`);

    }
  });
});