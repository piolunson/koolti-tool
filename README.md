# KOOLTI-TOOL v8.1.0

![Version](https://img.shields.io/badge/version-v8.1.0-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![License](https://img.shields.io/badge/license-Custom--NC-red)
![Modules](https://img.shields.io/badge/modules-102-purple)
![Stars](https://img.shields.io/github/stars/piolunson/koolti-tool)
![Last Commit](https://img.shields.io/github/last-commit/piolunson/koolti-tool)

A terminal-based network & security toolkit with **102 modules**, a plugin system, and auto-update.

```
  ██╗  ██╗ ██████╗  ██████╗ ██╗  ████████╗██╗
  ██║ ██╔╝██╔═══██╗██╔═══██╗██║  ╚══██╔══╝██║
  █████╔╝ ██║   ██║██║   ██║██║     ██║   ██║
  ██╔═██╗ ██║   ██║██║   ██║██║     ██║   ██║
  ██║  ██╗╚██████╔╝╚██████╔╝███████╗██║   ██║
  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝   ╚═╝
```

## Requirements

```bash
pip install requests psutil rich
```

## Installation

```bash
git clone https://github.com/piolunson/koolti-tool.git
cd koolti-tool
pip install -r requirements.txt
python koolti_tool.py
```

Optional GPU support for Hash Cracker (module 64):
```bash
# hashcat — recommended, ~15 billion H/s, works out of the box
winget install hashcat        # Windows
sudo apt install hashcat      # Linux

# CuPy — Python-native CUDA kernel (CUDA 12.x only, MD5)
pip install cupy-cuda12x
```

## Usage

```bash
python koolti_tool.py
```

Enter a module number and press Enter. Type `h` for help, `u` to check updates, `q` to quit.

## Preview

![ss1](img/ss1.jpg)

## Modules

### 🌐 NETWORK (1–30)
| # | Module | Description |
|---|--------|-------------|
| 1 | IP Tracker | Geolocation of IP address |
| 2 | DNS Lookup | Resolve domain names |
| 3 | Port Scanner | Scan open ports |
| 4 | MAC Lookup | Identify NIC manufacturer |
| 5 | Local Network Info | Network interfaces |
| 6 | Ping Tool | Test host reachability |
| 7 | Subdomain Finder | DNS subdomain discovery |
| 8 | Traceroute | Trace packet route |
| 9 | Reverse IP Lookup | Hostname from IP |
| 10 | GeoIP Info | Detailed geographic info |
| 11 | Network Interface Stats | Bytes sent/received per interface |
| 12 | ARP Scanner | Discover live hosts on LAN |
| 13 | Banner Grabber | Read raw service banners |
| 14 | HTTP Method Tester | Test which HTTP methods are allowed |
| 15 | SMTP Checker | Test SMTP connectivity + EHLO |
| 16 | FTP Checker | Test FTP + anonymous login detection |
| 17 | SSH Checker | SSH port + banner + version |
| 18 | SNMP Checker | SNMP community string bruteforce |
| 19 | BGP ASN Lookup | Autonomous System info via bgpview.io |
| 20 | IP Range Scanner | Ping sweep a CIDR range |
| 21 | Network Speed Test | Download speed via Cloudflare |
| 22 | WiFi SSID Scanner | List nearby WiFi networks |
| 23 | mDNS Discovery | Discover local network services |
| 24 | DNS Zone Transfer | Attempt AXFR zone transfer |
| 25 | Open Redirect Tester | Test for open redirect vulnerabilities |
| 26 | CORS Policy Checker | Analyze CORS headers and misconfigs |
| 27 | CDN Detector | Detect CDN provider from headers |
| 28 | IPv6 Checker | IPv6 connectivity and address info |
| 29 | Port Knock Detector | Scan for port-knock protected ranges |
| 30 | Shodan IP Lookup | Full Shodan API query (requires API key) |

### 🕸 WEB / OSINT (31–62)
| # | Module | Description |
|---|--------|-------------|
| 31 | Admin Finder | Discover admin and login panels |
| 32 | CMS Detector | Detect CMS platform (WP, Joomla, etc.) |
| 33 | WAF Detector | Detect Web Application Firewall |
| 34 | HTTP Header Inspector | Analyze HTTP + security headers |
| 35 | Link Extractor | Extract all links from a page |
| 36 | WHOIS Lookup | Domain registration info via RDAP |
| 37 | Robots.txt Checker | Analyze robots.txt + sitemap.xml |
| 38 | URL Scanner | Redirect chain + SSL + server info |
| 39 | Email Validator | Format, domain, and disposable check |
| 40 | Wayback Machine | Check archived versions on archive.org |
| 41 | Tech Stack Detector | Detect JS frameworks, CDNs, analytics |
| 42 | Broken Link Checker | Find dead links on a page |
| 43 | SSL Certificate Info | TLS cert details + expiry countdown |
| 44 | HTTP Status Bulk Checker | Check status of multiple URLs at once |
| 45 | Google Dork Generator | Generate targeted Google dork queries |
| 46 | HTTP Parameter Fuzzer | Fuzz URL parameters for unexpected responses |
| 47 | JS File Extractor | Find external + inline JS on a page |
| 48 | Form Extractor | Extract forms, inputs, and hidden fields |
| 49 | Cookie Inspector | Analyze cookies and Secure/HttpOnly flags |
| 50 | IP Reputation Check | Check if IP is proxy/hosting/flagged |
| 51 | Path Traversal Tester | Test for directory traversal vulnerabilities |
| 52 | SQL Error Detector | Detect SQL error messages in responses |
| 53 | Subdomain Takeover Check | Check subdomains for takeover risk |
| 54 | TLS Version Checker | Check supported TLS 1.0–1.3 versions |
| 55 | WhatWeb Lite | Quick tech fingerprint from headers + HTML |
| 56 | Latency Map | Ping 6 global endpoints and compare RTT |
| 57 | Certificate Transparency | Find all SSL certs via crt.sh |
| 58 | HTTP Cache Inspector | Analyze Cache-Control and caching headers |
| 59 | Security Headers Score | Grade site headers A+/A/B/C/D/F |
| 60 | DNS History Lookup | Historical DNS records via HackerTarget |
| 61 | Multi-Port Banner Scan | Grab banners from 13 common ports at once |
| 62 | Network Topology | Map route hops via TTL probing |

### 🔐 CRYPTO (63–75)
| # | Module | Description |
|---|--------|-------------|
| 63 | Hash Generator | MD5 / SHA-1/256/384/512 / SHA3 / NTLM |
| 64 | Hash Cracker | CPU multiprocessing + GPU (hashcat / CuPy) |
| 65 | Base64 Tool | Encode and decode Base64 |
| 66 | Caesar Cipher | Encrypt / decrypt / brute force all 25 shifts |
| 67 | Password Strength | Score password with tips (1–8 pts) |
| 68 | Wordlist Generator | Generate password variants from a base word |
| 69 | ROT13 Cipher | Symmetric ROT13 encoding |
| 70 | XOR Cipher | XOR encrypt with a key (HEX + Base64 output) |
| 71 | Morse Code | Encode and decode Morse code |
| 72 | Binary Converter | Text ↔ binary (8-bit per char) |
| 73 | Hex Converter | Text ↔ hexadecimal |
| 74 | URL Encoder/Decoder | Percent-encode and decode URLs |
| 75 | JWT Decoder | Decode JWT header + payload (no verify) |

### 💻 SYSTEM (76–85)
| # | Module | Description |
|---|--------|-------------|
| 76 | System Info | OS, CPU, RAM, disk usage bars |
| 77 | File Analyzer | Metadata + MD5/SHA-256 of any file |
| 78 | WiFi Passwords | Read saved WiFi passwords (Windows only) |
| 79 | Process Viewer | Top 20 processes by RAM usage |
| 80 | Disk Usage | All partitions with usage bars |
| 81 | Environment Variables | List + filter system env vars |
| 82 | Open Connections | Active TCP/UDP network connections |
| 83 | File Hash Verifier | Verify file integrity against known hash |
| 84 | Directory Scanner | List directory contents with sizes |
| 85 | Log File Reader | Read and keyword-filter log files |

### 🛠 UTILITIES (86–102)
| # | Module | Description |
|---|--------|-------------|
| 86 | IP Calculator (CIDR) | Network, broadcast, hosts, type |
| 87 | Random Password Generator | Secure random passwords with strength stars |
| 88 | UUID Generator | UUID v1 (time-based) or v4 (random) |
| 89 | Text Case Converter | UPPER / lower / snake_case / CamelCase / etc. |
| 90 | Lorem Ipsum Generator | Configurable placeholder text |
| 91 | JSON Formatter | Format, validate, and syntax-highlight JSON |
| 92 | Unix Timestamp Converter | Timestamp ↔ date (UTC + local) |
| 93 | Color Code Converter | HEX ↔ RGB + terminal color preview |
| 94 | String Analyzer | Char frequency, word count, top letters |
| 95 | Number Base Converter | DEC / BIN / OCT / HEX / Unicode |
| 96 | Regex Tester | Test regex with match highlighting |
| 97 | ASCII Art Generator | Text → block ASCII art (A–Z, 0–9) |
| 98 | History Viewer | Browse saved session history by date |
| 99 | History Clear | Permanently delete all history files |
| 100 | Network Topology (ext) | Extended TTL-based route mapping |
| 101 | Plugin Manager | View and manage loaded plugins |
| 102 | Check for Update | Manually check for a newer version |

## Plugin System

You can extend koolti-tool with your own modules without touching the main file.

**How it works:**
1. Create a `.py` file in `~/kooltitool/plugins/`
2. Restart koolti-tool
3. Your plugin appears in the menu as slot `200`, `201`, `202`...

**Minimal plugin template:**
```python
def run():
    print("Hello from my plugin!")

def register():
    return {
        "name":        "My Plugin",
        "description": "Does something cool",
        "category":    "NET",   # NET / WEB / CRY / SYS / UTL
        "author":      "yourname",
        "version":     "1.0.0",
        "run":         run,
    }
```

A full example is included in `example_plugin.py`.  
A `HOW_TO_WRITE_A_PLUGIN.md` guide is automatically created in the plugins folder on first run.

> Want your plugin included in the official release?  
> Contact **piolunson@proton.me** — accepted plugins get you credited as a contributor.

## Auto-Update

koolti-tool checks for updates automatically every time it starts.  
If a new version is available you will see:

```
  ██ UPDATE AVAILABLE  v8.1.0 → v8.2.0
  https://github.com/piolunson/koolti-tool/releases
```

You can also check manually by typing `u` in the menu or running module `[102]`.

## History

All module results are automatically saved to:

```
~/kooltitool/history/YYYY-MM-DD/HHMMSS_NNN_module_name.json
```

Password-related modules **(64, 67, 68, 87)** are excluded from history.  
Use module `98` to browse saved sessions, module `99` to clear them.

## Repository Structure

```
koolti-tool/
├── koolti_tool_v8.py      ← main program
├── version.txt            ← current version (used for auto-update)
├── example_plugin.py      ← plugin template
├── requirements.txt
├── README.md
├── LICENSE
├── SECURITY.md
├── CONTRIBUTING.md
├── .gitignore
└── img/
    └── ss1.jpg
```

## Changelog

### v8.1.0
- Added **Plugin System** — extend koolti-tool with `.py` files dropped into `~/kooltitool/plugins/`
- Added **Auto-Update** — checks GitHub for new versions on every startup
- Added `[u]` shortcut in menu to manually trigger update check
- Added module `[101]` Plugin Manager and `[102]` Check for Update
- Added `version.txt` for update mechanism
- Added `example_plugin.py` with full plugin template
- Added `SECURITY.md` for responsible vulnerability disclosure
- Added `requirements.txt`
- Total: 102 modules

### v8.0.0
- Added 20 new modules (46–62, 98–100)
- Added automatic session history system (`~/kooltitool/history/`)
- Full English rewrite — zero comments, zero Polish text

### v7.1.1
- Fixed import issues in several modules

### v7.1.0
- Added 20 new NET modules
- Improved multiprocessing Hash Cracker
- Better TUI — ASCII logo, progress bars, color categories

### v7.0.0
- Full rewrite — 80 modules
- GPU hash cracking (hashcat + CuPy CUDA)
- CUDA 13.x detection with graceful fallback

### v6.0.0
- 60 modules, TUI rewrite

### v5.0.0
- First major release — 25 modules

## Legal Notice

You are solely responsible for your actions.

This tool is intended for **educational purposes** and **authorized security testing only**.  
Use only on systems you own or have **explicit written permission** to test.  
Unauthorized scanning or exploitation may be illegal in your jurisdiction.

## License

This project uses a **custom non-commercial license**.  
See [LICENSE](LICENSE) for full details.

**In short:**
- ✅ Free to use and distribute for non-commercial purposes
- ✅ Must keep original copyright notice
- ❌ Cannot sell or use commercially without permission
- ❌ Cannot modify without contacting the author first

**To request permission to modify or use commercially:**  
📧 [piolunson@proton.me](mailto:piolunson@proton.me)
