# -*- coding: utf-8 -*-

# !pip install gradio
import tensorflow as tf
import tensorflow 
import numpy as np
import gradio as gr
from tensorflow.keras.models import load_model

# Load the pre-trained model
model_path = r"ecg_classification_model.h5"
model = load_model(model_path)
# Suppress the warning by recompiling the model (no metrics needed)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')

# Detailed and broad class labels
detailed_class_labels = {
    0: 'Normal beat',
    1: 'Ventricular ectopic beat',
    2: 'Supraventricular ectopic beat',
    3: 'Fusion beat',
    4: 'Unknown or other types'
}

broad_class_labels = {
    'Normal': [0],
    'Abnormal': [1, 2, 3, 4]
}

# Preprocessing function
def preprocess_ecg_signal(signal, num_timesteps=187, num_features=1):
    signal = np.array(signal)
    std_dev = np.std(signal)

    if std_dev == 0:
        signal = (signal - np.mean(signal))
    else:
        signal = (signal - np.mean(signal)) / std_dev

    if signal.shape[0] < num_timesteps:
        signal = np.pad(signal, (0, num_timesteps - signal.shape[0]), 'constant')
    elif signal.shape[0] > num_timesteps:
        signal = signal[:num_timesteps]

    signal = signal.reshape((1, num_timesteps, num_features))
    return signal

# Core classification function

def classify_ecg_signal_core(signal):
    preprocessed_signal = preprocess_ecg_signal(signal)
    predictions = model.predict(preprocessed_signal)
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    detailed_label = detailed_class_labels[predicted_class_index]

    broad_label = None
    for label, classes in broad_class_labels.items():
        if predicted_class_index in classes:
            broad_label = label
            break

    return detailed_label, broad_label, predictions

# Gradio-compatible classification function
def classify_ecg_signal(signal_str):
    try:
        # Convert string to list of floats
        signal = list(map(float, signal_str.split(',')))

        if not signal:
            return "Please enter ECG signal data.", None, None

        # Classify the signal data
        detailed_label, broad_label, predictions = classify_ecg_signal_core(signal)

        return f"**Detailed Classification:** {detailed_label}", f"**Broad Classification:** {broad_label}", predictions.tolist()

    except ValueError:
        return "Please enter valid numbers separated by commas.", None, None
    except Exception as e:
        return f"An error occurred: {e}", None, None

# Gradio interface setup
inputs = gr.Textbox(lines=5, placeholder="Enter ECG signal data, separated by commas")
outputs = [gr.Textbox(label="Detailed Classification"),
           gr.Textbox(label="Broad Classification"),
           gr.JSON(label="Class Probabilities")]

interface = gr.Interface(
    fn=classify_ecg_signal,
    inputs=inputs,
    outputs=outputs,
    title="ECG Signal Classification",
    description="Enter a comma-separated list of ECG signal values to classify."
)

interface.launch()

# 2054, 2051, 2053, 2053, 2056, 2054, 2054, 2054, 2053, 2056, 
#     2053, 2055, 2057, 2053, 2053, 2055, 2053, 2052, 2055, 2050, 
#     2052, 2049, 2050, 2052, 2048, 2050, 2051, 2048, 2050, 2041, 
#     2040, 2041, 2051, 2040, 2050, 2050, 2040, 2041, 2049, 2049, 
#     2049, 2038, 2051, 2041, 2049, 2050, 2049, 2049, 2040, 2041, 
#     2050, 2051, 2041, 2050, 2051, 2052, 2050, 2053, 2051, 2056, 
#     2056, 2056, 2059, 2063, 2062, 2064, 2067, 2064, 2064, 2067, 
#     2070, 2069, 2070, 2075, 2071, 2073, 2073, 2074, 2078, 2074, 
#     2076, 2080, 2077, 2082, 2082, 2083, 2082, 2085, 2085, 2085, 
#     2085, 2083, 2086, 2084, 2087, 2086, 2085, 2090, 2090, 2089, 
#     2092, 2089, 2090, 2090, 2087, 2090, 2092, 2088, 2087, 2090, 
#     2088, 2085, 2086, 2082, 2084, 2082, 2081, 2077, 2080, 2079, 
#     2078, 2076, 2072, 2072, 2069, 2065, 2067, 2068, 2065, 2062, 
#     2063, 2064, 2064, 2061, 2059, 2060, 2061, 2060, 2057, 2061, 
#     2059, 2062, 2059, 2062, 2064, 2059, 2061, 2066, 2064, 2069, 
#     2069, 2070, 2071, 2072, 2071, 2076, 2077, 2078, 2076, 2077, 
#     2083, 2082, 2082, 2084, 2080, 2085, 2087, 2084, 2088, 2087, 
#     2091, 2091, 2091, 2093, 2097, 2095, 2097, 2100, 2103, 2103, 
#     2103, 2110, 2108, 2109, 2109, 2111, 2111, 2111, 2114, 2115, 
#     2112, 2117, 2117, 2116, 2117, 2115, 2119, 2118, 2117, 2117, 
#     2118, 2117, 2119, 2122, 2122, 2122, 2122, 2122, 2118, 2119, 
#     2117, 2121, 2117, 2114, 2114, 2113, 2111, 2109, 2111, 2103, 
#     2105, 2100, 2102, 2099, 2093, 2092, 2093, 2088, 2086, 2082, 
#     2082, 2082, 2077, 2076, 2077, 2076, 2072, 2069, 2070, 2068, 
#     2067, 2061, 2057, 2057, 2057, 2050, 2052, 2052, 2054, 2049, 
#     2050, 2055, 2056, 2054, 2056, 2062, 2062, 2068, 2070, 2072, 
#     2075, 2080, 2079, 2082, 2085, 2087, 2090, 2096, 2099, 2101

