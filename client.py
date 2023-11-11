import socket
import pyaudio
import threading

# Function to receive audio from a specified socket
def receive_audio(sock, stream):
    while True:
        try:
            data = sock.recv(1024)
            stream.write(data)
        except:
            break

# Function to create a server socket
def create_server_socket(host, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(4)
    return server_socket

# PyAudio setup
p = pyaudio.PyAudio()
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024

# Use the local IP address of the receiver machine on the WiFi network
host = '192.168.41.137'  # Change this to the actual local IP address of the receiver machine
port1, port2, port3, port4 = 5000, 5001, 5002, 5003

server_socket1 = create_server_socket(host, port1)
server_socket2 = create_server_socket(host, port2)
server_socket3 = create_server_socket(host, port3)
server_socket4 = create_server_socket(host, port4)

# Accept connections from senders
client_socket1, _ = server_socket1.accept()
client_socket2, _ = server_socket2.accept()
client_socket3, _ = server_socket3.accept()
client_socket4, _ = server_socket4.accept()

# Open streams for each incoming audio
stream1 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input=True, frames_per_buffer=CHUNK)
stream2 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input=True, frames_per_buffer=CHUNK)
stream3 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input=True, frames_per_buffer=CHUNK)
stream4 = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, input=True, frames_per_buffer=CHUNK)

# Start threads for sending and receiving audio for each user
threading.Thread(target=receive_audio, args=(client_socket1, stream1)).start()
threading.Thread(target=receive_audio, args=(client_socket2, stream2)).start()
threading.Thread(target=receive_audio, args=(client_socket3, stream3)).start()
threading.Thread(target=receive_audio, args=(client_socket4, stream4)).start()

# Wait for threads to finish (you can implement a more sophisticated termination mechanism)
threading.Event().wait()

# Close sockets and streams on program termination
server_socket1.close()
server_socket2.close()
server_socket3.close()
server_socket4.close()
client_socket1.close()
client_socket2.close()
client_socket3.close()
client_socket4.close()
stream1.stop_stream()
stream1.close()
stream2.stop_stream()
stream2.close()
stream3.stop_stream()
stream3.close()
stream4.stop_stream()
stream4.close()
p.terminate()
