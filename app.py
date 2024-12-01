
import cv2
import numpy as np
import streamlit as st
import streamlit.components.v1 as components
from PIL import Image
import tempfile
import requests
import torch
from datetime import datetime
from datetime import datetime

@st.cache_resource
def get_predictor_model():
    from model import Model
    model = Model()
    return model

def send_telegram_message(message, chat_id, video_path=None, image_path=None, location=None, timestamp=None):
    bot_token = '///'
    send_message_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    send_video_url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    send_photo_url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
    
    if location and timestamp:
        location_text = f"Emergency Alert: {message}\nLocation: {location}\nTime: {timestamp}"
    elif location:
        location_text = f"Emergency Alert: {message}\nLocation: {location}"
    else:
        location_text = f"Emergency Alert: {message}"

    if video_path:
        with open(video_path, 'rb') as video_file:
            video_data = {
                'chat_id': chat_id,
                'caption': location_text,
            }
            files = {'video': video_file}
            try:
                print(f"Attempting to send video to chat ID {chat_id}...")
                response = requests.post(send_video_url, data=video_data, files=files)
                print(f"Response Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                if response.status_code == 200:
                    print("Telegram video message sent successfully!")
                else:
                    print(f"Failed to send Telegram video message: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to send Telegram video message: {e}")
    elif image_path:
        with open(image_path, 'rb') as image_file:
            image_data = {
                'chat_id': chat_id,
                'caption': location_text,
            }
            files = {'photo': image_file}
            try:
                print(f"Attempting to send image to chat ID {chat_id}...")
                response = requests.post(send_photo_url, data=image_data, files=files)
                print(f"Response Code: {response.status_code}")
                print(f"Response Text: {response.text}")
                if response.status_code == 200:
                    print("Telegram image message sent successfully!")
                else:
                    print(f"Failed to send Telegram image message: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"Failed to send Telegram image message: {e}")
    else:
        params = {
            'chat_id': chat_id,
            'text': location_text
        }
        try:
            print(f"Attempting to send Telegram message to chat ID {chat_id}...")
            response = requests.post(send_message_url, params=params)
            print(f"Response Code: {response.status_code}")
            print(f"Response Text: {response.text}")
            if response.status_code == 200:
                print("Telegram message sent successfully!")
            else:
                print(f"Failed to send Telegram message: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Failed to send Telegram message: {e}")

model = get_predictor_model()

html_code = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Get User Location</title>
</head>
<body>

<h2>Get User Location</h2>

<p id="demo"></p>

<form id="locationForm">
    <input type="hidden" id="latitude" name="latitude">
    <input type="hidden" id="longitude" name="longitude">
</form>

<script>
var x = document.getElementById("demo");

function getLocation() {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition, showError);
  } else { 
    x.innerHTML = "Geolocation is not supported by this browser.";
  }
}

function showPosition(position) {
  var latitude = position.coords.latitude;
  var longitude = position.coords.longitude;

  x.innerHTML = "Latitude: " + latitude + 
  "<br>Longitude: " + longitude;

  document.getElementById("latitude").value = latitude;
  document.getElementById("longitude").value = longitude;

 
  var iframe = document.createElement("iframe");
  iframe.style.display = "none";
  iframe.src = "/?latitude=" + latitude + "&longitude=" + longitude;
  document.body.appendChild(iframe);
}

function showError(error) {
  switch(error.code) {
    case error.PERMISSION_DENIED:
      x.innerHTML = "User denied the request for Geolocation."
      break;
    case error.POSITION_UNAVAILABLE:
      x.innerHTML = "Location information is unavailable."
      break;
    case error.TIMEOUT:
      x.innerHTML = "The request to get user location timed out."
      break;
    case error.UNKNOWN_ERROR:
      x.innerHTML = "An unknown error occurred."
      break;
  }
}
</script>

<button onclick="getLocation()">Try It</button>

</body>
</html>
"""

st.title('Telegram Message Debug Test')


components.html(html_code, height=300)

latitude = st.query_params.get('latitude', [None])[0]
longitude = st.query_params.get('longitude', [None])[0]


now = datetime.now()
current_date_time = now.strftime("%Y-%m-%d %H:%M:%S")  


st.write(f"Current Date and Time: {current_date_time}")



if latitude and longitude:
    location = f"Latitude: {latitude}, Longitude: {longitude}"
else:
    location = "Location not available"

uploaded_file = st.file_uploader("Choose an image or video file...")


start_camera = st.checkbox("Use Camera", key="start_camera")

if uploaded_file is not None:
    file_type = uploaded_file.type.split('/')[0]

    if file_type == 'image':
        image = Image.open(uploaded_file).convert('RGB')
        st.write('Original Image')
        st.image(image)

        label_text = model.predict(image=image)['label'].title()
        st.write(f'Predicted label is: **{label_text}**')

        print("Prediction:", label_text)  

        if "violence" in label_text.lower():
            print("Violence detected, preparing to send Telegram message...")
            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                image.save(tmp_file.name)
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_telegram_message("Violence detected in uploaded image", "1747349588", image_path=tmp_file.name, location=location, timestamp=timestamp)
            print("Telegram message sent function executed.")

    elif file_type == 'video':
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        
        st.video(video_path)
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            violence_detected = False
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                st.image(frame, channels="RGB")
                
                label_text = model.predict(image=frame)['label'].title()
                st.write(f'Predicted label for current frame: **{label_text}**')

                print("Prediction for video frame:", label_text)  

                if "violence" in label_text.lower() and not violence_detected:
                    print("Violence detected, preparing to send Telegram message...")
                    violence_detected = True
                    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                        Image.fromarray(frame).save(tmp_file.name)
                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        send_telegram_message("Violence detected in video stream", "1747349588", image_path=tmp_file.name, location=location, timestamp=timestamp)

           
            if violence_detected:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                send_telegram_message("Violence detected in video stream", "1747349588", video_path=video_path, location=location, timestamp=timestamp)
                print("Telegram video message sent function executed.")
                
        cap.release()

if start_camera:
    

    st.write("Starting the camera...")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.write("Error: Unable to open camera.")
    else:
        stop_camera = st.checkbox("Stop Camera", key="stop_camera")
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.write("Failed to grab frame.")
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            st.image(frame_rgb, channels="RGB")

            label_text = model.predict(image=frame_rgb)['label'].title()
            st.write(f'Predicted label: **{label_text}**')
            
            

            print("Prediction:", label_text)  

            if "violence" in label_text.lower():
                print("Violence detected, preparing to send Telegram message...")
                with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
                    Image.fromarray(frame_rgb).save(tmp_file.name)
                    send_telegram_message("Violence detected in live stream", "1747349588", image_path=tmp_file.name, location=location)
                print("Telegram message sent function executed.")

            if stop_camera:
                break
        cap.release()

st.write("End of App")



