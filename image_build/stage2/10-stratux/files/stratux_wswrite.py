import websocket
import json
import threading
import time
import logging
import os
from threading import Lock
import signal
import sys

#Version 2.0.0

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Global storage for aircraft information
aircraft_data = {}
aircraft_data_lock = Lock()  # Lock for thread-safe access to aircraft_data
file_path = '/run/dump1090-mutability/aircraft.json'

# Ensure the directory exists
os.makedirs(os.path.dirname(file_path), exist_ok=True)

def on_message(ws, message):
    global aircraft_data
    try:
        data = json.loads(message) # Parse the JSON message

        # Directly extract data ensuring all required fields are present and non-empty
        flight = data.get('Tail', '').strip()
        lat = data.get('Lat', None)
        lon = data.get('Lng', None)
        altitude = data.get('Alt', None)
        track = data.get('Track', None)
        speed = data.get('Speed', None)
        squawk = data.get('Squawk', None)
        vert_rate = data.get('Vvel', None)

        # Check all required fields are not only present but also contain valid data
        if all([flight, lat, lon, altitude is not None, track is not None, speed is not None]):
            new_data = {
                "flight": flight,
                "lat": lat,
                "lon": lon,
                "altitude": altitude,
                "track": track,
                "speed": speed,
                "squawk": squawk,
                "vert_rate": vert_rate,
                "last_update": time.time()  # Capture last update time for expiry checks
            }

            # Thread-safe modification of aircraft_data
            with aircraft_data_lock:
                aircraft_data[flight] = new_data  # This updates or adds a new entry
        else:
            logging.warning(f"Incomplete data for aircraft, not adding: {data}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info("### WebSocket closed ###")

def on_open(ws):
    logging.info("WebSocket connection opened")

def start_websocket():
    websocket.enableTrace(False)  # Set to True for debugging WebSocket communication
    delay = 1  # Start with a 1-second delay
    while True:
        try:
            ws = websocket.WebSocketApp("ws://localhost/traffic",
                                        on_message=on_message,
                                        on_error=on_error,
                                        on_close=on_close)
            ws.on_open = on_open
            ws.run_forever()
            delay = 1  # Reset delay on successful connection
        except Exception as e:
            logging.error(f"WebSocket error: {e}. Reconnecting in {delay} seconds...")
            time.sleep(delay)
            delay = min(delay * 2, 60)  # Exponential backoff, max 60 seconds

def write_data_to_file():
    global aircraft_data
    while True:
        current_time = time.time()
        to_write = []
        keys_to_remove = []

        # Prepare the data to write
        with aircraft_data_lock:  # Thread-safe access
            for flight, info in aircraft_data.items():
                if current_time - info['last_update'] <= 2:  # Only write if updated in the last 2 seconds
                    to_write.append(info)
                else:
                    keys_to_remove.append(flight)

            # Remove stale entries after 2 seconds without updates
            for flight in keys_to_remove:
                del aircraft_data[flight]

        # Write current valid data to file
        try:
            output_data = {
                "now": current_time,
                "messages": len(to_write),
                "aircraft": to_write
            }
            temp_file = file_path + '.tmp'  # Temporary file for atomic writes
            with open(temp_file, 'w') as f:
                json.dump(output_data, f, indent=4)
            os.replace(temp_file, file_path)  # Atomically replace the old file
        except Exception as e:
            logging.error(f"Failed to write data to file: {e}")

        # Wait 1 second before the next write
        time.sleep(1)

def signal_handler(sig, frame):
    logging.info("Shutting down gracefully...")
    sys.exit(0)

# Attach signal handler for graceful shutdown
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Thread for the WebSocket client
thread_ws = threading.Thread(target=start_websocket)
thread_ws.daemon = True
thread_ws.start()

# Thread for writing data to file
thread_file = threading.Thread(target=write_data_to_file)
thread_file.daemon = True
thread_file.start()

# Keep the main thread alive
while True:
    time.sleep(100)

