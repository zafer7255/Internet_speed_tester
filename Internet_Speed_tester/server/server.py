import socket
import threading
import time


def get_ip():
    try:
        # Create a socket to get the local IP address
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to Google's public DNS server
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except socket.error:
        return "Unable to retrieve IP"


def latency_jitter_test(client_socket):
    for _ in range(5):
        start_time = time.time()
        client_socket.send("Ping".encode())
        response = client_socket.recv(1024)
        end_time = time.time()

        round_trip_time = (end_time - start_time) * 1000
        print(f"Latency/Jitter Test - Round-trip time: {round_trip_time:.2f} ms")

def download_speed_test(client_socket):
    file_size = 1024 * 1024  # 1 MB
    start_time = time.time()
    client_socket.send(f"Download-{file_size}".encode())
    received_data = client_socket.recv(file_size)
    end_time = time.time()

    download_speed = file_size / (end_time - start_time)
    print(f"Download Speed Test - Speed: {download_speed / 1024:.2f} KB/s")

def upload_speed_test(client_socket):
    
    increase_everytime = 1
    file_size = 1024 * 1024  # 1 MB
    start_time = time.time()
    client_socket.send(f"Upload-{file_size}{increase_everytime}".encode())
    client_socket.recv(1024)
    client_socket.send(b'0' * file_size)
    end_time = time.time()
    increase_everytime = increase_everytime * 2

    upload_speed = file_size / (end_time - start_time)
    print(f"Upload Speed Test - Speed: {upload_speed / 1024:.2f} KB/s")

def handle_client(client_socket):
    print(f"Connection from {client_socket.getpeername()}")

    latency_jitter_test(client_socket)
    upload_speed_test(client_socket)
    download_speed_test(client_socket)

    client_socket.close()

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((get_ip(), 12345))
    server_socket.listen(5)

    print(f"Server listening on {get_ip()}:12345")

    while True:
        client_socket, client_addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()

if __name__ == "__main__":
    main()

