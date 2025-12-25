#!/usr/bin/env python3
# ============================================
# SaeedScan v1.0
# Advanced Ethical Async Port Scanner
# Author: Saeed
# ============================================
__version__ = "1.0.0"

import socket
import asyncio
import argparse
import json
import random
import time
from datetime import datetime

# ============ CONFIG ============
DEFAULT_TIMEOUT = 1
RATE_LIMIT_MIN = 0.03   # evasion
RATE_LIMIT_MAX = 0.2
# ================================


# ---------- Service Detection ----------
def get_service_name(port):
    try:
        return socket.getservbyport(port)
    except:
        return "unknown"


# ---------- OS Fingerprinting (Soft) ----------
def guess_os(ttl):
    if ttl >= 128:
        return "Windows"
    elif ttl >= 64:
        return "Linux / Unix"
    else:
        return "Unknown"


# ---------- Evasion (Jitter) ----------
async def jitter():
    await asyncio.sleep(random.uniform(RATE_LIMIT_MIN, RATE_LIMIT_MAX))


# ---------- Async Port Scan + Banner ----------
async def scan_port(host, port, timeout):
    await jitter()

    try:
        conn = asyncio.open_connection(host, port)
        reader, writer = await asyncio.wait_for(conn, timeout=timeout)

        banner = ""
        try:
            writer.write(b"\r\n")
            await writer.drain()
            banner_bytes = await asyncio.wait_for(reader.read(1024), timeout=1)
            banner = banner_bytes.decode(errors="ignore").strip()
        except:
            banner = ""

        writer.close()
        await writer.wait_closed()

        return {
            "port": port,
            "status": "open",
            "service": get_service_name(port),
            "banner": banner
        }

    except:
        return None


# ---------- Scan Engine ----------
async def run_scan(host, ports, timeout):
    ports = list(ports)
    random.shuffle(ports)  # evasion

    tasks = [scan_port(host, p, timeout) for p in ports]
    results = await asyncio.gather(*tasks)

    return [r for r in results if r]


# ---------- Output ----------
def save_results(results, target):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    txt_file = f"saeedscan_{target}_{timestamp}.txt"
    json_file = f"saeedscan_{target}_{timestamp}.json"

    with open(txt_file, "w") as f:
        for r in results:
            f.write(f"Port {r['port']} | {r['service']} | {r['banner']}\n")

    with open(json_file, "w") as f:
        json.dump(results, f, indent=4)

    print("\n[✓] Results saved:")
    print(f" - {txt_file}")
    print(f" - {json_file}")


# ---------- Helpers ----------
def parse_ports(port_range):
    if "-" in port_range:
        start, end = port_range.split("-")
        return range(int(start), int(end) + 1)
    return [int(port_range)]


def banner():
    print("""
╔══════════════════════════════════╗
║          SaeedScan v1.0          ║
║  Advanced Ethical Port Scanner   ║
║          Author: Saeed           ║
╚══════════════════════════════════╝
""")


# ---------- Main ----------
def main():
    banner()

    parser = argparse.ArgumentParser(
        description="SaeedScan - Advanced Ethical Async Port Scanner"
    )
    parser.add_argument("target", help="Target IP or Host (authorized only)")
    parser.add_argument("-p", "--ports", default="1-1024",
                        help="Port range (e.g. 1-1000)")
    parser.add_argument("-t", "--timeout", type=int,
                        default=DEFAULT_TIMEOUT, help="Timeout seconds")
    parser.add_argument("-s", "--save", action="store_true",
                        help="Save results to TXT & JSON")

    args = parser.parse_args()

    ports = parse_ports(args.ports)

    print(f"[+] Target : {args.target}")
    print(f"[+] Ports  : {args.ports}")
    print("[+] Scan started...\n")

    start = time.time()
    results = asyncio.run(run_scan(args.target, ports, args.timeout))
    end = time.time()

    for r in results:
        print(f"[OPEN] {r['port']:>5} | {r['service']:<10} | {r['banner']}")

    print("\n[✓] Scan completed")
    print(f"[✓] Time elapsed : {end - start:.2f}s")
    print(f"[✓] Open ports   : {len(results)}")

    if args.save:
        save_results(results, args.target)



parser.add_argument(
    "--version",
    action="version",
    version=f"SaeedScan v{__version__}"
)
