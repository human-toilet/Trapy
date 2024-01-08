import socket

def send_data_to_server(address, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as client_socket:
        client_socket.sendto(data.encode(), address)

if __name__ == "__main__":
    server_address = ('127.0.0.1', 9000)  # Cambia esto por la dirección y puerto del servidor
    message = "Hello, server!"  # Mensaje que deseas enviar

    send_data_to_server(server_address, message)