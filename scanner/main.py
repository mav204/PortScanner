import time

from scanner import services, banner, core, report

HOST="127.0.0.1"
PORTS=[i for i in range (1,65536)]
TIMEOUT=1
MAX_WORKERS=100

def main():
    start = time.perf_counter()
    ports_details=core.deploy_port_scan(HOST,PORTS,TIMEOUT,MAX_WORKERS)
    for p in ports_details:
        if p["state"] == "open":
            p["service"] = services.service_name(p["port"])
            p["banner"] = banner.banner_name(HOST, p["port"], TIMEOUT)
            print(p)
    duration = time.perf_counter() - start
    open_count = sum(1 for p in ports_details if p["state"] == "open")
    print(f"Scanare terminata in {duration:.2f} s: {open_count} porturi deschise din {len(PORTS)}")

    path = report.generate_pdf(ports_details, HOST, PORTS, TIMEOUT, MAX_WORKERS, duration)
    print(f"Raport salvat in {path}")

    

if __name__=="__main__":
    main()