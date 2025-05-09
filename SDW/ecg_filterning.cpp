#include "SDW.h"
#include <cstdio>
#include <unistd.h>
#include <string>
#include <websocketpp/client.hpp>
#include <websocketpp/config/asio_client.hpp>
#include <nlohmann/json.hpp>

#define CHIP_SELECT_PIN 10

using json = nlohmann::json;
using websocketpp::lib::placeholders::_1;
using websocketpp::lib::placeholders::_2;
using websocketpp::lib::bind;

typedef websocketpp::client<websocketpp::config::asio_client> client;
typedef websocketpp::config::asio_client::message_type::ptr message_ptr;

SDW sdw1;
client ws_client;
websocketpp::connection_hdl connection_hdl;
bool connected = false;

// WebSocket configuration
const std::string websocket_server = "ws://http://127.0.0.1:5000/ws"; // Update with your server

SDW_SensorSpec raw_ecg_spec = {1,0,AnIn_2};
probe ecg_measure;
probe ecg_filtered;
probe ecg_sqr;
probe ecg_bpm;
probe ecg_period;

void on_open(client* c, websocketpp::connection_hdl hdl) {
    connected = true;
    connection_hdl = hdl;
    printf("WebSocket connected\n");
}

void on_fail(client* c, websocketpp::connection_hdl hdl) {
    connected = false;
    printf("WebSocket connection failed\n");
}

void on_close(client* c, websocketpp::connection_hdl hdl) {
    connected = false;
    printf("WebSocket disconnected\n");
}

void initialize_websocket() {
    try {
        // Set logging to be pretty verbose
        ws_client.set_access_channels(websocketpp::log::alevel::none);
        ws_client.clear_access_channels(websocketpp::log::alevel::frame_payload);

        // Initialize ASIO
        ws_client.init_asio();

        // Register handlers
        ws_client.set_open_handler(bind(&on_open, &ws_client, ::_1));
        ws_client.set_fail_handler(bind(&on_fail, &ws_client, ::_1));
        ws_client.set_close_handler(bind(&on_close, &ws_client, ::_1));

        // Create a connection to the given URI
        websocketpp::lib::error_code ec;
        client::connection_ptr con = ws_client.get_connection(websocket_server, ec);
        
        if (ec) {
            printf("Could not create connection: %s\n", ec.message().c_str());
            return;
        }

        ws_client.connect(con);
        
        // Start the ASIO io_service run loop in a separate thread
        std::thread t([&]() { ws_client.run(); });
        t.detach();
    } catch (const std::exception& e) {
        printf("WebSocket initialization error: %s\n", e.what());
    }
}

void send_websocket_data(const json& data) {
    if (!connected) return;
    
    try {
        std::string payload = data.dump();
        ws_client.send(connection_hdl, payload, websocketpp::frame::opcode::text);
    } catch (const std::exception& e) {
        printf("WebSocket send error: %s\n", e.what());
        connected = false;
    }
}

int main() {
    // Initialize WebSocket connection
    initialize_websocket();
    
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
        sdw1.getProbes();

        // Create JSON data
        json data;
        data["time_ms"] = time_ms;
        data["ecg_measure"] = ecg_measure.getVal();
        data["ecg_filtered"] = ecg_filtered.getVal();
        data["ecg_sqr"] = ecg_sqr.getVal();
        data["ecg_bpm"] = ecg_bpm.getVal();
        data["ecg_period"] = ecg_period.getVal();

        // Send via WebSocket
        send_websocket_data(data);

        // Also print to stdout for debugging
        printf("%s\n", data.dump().c_str());
        fflush(stdout);

        time_ms += 10;
        usleep(10000); // Sleep for 10ms (100Hz sampling)
    }

    return 0;
}