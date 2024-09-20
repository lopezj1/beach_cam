const restartNotification = document.getElementById('restart-notification');
const videoStream = document.getElementById('video-stream');

// Function to show the restart notification
function showRestartNotification() {
    restartNotification.style.display = 'block';
    setTimeout(() => {
        restartNotification.style.display = 'none';
    }, 3000);  // Hide after 3 seconds
}

// Add an event listener to detect header resets
videoStream.addEventListener('load', function () {
    // Check the response headers for the loop reset marker
    fetch(this.src, { method: 'HEAD' })
        .then(response => {
            if (response.headers.get('X-Loop-Reset') === 'true') {
                showRestartNotification();
            }
        });
});

// Poll the stream to check for loop reset
setInterval(() => {
    videoStream.src = videoStream.src.split('?')[0] + '?' + new Date().getTime();  // Update stream with cache buster
}, 1000);
