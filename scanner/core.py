from concurrent.futures import ThreadPoolExecutor
import socket


def port_state(host, port, timeout):
    with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
        s.settimeout(timeout)
        try:
            s.connect((host,port))
        except TimeoutError:
            #print('Conexion timeout')
            return "filtered"
        except ConnectionRefusedError:
            #print('Conexiune refuzata')
            return "closed"
        return "open"
     #cu with se face close automat

#varianta neparalela
def scan_ports(host, ports, timeout):
    port_details = []
    for port in ports:
        state = port_state(host, port, timeout)
        port_details.append({"port": port, "state": state})
    return port_details


def deploy_port_scan(host, ports, timeout,workes):
    with ThreadPoolExecutor(max_workers=workes) as executor:
        states=executor.map(port_state,[host]*len(ports),ports,[timeout]*len(ports))
    
    port_details=[]
    for p,s in zip(ports,states):
        port_details.append({"port": p, "state": s})
    
    return port_details
        
        
        