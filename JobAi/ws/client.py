import websocket
import threading

# WebSocket URL
ws_url = ["ws://localhost:8000","ws://localhost:8000/ws/chat/","wss://dev.jobai.com/ws/chat","wss://api.jobai.com/ws/chat/"][-1]

# Function to handle incoming messages
def on_message(ws, message):
    print(f"Received: {message}")

# Function to handle errors
def on_error(ws, error):
    print(f"Error: {error}")

# Function to handle connection close
def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

# Function to handle connection open
def on_open(ws):
    print("Connected")
    
    # Send initial messages
    auth_message = dict(TOKEN="1234")
    initial_messages = [auth_message]
    for msg in initial_messages:
        ws.send(msg)

# Create WebSocket instance
ws = websocket.WebSocketApp(ws_url,
                            on_message=on_message,
                            on_error=on_error,
                            on_close=on_close)

# Attach on_open function to WebSocket instance
ws.on_open = on_open

# Start the WebSocket connection in a separate thread
ws_thread = threading.Thread(target=ws.run_forever)
ws_thread.start()

# Wait for the WebSocket thread to finish
ws_thread.join()
