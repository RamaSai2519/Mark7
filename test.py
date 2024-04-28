import socketio

socket = socketio.Client()

@socket.on('connect')
def on_connect():
    print('Connected to server')

@socket.on('disconnect')
def on_disconnect():
    print('Disconnected from server')

@socket.on('error_notification')
def on_error_notification(data):
    socket.emit('ack_error_notification', {'message': 'Received error notification'})
    print('Received error notification:', data)

if __name__ == '__main__':
    try:
        socket.connect('http://15.206.127.248')

        input("Press Enter to disconnect from server...\n")

        socket.disconnect()
    except Exception as e:
        print('An error occurred:', e)