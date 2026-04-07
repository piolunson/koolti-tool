# KOOLTI-TOOL v10.0.0

![Version](https://img.shields.io/badge/version-v10.0.0-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![License](https://img.shields.io/badge/license-Custom--NC-red)
![Modules](https://img.shields.io/badge/modules-151-purple)
![Bundles](https://img.shields.io/badge/bundles-8-orange)
![Stars](https://img.shields.io/github/stars/piolunson/koolti-tool)
![Last Commit](https://img.shields.io/github/last-commit/piolunson/koolti-tool)

A terminal-based network & security toolkit with **151 modules**, **8 bundles**, **tool installer** for 20 external tools, plugin system and auto-update.

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

## Usage

```bash
python koolti_tool.py
```

### Main Menu

```
MAIN MENU
  [1]  🌐  Modules        — browse 151 modules by category
  [2]  📦  Bundles        — run full workflow on one target
  [3]  🔧  Tool Installer — install nmap, sqlmap, hashcat...

  [h] Help   [/] Search   [fav] Favourites   [u] Update   [q] Quit
```

### Modules Menu

```
MODULES — SELECT CATEGORY
  [1]  🌐  NETWORK         51 modules
  [2]  🕸  WEB / OSINT     49 modules
  [3]  🔐  CRYPTO          20 modules
  [4]  💻  SYSTEM          11 modules
  [5]  🛠  UTILITIES       20 modules
```

Pick a category → enter module number → runs.

| Shortcut | Action |
|----------|--------|
| `1` | Modules menu |
| `2` or `b` | Bundles menu |
| `3` or `i` | Tool installer |
| `/` or `search` | Search by keyword |
| `fav` | Favourites |
| `u` | Check for updates |
| `↑ ↓` | Command history |
| `q` | Quit |

## Preview

![ss1](img/ss1.jpg)

## Modules

### 🌐 NETWORK (51 modules)

| # | Module | # | Module |
|---|--------|---|--------|
| 1 | IP Tracker | 2 | DNS Lookup |
| 3 | Port Scanner | 4 | MAC Lookup |
| 5 | Local Network Info | 6 | Ping Tool |
| 7 | Subdomain Finder | 8 | Traceroute |
| 9 | Reverse IP Lookup | 10 | GeoIP Info |
| 11 | Network Interface Stats | 12 | ARP Scanner |
| 13 | Banner Grabber | 14 | HTTP Method Tester |
| 15 | SMTP Checker | 16 | FTP Checker |
| 17 | SSH Checker | 18 | SNMP Checker |
| 19 | BGP ASN Lookup | 20 | IP Range Scanner |
| 21 | Network Speed Test | 22 | WiFi SSID Scanner |
| 23 | mDNS Discovery | 24 | DNS Zone Transfer |
| 25 | Open Redirect Tester | 26 | CORS Policy Checker |
| 27 | CDN Detector | 28 | IPv6 Checker |
| 29 | Port Knock Detector | 30 | Shodan IP Lookup |
| 56 | Latency Map | 60 | DNS History Lookup |
| 61 | Multi-Port Banner Scan | 62 | Network Topology |
| 115 | **Nmap Scanner** | 122 | **Subfinder** |
| 125 | **Masscan** | 127 | **Curl Tool** |
| 128 | **Netcat** | 129 | **WHOIS (System)** |
| 130 | **Amass** | 132 | **Enum4Linux** |
| 133 | **Aircrack-ng** | 140 | Bulk DNS Resolver |
| 141 | IP Blacklist Check | 142 | Port Service Identifier |
| 147 | Open Ports + Banner | 149 | IP Geofence Checker |
| 150 | ASN/BGP Route Lookup | 151 | IP to ASN |

> **Bold** = requires external tool (use Tool Installer `[3]`)

### 🕸 WEB / OSINT (49 modules)

| # | Module | # | Module |
|---|--------|---|--------|
| 31 | Admin Finder | 32 | CMS Detector |
| 33 | WAF Detector | 34 | HTTP Header Inspector |
| 35 | Link Extractor | 36 | WHOIS Lookup |
| 37 | Robots.txt Checker | 38 | URL Scanner |
| 39 | Email Validator | 40 | Wayback Machine |
| 41 | Tech Stack Detector | 42 | Broken Link Checker |
| 43 | SSL Certificate Info | 44 | HTTP Status Bulk Check |
| 45 | Google Dork Generator | 46 | HTTP Parameter Fuzzer |
| 47 | JS File Extractor | 48 | Form Extractor |
| 49 | Cookie Inspector | 50 | IP Reputation Check |
| 51 | Path Traversal Tester | 52 | SQL Error Detector |
| 53 | Subdomain Takeover Check | 54 | TLS Version Checker |
| 55 | WhatWeb Lite | 57 | Certificate Transparency |
| 58 | HTTP Cache Inspector | 59 | Security Headers Score |
| 105 | XSS Scanner | 106 | Directory Bruteforcer |
| 107 | API Endpoint Fuzzer | 108 | Email Harvester |
| 109 | HTTP Smuggling Detector | 116 | **SQLMap** |
| 118 | **Gobuster** | 119 | **Nikto** |
| 120 | **WPScan** | 121 | **Nuclei** |
| 123 | **FFUF** | 131 | **DIRB** |
| 134 | **Metasploit** | 135 | Breach Check (HIBP) |
| 136 | Username Checker | 137 | CVE Lookup |
| 138 | Tech CVE Checker | 139 | Shodan Search |
| 143 | HTTP Response Timer | 146 | Headers Compare |
| 148 | Google Cache Checker | | |

### 🔐 CRYPTO (20 modules)

| # | Module | # | Module |
|---|--------|---|--------|
| 63 | Hash Generator | 64 | Hash Cracker (CPU+GPU) |
| 65 | Base64 Tool | 66 | Caesar Cipher |
| 67 | Password Strength | 68 | Wordlist Generator |
| 69 | ROT13 Cipher | 70 | XOR Cipher |
| 71 | Morse Code | 72 | Binary Converter |
| 73 | Hex Converter | 74 | URL Encoder/Decoder |
| 75 | JWT Decoder | 110 | Vigenère Cipher |
| 111 | Atbash Cipher | 112 | Hash Identifier |
| 113 | Advanced Password Gen | 114 | Encoding Detector |
| 124 | **Hydra** | 126 | **John the Ripper** |

### 💻 SYSTEM (11 modules)

| # | Module | # | Module |
|---|--------|---|--------|
| 76 | System Info | 77 | File Analyzer |
| 78 | WiFi Passwords (Win) | 79 | Process Viewer |
| 80 | Disk Usage | 81 | Environment Variables |
| 82 | Open Connections | 83 | File Hash Verifier |
| 84 | Directory Scanner | 85 | Log File Reader |
| 145 | File Strings Extractor | | |

### 🛠 UTILITIES (20 modules)

| # | Module | # | Module |
|---|--------|---|--------|
| 86 | IP Calculator (CIDR) | 87 | Random Password Gen |
| 88 | UUID Generator | 89 | Text Case Converter |
| 90 | Lorem Ipsum Generator | 91 | JSON Formatter |
| 92 | Unix Timestamp Converter | 93 | Color Code Converter |
| 94 | String Analyzer | 95 | Number Base Converter |
| 96 | Regex Tester | 97 | ASCII Art Generator |
| 98 | History Viewer | 99 | History Clear |
| 101 | Plugin Manager | 102 | Check for Update |
| 103 | Favourites | 104 | Module Search |
| 117 | Tool Installer | 144 | Network Calculator |

## Bundles

Type `2` or `b` in main menu. Bundles accept one target and run all relevant modules automatically.

| # | Bundle | What it does |
|---|--------|-------------|
| 1 | **Website Bundle** | IP, DNS, WHOIS, HTTP headers, SSL cert, CMS, open ports, security headers score, subdomains |
| 2 | **Hash Bundle** | Auto-detects hash type → dictionary → wordlist → brute force |
| 3 | **Email Bundle** | Format check, domain DNS, disposable check, WHOIS, password breach check |
| 4 | **Network Scan Bundle** | GeoIP, port scan, banner grab, reverse DNS, traceroute |
| 5 | **Subdomain Bundle** | 70+ subdomain checks + HTTP status on found ones |
| 6 | **WordPress Bundle** | WP version, login page, xmlrpc.php, user enumeration, exposed files |
| 7 | **API Security Bundle** | Endpoint discovery, auth check, CORS, rate limiting, security headers |
| 8 | **Password Audit Bundle** | Strength score + breach check (single or file with multiple passwords) |

## Tool Installer

Type `3` or `i` in main menu. Shows install commands for 20 external tools and lets you run them directly.

| Tool | Category | Description |
|------|----------|-------------|
| hashcat | CRYPTO | GPU hash cracker ~15B H/s |
| nmap | NET | Network mapper & port scanner |
| sqlmap | WEB | Automatic SQL injection |
| nikto | WEB | Web server vulnerability scanner |
| gobuster | WEB | Directory/DNS bruteforcer |
| hydra | CRYPTO | Network login bruteforcer |
| subfinder | NET | Passive subdomain discovery |
| nuclei | WEB | Fast vuln scanner with templates |
| ffuf | WEB | Fast web fuzzer |
| masscan | NET | Mass IP port scanner |
| wpscan | WEB | WordPress vulnerability scanner |
| john | CRYPTO | John the Ripper password cracker |
| netcat | NET | TCP/UDP network utility |
| curl | NET | HTTP request tool |
| whois | NET | System WHOIS lookup |
| amass | NET | Attack surface mapper |
| dirb | WEB | Web content scanner |
| enum4linux | NET | Windows/Samba enumeration |
| aircrack-ng | NET | WiFi security toolkit |
| metasploit | WEB | Penetration testing framework |

## Plugin System

Drop a `.py` file into `~/kooltitool/plugins/` and restart.

```python
def run():
    print("Hello from my plugin!")

def register():
    return {
        "name":        "My Plugin",
        "description": "Does something cool",
        "category":    "NET",
        "author":      "yourname",
        "version":     "1.0.0",
        "run":         run,
    }
```

Plugin appears as slot `200`, `201`, `202`...
Want it in the official release? → piolunson@proton.me

## Auto-Update

Checks GitHub `version.txt` automatically on every startup.
Type `u` to check manually.

## History

Results saved to `~/kooltitool/history/YYYY-MM-DD/` as JSON.
Password modules excluded. Browse with `[98]`, clear with `[99]`.

## Media & YouTube

See [MEDIA.md](MEDIA.md) for full policy.

- ✅ Free videos, tutorials, streams — allowed
- ❌ Paid courses using koolti-tool as core content — contact first
- ❌ Promoting illegal use — never allowed
- Required: link to repo + credit to piolunson

## Changelog

See [CHANGELOG.md](CHANGELOG.md)

## Legal Notice

For **educational purposes** and **authorized testing only**.
Use only on systems you own or have explicit written permission to test.

## License

Custom non-commercial license — see [LICENSE](LICENSE).

- ✅ Free non-commercial use
- ❌ No selling or commercial use without permission
- ❌ No modification without contacting the author first

📧 [piolunson@proton.me](mailto:piolunson@proton.me)
