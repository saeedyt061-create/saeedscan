#!/usr/bin/env python3
import argparse
import socket
import sys
from datetime import datetime

from saeedscan import __version__


def ethical_warning():
    print("""
⚠️  Ethical Warning
This tool is intended for EDUCATIONAL and AUTHORIZED security testing only.
Unauthorized scanning of systems you do not own or have permission to test
may be illegal in your country.
""")
    choice = input("Do you confirm you have permission? (yes/no): ").strip().lower()
    if choice != "yes":
        print("Exiting...")
        sys.exit(1)


import threading
from queue import Queue

open_ports = []
queue = Queue()


def worker(target, timeout):
    while not queue.empty():
        port = queue.get()
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((target, port)) == 0:
                    print(f"[OPEN] Port {port}")
                    open_ports.append(port)
        except Exception:
            pass
        finally:
            queue.task_done()


def scan_ports(target, start_port, end_port, timeout, threads=100):
    print(f"\n🔍 Scanning {target}")
    print(f"Ports: {start_port}-{end_port}")
    print(f"Threads: {threads}")
    print(f"Start time: {datetime.now()}\n")

    for port in range(start_port, end_port + 1):
        queue.put(port)

    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker, args=(target, timeout))
        t.daemon = True
        t.start()
        thread_list.append(t)

    queue.join()
def main():
    parser = argparse.ArgumentParser(
        description="SaeedScan - Ethical Port Scanner"
    )

    parser.add_argument("target", help="Target IP or hostname")
    parser.add_argument(
        "-p", "--ports",
        default="1-1024",
        help="Port range (default: 1-1024)"
    )
    parser.add_argument(
        "-t", "--timeout",
        type=float,
        default=0.5,
        help="Socket timeout (default: 0.5)"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"SaeedScan {__version__}"
    )

    args = parser.parse_args()

    ethical_warning()

    try:
        start_port, end_port = map(int, args.ports.split("-"))
    except ValueError:
        print("Invalid port range format. Use start-end")
        sys.exit(1)


    scan_ports(args.target, start_port, end_port, args.timeout)

if __name__ == "__main__":
    main()

