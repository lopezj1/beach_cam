function startVideoStream() {
    const videoElement = document.getElementById('video-stream');
    let streamUrl = '/video_feed';  // The video stream endpoint

    function updateStream() {
        fetch(streamUrl)
            .then(response => {
                const reader = response.body.getReader();
                let decoder = new TextDecoder();

                function readStream() {
                    return reader.read().then(({ done, value }) => {
                        if (done) {
                            // Restart stream after it ends
                            console.log('Stream ended. Restarting...');
                            updateStream();  // Restart the stream
                            return;
                        }

                        const text = decoder.decode(value, { stream: true });
                        if (text.includes('Video replaying')) {
                            alert('The video is replaying.');
                        } else {
                            // Assuming the value is a frame and rendering it
                            videoElement.src = 'data:image/jpeg;base64,' + btoa(text);
                        }
                        return readStream();  // Continue reading stream
                    });
                }
                return readStream();
            })
            .catch(err => {
                console.error('Error fetching stream:', err);
                setTimeout(updateStream, 1000);  // Retry fetching stream after 1 second
            });
    }

    updateStream();  // Start the stream when the page loads
}

window.onload = startVideoStream;