# Port_Scanner

A multithreaded TCP port scanner written in Python, with service identification, banner grabbing and a PDF report. It is a learning project for network security, and its results are checked against Nmap.

> ⚠️ **Scan only hosts you own or are explicitly allowed to test.** Unauthorized port scanning can be illegal. The examples here target `127.0.0.1` and `scanme.nmap.org`, which the Nmap project provides for this purpose.

## Features

- **TCP connect scan.** Each port is classified as `open`, `closed` or `filtered`.
- **Multithreaded.** It uses `concurrent.futures.ThreadPoolExecutor`, so timeouts on filtered ports overlap instead of adding up.
- **Service names.** The port number is looked up in the system's service list (`/etc/services`).
- **Banner grabbing.** It reads what a service announces after connecting, for example `SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13`.
- **PDF report.** Each report has the scan details, a summary of open, closed and filtered ports, a table of open ports, and a list of services worth reviewing. Reports are saved with a timestamp in `reports/`.

## How it works

The scanner tries a full TCP handshake (`connect()`) on every port. The reply determines the state:

| Reply from the target | Python result | State |
|---|---|---|
| SYN-ACK: connection accepted | `connect()` succeeds | **open** |
| RST: connection refused | `ConnectionRefusedError` | **closed** |
| No reply before the timeout | `TimeoutError` | **filtered** (probably a firewall) |

Data flows through the modules like this:

```
main.py ──► core.deploy_port_scan()   scans all ports in parallel
              │
              ▼   [{"port": 22, "state": "open"}, ...]
main.py ──► for each open port:
              services.service_name()  →  "service"
              banner.banner_name()     →  "banner"
              │
              ▼
          report.generate_pdf()        →  reports/<timestamp>_portscan.pdf
```

## Project structure

```
PortScanner/
├── scanner/
│   ├── core.py       # port_state(): one port; deploy_port_scan(): many ports, in parallel
│   ├── services.py   # port number → service name
│   ├── banner.py     # banner grabbing
│   ├── report.py     # PDF report (fpdf2)
│   └── main.py       # entry point: settings, glue between modules, timing
├── reports/          # generated PDFs (git-ignored)
└── requirements.txt
```

## Installation

You need Python 3.10 or later.

```bash
git clone https://github.com/mav204/PortScanner.git
cd PortScanner
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Usage

The scan settings are constants at the top of `scanner/main.py`:

```python
HOST = "127.0.0.1"
PORTS = range(1, 65536)
TIMEOUT = 1          # seconds to wait per port
MAX_WORKERS = 100    # number of threads
```

Run the scanner from the project folder:

```bash
python3 -m scanner.main
```

It prints the open ports and a summary in the terminal, then saves the PDF report in `reports/`.

## Validation against Nmap

I ran both tools against two targets, using the same scan type in Nmap (`-sT`, TCP connect), and compared the results.

### 1. Remote host: `scanme.nmap.org` (ports 1–1024)

Settings in `main.py`: `HOST = "scanme.nmap.org"` and `PORTS = range(1, 1025)`.

**Port_Scanner:**

```
{'port': 22, 'state': 'open', 'service': 'ssh', 'banner': 'SSH-2.0-OpenSSH_6.6.1p1 Ubuntu-2ubuntu2.13'}
{'port': 80, 'state': 'open', 'service': 'http', 'banner': None}

open: 2   filtered: 8   closed: 1014
Scanare terminata in 3.73 s: 2 porturi deschise din 1024
```

**Nmap:**

```
$ nmap -sT -p 1-1024 scanme.nmap.org
Warning: Hostname scanme.nmap.org resolves to 2 IPs. Using 45.33.32.156.
Nmap scan report for scanme.nmap.org (45.33.32.156)
Host is up (0.19s latency).
Not shown: 1014 closed tcp ports (conn-refused)
PORT    STATE    SERVICE
22/tcp  open     ssh
23/tcp  filtered telnet
25/tcp  filtered smtp
80/tcp  open     http
135/tcp filtered msrpc
136/tcp filtered profile
137/tcp filtered netbios-ns
138/tcp filtered netbios-dgm
139/tcp filtered netbios-ssn
445/tcp filtered microsoft-ds

