# Edge AI-Powered ECG Monitoring System

A real-time, portable ECG monitoring solution powered by Edge AI. This system filters ECG signals, detects anomalies, and provides visualization through a 7" touchscreen interface using a Raspberry Pi and a custom DSP-based board.

---

Video Demo :
https://drive.google.com/drive/folders/1yti6jyNpjtF1IYLHnfJoG0vB7w5mRzdy?usp=drive_link


## 🩺 Overview

This project enables intelligent ECG monitoring using Edge AI technologies. The system:
- Captures ECG signals via the AD8232 module and electrodes
- Filters the signal in real-time 
- Detects QRS complexes and rhythm anomalies
- Displays live signal and health insights on a 7" touchscreen via the Raspberry Pi

---

## 🧠 Key Features

- 🕒 **Real-Time Signal Processing**  
- 🧹 **Noise Filtering using IIR Filters**
- 📈 **QRS Complex & Anomaly Detection**
- 🧠 **Edge AI Inference (Local Model)**
- 📊 **Visualization Interface (PyQt5/Matplotlib)**
- 🔌 **SPI Communication (C on Raspberry Pi)**
- 💾 **Offline Data Storage**

---

## 📦 Requirements

### Raspberry Pi (Tested on Raspberry Pi 5)

- OS: Raspberry Pi OS 64-bit
- Libraries:
  ```text
  numpy==1.26.4
  scipy==1.13.0
  matplotlib==3.8.4
  pyqt5==5.15.10
  spidev==3.6
  joblib==1.4.2
Display: 7" HD touchscreen (Luckfox v1.1)

DSP-Based Board
Developed by Shanon Technologies

Performs real-time filtering using optimized embedded C

🔌 Hardware Architecture

[AD8232 ECG Sensor] --analog--> [DSP Board] --SPI--> [Raspberry Pi 5] --HDMI--> [7" Touchscreen]

🛠️ Installation
Clone the repository

git clone https://github.com/07SAIF07/Edge-AI-Powered-ECG-Monitoring-System.git
cd Edge-AI-Powered-ECG-Monitoring-System
Install Python dependencies

pip install -r requirements.txt
Compile C SPI driver

cd spi_comm/
make

Run the visualization app

python3 main.py

📷 Screenshots

![Screenshot 2025-05-22 142011](https://github.com/user-attachments/assets/e8ac7e17-7887-4063-9346-f2b9abb326c3)

🧪 Model Details

Type:  CNN 
![2361 (1)](https://github.com/user-attachments/assets/197865c4-dfb8-4e10-a2d4-709cef086e42)

Trained on: MIT-BIH dataset

Function: Detects arrhythmias and QRS intervals

👨‍💻 Team

-Saifeddine Brahmi
-Yassine Bouzaiene
-Taher Bouhlel

Supervised by Mme Chiraz Zribi
ENSI Tunisia – Class of 2025

📄 License
This project is licensed under the MIT License.




