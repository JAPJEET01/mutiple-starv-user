import socket
import pyaudio
import threading

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

# Stream for sending audio to the server
output_stream = p.open(format=format, channels=channels, rate=rate, output=True, frames_per_buffer=chunk)

# Stream for receiving audio from the server
input_stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

def receive_audio():
    try:
        while True:
            # Receive audio data from the server
            data = client_socket.recv(chunk)
            
            # Play the received audio data
            output_stream.write(data)
    except Exception as e:
        print(f"Error in receive_audio: {e}")
    finally:
        # Clean up
        output_stream.stop_stream()
        output_stream.close()
        p.terminate()

def send_audio():
    try:
        while True:
            # Record audio data from the microphone
            data = input_stream.read(chunk)
            
            # Send the recorded audio data to the server
            client_socket.sendall(data)
    except Exception as e:
        print(f"Error in send_audio: {e}")
    finally:
        # Clean up
        input_stream.stop_stream()
        input_stream.close()
        p.terminate()

# Create threads for receiving and sending audio
receive_thread = threading.Thread(target=receive_audio)
send_thread = threading.Thread(target=send_audio)

# Start the threads
receive_thread.start()
send_thread.start()

# Wait for the threads to finish
receive_thread.join()
send_thread.join()

# Close the client socket
client_socket.close()