Nmap done: 1 IP address (1 host up) scanned in 42.00 seconds
```

**Result:** both tools report the same open ports (22 and 80) and the same counts: 2 open, 8 filtered and 1,014 closed.

- **The filtered ports are a firewall at work.** Telnet, SMTP and the Windows file-sharing ports (135–139, 445) are often abused, so many networks drop traffic to them. Neither tool gets a reply, so both mark them `filtered`.
- **The banner gives more than the service name.** Both tools say port 22 is `ssh`, but only the banner reveals the exact software and version: OpenSSH 6.6.1p1 on Ubuntu. With a version you can look up known vulnerabilities (CVEs).
- **Port 80 has no banner.** HTTP waits for the client to send a request first, so a plain banner grab only gets silence until the timeout.

### 2. Local machine: `127.0.0.1` (all 65,535 ports)

> For privacy, I removed the lines for local database and remote-desktop services (MySQL and VNC) from the outputs below. The remaining rows are unchanged.

**Port_Scanner:**

```
{'port': 5000, 'state': 'open', 'service': 'commplex-main', 'banner': None}
{'port': 7000, 'state': 'open', 'service': 'afs3-fileserver', 'banner': None}
{'port': 7768, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 44950, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 44960, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 49256, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 53548, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 53576, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 53577, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 53608, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 53712, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 57621, 'state': 'open', 'service': 'unknown', 'banner': None}
{'port': 58728, 'state': 'open', 'service': 'unknown', 'banner': '\x01\x00\x00\x00'}
{'port': 62912, 'state': 'open', 'service': 'unknown', 'banner': None}
Scanare terminata in 17.60 s: 17 porturi deschise din 65535
```

**Nmap:**

```
$ nmap -sT -p 1-65535 127.0.0.1
Strange read error from 127.0.0.1 (22 - 'Invalid argument')
Nmap scan report for localhost (127.0.0.1)
Host is up (0.000017s latency).
Not shown: 65516 closed tcp ports (conn-refused)
PORT      STATE    SERVICE
88/tcp    open     kerberos-sec
5000/tcp  open     upnp
7000/tcp  open     afs3-fileserver
7768/tcp  open     unknown
44950/tcp open     unknown
44960/tcp open     unknown
49256/tcp open     unknown
52887/tcp filtered unknown
53548/tcp open     unknown
53576/tcp open     unknown
53577/tcp open     unknown
53608/tcp open     unknown
53712/tcp open     unknown
57621/tcp open     unknown
58728/tcp open     unknown
62912/tcp open     unknown

Nmap done: 1 IP address (1 host up) scanned in 1.16 seconds
```

**Result:** every port that Port_Scanner reported as open was also open in Nmap. There are two differences, and neither is caused by the scanner:

- **Port 88** is the macOS Kerberos service, which starts on demand and stops when idle. It was running when Nmap scanned and had stopped a few minutes later, when Port_Scanner ran. Earlier Port_Scanner runs reported it as `open`.
- **Port 52887** is in the range the OS hands out for temporary client connections. Nmap also printed `Strange read error from 127.0.0.1`, which points to a short-lived local connection, not a firewall.

**Service names.** Both tools guess the service from the port number, so they mostly agree, but the guesses can be wrong. On macOS, ports 5000 and 7000 belong to the **AirPlay Receiver**, not to `commplex-main`/`upnp` or `afs3-fileserver`. The high ports (44950 and up) are opened by desktop applications and have no registered name.

**Limitations of a localhost scan:**

- **There are no filtered ports.** Traffic to `127.0.0.1` never leaves the machine and is not filtered by a firewall, so every port is either open or closed. Use a remote target such as `scanme.nmap.org` to test the `filtered` state.
- **The results change between runs.** Applications open and close ports all the time, so two scans a few minutes apart can differ, as port 88 shows. Run tools back to back when you compare them.
- **The timings are not realistic.** The round-trip time on the loopback interface is about 0.00002 s, compared with 0.19 s to `scanme.nmap.org`, so localhost speed says little about scanning over a real network.

### Speed

| Target | Port_Scanner | Nmap `-sT` |
|---|---|---|
| `scanme.nmap.org`, 1,024 ports | **3.7 s** | 42.0 s |
| `127.0.0.1`, 65,535 ports | 17.6 s | **1.2 s** |

The results point in opposite directions, for different reasons.

**On the remote host, Port_Scanner is about 11× faster.** It waits a fixed 1 second per port and never retries. Nmap is deliberately careful on real networks: it resends probes that get no reply, so it doesn't mistake a lost packet for a filtered port, and it slows down when it detects packet loss. It trades speed for accuracy.

**On localhost, Nmap is about 15× faster.** Most of Port_Scanner's time there is spent on banner grabbing, not on the scan:

| Port_Scanner on `127.0.0.1` | Time |
|---|---|
| Port scan only | 4.1 s |
| Banner grabbing (17 open ports) | 13.0 s |
| **Total** | **17.6 s** |

Banner grabbing runs **one port at a time**, and services that wait for the client to speak first make it wait the full 1-second timeout each. The scan itself is also slower than Nmap's. Port_Scanner uses 100 threads with blocking sockets, while Nmap uses non-blocking sockets and an event loop to keep hundreds of probes in flight with very little overhead.

## Limitations and next steps

- [ ] Run banner grabbing in parallel, as the port scan already does
- [ ] Retry ports that time out, to reduce false `filtered` results on unreliable networks
- [ ] SYN ("half-open") scan with Scapy: faster, and it never completes the handshake
- [ ] Send protocol-specific probes (for example an HTTP `HEAD` request) to get banners from services that don't speak first
- [ ] Validate the settings in `main.py` (port range, host, thread count)
- [ ] IPv6 and UDP scanning

## Built with

- Python standard library: `socket`, `concurrent.futures`, `time`, `pathlib`
- [fpdf2](https://github.com/py-pdf/fpdf2) for the PDF report
- [Nmap](https://nmap.org) for validation
