import socket
import pyaudio
import threading
import tkinter as tk
import RPi.GPIO as GPIO
import time

# Sender configuration
SENDER_HOST = '0.0.0.0'  # Host IP
SENDER_PORT = 12345      # Port for sender
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 44100
CHUNK = 1024
MAX_PACKET_SIZE = 4096  # Maximum size of each packet

last_time = time.time()

GPIO.setmode(GPIO.BCM)
gpio_pin = 17  # Change this to the actual GPIO pin number you're using
GPIO.setup(gpio_pin, GPIO.OUT)
sending = True
GPIO.output(gpio_pin, GPIO.HIGH)

# Initialize PyAudio
audio = pyaudio.PyAudio()
sender_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

# List of receivers with their IP addresses and ports
RECEIVER_LIST = [
    {'ip': '192.168.41.208', 'port': 12346},
    {'ip': '192.168.41.209', 'port': 12347},
    # Add more receivers as needed
]

# Set up sender and receiver sockets
sender_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
receiver_sockets = [socket.socket(socket.AF_INET, socket.SOCK_DGRAM) for _ in RECEIVER_LIST]

for receiver in RECEIVER_LIST:
    receiver_socket = next(filter(lambda x: x['ip'] == receiver['ip'], RECEIVER_LIST))
    receiver_socket.bind((SENDER_HOST, receiver['port']))

ptt_active = False

def send_audio():
    global sending
    while True:
        if sending:
            data = sender_stream.read(CHUNK)
            for receiver in RECEIVER_LIST:
                receiver_ip = receiver['ip']
                receiver_port = receiver['port']
                for i in range(0, len(data), MAX_PACKET_SIZE):
                    chunk = data[i:i + MAX_PACKET_SIZE]
                    sender_socket.sendto(chunk, (receiver_ip, receiver_port))

def receive_audio():
    global sending, last_time
    while True:
        data, _ = receiver_socket.recvfrom(MAX_PACKET_SIZE)
        receiver_stream.write(data)

def yoyo_audio():
    global sending, last_time
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind(('0.0.0.0', 12356))  # Change the port if needed

    while True:
        data, _ = server_socket.recvfrom(1024)
        if data == b'high':  # relay on
            GPIO.output(gpio_pin, GPIO.LOW)
            sending = False
        elif data == b'low':
            GPIO.output(gpio_pin, GPIO.HIGH)
            sending = True
        if not sending:
            last_time = time.time()

def checktime():
    global last_time, sending
    while True:
        time_elapsed = time.time() - last_time
        if time_elapsed >= 1:
            GPIO.output(gpio_pin, GPIO.HIGH)
            sending = True
            print("sending")
        time.sleep(0.1)

# Start sender and receiver threads
sender_thread = threading.Thread(target=send_audio, daemon=True)
receiver_thread = threading.Thread(target=receive_audio, daemon=True)
yoyo_thread = threading.Thread(target=yoyo_audio, daemon=True)
checkthread = threading.Thread(target=checktime, daemon=True)
sender_thread.start()
receiver_thread.start()
yoyo_thread.start()
checkthread.start()

def key_pressed(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = True
        print("Talking...")

def key_released(event):
    global ptt_active
    if event.keysym == 'Control_L':
        ptt_active = False
        print("Not talking...")

root = tk.Tk()
root.bind('<KeyPress>', key_pressed)
root.bind('<KeyRelease>', key_released)
root.mainloop()
