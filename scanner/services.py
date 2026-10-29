import socket
def service_name(port):
    try:
        return socket.getservbyport(port,"tcp")
    except OSError:
        return "unknown"


