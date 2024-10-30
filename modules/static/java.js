window.onload = function () {
    const videoStream = document.getElementById('stream');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    // Optional: Refresh the image periodically to ensure the stream stays updated
    setInterval(function() {
        videoStream.src = "/video_feed?" + new Date().getTime();  // Add timestamp to bypass cache
    }, 5000);  // Reload every 5 seconds

    // Start Stream
    startBtn.addEventListener('click', function() {
        videoStream.src = "/video_feed";
    });

    // Stop Stream
    stopBtn.addEventListener('click', function() {
        videoStream.src = "/static/no_streaming.png";  // Placeholder image when stopped
    });

    var socket = io();

    socket.on('light_level_update', function(lightLevel){
        document.getElementById('light-level').textContent = 'Light level: ' + lightLevel.toFixed(2) + 'lux';
    });
};