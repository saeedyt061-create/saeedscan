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


def scan_ports(target, start_port, end_port, timeout):
    print(f"\n🔍 Scanning {target}")
    print(f"Ports: {start_port}-{end_port}")
    print(f"Start time: {datetime.now()}\n")

    for port in range(start_port, end_port + 1):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                result = s.connect_ex((target, port))
                if result == 0:
                    print(f"[OPEN] Port {port}")
        except KeyboardInterrupt:
            print("\nScan interrupted by user.")
            sys.exit(0)
        except Exception:
            pass


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

