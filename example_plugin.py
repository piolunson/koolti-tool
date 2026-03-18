"""
KOOLTI-TOOL Example Plugin
Save this file to ~/kooltitool/plugins/ and restart koolti-tool.
"""

import socket


def run():
    print("  Enter a domain to resolve:")
    domain = input("  ❯ ").strip()
    if not domain:
        return
    try:
        ip = socket.gethostbyname(domain)
        print(f"\n  ✔  {domain}  →  {ip}")
    except Exception as e:
        print(f"\n  ✘  {e}")


def register():
    return {
        "name":        "Quick DNS Resolve",
        "description": "Instantly resolve a domain to IP",
        "category":    "NET",
        "author":      "yourname",
        "version":     "1.0.0",
        "run":         run,
    }
