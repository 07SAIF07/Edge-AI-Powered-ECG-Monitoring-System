# -*- coding: utf-8 -*-
"""main.py"""

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np
from tensorflow.keras.models import load_model

# Load the pre-trained model
model_path = r"ecg_classification_model.h5"
model = load_model(model_path)
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')  # No metrics needed

# Class label dictionaries
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

# FastAPI app instance
app = FastAPI()

# Enable CORS (use "*" during dev, restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def healthcheck():
    if model is not None:
        return "ok"
    return "error"

# Request model
class SignalInput(BaseModel):
    signal: list[float]

# Preprocessing function
def preprocess_ecg_signal(signal, num_timesteps=187, num_features=1):
    signal = np.array(signal)
    std_dev = np.std(signal)
    signal = (signal - np.mean(signal)) if std_dev == 0 else (signal - np.mean(signal)) / std_dev
    if signal.shape[0] < num_timesteps:
        signal = np.pad(signal, (0, num_timesteps - signal.shape[0]), 'constant')
    elif signal.shape[0] > num_timesteps:
        signal = signal[:num_timesteps]
    return signal.reshape((1, num_timesteps, num_features))

# HTTP endpoint
@app.post("/predict")
def classify_ecg_signal(data: SignalInput):
    try:
        signal = data.signal
        if not signal:
            raise HTTPException(status_code=400, detail="Signal is empty.")
        processed = preprocess_ecg_signal(signal)
        predictions = model.predict(processed)
        class_idx = int(np.argmax(predictions, axis=1)[0])
        detailed_label = detailed_class_labels[class_idx]
        broad_label = next(k for k, v in broad_class_labels.items() if class_idx in v)

        return {
            "detailed_class": detailed_label,
            "broad_class": broad_label,
            "probabilities": predictions.tolist()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# WebSocket endpoint
@app.websocket("/ws/predict")
async def websocket_predict(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_json()
            signal = data.get("signal", [])

            if not signal:
                await websocket.send_json({"error": "Signal is empty."})
                continue

            try:
                processed = preprocess_ecg_signal(signal)
                predictions = model.predict(processed)
                class_idx = int(np.argmax(predictions, axis=1)[0])
                detailed_label = detailed_class_labels[class_idx]
                broad_label = next(k for k, v in broad_class_labels.items() if class_idx in v)

                await websocket.send_json({
                    "detailed_class": detailed_label,
                    "broad_class": broad_label,
                    "probabilities": predictions.tolist()
                })

            except Exception as e:
                await websocket.send_json({"error": str(e)})

    except Exception as e:
        print(f"WebSocket connection closed: {e}")
