window.onload = function () {
    const videoStream = document.getElementById('stream');
    const startBtn = document.getElementById('start-btn');
    const stopBtn = document.getElementById('stop-btn');

    // Optional: Refresh the image periodically to ensure the stream stays updated
    setInterval(function() {
        videoStream.src = "/video_feed?" + new Date().getTime();  // Add timestamp to bypass cache
    }, 5*1000);  // Reload every 5 seconds

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
    setInterval(lightSensorStatus, 10*1000);

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
    setInterval(tempSensorStatus, 10*1000);

    function formatTimestamp(timestamp) {
        // Extract date and time components from the input
        const year = timestamp.slice(0, 4);
        const month = timestamp.slice(4, 6);
        const day = timestamp.slice(6, 8);
        const hours = timestamp.slice(9, 11);
        const minutes = timestamp.slice(11, 13);
        const seconds = timestamp.slice(13, 15);
    
        // Create a Date object
        const date = new Date(`${year}-${month}-${day}T${hours}:${minutes}:${seconds}`);
    
        // Format the date
        const options = { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit' };
        return date.toLocaleString('en-US', options).replace(',', '');
    }

    // Add this to your existing window.onload function
    function updateBirdDetections() {
        fetch('/get_latest')
        .then(response => response.json())
        .then(data => {
            const tbody = document.getElementById('bird-detection-records');
            const countBadge = document.getElementById('detection-count');
            tbody.innerHTML = '';
            
            // Update detection count
            countBadge.textContent = `${data.length} detections`;
            
            data.forEach(record => {
                const formattedTime = formatTimestamp(record.timestamp);
                const row = `
                    <tr>
                        <td class="detection-time">${formattedTime}</td>
                        <td>${record.bird_name}</td>
                        <td>
                            <img src="${record.image_path}" 
                                alt="${record.bird_name}" 
                                class="img-fluid rounded" 
                                onclick="window.open(this.src, '_blank')">
                        </td>
                        <td>
                            <audio controls class="audio-player">
                                <source src="${record.audio_path}" type="audio/wav">
                                Your browser does not support the audio element.
                            </audio>
                        </td>
                    </tr>
                `;
                tbody.innerHTML += row;
            });
        })
        .catch(error => {
            console.error('Error fetching bird detections:', error);
        });
    }

    // Initial load
    updateBirdDetections();

    // Refresh every 10 minutes
    setInterval(updateBirdDetections, 10*60*1000);
};