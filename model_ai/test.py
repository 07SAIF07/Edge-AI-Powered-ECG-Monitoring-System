import asyncio
import websockets
import json

# Sample ECG signal data
signal_data = [
    2054, 2051, 2053, 2053, 2056, 2054, 2054, 2054, 2053, 2056,
    2053, 2055, 2057, 2053, 2053, 2055, 2053, 2052, 2055, 2050,
    2096, 2099, 2101
]

async def test_websocket():
    uri = "ws://127.0.0.1:8000/ws/predict"  # Make sure your API is running locally
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"signal": signal_data}))
        response = await websocket.recv()
        result = json.loads(response)

        print("✅ WebSocket test passed! Response:")
        print(json.dumps(result, indent=2))

if __name__ == "__main__":
    asyncio.run(test_websocket())
