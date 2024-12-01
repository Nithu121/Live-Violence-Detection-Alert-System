
import cv2
import numpy as np
import streamlit as st
from PIL import Image
import tempfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

@st.cache_resource
def get_predictor_model():
    from model import Model
    model = Model()
    return model

def send_email(subject, body, to_email):
    from_email = "nithushetty121@gmail.com"
    password = "Nithu@2003"

    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_email, password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

header = st.container()
model = get_predictor_model()

with header:
    st.title('Hello!')
    st.text('Using this app you can classify whether there is fight on a street, fire, car crash, or everything is okay.')

uploaded_file = st.file_uploader("Choose an image or video file...")


start_camera = st.checkbox("Use Camera", key="start_camera")

if uploaded_file is not None:
    file_type = uploaded_file.type.split('/')[0]

    if file_type == 'image':
        image = Image.open(uploaded_file).convert('RGB')
        image = np.array(image)
        label_text = model.predict(image=image)['label'].title()
        st.write(f'Predicted label is: **{label_text}**')
        st.write('Original Image')
        if len(image.shape) == 3:
            cv_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        st.image(image)

    elif file_type == 'video':
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(uploaded_file.read())
            video_path = tmp_file.name
        
        st.video(video_path)
        cap = cv2.VideoCapture(video_path)
        if cap.isOpened():
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                label_text = model.predict(image=frame)['label'].title()
                st.write(f'Predicted label for current frame: **{label_text}**')
                st.image(frame)
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
            label_text = model.predict(image=frame_rgb)['label'].title()
            st.image(frame_rgb, channels="RGB")
            st.write(f'Predicted label: **{label_text}**')

            if "violence" in label_text.lower():
                send_email("Violence Detected", f"Violence detected in video stream", "nithushetty121@gmail.com")

            if stop_camera:
                break
        cap.release()

st.write("End of App")
