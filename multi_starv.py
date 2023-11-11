import socket
import pyaudio
import threading
import tkinter as tk

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345     # Port for sender
RECEIVER_IPS = ['192.168.41.219', '192.168.41.220', '192.168.41.221']  # List of Receiver's IP addresses
RECEIVER_PORT = 12346   # Port for receiver
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet
server_ip = '192.168.41.219'  # Raspberry Pi's IP address
server_port = 12356
sending = True

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
receiver_streams = [audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=CHUNK)
                    for _ in RECEIVER_IPS]

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in RECEIVER_IPS]
for i, receiver_socket in enumerate(receiver_sockets):
    receiver_socket.bind((SENDER_HOST, RECEIVER_PORT + i))

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

ptt_active = False


def send_audio():
    while True:
        data = sender_stream.read(CHUNK)
        for i in range(0, len(data), MAX_PACKET_SIZE):
            chunk = data[i:i + MAX_PACKET_SIZE]
            for receiver_ip, receiver_port in zip(RECEIVER_IPS, range(RECEIVER_PORT, RECEIVER_PORT + len(RECEIVER_IPS))):
                sender_socket.sendto(chunk, (receiver_ip, receiver_port))


def receive_audio(index):
    while True:
        data, _ = receiver_sockets[index].recvfrom(MAX_PACKET_SIZE)
        receiver_streams[index].write(data)


# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio)
receiver_threads = [threading.Thread(target=receive_audio, args=(i,)) for i in range(len(RECEIVER_IPS))]

sender_thread.start()
for receiver_thread in receiver_threads:
    receiver_thread.start()


def key_pressed(event):
    if event.keysym == 'p':
        client_socket.sendto(b'high', (server_ip, server_port))
    global ptt_active
    if event.keysym == 'p':
        ptt_active = True
        print("Talking...")

def key_released(event):
    if event.keysym == 't':
        client_socket.sendto(b'low', (server_ip, server_port))

    global ptt_active
    if event.keysym == 't':
        ptt_active = False
        print("Not talking...")

root = tk.Tk()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
root.mainloop()
