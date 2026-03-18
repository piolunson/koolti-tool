# KOOLTI-TOOL v7.0

![Version](https://img.shields.io/badge/version-v9-blue)
![Python](https://img.shields.io/badge/python-3.x-yellow)
![License](https://img.shields.io/badge/license-MIT-green)

A terminal-based network & security toolkit with 80 modules across 5 categories.

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

Optional GPU support:
```bash
# hashcat (recommended — works out of the box, ~15B H/s)
winget install hashcat        # Windows
sudo apt install hashcat      # Linux

# CuPy (CUDA 12.x only, MD5 kernel)
pip install cupy-cuda12x
```

## Usage

```bash
python koolti_tool.py
```

Enter a module number and press Enter. Type `h` for help, `q` to quit.

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
| 11 | Network Interface Stats | Bytes sent/received |
| 12 | ARP Scanner | Discover LAN hosts |
| 13 | Banner Grabber | Read service banners |
| 14 | HTTP Method Tester | Test allowed HTTP methods |
| 15 | SMTP Checker | Test SMTP connectivity |
| 16 | FTP Checker | Test FTP + anonymous login |
| 17 | SSH Checker | SSH banner and version |
| 18 | SNMP Checker | SNMP community string check |
| 19 | BGP ASN Lookup | Autonomous System info |
| 20 | IP Range Scanner | Ping scan CIDR range |
| 21 | Network Speed Test | Download speed test |
| 22 | WiFi SSID Scanner | List nearby WiFi networks |
| 23 | mDNS Discovery | Discover local services |
| 24 | DNS Zone Transfer | Attempt AXFR transfer |
| 25 | Open Redirect Tester | Test open redirect vulns |
| 26 | CORS Checker | CORS policy analysis |
| 27 | CDN Detector | Detect CDN provider |
| 28 | IPv6 Checker | IPv6 connectivity check |
| 29 | IPv6 Checker (ext) | Extended IPv6 info |
| 30 | Shodan IP Lookup | Shodan API query |

### 🕸 WEB / OSINT (31–45)
| # | Module | Description |
|---|--------|-------------|
| 31 | Admin Finder | Discover admin panels |
| 32 | CMS Detector | Detect CMS platform |
| 33 | WAF Detector | Detect web firewall |
| 34 | HTTP Header Inspector | Analyze security headers |
| 35 | Link Extractor | Extract all page links |
| 36 | WHOIS Lookup | Domain registration info |
| 37 | Robots.txt Checker | Analyze robots.txt + sitemap |
| 38 | URL Scanner | Redirect chain + SSL check |
| 39 | Email Validator | Validate email address |
| 40 | Wayback Machine | Check archived versions |
| 41 | Tech Stack Detector | Detect site technologies |
| 42 | Broken Link Checker | Find dead links |
| 43 | SSL Certificate Info | TLS cert details + expiry |
| 44 | HTTP Status Bulk Checker | Check multiple URLs |
| 45 | Google Dork Generator | Generate dork queries |

### 🔐 CRYPTO (46–58)
| # | Module | Description |
|---|--------|-------------|
| 46 | Hash Generator | MD5/SHA/NTLM/SHA3 |
| 47 | Hash Cracker | CPU + GPU (hashcat/CuPy) |
| 48 | Base64 Tool | Encode/decode Base64 |
| 49 | Caesar Cipher | Encrypt/decrypt/brute force |
| 50 | Password Strength | Evaluate password security |
| 51 | Wordlist Generator | Generate password lists |
| 52 | ROT13 Cipher | ROT13 encoding |
| 53 | XOR Cipher | XOR encryption |
| 54 | Morse Code | Encode/decode Morse |
| 55 | Binary Converter | Text ↔ binary |
| 56 | Hex Converter | Text ↔ hexadecimal |
| 57 | URL Encoder/Decoder | URL encoding |
| 58 | JWT Decoder | Decode JWT tokens |

### 💻 SYSTEM (59–68)
| # | Module | Description |
|---|--------|-------------|
| 59 | System Info | OS + hardware stats |
| 60 | File Analyzer | File metadata + hash |
| 61 | WiFi Passwords | Saved WiFi keys (Windows) |
| 62 | Process Viewer | Top processes by RAM |
| 63 | Disk Usage | Partition usage |
| 64 | Environment Variables | System env vars |
| 65 | Open Connections | Active network connections |
| 66 | File Hash Verifier | Verify file integrity |
| 67 | Directory Scanner | List directory contents |
| 68 | Log File Reader | Read + filter log files |

### 🛠 UTILITIES (69–80)
| # | Module | Description |
|---|--------|-------------|
| 69 | IP Calculator (CIDR) | Network IP calculator |
| 70 | Random Password Generator | Secure password generator |
| 71 | UUID Generator | v1/v4 UUID generator |
| 72 | Text Case Converter | snake_case, CamelCase, etc. |
| 73 | Lorem Ipsum Generator | Placeholder text |
| 74 | JSON Formatter | Format + validate JSON |
| 75 | Unix Timestamp Converter | Date ↔ timestamp |
| 76 | Color Code Converter | HEX ↔ RGB |
| 77 | String Analyzer | Character frequency stats |
| 78 | Number Base Converter | DEC/BIN/OCT/HEX |
| 79 | Regex Tester | Test regular expressions |
| 80 | ASCII Art Generator | Text → ASCII art |

## Legal Notice

This tool is intended for educational purposes and authorized security testing only.  
Use only on systems you own or have explicit written permission to test.  
Unauthorized scanning or exploitation may be illegal in your jurisdiction.

## License

MIT License
 
