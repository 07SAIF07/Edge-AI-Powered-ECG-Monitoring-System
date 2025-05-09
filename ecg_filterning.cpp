#include "SDW.h"
#include <cstdio>
#include <unistd.h>
#include <WebSocketsClient.h>
#include <ArduinoJson.h>

#define CHIP_SELECT_PIN 10

SDW sdw1;
WebSocketsClient webSocket;

// WebSocket configuration
const char* websocket_server = "127.0.0.1:5000"; // server IP
const int websocket_port = 5000;                 //  server port
const char* websocket_path = "/ws";              //  server path

SDW_SensorSpec raw_ecg_spec = {1,0,AnIn_2};
probe ecg_measure;
probe ecg_filtered;
probe ecg_sqr;
probe ecg_bpm;
probe ecg_period;

void webSocketEvent(WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            printf("[WSc] Disconnected!\n");
            break;
        case WStype_CONNECTED:
            printf("[WSc] Connected to url!\n");
            break;
        case WStype_TEXT:
            printf("[WSc] Received text: %s\n", payload);
            break;
        case WStype_ERROR:
            printf("[WSc] Error!\n");
            break;
    }
}

int main() {
    /* Initialize WebSocket */
    webSocket.begin(websocket_server, websocket_port, websocket_path);
    webSocket.onEvent(webSocketEvent);
    webSocket.setReconnectInterval(5000);

    /* Create SDW instance */
    sdw1 = SDW(CHIP_SELECT_PIN);

    /* Set Sampling Frequency and Discretization Algorithm */
    sdw1.startDesign(250, Tustin);

    /* Set Monitoring Interface over SPI */
    sdw1.setMonitoringInterface(MonitoringOverSpi);

    /* Create Blocks */
    sensor raw_ecg = sensor(&raw_ecg_spec);
    butter lowPass = butter(10, 15, passLow);
    butter highPass = butter(10, 5, passHigh);
    tf derivative = tf("[25 0]", "[0.00001 1]");
    node Abs = node("[1]","[1]", Abs1);
    butter Average = butter(10, 5, passLow);
    schmidt ecgToSqr = schmidt();
    input Vmax = input("Vmax", 100.0);
    input Vmin = input("Vmin", 0.0);
    input LTH = input("LTH", 60);
    input HTH = input("HTH", 150);
    period periodMeasure = period(100, 0, 0.001);
    maxObserve MAX = maxObserve(7);

    ecg_measure = probe("ecg_measure");
    ecg_filtered = probe("ecg_filtered");
    ecg_sqr = probe("ecg_sqr");
    ecg_bpm = probe("ecg_bpm");
    ecg_period = probe("ecg_period");

    /* Connect Blocks */
    raw_ecg.out(0) > lowPass;
    lowPass > highPass;
    highPass > derivative;
    derivative > Abs.in(0);
    Abs.out(0) > Average;
    Average > ecgToSqr.in(0);
    Vmax > ecgToSqr.in(1);
    Vmin > ecgToSqr.in(2);
    LTH > ecgToSqr.in(3);
    HTH > ecgToSqr.in(4);
    ecgToSqr.out(0) > periodMeasure;
    periodMeasure > MAX;

    raw_ecg.out(0) > ecg_measure;
    Average > ecg_filtered;
    ecgToSqr.out(0) > ecg_sqr;
    periodMeasure > ecg_period;
    MAX > ecg_bpm;

    /* Finalize and check Design Integrity */
    sdw1.stopDesign();

    /* Start Sampling */
    sdw1.startSampling();

    unsigned long time_ms = 0;
    while (1) {
        webSocket.loop();
        sdw1.getProbes();

        // Create JSON object with probe data
        StaticJsonDocument<200> doc;
        doc["time_ms"] = time_ms;
        doc["ecg_measure"] = ecg_measure.getVal();
        doc["ecg_filtered"] = ecg_filtered.getVal();
        doc["ecg_sqr"] = ecg_sqr.getVal();
        doc["ecg_bpm"] = ecg_bpm.getVal();
        doc["ecg_period"] = ecg_period.getVal();

        // Serialize JSON to string
        String jsonString;
        serializeJson(doc, jsonString);

        // Send data via WebSocket
        webSocket.sendTXT(jsonString);

        // Optional: Print to stdout for debugging
        printf("%s\n", jsonString.c_str());
        fflush(stdout);

        time_ms += 10;
        usleep(10000); // Sleep for 10ms 
    }

    return 0;
}