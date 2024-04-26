import socketio

# Create a SocketIO instance
socket = socketio.Client()

# Define event handler for connection
@socket.on('connect')
def on_connect():
    print('Connected to server')

# Define event handler for disconnection
@socket.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

# Define event handler for error notifications
@socket.on('error_notification')
def on_error_notification(data):
    socket.emit('ack_error_notification', {'message': 'Received error notification'})
    print('Received error notification:', data)

if __name__ == '__main__':
    try:
        # Connect to the WebSocket server
        socket.connect('http://15.206.127.248')

        # Wait for user to press Enter to disconnect
        input("Press Enter to disconnect from server...\n")

        # Disconnect from the WebSocket server
        socket.disconnect()
    except Exception as e:
        print('An error occurred:', e)