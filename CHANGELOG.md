# Changelog

All notable changes to koolti-tool are documented here.

## [v8.2.1] — 2026-03-19

### Changed
- Version bump to 8.2.1
- Added `MEDIA.md` — official YouTube and content creator policy

### Fixed
- Stability improvements and minor fixes

---

## [v8.2.0] — 2026-03-19

### Added
- **Module Search** `[104]` — find any module by name or keyword
  - Shortcut: type `/` or `search` in the menu
- **Favourites** `[103]` — save your most-used modules
  - Shortcut: type `fav` in the menu
  - Saved to `~/kooltitool/favourites.json`
- **Command History** — arrow keys ↑/↓ navigate previous commands
  - Works via readline on Linux/Mac, plain history on Windows
  - Saved to `~/kooltitool/cmd_history.json`
- Keyboard shortcuts shown in prompt: `/`, `fav`, `u`, `h`
- **5 new WEB modules:**
  - `[105]` XSS Scanner — 10 payloads, detects reflection
  - `[106]` Directory Bruteforcer — 40 common paths
  - `[107]` API Endpoint Fuzzer — 30 REST/GraphQL endpoints
  - `[108]` Email Harvester — extract emails from a page
  - `[109]` HTTP Smuggling Detector — CL.TE and TE.CL probes
- **5 new CRYPTO modules:**
  - `[110]` Vigenère Cipher — polyalphabetic encryption/decryption
  - `[111]` Atbash Cipher — mirror alphabet (A↔Z)
  - `[112]` Hash Identifier — detect hash type from length/format
  - `[113]` Advanced Password Generator — 4 presets + custom rules
  - `[114]` Encoding Detector — auto-detect 6+ encodings

### Stats
- Total: **114 modules**
- File size: ~168 KB

---

## [v8.1.0] — 2026-03-18

### Added
- **Plugin System** — load external `.py` modules from `~/kooltitool/plugins/`
  - Plugins appear as slots 200, 201, 202...
  - Auto-generates `HOW_TO_WRITE_A_PLUGIN.md` guide on first run
- **Auto-Update** — checks GitHub `version.txt` silently on every startup
  - Shows banner when newer version is available
  - Shortcut: type `u` in menu
- `[101]` Plugin Manager
- `[102]` Check for Update
- `version.txt` — used by auto-update mechanism
- `example_plugin.py` — full working plugin template
- `SECURITY.md` — responsible vulnerability disclosure policy
- `requirements.txt`

---

## [v8.0.0] — 2026-03-17

### Added
- 20 new modules (46–62, 98–100):
  - HTTP Parameter Fuzzer, JS File Extractor, Form Extractor,
    Cookie Inspector, IP Reputation Check, Path Traversal Tester,
    SQL Error Detector, Subdomain Takeover Checker, TLS Version Checker,
    WhatWeb Lite, Latency Map, Certificate Transparency,
    HTTP Cache Inspector, Security Headers Score, DNS History Lookup,
    Multi-Port Banner Scan, Network Topology, History Viewer, History Clear
- Automatic session history (`~/kooltitool/history/`)
  - JSON per module per day
  - Password modules excluded
- Full English rewrite — zero comments, zero Polish text
- GitHub-ready project structure

---

## [v7.1.1]

### Fixed
- Import errors in several modules

---

## [v7.1.0]

### Added
- 20 new NET modules: Network Interface Stats, ARP Scanner, Banner Grabber,
  HTTP Method Tester, SMTP/FTP/SSH/SNMP Checkers, BGP ASN Lookup,
  IP Range Scanner, Network Speed Test, WiFi SSID Scanner, mDNS Discovery,
  DNS Zone Transfer, Open Redirect, CORS Checker, CDN Detector,
  IPv6 Checker, Port Knock Detector, Shodan IP Lookup

### Improved
- Hash Cracker: multiprocessing pool with initializer pattern (no pickle errors)
- Hash Cracker: built-in dictionary of 100+ common passwords checked first
- Hash Cracker: GPU support via hashcat subprocess and CuPy CUDA kernel
- Hash Cracker: CUDA 13.x auto-detection with graceful fallback

---

## [v7.0.0]

### Added
- Full rewrite — 80 modules across 5 categories
- ASCII logo, color-coded TUI, progress bars
- Multiprocessing Hash Cracker
- GPU hash cracking (hashcat + CuPy CUDA kernel for MD5)
- CUDA version detection

---

## [v6.0.0]

### Added
- 60 modules
- TUI rewrite: ASCII logo, color categories, progress bars
- Category tags: NET / WEB / CRY / SYS / UTL

---

## [v5.0.0]

### Added
- First major release — 25 modules
- Hash generator with NTLM pure-Python fallback
- Multiprocessing brute force cracker

 
