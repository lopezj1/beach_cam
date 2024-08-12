import cv2
import numpy as np
import requests

# URL of the image
image_url = "https://splash.thesurfersview.com/sunba/sshoceanclub/latest.jpg"  # Replace with your image URL

# Download the image from the URL
response = requests.get(image_url)
if response.status_code == 200:
    # Convert the response content to a NumPy array
    image_array = np.frombuffer(response.content, np.uint8)
    
    # Decode the image array into an OpenCV image
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    
    # Check if the image was loaded correctly
    if image is None:
        print("Error: Image could not be decoded.")
        exit()

    # Display the image in an OpenCV window
    cv2.imshow("Image from URL", image)

    # Wait for a key press to close the window
    cv2.waitKey(0)  # 0 means wait indefinitely

    # Close all OpenCV windows
    cv2.destroyAllWindows()
else:
    print(f"Error: Failed to download image. Status code: {response.status_code}")
