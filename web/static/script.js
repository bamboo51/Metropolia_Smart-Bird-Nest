window.onload = function () {
    const videoStream = document.getElementById('stream');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    // Optional: Refresh the image periodically to ensure the stream stays updated
    setInterval(function() {
        videoStream.src = "/video_feed?" + new Date().getTime();  // Add timestamp to bypass cache
    }, 5000);  // Reload every 5 seconds

    /*
    // Start Stream
    startBtn.addEventListener('click', function() {
        videoStream.src = "/video_feed";
    });

    // Stop Stream
    stopBtn.addEventListener('click', function() {
        videoStream.src = "/static/no_streaming.png";  // Placeholder image when stopped
    });
    */

    // light sensor reading
    function lightSensorStatus(){
        console.log("light sensor loading...");
        fetch('/light_sensor_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('lightsensor-status').textContent = data.light_level.toFixed(2) + " lux";
        })
        .catch(error => {
            console.error('Error fetching sensor data:', error);
            document.getElementById('lightsensor-status').textContent = "Error";
        });
    }
    setInterval(lightSensorStatus, 1000);

    function tempSensorStatus(){
        console.log("temp sensor loading...")
        fetch('/temp_humd_status')
        .then(response => response.json())
        .then(data => {
            document.getElementById('tempsensor-status').textContent = data.temperature + " C";
            document.getElementById('humdsensor-status').textContent = data.humidity + " %";
        })
        .catch(error =>{
            document.getElementById('tempsensor-status').textContent = "Error";
            document.getElementById('humdsensor-status').textContent = "Error";
        })
    }
    setInterval(tempSensorStatus, 1000);
};