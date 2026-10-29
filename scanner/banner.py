import socket
def banner_name(host,port,timeout):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host,port))
            rec_bytes=s.recv(1024)
            if not rec_bytes:
                return None
            rec_str=rec_bytes.decode(errors="replace")
            rec_str=rec_str.strip()
            return rec_str
        except OSError:
            return None
            