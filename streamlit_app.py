import streamlit as st
import numpy as np
import tensorflow as tf
from PIL import Image, ImageOps

# Set Streamlit page configuration
st.set_page_config(page_title="Brain Tumour Detection", page_icon="🧠", layout="centered")

st.title("🧠 Brain Tumour Detection AI")
st.write("Upload an MRI scan to securely and instantly detect the presence of a Brain Tumour using Deep Learning.")

# Hide Streamlit default menus for a cleaner UI
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# -----------------------------------------------
# Model Loading (Cached to prevent Memory Crashes)
# -----------------------------------------------
@st.cache_resource
def load_disease_model():
    # Load the Keras model
    model = tf.keras.models.load_model('save.h5')
    return model

with st.spinner("Loading AI Model (This takes a moment on first run)..."):
    model = load_disease_model()

# -----------------------------------------------
# File Uploader
# -----------------------------------------------
uploaded_file = st.file_uploader("Choose an MRI image...", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # Read the image
    image = Image.open(uploaded_file).convert('RGB')
    
    # Show the image to the user
    st.image(image, caption='Uploaded MRI Scan', use_container_width=True)
    
    st.markdown("---")
    
    if st.button("Predict"):
        with st.spinner("Analyzing scan..."):
            try:
                # Preprocess the image exactly as in app.py
                try:
                    # For newer Pillow versions
                    resample_filter = Image.Resampling.LANCZOS
                except AttributeError:
                    # For older Pillow versions
                    resample_filter = Image.ANTIALIAS
                    
                processed_image = ImageOps.fit(image, (224, 224), resample_filter)
                img_array = np.array(processed_image) / 255.0
                img_array = np.expand_dims(img_array, axis=0)

                # Make the prediction
                pred = model.predict(img_array)
                max_prob = float(np.max(pred)) * 100
                pred_class = np.argmax(pred, axis=1)[0]
                
                # Output Results
                if pred_class == 0:
                    st.error("🚨 **Result: Brain Tumor Detected**")
                    st.error(f"**Confidence:** {max_prob:.2f}%")
                    st.write("**Symptoms:** unexplained weight loss, double vision or a loss of vision, increased pressure felt in the back of the head, dizziness and a loss of balance, sudden inability to speak, hearing loss, weakness or numbness that gradually worsens on one side of the body.")
                elif pred_class == 1:
                    st.success("✅ **Result: Normal (No Tumor Detected)**")
                    st.success(f"**Confidence:** {max_prob:.2f}%")
                    st.write("You Are Safe, But Do keep precaution.")
                    
            except Exception as e:
                st.error(f"An error occurred during prediction: {e}")
