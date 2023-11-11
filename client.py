import socket
import pyaudio

# Server configuration
host = 'server_ip'  # Replace with the IP address of the server
port = 12345

# PyAudio configuration
chunk = 1024
format = pyaudio.paInt16
channels = 1
rate = 44100

# Create a socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((host, port))

# Initialize PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

try:
    while True:
        # Record audio data from the microphone
        data = stream.read(chunk)
        
        # Send the recorded audio data to the server
        client_socket.sendall(data)
except KeyboardInterrupt:
    print("Client stopped by user.")
finally:
    # Clean up
    stream.stop_stream()
    stream.close()
    p.terminate()
    client_socket.close()
