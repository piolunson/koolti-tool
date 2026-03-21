#!/usr/bin/env python3
"""
KOOLTI-TOOL v8.2.1
A terminal-based network & security toolkit.
https://github.com/yourname/koolti-tool

Usage: python koolti_tool.py
Requirements: pip install requests psutil rich
"""

import os, sys, socket, requests, hashlib, random, string
import base64, re, itertools, time, platform, subprocess, tempfile
from datetime import datetime
from multiprocessing import Pool, cpu_count, Value

import json
from pathlib import Path

HISTORY_DIR  = Path.home() / "kooltitool" / "history"
NO_HISTORY   = {46, 47, 50, 51, 70}  # modules that handle passwords

def history_init():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)

def history_log(module_id: int, module_name: str, data: dict):
    if module_id in NO_HISTORY:
        return
    history_init()
    entry = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "module_id": module_id,
        "module_name": module_name,
        "data": data,
    }
    fname = HISTORY_DIR / datetime.now().strftime("%Y-%m-%d") / f"{datetime.now().strftime('%H%M%S')}_{module_id:03d}_{module_name.lower().replace(' ','_')[:30]}.json"
    fname.parent.mkdir(parents=True, exist_ok=True)
    with open(fname, "w", encoding="utf-8") as f:
        json.dump(entry, f, ensure_ascii=False, indent=2, default=str)

def history_capture(fn_name: str):
    import io, contextlib
    buf = io.StringIO()
    return buf


RST  = '\033[0m';  BOLD = '\033[1m';  DIM  = '\033[2m'
ULIN = '\033[4m';  BLK  = '\033[30m'; WHT  = '\033[37m'
LRED = '\033[91m'; LGRN = '\033[92m'; LYLW = '\033[93m'
LBLU = '\033[94m'; LMAG = '\033[95m'; LCYN = '\033[96m'; LWHT = '\033[97m'
BG_BLK='\033[40m'; BG_YLW='\033[43m'; BG_BLU='\033[44m'
BG_MAG='\033[45m'; BG_CYN='\033[46m'; BG_LBLU='\033[104m'; BG_LMAG='\033[105m'
W = RST


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def term_width():
    try:    return os.get_terminal_size().columns
    except: return 80

def cprint(text, end='\n'):
    w = term_width()
    plain = re.sub(r'\033\[[0-9;]*m', '', text)
    print(' ' * max(0, (w - len(plain)) // 2) + text, end=end)

def hline(char='─', color=DIM+WHT, width=None):
    print(f"{color}{char * (width or min(term_width(), 90))}{RST}")

def status_ok(m):   print(f"  {LGRN}✔{RST}  {m}")
def status_warn(m): print(f"  {LYLW}⚠{RST}  {m}")
def status_err(m):  print(f"  {LRED}✘{RST}  {m}")
def status_info(m): print(f"  {LCYN}ℹ{RST}  {m}")

def progress_bar(current, total, width=40, label=''):
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = f"{LGRN}{'█'*filled}{DIM}{'░'*(width-filled)}{RST}"
    print(f"\r  {bar} {LYLW}{pct*100:5.1f}%{RST} {DIM}{label}{RST}", end='', flush=True)

def ask(prompt, default=''):
    val = input(f"\n  {LCYN}❯{RST} {BOLD}{prompt}{RST} {DIM}{'['+default+']' if default else ''}{RST} ").strip()
    return val if val else default

def pause():
    input(f"\n  {DIM}Press Enter to continue...{RST}")

def tag_new(): return f"{BG_LMAG}{BLK}{BOLD} NEW {RST}"
def tag_net(): return f"{BG_BLU}{LWHT} NET {RST}"
def tag_cry(): return f"{BG_YLW}{BLK} CRY {RST}"
def tag_sys(): return f"{BG_BLK}{LWHT} SYS {RST}"
def tag_web(): return f"{BG_MAG}{LWHT} WEB {RST}"
def tag_utl(): return f"{BG_CYN}{BLK} UTL {RST}"

LOGO = f"""
{LCYN}  ██╗  ██╗ ██████╗  ██████╗ ██╗  ████████╗██╗
{LCYN}  ██║ ██╔╝██╔═══██╗██╔═══██╗██║  ╚══██╔══╝██║
{LCYN}  █████╔╝ ██║   ██║██║   ██║██║     ██║   ██║
{LCYN}  ██╔═██╗ ██║   ██║██║   ██║██║     ██║   ██║
{LCYN}  ██║  ██╗╚██████╔╝╚██████╔╝███████╗██║   ██║
{LCYN}  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚══════╝╚═╝   ╚═╝{RST}"""

def logo():
    clear()
    print()
    print(LOGO)
    print()
    cprint(f"{DIM}{'▰'*55}{RST}")
    cprint(f"  {BOLD}{LWHT}v8.0{RST}  {DIM}·{RST}  {LCYN}Real Engine{RST}  {DIM}·{RST}  {LMAG}100+ Modules{RST}  {DIM}·{RST}  {LYLW}{datetime.now().strftime('%Y-%m-%d  %H:%M:%S')}{RST}  ")
    cprint(f"{DIM}{'▰'*55}{RST}")
    print()

CATEGORIES = {
    'NET': ('NETWORK',     LBLU,  tag_net()),
    'WEB': ('WEB / OSINT', LMAG,  tag_web()),
    'CRY': ('CRYPTO',      LYLW,  tag_cry()),
    'SYS': ('SYSTEM',      LGRN,  tag_sys()),
    'UTL': ('UTILITIES',   LCYN,  tag_utl()),
}


def draw_menu():
    w = min(term_width(), 90)
    current_cat = None
    for (nr, name, cat, is_new) in MENU_DATA:
        if cat != current_cat:
            current_cat = cat
            cat_name, cat_color, _ = CATEGORIES[cat]
            print()
            print(f"  {cat_color}{BOLD}  {'─'*3} {cat_name} {'─'*(w - len(cat_name) - 10)}{RST}")
        new_tag = f" {tag_new()}" if is_new else ""
        cat_color = CATEGORIES[cat][1]
        print(f"    {cat_color}{BOLD}[{nr:02d}]{RST}  {LWHT}{name}{RST}{new_tag}")
    print()
    hline('─', DIM, w)
    if _loaded_plugins:
        print()
        print(f"  {LCYN}{BOLD}  {'─'*3} PLUGINS {'─'*20}{RST}")
        for slot, p in _loaded_plugins.items():
            print(f"    {LYLW}{BOLD}[{slot}]{RST}  {LWHT}{p.get('name','Plugin')}{RST}  {DIM}by {p.get('author','?')} v{p.get('version','?')}{RST}")
    print()
    hline('─', DIM, w)
    print(f"  {DIM}[q]{RST}  Quit        {DIM}[h]{RST}  Help        {DIM}[u]{RST}  Check update")

def mod_header(title, subtitle='', icon='◈', color=LCYN):
    w = min(term_width(), 90)
    print()
    hline('═', color, w)
    cprint(f"{color}{BOLD}{icon}  {title.upper()}  {icon}{RST}")
    if subtitle:
        cprint(f"{DIM}{subtitle}{RST}")
    hline('═', color, w)
    print()


def mod_ip_tracker():
    mod_header("IP TRACKER", "Geolocation of an IP address", '🌍', LBLU)
    ip = ask("IP or domain")
    if not ip: return
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=6)
        d = r.json()
        if d.get("status") == "success":
            for k, v in [("Country", f"{d.get('country')} ({d.get('countryCode')})"),
                         ("Region",  d.get('regionName','N/A')),
                         ("City",    d.get('city','N/A')),
                         ("ZIP",     d.get('zip','N/A')),
                         ("ISP",     d.get('isp','N/A')),
                         ("Org",     d.get('org','N/A')),
                         ("AS",      d.get('as','N/A')),
                         ("Coords",  f"{d.get('lat')}, {d.get('lon')}"),
                         ("Timezone",d.get('timezone','N/A'))]:
                print(f"  {LCYN}{BOLD}{k:<14}{RST}  {LWHT}{v}{RST}")
        else:
            status_err(d.get('message','unknown error'))
    except Exception as e:
        status_err(str(e))


def mod_dns_lookup():
    mod_header("DNS LOOKUP", "Resolve domain names", '🔍', LBLU)
    host = ask("Domain / host")
    if not host: return
    try:
        print()
        for res in socket.getaddrinfo(host, 80, socket.AF_INET):
            print(f"  {LGRN}→{RST}  {LWHT}{res[4][0]}{RST}  {DIM}(IPv4){RST}")
        try:
            for res in socket.getaddrinfo(host, 80, socket.AF_INET6):
                print(f"  {LMAG}→{RST}  {LWHT}{res[4][0]}{RST}  {DIM}(IPv6){RST}")
        except: pass
    except Exception as e:
        status_err(str(e))


def mod_port_scanner():
    mod_header("PORT SCANNER", "Scan for open ports", '🔌', LBLU)
    target = ask("IP or domain")
    if not target: return
    ports = {20:"FTP-data",21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",
             53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",
             445:"SMB",465:"SMTPS",993:"IMAPS",995:"POP3S",1433:"MSSQL",
             3306:"MySQL",3389:"RDP",5432:"PostgreSQL",5900:"VNC",
             6379:"Redis",8080:"HTTP-Alt",8443:"HTTPS-Alt",27017:"MongoDB"}
    print(); status_info(f"Scanning {len(ports)} ports on {BOLD}{target}{RST}..."); print()
    found = []
    items = list(ports.items())
    for i, (port, svc) in enumerate(items):
        progress_bar(i, len(items), 40, f"{port}/tcp")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)
        if s.connect_ex((target, port)) == 0: found.append((port, svc))
        s.close()
    progress_bar(len(items), len(items), 40, "Done"); print('\n')
    if found:
        print(f"  {LGRN}{BOLD}{'PORT':<8}{'SERVICE':<15}STATUS{RST}")
        hline('─', DIM, 40)
        for port, svc in found:
            print(f"  {LGRN}{BOLD}{str(port)+'/tcp':<8}{RST}{LWHT}{svc:<15}{RST}{LGRN}OPEN{RST}")
    else:
        status_warn("No open ports found")


def mod_mac_lookup():
    mod_header("MAC LOOKUP", "Identify network card manufacturer", '📡', LBLU)
    mac = ask("MAC (e.g. 00:11:22:33:44:55)")
    if not mac: return
    mac = mac.replace('-', ':').upper()
    try:
        r = requests.get(f"https://api.macvendors.com/{mac}", timeout=6)
        if r.status_code == 200 and len(r.text) > 3:
            status_ok(f"Vendor: {BOLD}{r.text.strip()}{RST}")
        else:
            status_warn("No vendor info found")
    except:
        status_err("API request failed")


def mod_local_network():
    import psutil
    mod_header("LOCAL NETWORK INFO", "Network interfaces on this machine", '🖧', LBLU)
    print()
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    print(f"  {BOLD}{LCYN}{'INTERFACE':<16}{'IP':<18}{'MAC':<20}{'STATUS'}{RST}")
    hline('─', DIM, 70)
    for iface, addresses in addrs.items():
        ip = mac = 'N/A'
        for a in addresses:
            if 'AF_INET' in str(a.family) and a.address != '127.0.0.1': ip = a.address
            if 'AF_LINK' in str(a.family) or 'AF_PACKET' in str(a.family): mac = a.address
        stat = stats.get(iface)
        up = f"{LGRN}UP{RST}" if stat and stat.isup else f"{LRED}DOWN{RST}"
        print(f"  {LBLU}{iface:<16}{RST}{LWHT}{ip:<18}{RST}{DIM}{mac:<20}{RST}{up}")


def mod_ping():
    mod_header("PING TOOL", "Test host reachability", '📶', LBLU)
    host = ask("IP or domain")
    if not host: return
    count = ask("Number of pings", "4")
    try: count = int(count)
    except: count = 4
    param = "-n" if platform.system().lower() == "windows" else "-c"
    print()
    try:
        result = subprocess.run(["ping", param, str(count), host],
                                capture_output=True, text=True, timeout=30)
        col = LGRN if result.returncode == 0 else LRED
        for line in result.stdout.splitlines():
            print(f"  {col}{line}{RST}")
    except Exception as e:
        status_err(str(e))


def mod_subdomain_finder():
    mod_header("SUBDOMAIN FINDER", "Discover subdomains via DNS", '🕸', LBLU)
    domain = ask("Base domain (e.g. example.com)")
    if not domain: return
    subs = ["www","mail","ftp","smtp","pop","imap","webmail","admin","cpanel",
            "vpn","api","dev","test","staging","blog","shop","store","portal",
            "app","mobile","m","ns1","ns2","dns","mx","autodiscover","remote",
            "cdn","static","media","assets","img","git","gitlab","jira",
            "jenkins","ci","forum","wiki","status","docs","help","support"]
    print(); status_info(f"Checking {len(subs)} subdomains for {BOLD}{domain}{RST}..."); print()
    found = []
    for i, sub in enumerate(subs):
        progress_bar(i, len(subs), 40, sub)
        full = f"{sub}.{domain}"
        try:
            ip = socket.gethostbyname(full)
            found.append((full, ip))
        except: pass
    progress_bar(len(subs), len(subs), 40, "Done"); print('\n')
    if found:
        print(f"  {BOLD}{LGRN}{'SUBDOMAIN':<42}{'IP'}{RST}")
        hline('─', DIM, 60)
        for full, ip in found:
            print(f"  {LGRN}✔{RST}  {LWHT}{full:<40}{RST}  {LCYN}{ip}{RST}")
    else:
        status_warn("No subdomains found")


def mod_traceroute():
    mod_header("TRACEROUTE", "Trace packet route to host", '🗺', LBLU)
    host = ask("IP or domain")
    if not host: return
    cmd = ["tracert", host] if platform.system().lower() == "windows" else ["traceroute", "-m", "20", host]
    print()
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for i, line in enumerate(proc.stdout):
            line = line.rstrip()
            if not line: continue
            col = LGRN if i % 2 == 0 else LCYN
            print(f"  {DIM}{i:>3}.{RST}  {col}{line}{RST}")
        proc.wait()
    except FileNotFoundError:
        status_err("traceroute/tracert not available on this system")
    except Exception as e:
        status_err(str(e))


def mod_reverse_ip():
    mod_header("REVERSE IP LOOKUP", "Find hostname from IP", '🔄', LBLU)
    ip = ask("IP address")
    if not ip: return
    try:
        hostname = socket.gethostbyaddr(ip)
        status_ok(f"Hostname: {BOLD}{hostname[0]}{RST}")
        for alias in hostname[1]: status_info(f"Alias: {alias}")
        status_info(f"Addresses: {', '.join(hostname[2])}")
    except socket.herror as e:
        status_warn(f"Not found: {e}")
    except Exception as e:
        status_err(str(e))
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=6)
        d = r.json()
        if d.get("status") == "success":
            print()
            status_info(f"ISP: {d.get('isp')}")
            status_info(f"Org: {d.get('org')}")
            status_info(f"Location: {d.get('city')}, {d.get('country')}")
    except: pass


def mod_geoip():
    mod_header("GEOIP INFO", "Detailed geographic info for an IP", '🌐', LBLU)
    ip = ask("IP or domain (empty = your IP)")
    try:
        url = f"http://ip-api.com/json/{ip}" if ip else "http://ip-api.com/json/"
        r = requests.get(url, timeout=6)
        d = r.json()
        if d.get("status") == "success":
            lat, lon = d.get('lat'), d.get('lon')
            print()
            for k, v in [("Query IP", d.get('query')), ("Country", f"{d.get('country')} [{d.get('countryCode')}]"),
                         ("City", d.get('city')), ("Coords", f"{lat}, {lon}"),
                         ("Timezone", d.get('timezone')), ("ISP", d.get('isp'))]:
                print(f"  {LCYN}{k:<14}{RST}  {LWHT}{v}{RST}")
            print()
            status_info(f"Google Maps: {ULIN}{LBLU}https://maps.google.com/?q={lat},{lon}{RST}")
        else:
            status_err(d.get('message','error'))
    except Exception as e:
        status_err(str(e))


def mod_net_iface_stats():
    import psutil
    mod_header("NETWORK INTERFACE STATS", "Bytes sent/received per interface", '📊', LBLU)
    print()
    io = psutil.net_io_counters(pernic=True)
    print(f"  {BOLD}{LCYN}{'INTERFACE':<18}{'SENT':<16}{'RECEIVED':<16}{'PACKETS OUT':<14}{'PACKETS IN'}{RST}")
    hline('─', DIM, 78)
    for iface, c in io.items():
        def fmt(b): return f"{b/1024**3:.2f}GB" if b>1024**3 else f"{b/1024**2:.1f}MB" if b>1024**2 else f"{b/1024:.1f}KB"
        print(f"  {LBLU}{iface:<18}{RST}{LYLW}{fmt(c.bytes_sent):<16}{RST}{LGRN}{fmt(c.bytes_recv):<16}{RST}"
              f"{DIM}{c.packets_sent:<14}{RST}{DIM}{c.packets_recv}{RST}")


def mod_arp_scanner():
    mod_header("ARP SCANNER", "Discover hosts on local network", '📡', LBLU)
    network = ask("Network prefix (e.g. 192.168.1)", "192.168.1")
    print()
    status_info(f"Scanning {network}.1-254 ...")
    print()
    found = []
    for i in range(1, 255):
        ip = f"{network}.{i}"
        param = "-n" if platform.system().lower() == "windows" else "-c"
        r = subprocess.run(["ping", param, "1", "-w", "100", ip],
                           capture_output=True, text=True)
        if r.returncode == 0:
            try:   hostname = socket.gethostbyaddr(ip)[0]
            except: hostname = "unknown"
            found.append((ip, hostname))
            print(f"  {LGRN}✔{RST}  {LWHT}{ip:<18}{RST}  {DIM}{hostname}{RST}")
    print()
    status_info(f"Found {len(found)} host(s)")


def mod_banner_grabber():
    mod_header("BANNER GRABBER", "Read service banners from open ports", '🏷', LBLU)
    host = ask("Host / IP")
    port = int(ask("Port", "80"))
    if not host: return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((host, port))
        s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
        banner = s.recv(1024).decode('utf-8', errors='replace')
        s.close()
        print()
        for line in banner.splitlines():
            print(f"  {LCYN}{line}{RST}")
    except Exception as e:
        status_err(str(e))


def mod_http_methods():
    mod_header("HTTP METHOD TESTER", "Test which HTTP methods are allowed", '🔧', LBLU)
    url = ask("URL (e.g. https://example.com)")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    methods = ["GET","POST","PUT","DELETE","PATCH","HEAD","OPTIONS","TRACE","CONNECT"]
    print()
    print(f"  {BOLD}{LCYN}{'METHOD':<12}{'STATUS':<10}{'SERVER'}{RST}")
    hline('─', DIM, 50)
    for method in methods:
        try:
            r = requests.request(method, url, timeout=6, allow_redirects=False)
            col = LGRN if r.status_code < 400 else (LYLW if r.status_code < 500 else LRED)
            srv = r.headers.get("Server","")[:25]
            print(f"  {col}{method:<12}{r.status_code:<10}{RST}{DIM}{srv}{RST}")
        except:
            print(f"  {LRED}{method:<12}{'ERR':<10}{RST}")


def mod_smtp_checker():
    mod_header("SMTP CHECKER", "Test SMTP server connectivity", '✉', LBLU)
    host = ask("SMTP host (e.g. smtp.gmail.com)")
    port = int(ask("Port", "587"))
    if not host: return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(8)
        s.connect((host, port))
        banner = s.recv(1024).decode('utf-8', errors='replace').strip()
        status_ok(f"Connected to {host}:{port}")
        status_info(f"Banner: {banner}")
        s.sendall(b"EHLO test\r\n")
        resp = s.recv(2048).decode('utf-8', errors='replace')
        print()
        for line in resp.splitlines():
            print(f"  {DIM}{line}{RST}")
        s.sendall(b"QUIT\r\n")
        s.close()
    except Exception as e:
        status_err(str(e))


def mod_ftp_checker():
    mod_header("FTP CHECKER", "Test FTP server and anonymous login", '📁', LBLU)
    host = ask("FTP host")
    if not host: return
    try:
        import ftplib
        ftp = ftplib.FTP(timeout=8)
        ftp.connect(host, 21)
        status_ok(f"Connected: {ftp.getwelcome()}")
        try:
            ftp.login('anonymous', 'anon@anon.com')
            status_warn("Anonymous login ALLOWED")
            files = ftp.nlst()[:10]
            if files:
                status_info("Files in root:")
                for f in files: print(f"    {DIM}{f}{RST}")
        except ftplib.error_perm:
            status_ok("Anonymous login denied (good)")
        ftp.quit()
    except Exception as e:
        status_err(str(e))


def mod_ssh_checker():
    mod_header("SSH CHECKER", "Test SSH server availability and banner", '🔑', LBLU)
    host = ask("Host")
    port = int(ask("Port", "22"))
    if not host: return
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(8)
        s.connect((host, port))
        banner = s.recv(256).decode('utf-8', errors='replace').strip()
        status_ok(f"SSH port {port} is open")
        status_info(f"Banner: {banner}")
        s.close()
        if "OpenSSH" in banner:
            ver = re.search(r'OpenSSH[_\s]([\d.]+)', banner)
            if ver: status_info(f"OpenSSH version: {ver.group(1)}")
    except Exception as e:
        status_err(str(e))


def mod_snmp_checker():
    mod_header("SNMP CHECKER", "Check SNMP port and community strings", '📟', LBLU)
    host = ask("Host / IP")
    if not host: return
    community_strings = ["public", "private", "community", "admin", "default", "snmp"]
    print()
    status_info(f"Checking SNMP on {host}:161 ...")
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(3)
    found_any = False
    for comm in community_strings:
        try:
            packet = (b"\x30\x26\x02\x01\x00\x04" + bytes([len(comm)]) +
                      comm.encode() + b"\xa0\x19\x02\x04\x00\x00\x00\x01"
                      b"\x02\x01\x00\x02\x01\x00\x30\x0b\x30\x09\x06\x05"
                      b"\x2b\x06\x01\x02\x01\x05\x00")
            s.sendto(packet, (host, 161))
            data, _ = s.recvfrom(1024)
            if data:
                status_warn(f"Community string WORKS: '{comm}'")
                found_any = True
        except socket.timeout:
            print(f"  {DIM}'{comm}' — no response{RST}")
        except Exception as e:
            print(f"  {LRED}'{comm}' — {e}{RST}")
    s.close()
    if not found_any:
        status_ok("No common SNMP community strings responded")


def mod_asn_lookup():
    mod_header("BGP ASN LOOKUP", "Look up Autonomous System Number info", '🌐', LBLU)
    target = ask("IP address or ASN (e.g. AS15169)")
    if not target: return
    try:
        if target.upper().startswith("AS"):
            r = requests.get(f"https://api.bgpview.io/asn/{target[2:]}", timeout=8)
        else:
            r = requests.get(f"https://api.bgpview.io/ip/{target}", timeout=8)
        d = r.json()
        if d.get("status") == "ok":
            data = d.get("data", {})
            print()
            if "asn" in data:
                print(f"  {LCYN}ASN          {RST}  {LWHT}AS{data.get('asn')}{RST}")
                print(f"  {LCYN}Name         {RST}  {LWHT}{data.get('name','N/A')}{RST}")
                print(f"  {LCYN}Country      {RST}  {LWHT}{data.get('country_code','N/A')}{RST}")
                print(f"  {LCYN}Description  {RST}  {LWHT}{data.get('description_short','N/A')}{RST}")
            else:
                for prefix in data.get("prefixes", [])[:5]:
                    asn = prefix.get("asn", {})
                    print(f"  {LGRN}→{RST}  {LWHT}{prefix.get('prefix',''):<20}{RST}  AS{asn.get('asn','')}  {DIM}{asn.get('name','')}{RST}")
        else:
            status_err("No data found")
    except Exception as e:
        status_err(str(e))


def mod_ip_range_scanner():
    mod_header("IP RANGE SCANNER", "Ping scan a CIDR range", '🔭', LBLU)
    try:
        import ipaddress
    except ImportError:
        status_err("ipaddress module not available"); return
    cidr = ask("CIDR range (e.g. 192.168.1.0/24)")
    if not cidr: return
    try:
        net = ipaddress.IPv4Network(cidr, strict=False)
        hosts = list(net.hosts())
        if len(hosts) > 256:
            status_warn(f"{len(hosts)} hosts — limiting to first 256")
            hosts = hosts[:256]
        print()
        status_info(f"Scanning {len(hosts)} hosts...")
        print()
        found = []
        param = "-n" if platform.system().lower() == "windows" else "-c"
        for i, ip in enumerate(hosts):
            progress_bar(i, len(hosts), 40, str(ip))
            r = subprocess.run(["ping", param, "1", "-w", "200", str(ip)],
                               capture_output=True, text=True)
            if r.returncode == 0:
                found.append(str(ip))
        progress_bar(len(hosts), len(hosts), 40, "Done"); print('\n')
        if found:
            for ip in found:
                print(f"  {LGRN}✔{RST}  {LWHT}{ip}{RST}")
        status_info(f"Online: {len(found)} / {len(hosts)}")
    except ValueError as e:
        status_err(str(e))


def mod_speed_test():
    mod_header("NETWORK SPEED TEST", "Measure download speed", '⚡', LBLU)
    print()
    status_info("Downloading 10MB test file from Cloudflare...")
    url = "https://speed.cloudflare.com/__down?bytes=10000000"
    try:
        start = time.time()
        r = requests.get(url, stream=True, timeout=30)
        total = 0
        for chunk in r.iter_content(chunk_size=65536):
            total += len(chunk)
            elapsed = time.time() - start
            speed_mbps = (total * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
            progress_bar(min(total, 10_000_000), 10_000_000, 35, f"{speed_mbps:.1f} Mbps")
        elapsed = time.time() - start
        print()
        speed_mbps = (total * 8) / (elapsed * 1_000_000)
        speed_mbs  = total / (elapsed * 1_000_000)
        print()
        status_ok(f"Download speed: {BOLD}{LGRN}{speed_mbps:.2f} Mbps{RST}  ({speed_mbs:.2f} MB/s)")
        status_info(f"Downloaded: {total/1_000_000:.1f} MB in {elapsed:.2f}s")
    except Exception as e:
        status_err(str(e))


def mod_wifi_ssid_scanner():
    mod_header("WIFI SSID SCANNER", "List nearby WiFi networks", '📡', LBLU)
    print()
    try:
        if platform.system().lower() == "windows":
            out = subprocess.check_output(["netsh", "wlan", "show", "networks", "mode=Bssid"],
                                          text=True, errors='replace')
            networks = re.findall(r'SSID\s+\d+\s+:\s+(.+)', out)
            signals  = re.findall(r'Signal\s+:\s+(\d+)%', out)
            auths    = re.findall(r'Authentication\s+:\s+(.+)', out)
            print(f"  {BOLD}{LCYN}{'SSID':<35}{'SIGNAL':<10}{'AUTH'}{RST}")
            hline('─', DIM, 65)
            for i, ssid in enumerate(networks):
                sig = signals[i] if i < len(signals) else "N/A"
                auth = auths[i].strip() if i < len(auths) else "N/A"
                sig_int = int(sig) if sig.isdigit() else 0
                col = LGRN if sig_int > 70 else (LYLW if sig_int > 40 else LRED)
                print(f"  {LWHT}{ssid.strip():<35}{RST}{col}{sig+'%':<10}{RST}{DIM}{auth}{RST}")
        else:
            out = subprocess.check_output(["nmcli", "-f", "SSID,SIGNAL,SECURITY", "dev", "wifi"],
                                          text=True, errors='replace')
            print(out)
    except Exception as e:
        status_err(str(e))


def mod_mdns_discovery():
    mod_header("mDNS / BONJOUR DISCOVERY", "Discover local network services", '🔊', LBLU)
    print()
    status_info("Listening for mDNS announcements (5 seconds)...")
    MDNS_ADDR = "224.0.0.251"
    MDNS_PORT = 5353
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(('', MDNS_PORT))
        mreq = socket.inet_aton(MDNS_ADDR) + socket.inet_aton('0.0.0.0')
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.settimeout(5)
        seen = set()
        end_time = time.time() + 5
        while time.time() < end_time:
            try:
                data, addr = sock.recvfrom(4096)
                ip = addr[0]
                if ip not in seen:
                    seen.add(ip)
                    print(f"  {LGRN}✔{RST}  {LWHT}{ip}{RST}")
            except socket.timeout:
                break
        sock.close()
        status_info(f"Found {len(seen)} device(s)")
    except Exception as e:
        status_err(f"mDNS error: {e}  (try running as administrator)")


def mod_dns_zone_transfer():
    mod_header("DNS ZONE TRANSFER", "Attempt AXFR DNS zone transfer", '📋', LBLU)
    domain = ask("Domain (e.g. example.com)")
    if not domain: return
    print()
    try:
        ns_records = socket.getaddrinfo(domain, 53)
        nameservers = [r[4][0] for r in ns_records]
        status_info(f"Trying nameservers: {nameservers}")
        for ns in nameservers[:3]:
            print(f"\n  {LCYN}NS: {ns}{RST}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(8)
                s.connect((ns, 53))
                query = (b"\x00\x1d\x00\x00\x01\x00\x00\x01\x00\x00\x00\x00\x00\x00" +
                         b"".join(bytes([len(p)]) + p.encode() for p in domain.split('.')) +
                         b"\x00\x00\xfc\x00\x01")
                s.send(len(query).to_bytes(2,'big') + query)
                resp = s.recv(4096)
                s.close()
                if len(resp) > 50:
                    status_warn(f"Zone transfer MAY be allowed — {len(resp)} bytes received")
                else:
                    status_ok("Zone transfer denied")
            except Exception as ex:
                status_err(str(ex))
    except Exception as e:
        status_err(str(e))


def mod_open_redirect():
    mod_header("OPEN REDIRECT TESTER", "Test for open redirect vulnerabilities", '↪', LBLU)
    url = ask("Base URL (e.g. https://example.com/redirect?url=)")
    if not url: return
    payloads = [
        "https://evil.com", "//evil.com", "///evil.com",
        "https:evil.com", "/%09/evil.com", "/\\evil.com",
        "https://example.com@evil.com", "https://evil%2ecom"
    ]
    print()
    print(f"  {BOLD}{LCYN}{'PAYLOAD':<35}{'STATUS':<10}{'LOCATION'}{RST}")
    hline('─', DIM, 70)
    for payload in payloads:
        try:
            r = requests.get(url + payload, timeout=6, allow_redirects=False)
            loc = r.headers.get("Location", "")
            if "evil.com" in loc.lower():
                col = LRED
                note = "VULNERABLE"
            elif loc:
                col = LYLW
                note = loc[:25]
            else:
                col = LGRN
                note = "No redirect"
            short = payload[:33]
            print(f"  {col}{short:<35}{r.status_code:<10}{note}{RST}")
        except Exception as e:
            print(f"  {LRED}{payload[:35]:<35}{'ERR':<10}{str(e)[:25]}{RST}")


def mod_cors_checker():
    mod_header("CORS POLICY CHECKER", "Check Cross-Origin Resource Sharing policy", '🔒', LBLU)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    origins = ["https://evil.com", "null", "https://example.com",
               "http://localhost", "https://attacker.io"]
    print()
    print(f"  {BOLD}{LCYN}{'ORIGIN':<35}{'ACAO HEADER':<35}{'ACAC'}{RST}")
    hline('─', DIM, 80)
    for origin in origins:
        try:
            r = requests.options(url, headers={"Origin": origin, "Access-Control-Request-Method": "GET"}, timeout=6)
            acao = r.headers.get("Access-Control-Allow-Origin", "not set")
            acac = r.headers.get("Access-Control-Allow-Credentials", "false")
            if acao == "*" or acao == origin:
                col = LYLW if acao == "*" else LRED
            else:
                col = LGRN
            print(f"  {col}{origin:<35}{acao[:33]:<35}{acac}{RST}")
        except Exception as e:
            print(f"  {LRED}{origin:<35}{'ERR':<35}{str(e)[:15]}{RST}")


def mod_cdn_detector():
    mod_header("CDN DETECTOR", "Detect if site uses a CDN", '☁', LBLU)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    cdn_signatures = {
        "Cloudflare":  ["cf-ray","cloudflare","cf-cache-status"],
        "Fastly":      ["x-fastly","fastly","x-cache: HIT, HIT"],
        "Akamai":      ["x-check-cacheable","akamai","x-akamai"],
        "AWS CloudFront": ["x-amz-cf-id","amazoncloudfront","cloudfront"],
        "Azure CDN":   ["x-ec-custom-error","azure","x-ms-request-id"],
        "MaxCDN":      ["x-hw","netdna"],
        "BunnyCDN":    ["bunny","bunnycdn"],
        "KeyCDN":      ["x-edge-location","keycdn"],
        "Sucuri":      ["x-sucuri-id","sucuri"],
    }
    try:
        r = requests.get(url, timeout=8)
        headers_str = str(dict(r.headers)).lower()
        print()
        detected = []
        for cdn, sigs in cdn_signatures.items():
            if any(s.lower() in headers_str for s in sigs):
                detected.append(cdn)
                status_ok(f"Detected: {BOLD}{cdn}{RST}")
        if not detected:
            status_warn("No CDN detected")
        print()
        for k, v in r.headers.items():
            if any(x in k.lower() for x in ["cf-","x-cache","via","x-amz","fastly"]):
                print(f"  {LCYN}{k:<30}{RST}  {DIM}{v[:50]}{RST}")
    except Exception as e:
        status_err(str(e))


def mod_ipv6_checker():
    mod_header("IPv6 CHECKER", "Check IPv6 connectivity and address info", '6️⃣', LBLU)
    host = ask("Domain or IPv6 address")
    if not host: return
    print()
    try:
        results = socket.getaddrinfo(host, 80, socket.AF_INET6)
        status_ok(f"IPv6 supported for {host}")
        for r in results:
            print(f"  {LGRN}→{RST}  {LWHT}{r[4][0]}{RST}")
    except socket.gaierror:
        status_warn(f"No IPv6 records for {host}")
    try:
        s6 = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s6.connect(("2606:4700:4700::1111", 80))
        local_ipv6 = s6.getsockname()[0]
        s6.close()
        status_ok(f"Your IPv6: {BOLD}{local_ipv6}{RST}")
    except:
        status_warn("No IPv6 connectivity detected on this machine")


def mod_shodan_lookup():
    mod_header("SHODAN IP LOOKUP", "Query Shodan API for host intel", '🔭', LBLU)
    ip = ask("IP address")
    api_key = ask("Shodan API key (free at shodan.io)")
    if not ip or not api_key: return
    try:
        r = requests.get(f"https://api.shodan.io/shodan/host/{ip}?key={api_key}", timeout=10)
        if r.status_code == 200:
            d = r.json()
            print()
            print(f"  {LCYN}IP           {RST}  {LWHT}{d.get('ip_str','N/A')}{RST}")
            print(f"  {LCYN}Org          {RST}  {LWHT}{d.get('org','N/A')}{RST}")
            print(f"  {LCYN}ISP          {RST}  {LWHT}{d.get('isp','N/A')}{RST}")
            print(f"  {LCYN}Country      {RST}  {LWHT}{d.get('country_name','N/A')}{RST}")
            print(f"  {LCYN}OS           {RST}  {LWHT}{d.get('os','Unknown')}{RST}")
            print(f"  {LCYN}Hostnames    {RST}  {LWHT}{', '.join(d.get('hostnames',[]))}{RST}")
            print(f"  {LCYN}Open Ports   {RST}  {LYLW}{', '.join(map(str, d.get('ports',[])))}{RST}")
            tags = d.get("tags", [])
            if tags:
                print(f"  {LCYN}Tags         {RST}  {LMAG}{', '.join(tags)}{RST}")
            vulns = d.get("vulns", {})
            if vulns:
                print(f"\n  {LRED}{BOLD}Vulnerabilities:{RST}")
                for cve in list(vulns.keys())[:8]:
                    print(f"    {LRED}• {cve}{RST}")
        elif r.status_code == 401:
            status_err("Invalid API key")
        elif r.status_code == 404:
            status_warn("No Shodan data for this IP")
        else:
            status_err(f"HTTP {r.status_code}")
    except Exception as e:
        status_err(str(e))


def mod_admin_finder():
    mod_header("ADMIN FINDER", "Search for admin panels", '🔐', LMAG)
    url = ask("Site URL")
    if not url: return
    if not url.startswith(('http://','https://')): url = 'https://' + url
    paths = ['/admin','/administrator','/admin/login','/adminpanel','/admin_area',
             '/login','/login.php','/signin','/auth','/auth/login','/user/login',
             '/account/login','/panel','/dashboard','/wp-admin','/wp-login.php',
             '/phpmyadmin','/pma','/cpanel','/backend','/manager','/console',
             '/joomla/administrator','/drupal/user/login','/typo3/login']
    headers = {'User-Agent': 'Mozilla/5.0'}
    print(); status_info(f"Scanning {len(paths)} paths on {BOLD}{url}{RST}"); print()
    try:
        main_r = requests.get(url, timeout=7, headers=headers)
        main_content = main_r.text.lower()[:3000]
    except: main_content = ""
    strong, redirects, forbidden = [], [], []
    for i, path in enumerate(paths):
        progress_bar(i, len(paths), 38, path)
        try:
            r = requests.get(url+path, timeout=5, headers=headers, allow_redirects=True)
            content = r.text.lower()[:2500]
            login_kw = ["login","password","username","sign in","dashboard","admin area"]
            is_real = any(kw in content for kw in login_kw)
            is_fake = len(r.text) < 2200 or (main_content and main_content in content)
            if r.status_code == 200 and is_real and not is_fake: strong.append((url+path, r.status_code))
            elif r.status_code in (301,302): redirects.append((url+path, r.status_code, r.url))
            elif r.status_code == 403: forbidden.append((url+path, r.status_code))
        except: pass
    progress_bar(len(paths), len(paths), 38, "Done"); print('\n')
    if strong:
        print(f"  {LGRN}{BOLD}LIKELY PANELS:{RST}")
        for u, c in strong: print(f"  {LGRN}[+]{RST} {LWHT}{u}{RST} {DIM}({c}){RST}")
    if redirects:
        print(f"\n  {LYLW}{BOLD}REDIRECTS:{RST}")
        for u, c, dest in redirects: print(f"  {LYLW}[→]{RST} {u} {DIM}→{RST} {dest}")
    if forbidden:
        print(f"\n  {LCYN}{BOLD}FORBIDDEN (403):{RST}")
        for u, c in forbidden: print(f"  {LCYN}[~]{RST} {u}")
    if not any([strong, redirects, forbidden]):
        status_warn("No admin panels found")


def mod_cms_detector():
    mod_header("CMS DETECTOR", "Detect content management system", '📦', LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "http://" + url
    cms_data = {
        "WordPress":   ["wp-content","wp-includes","wp-json"],
        "Joomla":      ["/administrator/","Joomla!"],
        "Drupal":      ["Drupal.settings","/sites/default/"],
        "Ghost":       ["ghost-sdk","ghost-frontend"],
        "PrestaShop":  ["prestashop"],
        "Shopify":     ["cdn.shopify.com"],
        "Wix":         ["wix.com","_wix"],
        "Squarespace": ["squarespace"],
        "Magento":     ["Magento","mage/cookies"],
        "TYPO3":       ["typo3/"],
        "Webflow":     ["webflow"],
    }
    try:
        r = requests.get(url, timeout=10)
        html = r.text.lower()
        print()
        detected = [name for name, markers in cms_data.items() if any(m.lower() in html for m in markers)]
        if detected:
            for cms in detected: status_ok(f"Detected: {BOLD}{LGRN}{cms}{RST}")
        else:
            status_warn("No known CMS detected")
    except Exception as e:
        status_err(str(e))


def mod_waf_detector():
    mod_header("WAF DETECTOR", "Detect Web Application Firewall", '🛡', LMAG)
    target = ask("URL")
    if not target: return
    if not target.startswith("http"): target = "http://" + target
    try:
        r = requests.get(target, params={"test": "<script>alert(1)</script>"}, timeout=10)
        h = r.headers
        server = h.get("Server","Unknown")
        sigs = {"cloudflare":"Cloudflare","aws-waf":"AWS WAF","sucuri":"Sucuri",
                "mod_security":"ModSecurity","akamai":"Akamai","imperva":"Imperva"}
        waf = next((name for sig, name in sigs.items()
                    if sig in server.lower() or sig in str(h).lower()), "None detected")
        print()
        print(f"  {LCYN}Target       {RST}  {LWHT}{target}{RST}")
        print(f"  {LCYN}Status       {RST}  {LWHT}{r.status_code}{RST}")
        print(f"  {LCYN}Server       {RST}  {LWHT}{server}{RST}")
        col = LRED if waf != "None detected" else LGRN
        print(f"  {LCYN}WAF          {RST}  {col}{BOLD}{waf}{RST}")
    except Exception as e:
        status_err(str(e))


def mod_header_inspector():
    mod_header("HTTP HEADER INSPECTOR", "Analyze HTTP headers and security", '🔎', LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    security_headers = ["strict-transport-security","content-security-policy",
                        "x-frame-options","x-xss-protection","x-content-type-options",
                        "referrer-policy","permissions-policy"]
    try:
        r = requests.get(url, timeout=8)
        print()
        print(f"  {BOLD}{LCYN}{'HEADER':<35}{'VALUE'}{RST}")
        hline('─', DIM, 75)
        for k, v in r.headers.items():
            kc = LGRN if k.lower() in security_headers else LCYN
            print(f"  {kc}{k:<35}{RST}{LWHT}{v[:45]+'...' if len(v)>45 else v}{RST}")
        print()
        missing = [h for h in security_headers if h not in [k.lower() for k in r.headers]]
        if missing:
            print(f"  {LRED}{BOLD}Missing security headers:{RST}")
            for m in missing: status_err(m)
        else:
            status_ok("All key security headers present")
    except Exception as e:
        status_err(str(e))


def mod_link_extractor():
    mod_header("LINK EXTRACTOR", "Extract all links from a page", '🔗', LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "http://" + url
    try:
        r = requests.get(url, timeout=10)
        links = list(set(re.findall(r'href=["\'](http[s]?://.*?)["\']', r.text)))[:30]
        print()
        print(f"  {BOLD}{LCYN}{'#':<4}{'URL'}{RST}")
        hline('─', DIM, 60)
        for i, link in enumerate(links, 1):
            print(f"  {LYLW}{i:<4}{RST}{LBLU}{link[:70]}{RST}")
        status_info(f"Found {len(links)} unique links")
    except Exception as e:
        status_err(str(e))


def mod_whois():
    mod_header("WHOIS LOOKUP", "Domain registration information", '📋', LMAG)
    domain = ask("Domain (e.g. example.com)")
    if not domain: return
    try:
        r = requests.get(f"https://rdap.org/domain/{domain}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            print()
            print(f"  {LCYN}Domain       {RST}  {LWHT}{domain.upper()}{RST}")
            print(f"  {LCYN}Registrar    {RST}  {LWHT}{data.get('port43','N/A')}{RST}")
            for event in data.get('events', []):
                print(f"  {LYLW}📅 {event.get('eventAction',''):<20}{RST}  {DIM}{event.get('eventDate','')[:10]}{RST}")
        else:
            status_warn("No domain info found")
    except:
        status_err("RDAP connection failed")


def mod_robots_checker():
    mod_header("ROBOTS.TXT & SITEMAP", "Analyze robots.txt and sitemap", '🤖', LMAG)
    url = ask("Site URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    url = url.rstrip('/')
    headers = {'User-Agent': 'Mozilla/5.0'}
    print()
    try:
        r = requests.get(f"{url}/robots.txt", timeout=8, headers=headers)
        if r.status_code == 200:
            status_ok("robots.txt found")
            print()
            for line in r.text.splitlines()[:25]:
                if line.lower().startswith("disallow"): print(f"  {LRED}{line}{RST}")
                elif line.lower().startswith("allow"):   print(f"  {LGRN}{line}{RST}")
                elif line.lower().startswith("sitemap"): print(f"  {LCYN}{line}{RST}")
                elif line.strip():                       print(f"  {DIM}{line}{RST}")
        else:
            status_warn(f"robots.txt not found ({r.status_code})")
    except Exception as e:
        status_err(str(e))
    print()
    for path in ["/sitemap.xml", "/sitemap_index.xml"]:
        try:
            r = requests.get(f"{url}{path}", timeout=8, headers=headers)
            if r.status_code == 200:
                urls_found = re.findall(r'<loc>(.*?)</loc>', r.text)
                status_ok(f"Sitemap found: {path}  ({len(urls_found)} URLs)")
                for u in urls_found[:5]: print(f"    {LBLU}→{RST} {u}")
                break
        except: pass
    else:
        status_warn("No sitemap found")


def mod_url_scanner():
    mod_header("URL SCANNER", "Analyze URL — redirects, SSL, server", '🔬', LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'}, allow_redirects=True)
        print()
        if r.history:
            print(f"  {LCYN}{BOLD}Redirect chain:{RST}")
            for resp in r.history: print(f"    {LYLW}{resp.status_code}{RST}  {DIM}→{RST}  {resp.url}")
            print(f"    {LGRN}{r.status_code}{RST}  {DIM}→{RST}  {r.url}  {LGRN}(FINAL){RST}")
        else:
            status_ok("No redirects")
        print()
        print(f"  {LCYN}Status       {RST}  {LWHT}{r.status_code}{RST}")
        print(f"  {LCYN}Size         {RST}  {LWHT}{len(r.content)/1024:.1f} KB{RST}")
        print(f"  {LCYN}Content-Type {RST}  {LWHT}{r.headers.get('Content-Type','N/A')}{RST}")
        print(f"  {LCYN}Server       {RST}  {LWHT}{r.headers.get('Server','N/A')}{RST}")
        ssl_s = f"{LGRN}✔ HTTPS active{RST}" if r.url.startswith("https://") else f"{LRED}✘ No HTTPS{RST}"
        print(f"  {LCYN}SSL/TLS      {RST}  {ssl_s}")
    except Exception as e:
        status_err(str(e))


def mod_email_validator():
    mod_header("EMAIL VALIDATOR", "Verify email address format and domain", '✉', LMAG)
    email = ask("Email address")
    if not email: return
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    print()
    if not re.match(pattern, email): status_err("Invalid email format"); return
    status_ok("Format valid")
    domain = email.split('@')[1]
    try:
        ip = socket.gethostbyname(domain)
        status_ok(f"Domain exists → {ip}")
    except:
        status_err("Domain does not respond"); return
    disposable = ["mailinator.com","tempmail.com","guerrillamail.com","yopmail.com","trashmail.com"]
    if domain.lower() in disposable: status_warn("Known disposable email domain!")
    else: status_ok("Domain not in disposable list")


def mod_wayback():
    mod_header("WAYBACK MACHINE", "Check archived versions of a site", '📜', LMAG)
    url = ask("URL (e.g. example.com)")
    if not url: return
    try:
        r = requests.get(f"http://archive.org/wayback/available?url={url}", timeout=10)
        snap = r.json().get("archived_snapshots", {}).get("closest", {})
        if snap.get("available"):
            print()
            status_ok("Archive available")
            print(f"\n  {LCYN}Status       {RST}  {LWHT}{snap.get('status')}{RST}")
            print(f"  {LCYN}Timestamp    {RST}  {LWHT}{snap.get('timestamp')}{RST}")
            print(f"  {LCYN}Archive URL  {RST}  {LBLU}{ULIN}{snap.get('url')}{RST}")
            r2 = requests.get(f"http://web.archive.org/cdx/search/cdx?url={url}&output=json&limit=5&fl=timestamp,statuscode", timeout=10)
            if r2.status_code == 200:
                records = r2.json()[1:]
                if records:
                    print(f"\n  {BOLD}Recent snapshots:{RST}")
                    for rec in records:
                        ts, sc = rec[0], rec[1]
                        dt = f"{ts[:4]}-{ts[4:6]}-{ts[6:8]} {ts[8:10]}:{ts[10:12]}"
                        print(f"    {DIM}{dt}{RST}  {LGRN if sc=='200' else LYLW}[{sc}]{RST}")
        else:
            status_warn("No archived versions found")
    except Exception as e:
        status_err(str(e))


def mod_tech_stack():
    mod_header("TECH STACK DETECTOR", "Detect technologies used by a site", '⚙', LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    techs = {
        "React":           ["react","reactjs","react.production"],
        "Vue.js":          ["vue.js","vue.min.js"],
        "Angular":         ["angular","ng-version"],
        "jQuery":          ["jquery","jquery.min.js"],
        "Bootstrap":       ["bootstrap.min.css","bootstrap.css"],
        "Tailwind CSS":    ["tailwindcss"],
        "Nginx":           ["nginx"],
        "Apache":          ["apache"],
        "Cloudflare":      ["cloudflare","cf-ray"],
        "Google Analytics":["google-analytics","gtag"],
        "WordPress":       ["wp-content","wp-includes"],
        "PHP":             ["x-powered-by: php"],
        "Node.js":         ["x-powered-by: express"],
        "ASP.NET":         ["x-aspnet","asp.net"],
    }
    try:
        r = requests.get(url, timeout=10, headers={'User-Agent':'Mozilla/5.0'})
        combined = r.text.lower() + str(dict(r.headers)).lower()
        print()
        found = [tech for tech, markers in techs.items() if any(m.lower() in combined for m in markers)]
        if found:
            for t in found: status_ok(f"{BOLD}{t}{RST}")
        else:
            status_warn("No known technologies detected")
    except Exception as e:
        status_err(str(e))


def mod_broken_links():
    mod_header("BROKEN LINK CHECKER", "Find dead links on a page", '💔', LMAG)
    url = ask("Page URL")
    if not url: return
    if not url.startswith("http"): url = "http://" + url
    try:
        res = requests.get(url, timeout=10)
        links = list(set(re.findall(r'href=["\'](http[s]?://[^"\']+)["\']', res.text)))[:20]
        print(); status_info(f"Checking {len(links)} links..."); print()
        broken = []
        for i, link in enumerate(links):
            progress_bar(i, len(links), 35)
            try:
                r = requests.head(link, timeout=5, allow_redirects=True)
                if r.status_code >= 400: broken.append((link, r.status_code))
            except: broken.append((link, "TIMEOUT"))
        progress_bar(len(links), len(links), 35); print('\n')
        if broken:
            print(f"  {LRED}{BOLD}Broken links:{RST}")
            for link, code in broken: print(f"  {LRED}[{code}]{RST}  {link[:65]}")
        else:
            status_ok("All checked links are working")
    except Exception as e:
        status_err(str(e))


def mod_ssl_info():
    mod_header("SSL CERTIFICATE INFO", "SSL/TLS certificate details", '🔒', LMAG)
    host = ask("Domain (e.g. google.com)")
    if not host: return
    try:
        import ssl
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
            s.settimeout(8); s.connect((host, 443))
            cert = s.getpeercert()
        print()
        subject = dict(x[0] for x in cert.get('subject', []))
        issuer  = dict(x[0] for x in cert.get('issuer', []))
        print(f"  {LCYN}Subject CN   {RST}  {LWHT}{subject.get('commonName','N/A')}{RST}")
        print(f"  {LCYN}Org          {RST}  {LWHT}{subject.get('organizationName','N/A')}{RST}")
        print(f"  {LCYN}Issuer       {RST}  {LWHT}{issuer.get('organizationName','N/A')}{RST}")
        print(f"  {LCYN}Valid from   {RST}  {LWHT}{cert.get('notBefore','N/A')}{RST}")
        print(f"  {LCYN}Valid until  {RST}  {LWHT}{cert.get('notAfter','N/A')}{RST}")
        sans = cert.get('subjectAltName', [])
        if sans:
            print(f"\n  {LCYN}SANs:{RST}")
            for _, val in sans[:8]: print(f"    {DIM}→{RST} {LWHT}{val}{RST}")
        try:
            exp = datetime.strptime(cert.get('notAfter',''), "%b %d %H:%M:%S %Y %Z")
            days = (exp - datetime.utcnow()).days
            print()
            if days > 30:   status_ok(f"Certificate valid for {days} more days")
            elif days > 0:  status_warn(f"Certificate expires in {days} days!")
            else:           status_err("Certificate EXPIRED!")
        except: pass
    except Exception as e:
        status_err(str(e))


def mod_bulk_status():
    mod_header("HTTP STATUS BULK CHECKER", "Check status of multiple URLs", '📊', LMAG)
    print(f"  {DIM}Enter URLs one per line. Empty line = done.{RST}\n")
    urls = []
    while True:
        u = input(f"  {LCYN}URL {len(urls)+1}:{RST} ").strip()
        if not u: break
        if not u.startswith("http"): u = "https://" + u
        urls.append(u)
    if not urls: return
    print()
    print(f"  {BOLD}{LCYN}{'STATUS':<8}{'URL'}{RST}")
    hline('─', DIM, 70)
    for u in urls:
        try:
            r = requests.head(u, timeout=6, allow_redirects=True)
            c = r.status_code
            col = LGRN if c < 300 else (LYLW if c < 400 else LRED)
            print(f"  {col}{BOLD}{c:<8}{RST}{u}")
        except:
            print(f"  {LRED}{'ERR':<8}{RST}{u}")


def mod_dork_generator():
    mod_header("GOOGLE DORK GENERATOR", "Generate Google search operators", '🎯', LMAG)
    domain  = ask("Target domain (optional)")
    keyword = ask("Keyword (optional)")
    print()
    dorks = [
        f'site:{domain} admin'           if domain else 'inurl:admin login',
        f'site:{domain} login'           if domain else 'inurl:login',
        f'site:{domain} filetype:pdf'    if domain else 'filetype:pdf confidential',
        f'site:{domain} filetype:xls'    if domain else 'filetype:xls password',
        f'site:{domain} inurl:backup'    if domain else 'inurl:backup filetype:zip',
        f'site:{domain} intext:password' if domain else 'intext:"index of /" passwords',
        f'site:{domain} inurl:config'    if domain else 'inurl:config.php',
        f'site:{domain} ext:sql'         if domain else 'ext:sql "phpMyAdmin"',
        f'site:{domain} inurl:wp-admin'  if domain else 'inurl:wp-admin',
        f'"{keyword}" site:{domain}'     if (keyword and domain) else f'"{keyword}"' if keyword else 'intitle:"Index of"',
    ]
    for i, dork in enumerate(dorks, 1):
        print(f"  {LYLW}{i:>2}.{RST}  {LWHT}{dork}{RST}")
        print(f"       {DIM}https://google.com/search?q={requests.utils.quote(dork)[:60]}...{RST}\n")


def _ntlm_hash(text):
    data = text.encode('utf-16le')
    try: return hashlib.new('md4', data).hexdigest()
    except ValueError: pass
    try:
        from Crypto.Hash import MD4
        return MD4.new(data).hexdigest()
    except ImportError: pass
    import struct
    def F(x,y,z): return (x&y)|((~x)&z)
    def G(x,y,z): return (x&y)|(x&z)|(y&z)
    def H(x,y,z): return x^y^z
    def rol(v,s): return ((v<<s)|(v>>(32-s)))&0xFFFFFFFF
    msg = bytearray(data); orig_len = len(msg)*8; msg.append(0x80)
    while len(msg)%64 != 56: msg.append(0)
    msg += struct.pack('<Q', orig_len)
    a,b,c,d = 0x67452301,0xEFCDAB89,0x98BADCFE,0x10325476
    for i in range(0, len(msg), 64):
        X = list(struct.unpack('<16I', msg[i:i+64])); aa,bb,cc,dd = a,b,c,d
        for j in [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15]:
            a=(a+F(b,c,d)+X[j])&0xFFFFFFFF; a=rol(a,[3,7,11,19][j%4]); a,b,c,d=d,a,b,c
        for j in [0,4,8,12,1,5,9,13,2,6,10,14,3,7,11,15]:
            a=(a+G(b,c,d)+X[j]+0x5A827999)&0xFFFFFFFF; a=rol(a,[3,5,9,13][j%4]); a,b,c,d=d,a,b,c
        for j in [0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15]:
            a=(a+H(b,c,d)+X[j]+0x6ED9EBA1)&0xFFFFFFFF; a=rol(a,[3,9,11,15][j%4]); a,b,c,d=d,a,b,c
        a=(a+aa)&0xFFFFFFFF; b=(b+bb)&0xFFFFFFFF; c=(c+cc)&0xFFFFFFFF; d=(d+dd)&0xFFFFFFFF
    return struct.pack('<4I',a,b,c,d).hex()


def mod_hash_generator():
    mod_header("HASH GENERATOR", "Generate cryptographic hashes", '🧮', LYLW)
    text = ask("Text to hash")
    if not text: return
    print()
    for name, val in [
        ("MD5",     hashlib.md5(text.encode()).hexdigest()),
        ("SHA-1",   hashlib.sha1(text.encode()).hexdigest()),
        ("SHA-256", hashlib.sha256(text.encode()).hexdigest()),
        ("SHA-384", hashlib.sha384(text.encode()).hexdigest()),
        ("SHA-512", hashlib.sha512(text.encode()).hexdigest()),
        ("SHA3-256",hashlib.sha3_256(text.encode()).hexdigest()),
        ("NTLM",    _ntlm_hash(text)),
    ]:
        print(f"  {LCYN}{name:<10}{RST}  {LYLW}{val}{RST}")


_HC_STOP = _HC_TARGET = _HC_ALGO = None

def _hc_init(stop, target, algo_id):
    global _HC_STOP, _HC_TARGET, _HC_ALGO
    _HC_STOP = stop; _HC_TARGET = target; _HC_ALGO = algo_id

def _hc_worker(args):
    cs_b, length, start_i, chunk = args
    if _HC_STOP.value: return None, 0
    base = len(cs_b); limit = base**length; checked = 0
    for i in range(start_i, min(start_i+chunk, limit)):
        if checked % 5000 == 0 and _HC_STOP.value: return None, checked
        n, c = i, []
        for _ in range(length): c.append(cs_b[n%base]); n //= base
        w = bytes(reversed(c)); a = _HC_ALGO
        if   a==1: h = hashlib.md5(w).digest()
        elif a==2: h = hashlib.sha1(w).digest()
        elif a==3: h = hashlib.sha256(w).digest()
        elif a==4: h = hashlib.sha512(w).digest()
        else:      h = bytes.fromhex(_ntlm_hash(w.decode('utf-8','replace')))
        if h == _HC_TARGET: return w.decode('utf-8','replace'), checked
        checked += 1
    return None, checked

_MD5_CUDA = r"""
#include <stdint.h>
#include <string.h>
__constant__ uint32_t K[64]={
  0xd76aa478,0xe8c7b756,0x242070db,0xc1bdceee,0xf57c0faf,0x4787c62a,0xa8304613,0xfd469501,
  0x698098d8,0x8b44f7af,0xffff5bb1,0x895cd7be,0x6b901122,0xfd987193,0xa679438e,0x49b40821,
  0xf61e2562,0xc040b340,0x265e5a51,0xe9b6c7aa,0xd62f105d,0x02441453,0xd8a1e681,0xe7d3fbc8,
  0x21e1cde6,0xc33707d4,0xf4d50d87,0x455a14ed,0xa9e3e905,0xfcefa3f8,0x676f02d9,0x8d2a4c8a,
  0xfffa3942,0x8771f681,0x6d9d6122,0xfde5380c,0xa4beea44,0x4bdecfa9,0xf6bb4b60,0xbebfbc70,
  0x289b7ec6,0xeaa127fa,0xd4ef3085,0x04881d05,0xd9d4d039,0xe6db99e5,0x1fa27cf8,0xc4ac5665,
  0xf4292244,0x432aff97,0xab9423a7,0xfc93a039,0x655b59c3,0x8f0ccc92,0xffeff47d,0x85845dd1,
  0x6fa87e4f,0xfe2ce6e0,0xa3014314,0x4e0811a1,0xf7537e82,0xbd3af235,0x2ad7d2bb,0xeb86d391};
__constant__ uint32_t S[64]={
  7,12,17,22,7,12,17,22,7,12,17,22,7,12,17,22,
  5, 9,14,20,5, 9,14,20,5, 9,14,20,5, 9,14,20,
  4,11,16,23,4,11,16,23,4,11,16,23,4,11,16,23,
  6,10,15,21,6,10,15,21,6,10,15,21,6,10,15,21};
__device__ void md5(const uint8_t*msg,uint32_t len,uint32_t*out){
  uint8_t buf[64]; memset(buf,0,64); memcpy(buf,msg,len);
  buf[len]=0x80; uint64_t bl=(uint64_t)len*8; memcpy(buf+56,&bl,8);
  uint32_t a0=0x67452301,b0=0xefcdab89,c0=0x98badcfe,d0=0x10325476;
  uint32_t*M=(uint32_t*)buf,a=a0,b=b0,c=c0,d=d0,f,g;
  #pragma unroll
  for(int i=0;i<64;i++){
    if(i<16){f=(b&c)|(~b&d);g=i;}
    else if(i<32){f=(d&b)|(~d&c);g=(5*i+1)%16;}
    else if(i<48){f=b^c^d;g=(3*i+5)%16;}
    else{f=c^(b|~d);g=(7*i)%16;}
    f=f+a+K[i]+M[g]; a=d; d=c; c=b;
    b=b+((f<<S[i])|(f>>(32-S[i])));}
  out[0]=a0+a;out[1]=b0+b;out[2]=c0+c;out[3]=d0+d;}
extern "C" __global__ void brute_md5(
  const uint8_t*cs,int cs_len,int pw_len,
  long long offset,long long batch,long long total,
  const uint32_t*tgt,long long*res){
  long long tid=(long long)blockIdx.x*blockDim.x+threadIdx.x;
  long long idx=offset+tid;
  if(tid>=batch||idx>=total)return;
  uint8_t pw[16]; long long n=idx;
  for(int i=pw_len-1;i>=0;i--){pw[i]=cs[n%cs_len];n/=cs_len;}
  uint32_t h[4]; md5(pw,pw_len,h);
  if(h[0]==tgt[0]&&h[1]==tgt[1]&&h[2]==tgt[2]&&h[3]==tgt[3])
    atomicExch((unsigned long long*)res,(unsigned long long)idx);}
"""

def _find_hashcat():
    for c in ['hashcat','hashcat.exe',r'C:\hashcat\hashcat.exe',
              os.path.expanduser('~/hashcat/hashcat.bin'),
              '/usr/bin/hashcat','/usr/local/bin/hashcat']:
        try:
            subprocess.check_output([c,'--version'], stderr=subprocess.DEVNULL)
            return c
        except: pass
    return None

def mod_hash_cracker():
    mod_header("HASH CRACKER", "CPU multiprocessing + GPU (hashcat / CuPy)", '🔨', LYLW)
    ALGO_NAMES = {'1':'MD5','2':'SHA-1','3':'SHA-256','4':'SHA-512','5':'NTLM'}
    ALGO_LENS  = {'1':32,   '2':40,    '3':64,       '4':128,      '5':32}
    HC_MODE    = {'1':'0',  '2':'100', '3':'1400',   '4':'1700',   '5':'1000'}
    hc = _find_hashcat()
    try:
        import cupy as cp; cp.cuda.Device(0).use(); cupy_ok = True
    except: cupy_ok = False
    hc_tag  = f"{LGRN}✔{RST}" if hc      else f"{LRED}✘  →  winget install hashcat{RST}"
    cup_tag = f"{LGRN}✔{RST}" if cupy_ok else f"{LRED}✘  →  pip install cupy-cuda12x{RST}"
    print(f"\n  {BOLD}Engine:{RST}")
    print(f"    {LYLW}[1]{RST} CPU multiprocessing  {LGRN}✔ always available{RST}")
    print(f"    {LYLW}[2]{RST} GPU hashcat          {hc_tag}")
    print(f"    {LYLW}[3]{RST} GPU CuPy CUDA        {cup_tag}  {DIM}(MD5 only){RST}")
    engine = ask("Engine (1/2/3)", "2" if hc else "3" if cupy_ok else "1")
    print(f"\n  {DIM}[1] MD5  [2] SHA-1  [3] SHA-256  [4] SHA-512  [5] NTLM{RST}\n")
    algo = ask("Algorithm (1-5)", "1")
    if algo not in ALGO_NAMES: status_err("Invalid choice"); return
    algo_id = int(algo)
    h_str = ask(f"{ALGO_NAMES[algo]} hash").strip().lower()
    if len(h_str) != ALGO_LENS.get(algo,32): status_warn(f"Hash length mismatch (expected {ALGO_LENS[algo]})")
    try:    target_bytes = bytes.fromhex(h_str)
    except: status_err("Invalid hex characters in hash"); return
    max_dl = int(ask("Max password length", "8")); max_dl = max(1,min(12,max_dl))
    print(f"\n  {DIM}[1] digits  [2] +lower  [3] +UPPER  [4] +special{RST}")
    cs = ask("Charset (1-4)", "2")
    CHARSETS = {'1':string.digits,'2':string.digits+string.ascii_lowercase,
                '3':string.digits+string.ascii_letters,'4':string.printable[:-6]}
    charset = CHARSETS.get(cs, CHARSETS['2']); cores = cpu_count()

    def oblicz(word):
        enc = word.encode('utf-8','replace')
        if algo_id==1: return hashlib.md5(enc).digest()
        if algo_id==2: return hashlib.sha1(enc).digest()
        if algo_id==3: return hashlib.sha256(enc).digest()
        if algo_id==4: return hashlib.sha512(enc).digest()
        return bytes.fromhex(_ntlm_hash(word))

    def _bar(done, total, rate, label=''):
        pct = min(100.0, done/total*100) if total>0 else 0.0
        filled = int(32*pct/100); col = LGRN if pct>80 else (LYLW if pct>40 else LCYN)
        bar = f"{col}{'█'*filled}{DIM}{'░'*(32-filled)}{RST}"
        r_s = (f"{rate/1e9:.2f}G/s" if rate>=1e9 else f"{rate/1e6:.1f}M/s" if rate>=1e6 else f"{rate/1e3:.0f}K/s")
        print(f"\r  {bar}  {pct:5.1f}%  {BOLD}{r_s}{RST}{'  '+DIM+label+RST if label else ''}   ", end='', flush=True)

    def _wynik(word, elapsed, total, method=''):
        rate = total/elapsed if elapsed>0 else 0
        r_s = (f"{rate/1e9:.2f}G H/s" if rate>=1e9 else f"{rate/1e6:.1f}M H/s" if rate>=1e6 else f"{rate/1e3:.1f}K H/s")
        print(f"\n\n  {LGRN}{'═'*46}{RST}")
        print(f"  {LGRN}{BOLD}  ⚡  PASSWORD FOUND!{RST}")
        print(f"  {LGRN}{'═'*46}{RST}")
        print(f"  {LCYN}Password    {RST}  {LYLW}{BOLD}{word}{RST}")
        print(f"  {LCYN}Algorithm   {RST}  {BOLD}{ALGO_NAMES[algo]}{RST}")
        if method: print(f"  {LCYN}Method      {RST}  {BOLD}{method}{RST}")
        print(f"  {LCYN}Time        {RST}  {BOLD}{elapsed:.3f}s{RST}")
        print(f"  {LCYN}Checked     {RST}  {BOLD}{total:,}{RST}")
        print(f"  {LCYN}Speed       {RST}  {LGRN}{BOLD}{r_s}{RST}")
        print(f"  {LGRN}{'═'*46}{RST}")

    TOP = ["123456","password","123456789","12345","qwerty","abc123","000000","1234",
           "password1","admin","letmein","welcome","monkey","dragon","master","login",
           "pass","shadow","sunshine","princess","iloveyou","superman","batman","1111",
           "111111","asdfgh","zxcvbnm","696969","654321","777777","888888","pass123",
           "test123","root","toor","admin123","changeme","default","guest","secret","test",
           "password12","password123","admin12","admin123","user123","pass12","test1",
           "test12","test123","root123","qwerty1","qwerty12","1q2w3e","1q2w3e4r",
           "passw0rd","p@ssword","pa$$word","adm1n","r00t","aaaaaa","abcdef","asd123",
           "samsung","router","cisco","netgear","1234567","1234567890","qwe123","mustang"]
    print(f"\n  {LCYN}[0]{RST} Dictionary: {len(TOP)} common passwords...")
    t0 = time.time(); total_checked = 0; found = None
    for w in TOP:
        total_checked += 1
        if oblicz(w) == target_bytes: found = w; break
    if found: _wynik(found, time.time()-t0, total_checked, "Built-in dictionary"); return
    status_ok(f"Not in dictionary ({time.time()-t0:.3f}s)")

    if engine == '2':
        if not hc:
            status_err("hashcat not found"); status_info("Windows: winget install hashcat"); engine = '1'
        else:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write(h_str + '\n'); hfile = f.name
            ofile = hfile + '.out'
            custom = ''.join(sorted(set(charset)))[:95]
            cmd = [hc,'-m',HC_MODE[algo],'-a','3','-o',ofile,'--outfile-format','2',
                   '--potfile-disable','--quiet','--status','--status-timer','1',
                   '--increment','--increment-min','1','--increment-max',str(max_dl),
                   '-1',custom,hfile,'?1'*max_dl]
            status_info(f"Running hashcat GPU — {ALGO_NAMES[algo]} — max len {max_dl}")
            t_hc = time.time()
            try:
                proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
                for line in proc.stdout:
                    line = line.strip()
                    if 'H/s' in line:
                        nums = re.findall(r'[\d.]+\s*[GMK]H/s', line)
                        if nums: print(f"\r  {LMAG}⚡ GPU: {BOLD}{nums[0]}{RST}              ", end='', flush=True)
                proc.wait()
            except KeyboardInterrupt:
                proc.terminate(); print(f"\n  {LYLW}Interrupted{RST}")
            elapsed_hc = time.time() - t_hc; print()
            found_hc = None
            if os.path.exists(ofile):
                with open(ofile) as f: raw = f.read().strip()
                if raw: found_hc = raw.split(':',1)[-1]
            for fp in [hfile, ofile]:
                try: os.unlink(fp)
                except: pass
            if found_hc: _wynik(found_hc, elapsed_hc, 0, "hashcat GPU")
            else: status_err(f"Password not found"); status_info(f"Time: {elapsed_hc:.1f}s")
            return

    if engine == '3':
        if not cupy_ok:
            status_err("CuPy not installed"); status_info("pip install cupy-cuda12x"); engine = '1'
        elif algo_id != 1:
            status_warn("CuPy kernel supports MD5 only — falling back to CPU"); engine = '1'
        else:
            import cupy as cp
            dev = cp.cuda.Device()
            gpu = cp.cuda.runtime.getDeviceProperties(dev.id)['name'].decode()
            status_info("GPU: " + BOLD + gpu + RST)
            _cv = cp.cuda.runtime.runtimeGetVersion() // 1000
            if _cv >= 13:
                status_err(f"CUDA {_cv}.x not yet supported by CuPy (max CUDA 12.x)")
                status_info("Install hashcat instead: winget install hashcat  → engine [2]")
                engine = '1'
                status_warn("Falling back to CPU multiprocessing")
            else:
                print("  Compiling CUDA kernel (~5s first run)...")
                try:
                    mod_cu = cp.RawModule(code=_MD5_CUDA)
                    kern   = mod_cu.get_function('brute_md5')
                    status_ok("Kernel ready!")
                except Exception as e:
                    err_s = str(e).lower()
                    if 'nvrtc' in err_s: status_err("nvrtc.dll missing"); status_info("pip install nvidia-cuda-nvrtc-cu12")
                    elif 'cuda_path' in err_s or 'auto-detect' in err_s:
                        status_err("CuPy cannot find CUDA Toolkit")
                        import glob as _g
                        hits = sorted(_g.glob(r'C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v*'), reverse=True)
                        if hits:
                            os.environ['CUDA_PATH'] = hits[0]; status_ok("Found CUDA: " + hits[0])
                            try:
                                mod_cu = cp.RawModule(code=_MD5_CUDA)
                                kern = mod_cu.get_function('brute_md5')
                                status_ok("Kernel compiled!"); engine = '3_ok'
                            except Exception as e2: status_err("Still failing: " + str(e2))
                        else: status_info("Set CUDA_PATH manually or use hashcat (engine [2])")
                    else: status_err("CUDA error: " + str(e))
                    if engine == '3': engine = '1'; status_warn("Falling back to CPU")

            if engine in ('3','3_ok'):
                tgt_u32 = cp.array([int.from_bytes(target_bytes[i:i+4],'little') for i in range(0,16,4)], dtype=cp.uint32)
                cs_gpu = cp.array(list(charset.encode()), dtype=cp.uint8); cs_len = len(charset)
                THREADS = 256; BATCH = 4_000_000
                t_gpu = time.time(); total_gpu = 0; found_gpu = None
                for length in range(1, max_dl+1):
                    if found_gpu: break
                    total_c = cs_len**length
                    status_info(f"Length {BOLD}{length}{RST}  →  {total_c:,} combinations  [GPU]")
                    res = cp.array([-1], dtype=cp.int64); offset = 0
                    while offset < total_c:
                        batch = min(BATCH, total_c-offset); blocks = (batch+THREADS-1)//THREADS
                        kern((blocks,),(THREADS,),(cs_gpu,cp.int32(cs_len),cp.int32(length),
                             cp.int64(offset),cp.int64(batch),cp.int64(total_c),tgt_u32,res))
                        cp.cuda.Stream.null.synchronize()
                        total_gpu += batch; offset += batch
                        _bar(offset, total_c, total_gpu/max(0.001,time.time()-t_gpu), "GPU")
                        if int(res[0]) >= 0:
                            n, pw = int(res[0]), []
                            for _ in range(length): pw.append(charset[n%cs_len]); n//=cs_len
                            found_gpu = ''.join(reversed(pw)); break
                    print()
                    if found_gpu: break
                elapsed_gpu = time.time()-t_gpu
                if found_gpu: _wynik(found_gpu, elapsed_gpu, total_gpu, f"CuPy CUDA ({gpu})")
                else: status_err(f"Not found (length 1-{max_dl})")
                return

    status_info(f"CPU multiprocessing  |  {BOLD}{cores}{RST} cores  |  charset {BOLD}{len(charset)}{RST} chars")
    cs_idx = int(cs) if cs in '1234' else 2
    stages = [("Digits only", string.digits),
              ("Digits + lowercase", string.digits+string.ascii_lowercase),
              ("Digits + lower + UPPER", string.digits+string.ascii_letters),
              ("Full charset", string.printable[:-6])][:cs_idx]
    g_start = time.time(); stop_flag = Value('b', 0)
    for snum, (sname, sch) in enumerate(stages, 1):
        if found: break
        sch_b = sch.encode(); base = len(sch_b); stop_flag.value = 0
        print(f"\n  {LCYN}[{snum}/{len(stages)}]{RST} {sname} {DIM}({base} chars){RST}")
        for length in range(1, max_dl+1):
            if found: break
            total_this = base**length; status_info(f"Length {BOLD}{length}{RST}  →  {total_this:,}")
            last_t = time.time()
            if length <= 3 or cores <= 1:
                checked = 0
                for combo in itertools.product(sch, repeat=length):
                    word = ''.join(combo); total_checked += 1; checked += 1
                    if oblicz(word) == target_bytes: found = word; break
                    if time.time()-last_t > 0.4:
                        _bar(checked, total_this, total_checked/max(0.001,time.time()-g_start)); last_t = time.time()
            else:
                chunk = max(5000, total_this//(cores*12))
                jobs  = [(sch_b,length,i,chunk) for i in range(0,total_this,chunk)]
                checked_len = 0
                try:
                    with Pool(cores, initializer=_hc_init, initargs=(stop_flag,target_bytes,algo_id)) as pool:
                        for result, cnt in pool.imap_unordered(_hc_worker, jobs, chunksize=2):
                            checked_len += cnt; total_checked += cnt
                            if result and not found:
                                found = result; stop_flag.value = 1; pool.terminate(); break
                            if time.time()-last_t > 0.35:
                                _bar(checked_len, total_this, total_checked/max(0.001,time.time()-g_start)); last_t = time.time()
                except Exception:
                    for combo in itertools.product(sch, repeat=length):
                        word = ''.join(combo); total_checked += 1
                        if oblicz(word) == target_bytes: found = word; break
            _bar(total_this, total_this, total_checked/max(0.001,time.time()-g_start)); print()
            if found: break
    elapsed = time.time()-g_start
    if found: _wynik(found, elapsed, total_checked, "CPU multiprocessing")
    else:
        print(); status_err(f"Password not found (length 1-{max_dl})")
        rate = total_checked/elapsed if elapsed>0 else 0
        status_info(f"Checked: {total_checked:,}  |  Time: {elapsed:.1f}s  |  {rate/1e6:.2f}M H/s")


def mod_base64():
    mod_header("BASE64 TOOL", "Encode and decode Base64", '🔡', LYLW)
    print(f"  {LYLW}[1]{RST} Encode    {LYLW}[2]{RST} Decode\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    try:
        if mode == "1": result = base64.b64encode(text.encode()).decode(); label = "Encoded"
        else:           result = base64.b64decode(text.strip().encode()).decode(); label = "Decoded"
        print(); status_ok(f"{label}: {BOLD}{LYLW}{result}{RST}")
    except Exception as e: status_err(str(e))


def mod_caesar():
    mod_header("CAESAR CIPHER", "Classic substitution cipher", '🏛', LYLW)
    print(f"  {LYLW}[1]{RST} Encrypt    {LYLW}[2]{RST} Decrypt    {LYLW}[3]{RST} Brute force\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    def caesar(t, s): return ''.join(chr((ord(c)-(ord('A') if c.isupper() else ord('a'))+s)%26+(ord('A') if c.isupper() else ord('a'))) if c.isalpha() else c for c in t)
    if mode in ("1","2"):
        shift = int(ask("Shift (1-25)", "3"))
        result = caesar(text, shift if mode=="1" else -shift)
        print(); status_ok(f"{'Encrypted' if mode=='1' else 'Decrypted'}: {BOLD}{LYLW}{result}{RST}")
    else:
        print(); print(f"  {BOLD}{LCYN}{'N':<4}{'RESULT'}{RST}"); hline('─', DIM, 60)
        for i in range(1, 26): print(f"  {LYLW}{i:<4}{RST}{LWHT}{caesar(text, i)}{RST}")


def mod_password_checker():
    mod_header("PASSWORD STRENGTH", "Evaluate password security", '💪', LYLW)
    password = ask("Password to check")
    if not password: return
    score = 0; tips = []
    if len(password) >= 8:  score += 1
    else: tips.append("At least 8 characters required")
    if len(password) >= 12: score += 1
    if len(password) >= 16: score += 1
    if any(c.isupper() for c in password): score += 1
    else: tips.append("Add uppercase letters (A-Z)")
    if any(c.islower() for c in password): score += 1
    else: tips.append("Add lowercase letters (a-z)")
    if any(c.isdigit() for c in password): score += 1
    else: tips.append("Add digits (0-9)")
    if any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password): score += 1
    else: tips.append("Add special characters (!@#...)")
    if password.lower() in ["password","qwerty","123456","admin","letmein"]:
        score = 1; tips.append("This is one of the most common passwords!")
    levels = [(2,"VERY WEAK",LRED),(4,"WEAK",LRED),(5,"MEDIUM",LYLW),(6,"STRONG",LGRN),(99,"VERY STRONG",LGRN)]
    label, color = "UNKNOWN", WHT
    for threshold, lbl, col in levels:
        if score <= threshold: label, color = lbl, col; break
    print()
    print(f"  {BOLD}Score:{RST}  {color}{BOLD}{label}{RST}  {DIM}({score}/8 pts){RST}")
    bar = f"{color}{'█'*score}{DIM}{'░'*(8-score)}{RST}"
    print(f"  {bar}")
    if tips: print(); [status_warn(t) for t in tips]


def mod_wordlist():
    mod_header("WORDLIST GENERATOR", "Generate password wordlist from base word", '📝', LYLW)
    base = ask("Base word")
    if not base: return
    variants = {base, base.upper(), base.lower(), base.capitalize()}
    for x in ['123','1234','12345','2024','2025','!','@','#','!!','pl','pass','admin']:
        variants.add(base+x); variants.add(x+base)
    variants.add(base.translate(str.maketrans('aeios','43105')))
    while len(variants) < 100:
        los = random.choice(list(variants))
        if random.random() > 0.5: los += random.choice(['!','@','#','1'])
        variants.add(los[:20])
    lista = sorted(list(variants))[:100]
    try:
        with open('wordlist.txt', 'w', encoding='utf-8') as f: f.write('\n'.join(lista))
        status_ok(f"Saved {len(lista)} passwords to {BOLD}wordlist.txt{RST}")
    except Exception as e: status_err(str(e))
    print()
    for i, w in enumerate(lista[:12], 1): print(f"  {DIM}{i:>3}.{RST}  {LYLW}{w}{RST}")
    if len(lista) > 12: print(f"  {DIM}  ... and {len(lista)-12} more{RST}")


def mod_rot13():
    mod_header("ROT13 CIPHER", "ROT13 substitution cipher", '🔀', LYLW)
    text = ask("Text")
    if not text: return
    result = text.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
    print(); status_ok(f"Result: {BOLD}{LYLW}{result}{RST}")
    status_info("ROT13 is symmetric — apply again to decode")


def mod_xor_cipher():
    mod_header("XOR CIPHER", "XOR encryption with key", '⊕', LYLW)
    text = ask("Text"); key = ask("Key")
    if not text or not key: return
    result = bytes(ord(t)^ord(key[i%len(key)]) for i, t in enumerate(text))
    print()
    print(f"  {LCYN}HEX    {RST}  {LYLW}{result.hex()}{RST}")
    print(f"  {LCYN}Base64 {RST}  {LYLW}{base64.b64encode(result).decode()}{RST}")
    status_info("XOR with the same key decrypts the text")


def mod_morse():
    mod_header("MORSE CODE", "Encode and decode Morse code", '•−', LYLW)
    MORSE = {'A':'.-','B':'-...','C':'-.-.','D':'-..','E':'.','F':'..-.','G':'--.','H':'....','I':'..','J':'.---','K':'-.-','L':'.-..','M':'--','N':'-.','O':'---','P':'.--.','Q':'--.-','R':'.-.','S':'...','T':'-','U':'..-','V':'...-','W':'.--','X':'-..-','Y':'-.--','Z':'--..','0':'-----','1':'.----','2':'..---','3':'...--','4':'....-','5':'.....','6':'-....','7':'--...','8':'---..','9':'----.',' ':'/'}
    REV = {v:k for k,v in MORSE.items()}
    print(f"  {LYLW}[1]{RST} Text → Morse    {LYLW}[2]{RST} Morse → Text\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    print()
    if mode == "1":
        result = ' '.join(MORSE.get(c.upper(),'?') for c in text)
        status_ok(f"Morse: {BOLD}{LYLW}{result}{RST}")
    else:
        result = ''.join(REV.get(code,'?') for word in text.split(' / ') for code in word.split()) + ' '
        status_ok(f"Text: {BOLD}{LYLW}{result.strip()}{RST}")


def mod_binary():
    mod_header("BINARY CONVERTER", "Convert text to/from binary", '01', LYLW)
    print(f"  {LYLW}[1]{RST} Text → Binary    {LYLW}[2]{RST} Binary → Text\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    print()
    if mode == "1":
        result = ' '.join(format(ord(c),'08b') for c in text)
        status_ok(f"Binary: {LYLW}{result[:80]}{'...' if len(result)>80 else ''}{RST}")
    else:
        try:
            result = ''.join(chr(int(b,2)) for b in text.split())
            status_ok(f"Text: {BOLD}{LYLW}{result}{RST}")
        except: status_err("Invalid binary format")


def mod_hex_converter():
    mod_header("HEX CONVERTER", "Convert text to/from hexadecimal", '0x', LYLW)
    print(f"  {LYLW}[1]{RST} Text → HEX    {LYLW}[2]{RST} HEX → Text\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    print()
    if mode == "1":
        result = text.encode().hex()
        status_ok(f"HEX: {LYLW}{' '.join(result[i:i+2] for i in range(0,len(result),2))[:80]}{RST}")
    else:
        try:
            result = bytes.fromhex(text.replace(' ','')).decode('utf-8','replace')
            status_ok(f"Text: {BOLD}{LYLW}{result}{RST}")
        except: status_err("Invalid hex format")


def mod_url_encoder():
    mod_header("URL ENCODER/DECODER", "Encode and decode URL strings", '🔗', LYLW)
    from urllib.parse import quote, unquote
    print(f"  {LYLW}[1]{RST} Encode    {LYLW}[2]{RST} Decode\n")
    mode = ask("Mode", "1"); text = ask("Text")
    if not text: return
    print()
    if mode == "1": status_ok(f"Encoded: {LYLW}{quote(text, safe='')}{RST}")
    else:           status_ok(f"Decoded: {LYLW}{unquote(text)}{RST}")


def mod_jwt_decoder():
    mod_header("JWT DECODER", "Decode JSON Web Tokens", '🎫', LYLW)
    import json
    token = ask("Paste JWT token")
    if not token: return
    parts = token.split('.')
    if len(parts) != 3: status_err("Invalid JWT format (expected 3 parts separated by '.')"); return
    def decode_part(p):
        pad = 4 - len(p)%4
        if pad != 4: p += '='*pad
        try: return json.loads(base64.urlsafe_b64decode(p).decode())
        except: return None
    print()
    header  = decode_part(parts[0])
    payload = decode_part(parts[1])
    if header:
        print(f"  {LCYN}{BOLD}HEADER:{RST}")
        for k, v in header.items(): print(f"    {LYLW}{k:<12}{RST}  {LWHT}{v}{RST}")
    print()
    if payload:
        print(f"  {LCYN}{BOLD}PAYLOAD:{RST}")
        for k, v in payload.items():
            if k in ('exp','iat','nbf'):
                try:    dt_str = datetime.utcfromtimestamp(v).strftime('%Y-%m-%d %H:%M:%S UTC')
                except: dt_str = ""
                print(f"    {LYLW}{k:<12}{RST}  {LWHT}{v}{RST}  {DIM}({dt_str}){RST}")
            else: print(f"    {LYLW}{k:<12}{RST}  {LWHT}{str(v)[:60]}{RST}")
    print(); status_warn("Signature is NOT verified — decode only!")


def mod_sys_info():
    import psutil
    mod_header("SYSTEM INFO", "Operating system and hardware info", '💻', LGRN)
    print()
    cpu_pct = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory(); disk = psutil.disk_usage('/')
    for k, v in [("OS", platform.system()), ("Version", platform.version()[:50]),
                 ("Arch", platform.machine()), ("CPU", platform.processor()[:50]),
                 ("Node", platform.node()), ("Python", platform.python_version())]:
        print(f"  {LGRN}{k:<16}{RST}  {LWHT}{v}{RST}")
    print()
    def usage_bar(pct, w=25):
        filled = int(w*pct/100); col = LGRN if pct<60 else (LYLW if pct<85 else LRED)
        return f"{col}{'█'*filled}{DIM}{'░'*(w-filled)}{RST}  {col}{pct:.1f}%{RST}"
    print(f"  {BOLD}{LGRN}CPU{RST}             {usage_bar(cpu_pct)}")
    print(f"  {BOLD}{LGRN}RAM{RST}             {usage_bar(ram.percent)}  {DIM}({ram.used//1024**2}/{ram.total//1024**2} MB){RST}")
    print(f"  {BOLD}{LGRN}Disk{RST}            {usage_bar(disk.percent)}  {DIM}({disk.used//1024**3}/{disk.total//1024**3} GB){RST}")


def mod_file_analyzer():
    mod_header("FILE ANALYZER", "Analyze a local file", '📄', LGRN)
    path = ask("File path")
    if not path or not os.path.exists(path): status_err("File not found"); return
    stats = os.stat(path); size_kb = round(stats.st_size/1024, 2)
    print()
    print(f"  {LGRN}Name         {RST}  {LWHT}{os.path.basename(path)}{RST}")
    print(f"  {LGRN}Size         {RST}  {LWHT}{size_kb} KB  ({stats.st_size} B){RST}")
    print(f"  {LGRN}Created      {RST}  {LWHT}{time.ctime(stats.st_ctime)}{RST}")
    print(f"  {LGRN}Modified     {RST}  {LWHT}{time.ctime(stats.st_mtime)}{RST}")
    print(f"  {LGRN}Permissions  {RST}  {LWHT}{oct(stats.st_mode)[-3:]}{RST}")
    tag = f"{LRED}EXECUTABLE{RST}" if os.access(path, os.X_OK) else f"{DIM}normal{RST}"
    print(f"  {LGRN}Type         {RST}  {tag}")
    try:
        with open(path, 'rb') as f: data = f.read()
        print(); print(f"  {LGRN}MD5    {RST}  {DIM}{hashlib.md5(data).hexdigest()}{RST}")
        print(f"  {LGRN}SHA-256{RST}  {DIM}{hashlib.sha256(data).hexdigest()}{RST}")
    except: pass


def mod_wifi_passwords():
    mod_header("WIFI PASSWORDS", "Read saved WiFi passwords (Windows only)", '📶', LGRN)
    if platform.system().lower() != "windows": status_warn("This module works on Windows only"); return
    try:
        data = subprocess.check_output(['netsh','wlan','show','profiles']).decode('utf-8',errors='ignore').split('\n')
        profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
        print(); print(f"  {BOLD}{LGRN}{'SSID':<30}{'PASSWORD'}{RST}"); hline('─', DIM, 60)
        for name in profiles:
            try:
                results = subprocess.check_output(['netsh','wlan','show','profile',name,'key=clear']).decode('utf-8',errors='ignore').split('\n')
                password = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
                print(f"  {LWHT}{name:<30}{RST}{LYLW}{password[0] if password else DIM+'(none/open)'+RST}{RST}")
            except: print(f"  {LWHT}{name:<30}{RST}{LRED}read error{RST}")
    except Exception as e: status_err(str(e))


def mod_processes():
    import psutil
    mod_header("PROCESS VIEWER", "Active system processes", '⚡', LGRN)
    print()
    procs = []
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent','status']):
        try: procs.append(p.info)
        except: pass
    procs.sort(key=lambda x: x.get('memory_percent') or 0, reverse=True)
    print(f"  {BOLD}{LCYN}{'PID':<8}{'NAME':<28}{'CPU%':<8}{'MEM%':<8}STATUS{RST}")
    hline('─', DIM, 65)
    for p in procs[:20]:
        cpu = p.get('cpu_percent') or 0; mem = p.get('memory_percent') or 0
        col = LRED if cpu>50 else (LYLW if cpu>10 else LWHT)
        print(f"  {DIM}{p.get('pid',''):<8}{RST}{col}{str(p.get('name',''))[:26]:<28}{RST}"
              f"{LYLW}{cpu:<8.1f}{RST}{LGRN}{mem:<8.1f}{RST}{DIM}{p.get('status','')}{RST}")
    status_info(f"Showing top 20 of {len(procs)} processes (by RAM)")


def mod_disk_usage():
    import psutil
    mod_header("DISK USAGE", "Disk partitions and usage", '💾', LGRN)
    print(); print(f"  {BOLD}{LCYN}{'PARTITION':<20}{'TOTAL':<12}{'USED':<12}{'FREE':<12}{'%'}{RST}"); hline('─', DIM, 65)
    for part in psutil.disk_partitions():
        try:
            u = psutil.disk_usage(part.mountpoint)
            col = LRED if u.percent>85 else (LYLW if u.percent>60 else LGRN)
            print(f"  {LWHT}{part.mountpoint[:18]:<20}{RST}{DIM}{u.total//1024**3:.1f}G{'':6}{RST}"
                  f"{LYLW}{u.used//1024**3:.1f}G{'':6}{RST}{LGRN}{u.free//1024**3:.1f}G{'':6}{RST}"
                  f"{col}{BOLD}{u.percent:.1f}%{RST}")
        except: pass


def mod_env_vars():
    mod_header("ENVIRONMENT VARIABLES", "System environment variables", '🌿', LGRN)
    print()
    filter_kw = ask("Filter (empty = show all)").upper()
    print()
    count = 0
    for k, v in sorted(os.environ.items()):
        if filter_kw and filter_kw not in k.upper(): continue
        print(f"  {LGRN}{k:<28}{RST}  {DIM}{v[:60]+'...' if len(v)>60 else v}{RST}"); count += 1
    print(); status_info(f"Showing {count} variables")


def mod_open_connections():
    import psutil
    mod_header("OPEN CONNECTIONS", "Active network connections", '🔌', LGRN)
    print(); print(f"  {BOLD}{LCYN}{'PROTO':<8}{'LOCAL':<26}{'REMOTE':<26}STATUS{RST}"); hline('─', DIM, 72)
    for c in psutil.net_connections(kind='inet')[:30]:
        laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else '-'
        raddr = f"{c.raddr.ip}:{c.raddr.port}" if c.raddr else '-'
        proto = 'TCP' if c.type.name == 'SOCK_STREAM' else 'UDP'
        col = LGRN if c.status == 'ESTABLISHED' else DIM
        print(f"  {LBLU}{proto:<8}{RST}{LWHT}{laddr:<26}{RST}{DIM}{raddr:<26}{RST}{col}{c.status}{RST}")


def mod_file_hash_verifier():
    mod_header("FILE HASH VERIFIER", "Verify file integrity", '✅', LGRN)
    path = ask("File path")
    if not path or not os.path.exists(path): status_err("File not found"); return
    expected = ask("Expected hash (optional)").strip().lower()
    try:
        with open(path, 'rb') as f: data = f.read()
        md5 = hashlib.md5(data).hexdigest(); sha1 = hashlib.sha1(data).hexdigest(); sha256 = hashlib.sha256(data).hexdigest()
        print()
        print(f"  {LGRN}MD5    {RST}  {LWHT}{md5}{RST}")
        print(f"  {LGRN}SHA-1  {RST}  {LWHT}{sha1}{RST}")
        print(f"  {LGRN}SHA-256{RST}  {LWHT}{sha256}{RST}")
        if expected:
            print()
            if expected in (md5, sha1, sha256): status_ok("Hash MATCH ✔")
            else:                               status_err("Hash MISMATCH ✘")
    except Exception as e: status_err(str(e))


def mod_dir_scanner():
    mod_header("DIRECTORY SCANNER", "Scan directory contents", '📁', LGRN)
    path = ask("Directory path", ".")
    if not os.path.isdir(path): status_err("Directory not found"); return
    show_hidden = ask("Show hidden files? (y/n)", "n").lower() == 'y'
    print(); total_files = total_dirs = total_size = 0
    for entry in sorted(os.scandir(path), key=lambda e: (not e.is_dir(), e.name.lower())):
        if not show_hidden and entry.name.startswith('.'): continue
        try:
            if entry.is_dir():
                print(f"  {LBLU}📁  {entry.name}/{RST}"); total_dirs += 1
            else:
                size = entry.stat().st_size; total_size += size
                size_str = f"{size//1024:,} KB" if size >= 1024 else f"{size} B"
                print(f"  {LWHT}📄  {entry.name:<40}{RST}  {DIM}{size_str}{RST}"); total_files += 1
        except: pass
    print(); status_info(f"Dirs: {total_dirs}  |  Files: {total_files}  |  Total: {total_size//1024} KB")


def mod_log_reader():
    mod_header("LOG FILE READER", "Read and filter log files", '📋', LGRN)
    path = ask("Log file path")
    if not path or not os.path.exists(path): status_err("File not found"); return
    filter_kw = ask("Filter keyword (empty = all)")
    lines_count = int(ask("Last N lines?", "50"))
    highlight = {'error':LRED,'err':LRED,'fail':LRED,'warn':LYLW,'warning':LYLW,'info':LCYN,'ok':LGRN,'success':LGRN}
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f: lines = f.readlines()
        if filter_kw: lines = [l for l in lines if filter_kw.lower() in l.lower()]
        lines = lines[-lines_count:]
        print()
        for line in lines:
            col = next((c for kw, c in highlight.items() if kw in line.lower()), RST)
            print(f"  {col}{line.rstrip()}{RST}")
        print(); status_info(f"Showing {len(lines)} lines")
    except Exception as e: status_err(str(e))


def mod_ip_calculator():
    mod_header("IP CALCULATOR (CIDR)", "Network IP calculator", '🧮', LCYN)
    cidr = ask("CIDR network (e.g. 192.168.1.0/24)")
    if not cidr or '/' not in cidr: status_err("Invalid CIDR format"); return
    try:
        import ipaddress
        net = ipaddress.IPv4Network(cidr, strict=False)
        hosts = list(net.hosts())
        print()
        print(f"  {LCYN}Network      {RST}  {LWHT}{net.network_address}{RST}")
        print(f"  {LCYN}Broadcast    {RST}  {LWHT}{net.broadcast_address}{RST}")
        print(f"  {LCYN}Netmask      {RST}  {LWHT}{net.netmask}{RST}")
        print(f"  {LCYN}Wildcard     {RST}  {LWHT}{net.hostmask}{RST}")
        print(f"  {LCYN}Prefix       {RST}  {LWHT}/{net.prefixlen}{RST}")
        print(f"  {LCYN}Usable hosts {RST}  {LGRN}{len(hosts):,}{RST}")
        if hosts:
            print(f"  {LCYN}First host   {RST}  {LWHT}{hosts[0]}{RST}")
            print(f"  {LCYN}Last host    {RST}  {LWHT}{hosts[-1]}{RST}")
        print(f"  {LCYN}Type         {RST}  {LWHT}{'Private' if net.is_private else 'Public'}{RST}")
    except Exception as e: status_err(str(e))


def mod_random_password():
    mod_header("RANDOM PASSWORD GENERATOR", "Generate secure random passwords", '🎲', LCYN)
    length = int(ask("Password length", "16"))
    count  = int(ask("How many?", "5"))
    use_upper   = ask("Uppercase letters? (y/n)", "y").lower() == 'y'
    use_digits  = ask("Digits? (y/n)", "y").lower() == 'y'
    use_special = ask("Special chars? (y/n)", "y").lower() == 'y'
    charset = string.ascii_lowercase
    if use_upper:   charset += string.ascii_uppercase
    if use_digits:  charset += string.digits
    if use_special: charset += "!@#$%^&*()_+-=[]{}|"
    print(); print(f"  {BOLD}{LCYN}{'#':<4}{'PASSWORD':<{length+4}}{'STRENGTH'}{RST}"); hline('─', DIM, length+20)
    for i in range(count):
        pwd = ''.join(random.choice(charset) for _ in range(length))
        score = sum([any(c.isupper() for c in pwd), any(c.isdigit() for c in pwd),
                     any(c in "!@#$%^&*()" for c in pwd), length>=12, length>=16])
        stars = f"{LGRN}{'★'*score}{'☆'*(5-score)}{RST}"
        print(f"  {LYLW}{i+1:<4}{RST}{LWHT}{pwd:<{length+4}}{RST}{stars}")


def mod_uuid_generator():
    import uuid
    mod_header("UUID GENERATOR", "Generate unique identifiers", '🆔', LCYN)
    count   = int(ask("How many UUIDs?", "5"))
    version = ask("Version (4=random, 1=time-based)", "4")
    print()
    for i in range(count):
        u = uuid.uuid1() if version == "1" else uuid.uuid4()
        print(f"  {LYLW}{i+1:>3}.{RST}  {LWHT}{u}{RST}  {DIM}(v{u.version}){RST}")
    print(); status_info("v4 = random, v1 = time + MAC based")


def mod_text_case():
    mod_header("TEXT CASE CONVERTER", "Convert text case and format", '🔤', LCYN)
    text = ask("Text")
    if not text: return
    print()
    for name, val in [("UPPER", text.upper()), ("lower", text.lower()),
                      ("Title Case", text.title()), ("Sentence", text.capitalize()),
                      ("sWAP cASE", text.swapcase()),
                      ("snake_case", re.sub(r'\s+','_',text.lower())),
                      ("kebab-case", re.sub(r'\s+','-',text.lower())),
                      ("CamelCase", ''.join(w.capitalize() for w in text.split())),
                      ("lowerCamel", text.split()[0].lower()+''.join(w.capitalize() for w in text.split()[1:]) if text.split() else '')]:
        print(f"  {LCYN}{name:<16}{RST}  {LWHT}{val}{RST}")


def mod_lorem_ipsum():
    mod_header("LOREM IPSUM GENERATOR", "Generate placeholder text", '📖', LCYN)
    words_pool = ["lorem","ipsum","dolor","sit","amet","consectetur","adipiscing","elit","sed","do","eiusmod","tempor","incididunt","ut","labore","et","dolore","magna","aliqua","enim","ad","minim","veniam","quis","nostrud","exercitation","ullamco","laboris","nisi","aliquip","ex","ea","commodo","consequat","duis","aute","irure","in","reprehenderit","voluptate","velit","esse","cillum","eu","fugiat","nulla","pariatur"]
    paras = int(ask("Paragraphs?", "2")); wpp = int(ask("Words per paragraph?", "50"))
    print()
    for _ in range(paras):
        words = random.choices(words_pool, k=wpp); words[0] = words[0].capitalize()
        print(f"  {DIM}{' '.join(words)}.{RST}\n")


def mod_json_formatter():
    import json
    mod_header("JSON FORMATTER", "Format and validate JSON", '{}', LCYN)
    print(f"  {DIM}Paste JSON (empty line = done):{RST}\n")
    lines = []
    while True:
        try:
            line = input("  ")
            if not line and lines: break
            lines.append(line)
        except EOFError: break
    try:
        parsed = json.loads('\n'.join(lines))
        formatted = json.dumps(parsed, indent=2, ensure_ascii=False)
        print()
        for line in formatted.splitlines():
            line_c = re.sub(r'"([^"]+)":', f'{LYLW}"\\1":{RST}', line)
            line_c = re.sub(r':\s*"([^"]*)"', f': {LGRN}"\\1"{RST}', line_c)
            line_c = re.sub(r':\s*(\d+\.?\d*)', f': {LCYN}\\1{RST}', line_c)
            line_c = re.sub(r':\s*(true|false|null)', f': {LMAG}\\1{RST}', line_c)
            print(f"  {line_c}")
        print(); status_ok(f"Valid JSON  |  Keys: {len(parsed) if isinstance(parsed,(dict,list)) else 1}")
    except json.JSONDecodeError as e: status_err(f"JSON error: {e}")


def mod_timestamp():
    mod_header("UNIX TIMESTAMP CONVERTER", "Convert Unix timestamps", '⏱', LCYN)
    print(f"  {LYLW}[1]{RST} Timestamp → Date    {LYLW}[2]{RST} Date → Timestamp    {LYLW}[3]{RST} Current time\n")
    mode = ask("Mode", "1"); print()
    if mode == "1":
        raw = ask("Unix timestamp")
        try:
            ts = int(raw)
            status_ok(f"UTC:   {BOLD}{datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}{RST}")
            status_ok(f"Local: {BOLD}{datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}{RST}")
        except: status_err("Invalid timestamp")
    elif mode == "2":
        date_str = ask("Date (YYYY-MM-DD HH:MM:SS)")
        try:
            ts = int(datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S").timestamp())
            status_ok(f"Timestamp: {BOLD}{LYLW}{ts}{RST}")
        except: status_err("Invalid date format")
    else:
        now = datetime.now()
        print(f"  {LCYN}Local time   {RST}  {LWHT}{now.strftime('%Y-%m-%d %H:%M:%S')}{RST}")
        print(f"  {LCYN}UTC time     {RST}  {LWHT}{datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}{RST}")
        print(f"  {LCYN}Timestamp    {RST}  {LYLW}{BOLD}{int(now.timestamp())}{RST}")


def mod_color_converter():
    mod_header("COLOR CODE CONVERTER", "Convert color codes", '🎨', LCYN)
    print(f"  {LYLW}[1]{RST} HEX → RGB    {LYLW}[2]{RST} RGB → HEX    {LYLW}[3]{RST} Terminal preview\n")
    mode = ask("Mode", "1"); print()
    if mode == "1":
        hex_code = ask("HEX color (e.g. #FF5733)").strip('#')
        try:
            r_v,g_v,b_v = int(hex_code[0:2],16),int(hex_code[2:4],16),int(hex_code[4:6],16)
            status_ok(f"RGB: {BOLD}rgb({r_v}, {g_v}, {b_v}){RST}")
            status_ok(f"HEX: {BOLD}#{hex_code.upper()}{RST}")
        except: status_err("Invalid HEX format")
    elif mode == "2":
        rgb = ask("RGB (e.g. 255,87,51)")
        try:
            r_v,g_v,b_v = [int(x.strip()) for x in rgb.split(',')]
            status_ok(f"HEX: {BOLD}#{r_v:02X}{g_v:02X}{b_v:02X}{RST}")
        except: status_err("Invalid RGB format")
    else:
        for name, bg in [("Red","\033[41m"),("Green","\033[42m"),("Yellow","\033[43m"),
                         ("Blue","\033[44m"),("Magenta","\033[45m"),("Cyan","\033[46m"),
                         ("LightBlue","\033[104m"),("LightMag","\033[105m"),("LightCyan","\033[106m")]:
            print(f"  {bg}{BLK}  {name:<12}  {RST}")


def mod_string_analyzer():
    mod_header("STRING ANALYZER", "Statistical text analysis", '🔍', LCYN)
    text = ask("Text to analyze")
    if not text: return
    freq = {}
    for c in text.lower():
        if c.isalpha(): freq[c] = freq.get(c, 0) + 1
    top = sorted(freq.items(), key=lambda x: -x[1])[:8]
    print()
    for k, v in [("Total chars", len(text)), ("Words", len(text.split())),
                 ("Lines", len(text.splitlines())), ("Digits", sum(1 for c in text if c.isdigit())),
                 ("Spaces", text.count(' ')), ("Uppercase", sum(1 for c in text if c.isupper())),
                 ("Special chars", sum(1 for c in text if not c.isalnum() and not c.isspace())),
                 ("Unique chars", len(set(text.lower())))]:
        print(f"  {LCYN}{k:<18}{RST}  {LWHT}{v}{RST}")
    if top:
        print(f"\n  {BOLD}Top letters:{RST}"); max_cnt = top[0][1]
        for ch, cnt in top:
            bar = f"{LGRN}{'█'*int(20*cnt/max_cnt)}{RST}"
            print(f"    {LYLW}'{ch}'{RST}  {bar}  {DIM}{cnt}x{RST}")


def mod_number_base():
    mod_header("NUMBER BASE CONVERTER", "Convert between number bases", '🔢', LCYN)
    num_str = ask("Number to convert"); base_from = int(ask("From base (e.g. 10)", "10"))
    if not num_str: return
    try:
        val = int(num_str, base_from); print()
        print(f"  {LCYN}DEC (10)   {RST}  {LWHT}{val}{RST}")
        print(f"  {LCYN}BIN (2)    {RST}  {LYLW}{bin(val)[2:]}{RST}")
        print(f"  {LCYN}OCT (8)    {RST}  {LYLW}{oct(val)[2:]}{RST}")
        print(f"  {LCYN}HEX (16)   {RST}  {LYLW}{hex(val)[2:].upper()}{RST}")
        if 0 <= val <= 0x10FFFF:
            try: print(f"  {LCYN}Unicode    {RST}  {LYLW}{chr(val)}{RST}  {DIM}(U+{val:04X}){RST}")
            except: pass
    except Exception as e: status_err(f"Conversion error: {e}")


def mod_regex_tester():
    mod_header("REGEX TESTER", "Test regular expressions", '🔭', LCYN)
    pattern_str = ask("Regular expression (e.g. \\d+)")
    test_text   = ask("Test text")
    if not pattern_str or not test_text: return
    flags_str = ask("Flags (i=ignore case, m=multiline, empty=none)", "")
    flags = 0
    if 'i' in flags_str: flags |= re.IGNORECASE
    if 'm' in flags_str: flags |= re.MULTILINE
    try:
        pattern = re.compile(pattern_str, flags)
        matches = list(pattern.finditer(test_text))
        print()
        if matches:
            status_ok(f"Found {len(matches)} match(es):")
            print()
            for i, m in enumerate(matches, 1):
                print(f"  {LYLW}[{i}]{RST}  {LGRN}'{m.group()}'{RST}  {DIM}pos {m.start()}-{m.end()}{RST}")
                for j, g in enumerate(m.groups(), 1): print(f"       {DIM}Group {j}: '{g}'{RST}")
        else:
            status_warn("No matches found")
        highlighted = pattern.sub(lambda m: f"{BG_LMAG}{BLK}{m.group()}{RST}", test_text)
        print(f"\n  {DIM}Text:{RST}  {highlighted[:100]}")
    except re.error as e:
        status_err(f"Regex error: {e}")


def mod_ascii_art():
    mod_header("ASCII ART GENERATOR", "Generate ASCII art from text", '🎭', LCYN)
    text = ask("Text (max 8 chars)")
    if not text: return
    text = text[:8].upper()
    FONT = {'A':["▄█▄","█ █","█▀█"],'B':["█▄ ","██▄","█▄▀"],'C':["▄█▀","█  ","▀█▄"],'D':["█▄ ","█ █","█▀ "],'E':["███","██ ","███"],'F':["███","██ ","█  "],'G':["▄█▀","█ █","▀██"],'H':["█ █","███","█ █"],'I':["███"," █ ","███"],'J':[" ██","  █","▀█▀"],'K':["█ █","██ ","█ █"],'L':["█  ","█  ","███"],'M':["█▄█","█ █","█ █"],'N':["█▄█","█ █","█ █"],'O':["▄█▄","█ █","▀█▀"],'P':["██▄","██▀","█  "],'Q':["▄█▄","█ █","▀██"],'R':["██▄","██▀","█ █"],'S':["▄█▀","▀█▄","▀█▀"],'T':["███"," █ "," █ "],'U':["█ █","█ █","▀█▀"],'V':["█ █","█ █"," █ "],'W':["█ █","█ █","█▄█"],'X':["█ █"," █ ","█ █"],'Y':["█ █"," █ "," █ "],'Z':["██▀"," █ ","▀██"],'0':["▄█▄","█ █","▀█▀"],'1':[" █ ","██ "," █ "],'2':["▀█▄"," █ ","███"],'3':["▀█▀"," █▄","▀█▀"],' ':["   ","   ","   "],'!':[ " █ "," █ "," ▪ "],'?':["▀█▄"," █▀"," ▪ "]}
    print()
    colors = [LRED,LYLW,LGRN,LCYN,LBLU,LMAG,LWHT,LRED]
    for row in range(3):
        line = ""
        for ci, char in enumerate(text):
            glyph = FONT.get(char, FONT.get('?', ["   ","   ","   "]))
            line += f"{colors[ci%len(colors)]}{glyph[row]}{RST}  "
        print(f"  {line}")
    print()


import json
from pathlib import Path

HISTORY_DIR = Path.home() / "kooltitool" / "history"
NO_HISTORY  = {46, 47, 50, 51, 70}


def history_init():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def history_log(module_id: int, module_name: str, data: dict):
    if module_id in NO_HISTORY:
        return
    history_init()
    entry = {
        "timestamp":   datetime.now().isoformat(timespec="seconds"),
        "module_id":   module_id,
        "module_name": module_name,
        "data":        data,
    }
    day_dir = HISTORY_DIR / datetime.now().strftime("%Y-%m-%d")
    day_dir.mkdir(parents=True, exist_ok=True)
    safe_name = module_name.lower().replace(" ", "_")[:30]
    fname = day_dir / f"{datetime.now().strftime('%H%M%S')}_{module_id:03d}_{safe_name}.json"
    with open(fname, "w", encoding="utf-8") as fh:
        json.dump(entry, fh, ensure_ascii=False, indent=2, default=str)


# ── 81: HTTP Parameter Fuzzer ────────────────────────────────────────────────

def mod_http_fuzzer():
    mod_header("HTTP PARAMETER FUZZER", "Fuzz URL parameters for unexpected responses", "🎯", LMAG)
    url   = ask("Base URL (e.g. https://example.com/page?id=1)")
    param = ask("Parameter to fuzz", "id")
    if not url or not param:
        return
    payloads = [
        "'", "''", '"', "<script>alert(1)</script>", "../",
        "1 OR 1=1", "{{7*7}}", "%00", "admin", "null",
        "undefined", "-1", "9999", "0", "true", "false",
        "<img src=x>", "'; DROP TABLE users--", "\\", "%27",
    ]
    print()
    print(f"  {BOLD}{LCYN}{'PAYLOAD':<26}{'STATUS':<8}{'SIZE':<10}NOTE{RST}")
    hline("─", DIM, 65)
    baseline_len = 0
    for i, payload in enumerate(payloads):
        try:
            r = requests.get(url, params={param: payload}, timeout=6,
                             headers={"User-Agent": "Mozilla/5.0"})
            size = len(r.content)
            if i == 0:
                baseline_len = size
            diff = size - baseline_len
            col  = LRED if r.status_code >= 500 else (LYLW if abs(diff) > 200 else LGRN)
            note = f"delta {diff:+d}B" if diff != 0 else "baseline"
            print(f"  {col}{payload[:25]:<26}{r.status_code:<8}{size:<10}{note}{RST}")
        except Exception as e:
            print(f"  {LRED}{payload[:25]:<26}{'ERR':<8}{'-':<10}{str(e)[:20]}{RST}")
    history_log(81, "HTTP Parameter Fuzzer", {"url": url, "param": param})


# ── 82: JS File Extractor ───────────────────────────────────────────────────

def mod_js_extractor():
    mod_header("JS FILE EXTRACTOR", "Find JavaScript files and inline scripts", "📜", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        q  = '["\']'
        scripts = re.findall(r'<script[^>]+src=' + q + r'([^"\']+)' + q, r.text, re.I)
        inline  = re.findall(r'(?s)<script[^>]*>(.{20,400}?)</script>', r.text, re.I)
        print()
        if scripts:
            print(f"  {BOLD}{LGRN}External JS ({len(scripts)}):{RST}")
            for s in scripts:
                full = s if s.startswith("http") else url.rstrip("/") + "/" + s.lstrip("/")
                print(f"  {LGRN}→{RST}  {LBLU}{full}{RST}")
        if inline:
            print()
            print(f"  {BOLD}{LYLW}Inline snippets ({len(inline)}):{RST}")
            for idx, snippet in enumerate(inline[:5], 1):
                clean = snippet.strip()[:120].replace("\n", " ")
                print(f"  {LYLW}[{idx}]{RST}  {DIM}{clean}...{RST}")
        status_info(f"Total: {len(scripts)} external, {len(inline)} inline")
        history_log(82, "JS File Extractor", {"url": url, "external": scripts,
                                               "inline_count": len(inline)})
    except Exception as e:
        status_err(str(e))


# ── 83: Form Extractor ──────────────────────────────────────────────────────

def mod_form_extractor():
    mod_header("FORM EXTRACTOR", "Extract forms and input fields from a page", "📋", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r     = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        forms = re.findall(r'(?s)<form[^>]*>(.*?)</form>', r.text, re.I)
        q     = '["\']'
        print()
        for i, form_html in enumerate(forms, 1):
            action_m = re.search(r'action=' + q + r'([^"\']*)'  + q, form_html, re.I)
            method_m = re.search(r'method=' + q + r'([^"\']*)' + q, form_html, re.I)
            inputs   = re.findall(r'<input[^>]+>', form_html, re.I)
            print(f"  {LMAG}{BOLD}Form #{i}{RST}")
            print(f"    {LCYN}Action{RST}  {LWHT}{action_m.group(1) if action_m else '(none)'}{RST}")
            print(f"    {LCYN}Method{RST}  {LWHT}{method_m.group(1).upper() if method_m else 'GET'}{RST}")
            for inp in inputs:
                name_m  = re.search(r'name='  + q + r'([^"\']*)' + q, inp, re.I)
                type_m  = re.search(r'type='  + q + r'([^"\']*)' + q, inp, re.I)
                n = name_m.group(1) if name_m else "(no name)"
                t = type_m.group(1) if type_m else "text"
                col = LRED if t in ("password", "hidden") else LWHT
                print(f"      {DIM}•{RST}  {col}{n}{RST}  {DIM}[{t}]{RST}")
            print()
        status_info(f"Found {len(forms)} form(s)")
        history_log(83, "Form Extractor", {"url": url, "form_count": len(forms)})
    except Exception as e:
        status_err(str(e))


# ── 84: Cookie Inspector ────────────────────────────────────────────────────

def mod_cookie_inspector():
    mod_header("COOKIE INSPECTOR", "Analyze cookies and security flags", "🍪", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r       = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        cookies = list(r.cookies)
        print()
        if not cookies:
            status_warn("No cookies found")
            return
        print(f"  {BOLD}{LCYN}{'NAME':<22}{'VALUE':<22}{'Secure':<9}{'HttpOnly':<10}{'SameSite'}{RST}")
        hline("─", DIM, 75)
        issues = []
        raw_header = r.headers.get("Set-Cookie", "")
        for c in cookies:
            secure   = c.secure
            httponly = "httponly" in raw_header.lower()
            samesite = "N/A"
            m = re.search(r'SameSite=([^;,\s]+)', raw_header, re.I)
            if m:
                samesite = m.group(1)
            sc = LGRN if secure   else LRED
            hc = LGRN if httponly else LYLW
            val_s = (c.value[:20] + "…") if len(c.value) > 20 else c.value
            print(f"  {LWHT}{c.name:<22}{RST}{DIM}{val_s:<22}{RST}"
                  f"{sc}{'✔' if secure else '✘':<9}{RST}"
                  f"{hc}{'✔' if httponly else '✘':<10}{RST}{DIM}{samesite}{RST}")
            if not secure:   issues.append(f"'{c.name}' missing Secure flag")
            if not httponly: issues.append(f"'{c.name}' missing HttpOnly flag")
        if issues:
            print()
            for issue in issues:
                status_warn(issue)
        history_log(84, "Cookie Inspector", {"url": url, "cookie_count": len(cookies)})
    except Exception as e:
        status_err(str(e))


# ── 85: IP Reputation Check ─────────────────────────────────────────────────

def mod_ip_reputation():
    mod_header("IP REPUTATION CHECK", "Check IP against threat intelligence", "🛡", LMAG)
    ip = ask("IP address")
    if not ip:
        return
    print()
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}?fields=status,country,isp,"
                         "org,proxy,hosting,query", timeout=6)
        d = r.json()
        if d.get("status") == "success":
            print(f"  {LCYN}IP          {RST}  {LWHT}{d.get('query')}{RST}")
            print(f"  {LCYN}Country     {RST}  {LWHT}{d.get('country','N/A')}{RST}")
            print(f"  {LCYN}ISP         {RST}  {LWHT}{d.get('isp','N/A')}{RST}")
            print(f"  {LCYN}Org         {RST}  {LWHT}{d.get('org','N/A')}{RST}")
            proxy   = d.get("proxy", False)
            hosting = d.get("hosting", False)
            pc = LRED if proxy   else LGRN
            hc = LYLW if hosting else LGRN
            print(f"  {LCYN}Proxy       {RST}  {pc}{BOLD}{'YES - possible VPN/proxy' if proxy else 'No'}{RST}")
            print(f"  {LCYN}Hosting     {RST}  {hc}{'YES - datacenter/hosting IP' if hosting else 'No'}{RST}")
    except Exception as e:
        status_err(f"ip-api: {e}")
    print()
    try:
        r2 = requests.get(f"https://api.hackertarget.com/geoip/?q={ip}", timeout=8)
        if r2.status_code == 200 and "error" not in r2.text.lower():
            status_info("HackerTarget GeoIP:")
            for line in r2.text.strip().splitlines():
                print(f"    {DIM}{line}{RST}")
    except: pass
    status_info("For full AbuseIPDB score: https://www.abuseipdb.com/check/" + ip)
    history_log(85, "IP Reputation Check", {"ip": ip})


# ── 86: Path Traversal Tester ───────────────────────────────────────────────

def mod_path_traversal():
    mod_header("PATH TRAVERSAL TESTER", "Test for directory traversal vulnerabilities", "🗂", LMAG)
    url   = ask("Base URL (e.g. https://example.com/file)")
    param = ask("Parameter name", "file")
    if not url or not param:
        return
    payloads = [
        "../etc/passwd",
        "../../etc/passwd",
        "../../../etc/passwd",
        "..\\..\\windows\\win.ini",
        "..%2F..%2Fetc%2Fpasswd",
        "%2e%2e%2f%2e%2e%2fetc%2fpasswd",
        "....//....//etc/passwd",
        "/etc/passwd",
        "c:\\windows\\win.ini",
    ]
    indicators = ["root:x:", "[boot loader]", "[fonts]", "daemon:", "nobody:"]
    print()
    for payload in payloads:
        try:
            r   = requests.get(url, params={param: payload}, timeout=6)
            hit = any(ind.lower() in r.text.lower() for ind in indicators)
            col  = LRED if hit else (LYLW if r.status_code == 200 else DIM)
            tag  = "[VULN!]" if hit else "[    ]"
            note = "VULNERABLE — file content detected!" if hit else f"({r.status_code})"
            print(f"  {col}{tag}  {payload:<38}  {note}{RST}")
        except Exception as e:
            print(f"  {DIM}[ ERR]  {payload:<38}  {str(e)[:25]}{RST}")
    history_log(86, "Path Traversal Tester", {"url": url, "param": param})


# ── 87: SQL Error Detector ──────────────────────────────────────────────────

def mod_sql_error_detector():
    mod_header("SQL ERROR DETECTOR", "Detect SQL error messages in responses", "💉", LMAG)
    url   = ask("URL (e.g. https://example.com/item?id=1)")
    param = ask("Parameter to test", "id")
    if not url or not param:
        return
    payloads = [
        "'", "''", "`", "1'", '1"',
        "1 AND 1=1", "1 AND 1=2",
        "1 OR 1=1", "1; SELECT 1--",
        "1 UNION SELECT NULL--",
    ]
    sql_errors = [
        "sql syntax", "mysql_fetch", "ora-", "sqlite_",
        "pg_query", "syntax error", "unclosed quotation",
        "microsoft ole db", "warning: mysql",
        "you have an error in your sql",
    ]
    print()
    print(f"  {BOLD}{LCYN}{'PAYLOAD':<28}{'STATUS':<8}SQL ERROR?{RST}")
    hline("─", DIM, 55)
    for payload in payloads:
        try:
            r     = requests.get(url, params={param: payload}, timeout=6)
            found = any(e in r.text.lower() for e in sql_errors)
            col   = LRED if found else LGRN
            note  = "POSSIBLE SQL ERROR LEAK" if found else "clean"
            print(f"  {col}{payload:<28}{r.status_code:<8}{note}{RST}")
        except Exception as e:
            print(f"  {DIM}{payload:<28}{'ERR':<8}{str(e)[:25]}{RST}")
    history_log(87, "SQL Error Detector", {"url": url, "param": param})


# ── 88: Subdomain Takeover Checker ──────────────────────────────────────────

def mod_subdomain_takeover():
    mod_header("SUBDOMAIN TAKEOVER CHECKER", "Check subdomains for takeover risk", "⚠", LBLU)
    domain = ask("Base domain (e.g. example.com)")
    if not domain:
        return
    subs = ["www","mail","ftp","dev","test","staging","api","blog","shop",
            "cdn","static","media","old","beta","demo","forum","portal"]
    fingerprints = {
        "github.io":    "There isn't a GitHub Pages site here",
        "heroku":       "No such app",
        "shopify":      "Sorry, this shop is currently unavailable",
        "fastly":       "Fastly error: unknown domain",
        "azure":        "404 Web Site not found",
        "bitbucket.io": "Repository not found",
        "netlify":      "Not Found - Request ID",
        "zendesk":      "Help Center Closed",
        "readme.io":    "Project doesnt exist",
    }
    print()
    status_info(f"Checking {len(subs)} subdomains...")
    print()
    vulns = []
    for sub in subs:
        full = f"{sub}.{domain}"
        try:
            socket.gethostbyname(full)
            try:
                r   = requests.get(f"https://{full}", timeout=5, allow_redirects=True)
                hit = next((svc for svc, fp in fingerprints.items()
                            if fp.lower() in r.text.lower()), None)
                if hit:
                    print(f"  {LRED}[VULN]{RST}  {full:<35}  {LRED}possible {hit} takeover{RST}")
                    vulns.append((full, hit))
                else:
                    print(f"  {LGRN}[ OK ]{RST}  {full:<35}")
            except:
                print(f"  {LYLW}[???]{RST}  {full:<35}  {DIM}resolves but HTTPS failed{RST}")
        except socket.gaierror:
            print(f"  {DIM}[---]{RST}  {full:<35}  no DNS{RST}")
    print()
    if vulns:
        status_warn(f"{len(vulns)} potential takeover(s) found!")
    else:
        status_ok("No obvious takeover vulnerabilities found")
    history_log(88, "Subdomain Takeover Checker", {"domain": domain, "vulns": vulns})


# ── 89: TLS Version Checker ─────────────────────────────────────────────────

def mod_tls_checker():
    import ssl as _ssl
    mod_header("TLS VERSION CHECKER", "Check supported TLS versions on a server", "🔐", LMAG)
    host = ask("Hostname (e.g. example.com)")
    port = int(ask("Port", "443"))
    if not host:
        return
    print()
    checks = [
        ("TLS 1.0", "TLSv1"),
        ("TLS 1.1", "TLSv1_1"),
        ("TLS 1.2", "TLSv1_2"),
        ("TLS 1.3", "TLSv1_3"),
    ]
    for name, attr in checks:
        version = getattr(_ssl.TLSVersion, attr, None)
        if version is None:
            print(f"  {DIM}{name:<10}  not available in this Python{RST}")
            continue
        try:
            ctx = _ssl.SSLContext(_ssl.PROTOCOL_TLS_CLIENT)
            ctx.minimum_version = version
            ctx.maximum_version = version
            ctx.check_hostname  = False
            ctx.verify_mode     = _ssl.CERT_NONE
            with ctx.wrap_socket(socket.socket(), server_hostname=host) as s:
                s.settimeout(5)
                s.connect((host, port))
                cipher = s.cipher()
            deprecated = name in ("TLS 1.0", "TLS 1.1")
            col  = LRED if deprecated else LGRN
            note = "⚠ DEPRECATED" if deprecated else "✔ secure"
            ciph = cipher[0] if cipher else ""
            print(f"  {col}{name:<10}  SUPPORTED    {DIM}{ciph:<30}{RST}  {col}{note}{RST}")
        except _ssl.SSLError:
            print(f"  {LGRN}{name:<10}  not supported{RST}")
        except Exception as e:
            print(f"  {DIM}{name:<10}  error: {str(e)[:40]}{RST}")
    history_log(89, "TLS Version Checker", {"host": host, "port": port})


# ── 90: WhatWeb Lite ────────────────────────────────────────────────────────

def mod_whatweb():
    mod_header("WHATWEB LITE", "Quick technology fingerprint from headers + HTML", "🔬", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r     = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"},
                             allow_redirects=True)
        html  = r.text
        heads = {k.lower(): v for k, v in r.headers.items()}
        q     = '["\']'
        gen_m = re.search(r'<meta[^>]+name=' + q + r'generator' + q +
                          r'[^>]+content=' + q + r'([^"\']+)' + q, html, re.I)
        title_m = re.search(r'<title>([^<]{1,80})</title>', html, re.I)
        parsed_host = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
        try:
            resolved_ip = socket.gethostbyname(parsed_host)
        except:
            resolved_ip = "N/A"
        print()
        rows = [
            ("Server",         heads.get("server", "")),
            ("X-Powered-By",   heads.get("x-powered-by", "")),
            ("X-Generator",    heads.get("x-generator", "")),
            ("Generator meta", gen_m.group(1) if gen_m else ""),
            ("Title",          title_m.group(1) if title_m else ""),
            ("IP",             resolved_ip),
            ("Final URL",      r.url),
            ("Status",         str(r.status_code)),
            ("Page size",      f"{len(r.content)/1024:.1f} KB"),
        ]
        for label, val in rows:
            if val:
                print(f"  {LCYN}{label:<20}{RST}  {LWHT}{str(val)[:65]}{RST}")
        history_log(90, "WhatWeb Lite", {"url": url, "final_url": r.url})
    except Exception as e:
        status_err(str(e))


# ── 91: Latency Map ─────────────────────────────────────────────────────────

def mod_latency_map():
    mod_header("LATENCY MAP", "Ping global endpoints and compare RTT", "🌍", LBLU)
    targets = {
        "Google DNS (US)":    "8.8.8.8",
        "Cloudflare (US)":    "1.1.1.1",
        "OpenDNS (US)":       "208.67.222.222",
        "Amazon AWS EU":      "52.94.76.1",
        "Microsoft Azure EU": "13.69.1.1",
        "Alibaba Cloud":      "47.88.0.1",
    }
    print()
    status_info("Pinging 6 global endpoints (3 pings each)...")
    print()
    print(f"  {BOLD}{LCYN}{'TARGET':<26}{'IP':<18}{'AVG RTT':<14}{'STATUS'}{RST}")
    hline("─", DIM, 70)
    param = "-n" if platform.system().lower() == "windows" else "-c"
    results = []
    for name, ip in targets.items():
        t0 = time.time()
        r  = subprocess.run(["ping", param, "3", ip],
                            capture_output=True, text=True)
        ms = round((time.time() - t0) * 1000 / 3, 1)
        ok = r.returncode == 0
        col = LGRN if ms < 50 else (LYLW if ms < 150 else LRED)
        print(f"  {LWHT}{name:<26}{RST}{DIM}{ip:<18}{RST}"
              f"{col}{str(ms)+' ms':<14}{RST}{'✔' if ok else '✘'}")
        results.append({"target": name, "ip": ip, "ms": ms, "ok": ok})
    history_log(91, "Latency Map", {"results": results})


# ── 92: Certificate Transparency ────────────────────────────────────────────

def mod_cert_transparency():
    mod_header("CERTIFICATE TRANSPARENCY", "Find SSL certs issued for a domain via crt.sh", "📜", LMAG)
    domain = ask("Domain (e.g. example.com)")
    if not domain:
        return
    try:
        r = requests.get(f"https://crt.sh/?q=%.{domain}&output=json", timeout=15)
        if r.status_code == 200:
            certs  = r.json()
            unique = {}
            for c in certs:
                name = c.get("name_value", "").strip()
                if name not in unique:
                    unique[name] = {
                        "issued": c.get("not_before", "")[:10],
                        "issuer": c.get("issuer_name", "")[:40],
                    }
            print()
            status_ok(f"Found {len(unique)} unique certificate name(s) via crt.sh")
            print()
            print(f"  {BOLD}{LCYN}{'DOMAIN / NAME':<40}{'ISSUED':<14}ISSUER{RST}")
            hline("─", DIM, 80)
            for name, info in list(unique.items())[:30]:
                print(f"  {LWHT}{name[:38]:<40}{RST}"
                      f"{DIM}{info['issued']:<14}{RST}"
                      f"{DIM}{info['issuer'][:30]}{RST}")
            if len(unique) > 30:
                status_info(f"... and {len(unique)-30} more (crt.sh has full list)")
            history_log(92, "Certificate Transparency",
                        {"domain": domain, "cert_count": len(unique)})
        else:
            status_err(f"crt.sh returned HTTP {r.status_code}")
    except Exception as e:
        status_err(str(e))


# ── 93: HTTP Cache Inspector ─────────────────────────────────────────────────

def mod_cache_inspector():
    mod_header("HTTP CACHE INSPECTOR", "Analyze caching headers and directives", "💾", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    cache_hdrs = ["cache-control", "expires", "etag", "last-modified", "vary",
                  "x-cache", "x-cache-hits", "cf-cache-status", "age", "pragma"]
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        print()
        found_any = False
        for h in cache_hdrs:
            val = r.headers.get(h)
            if val:
                print(f"  {LGRN}{h:<28}{RST}  {LWHT}{val}{RST}")
                found_any = True
        if not found_any:
            status_warn("No caching headers found")
        cc = r.headers.get("cache-control", "").lower()
        print()
        if "no-store" in cc:
            status_ok("no-store — response will NOT be cached")
        elif "no-cache" in cc:
            status_info("no-cache — must revalidate before serving from cache")
        elif "max-age" in cc:
            m = re.search(r"max-age=(\d+)", cc)
            if m:
                secs = int(m.group(1))
                status_info(f"max-age={secs}s  (~{secs//60} minutes)")
        elif not cc:
            status_warn("No Cache-Control header — caching behavior undefined")
        history_log(93, "HTTP Cache Inspector", {"url": url})
    except Exception as e:
        status_err(str(e))


# ── 94: Security Headers Score ──────────────────────────────────────────────

def mod_security_score():
    mod_header("SECURITY HEADERS SCORE", "Grade a site's HTTP security headers", "🏅", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    scored = {
        "strict-transport-security": ("HSTS",            20),
        "content-security-policy":   ("CSP",             20),
        "x-frame-options":           ("X-Frame-Options", 15),
        "x-content-type-options":    ("X-Content-Type",  15),
        "referrer-policy":           ("Referrer-Policy", 10),
        "permissions-policy":        ("Permissions",     10),
        "x-xss-protection":          ("XSS-Protection",   5),
        "cross-origin-opener-policy":("COOP",             5),
    }
    try:
        r       = requests.get(url, timeout=8, headers={"User-Agent": "Mozilla/5.0"})
        h_lower = {k.lower(): v for k, v in r.headers.items()}
        total   = 0
        max_pts = sum(v[1] for v in scored.values())
        rows    = []
        for header, (name, pts) in scored.items():
            present = header in h_lower
            if present:
                total += pts
            rows.append((name, present, pts, h_lower.get(header, "")))
        grade = ("A+" if total >= 95 else "A" if total >= 85 else "B" if total >= 70
                 else "C" if total >= 50 else "D" if total >= 30 else "F")
        gc = LGRN if grade in ("A+","A") else (LYLW if grade in ("B","C") else LRED)
        print()
        print(f"  {BOLD}Score:{RST}  {gc}{BOLD}{total}/{max_pts}   Grade: {grade}{RST}\n")
        print(f"  {BOLD}{LCYN}{'HEADER':<22}{'PTS':<6}{'STATUS':<10}VALUE{RST}")
        hline("─", DIM, 75)
        for name, present, pts, val in rows:
            col = LGRN if present else LRED
            print(f"  {col}{name:<22}{pts:<6}{'✔' if present else '✘':<10}{RST}"
                  f"{DIM}{val[:35]}{RST}")
        history_log(94, "Security Headers Score",
                    {"url": url, "score": total, "grade": grade})
    except Exception as e:
        status_err(str(e))


# ── 95: DNS History Lookup ───────────────────────────────────────────────────

def mod_dns_history():
    mod_header("DNS HISTORY LOOKUP", "Historical DNS records via HackerTarget", "🕰", LBLU)
    domain = ask("Domain (e.g. example.com)")
    if not domain:
        return
    print()
    try:
        r = requests.get(f"https://api.hackertarget.com/hostsearch/?q={domain}",
                         timeout=10)
        if r.status_code == 200 and "error" not in r.text.lower():
            lines = r.text.strip().splitlines()
            status_ok(f"Found {len(lines)} host record(s)")
            print()
            print(f"  {BOLD}{LCYN}{'HOSTNAME':<40}IP{RST}")
            hline("─", DIM, 60)
            for line in lines[:30]:
                parts = line.split(",")
                if len(parts) == 2:
                    print(f"  {LWHT}{parts[0]:<40}{RST}{LCYN}{parts[1]}{RST}")
        else:
            status_warn("No historical data found")
    except Exception as e:
        status_err(str(e))
    try:
        r2 = requests.get(f"https://api.hackertarget.com/dnslookup/?q={domain}",
                          timeout=10)
        if r2.status_code == 200 and "error" not in r2.text.lower():
            print()
            status_info("Current DNS records:")
            for line in r2.text.strip().splitlines():
                print(f"  {DIM}{line}{RST}")
    except: pass
    history_log(95, "DNS History Lookup", {"domain": domain})


# ── 96: Multi-Port Banner Scan ───────────────────────────────────────────────

def mod_banner_scan():
    mod_header("MULTI-PORT BANNER SCAN", "Grab banners from multiple common ports", "🏷", LBLU)
    host = ask("Host / IP")
    if not host:
        return
    ports = {21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP", 80:"HTTP",
             110:"POP3", 143:"IMAP", 443:"HTTPS", 3306:"MySQL",
             5432:"Postgres", 6379:"Redis", 8080:"HTTP-Alt", 27017:"MongoDB"}
    print()
    print(f"  {BOLD}{LCYN}{'PORT':<8}{'SERVICE':<12}BANNER{RST}")
    hline("─", DIM, 70)
    results = []
    for port, svc in ports.items():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            s.connect((host, port))
            if port in (80, 8080):
                s.sendall(b"HEAD / HTTP/1.0\r\nHost: " + host.encode() + b"\r\n\r\n")
            elif port == 25:
                s.sendall(b"EHLO test\r\n")
            raw    = s.recv(256).decode("utf-8", "replace").strip()
            banner = raw.splitlines()[0][:55] if raw else ""
            s.close()
            print(f"  {LGRN}{str(port)+'/tcp':<8}{RST}{LWHT}{svc:<12}{RST}{DIM}{banner}{RST}")
            results.append({"port": port, "service": svc, "banner": banner})
        except:
            print(f"  {DIM}{str(port)+'/tcp':<8}{svc:<12}closed/filtered{RST}")
    history_log(96, "Multi-Port Banner Scan", {"host": host, "open": results})


# ── 97: Network Topology (TTL hop map) ──────────────────────────────────────

def mod_net_topology():
    mod_header("NETWORK TOPOLOGY", "Map route hops via TTL probing", "🗺", LBLU)
    target = ask("Target (IP or domain)")
    if not target:
        return
    try:
        target_ip = socket.gethostbyname(target)
    except:
        target_ip = target
    print()
    print(f"  {BOLD}{LCYN}{'HOP':<6}{'RTT':<12}{'IP / HOST'}{RST}")
    hline("─", DIM, 60)
    for ttl in range(1, 21):
        try:
            if platform.system().lower() == "windows":
                cmd = ["ping", "-n", "1", "-i", str(ttl), "-w", "1000", target]
            else:
                cmd = ["ping", "-c", "1", "-t", str(ttl), "-W", "1", target]
            t0 = time.time()
            r  = subprocess.run(cmd, capture_output=True, text=True, timeout=3)
            rtt = round((time.time() - t0) * 1000, 1)
            ip_m = re.search(r"(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})", r.stdout)
            ip   = ip_m.group(1) if ip_m else "*"
            try:
                hostname = socket.gethostbyaddr(ip)[0][:35] if ip != "*" else ""
            except:
                hostname = ""
            col = LGRN if rtt < 50 else (LYLW if rtt < 150 else LRED)
            print(f"  {LYLW}{ttl:<6}{RST}{col}{str(rtt)+' ms':<12}{RST}"
                  f"{LWHT}{ip}{RST}  {DIM}{hostname}{RST}")
            if ip == target_ip:
                break
        except:
            print(f"  {LYLW}{ttl:<6}{RST}{DIM}{'*':<12}timeout{RST}")
    history_log(97, "Network Topology", {"target": target})


# ── 98: Open Port Knock Detector ─────────────────────────────────────────────

def mod_port_knock():
    mod_header("PORT KNOCK DETECTOR", "Detect port-knock sequences by scanning sequences", "👊", LBLU)
    host  = ask("Host / IP")
    start = int(ask("Start port", "7000"))
    end   = int(ask("End port",   "7010"))
    if not host:
        return
    print()
    status_info(f"Scanning ports {start}–{end} on {host}...")
    print()
    open_ports = []
    for port in range(start, end + 1):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.4)
        if s.connect_ex((host, port)) == 0:
            print(f"  {LGRN}[OPEN]{RST}  {port}/tcp")
            open_ports.append(port)
        else:
            print(f"  {DIM}[----]{RST}  {port}/tcp  filtered/closed")
        s.close()
    print()
    if not open_ports:
        status_info("No ports open in this range — possible port-knock protection")
    else:
        status_ok(f"Open: {open_ports}")
    history_log(98, "Port Knock Detector", {"host": host, "range": f"{start}-{end}",
                                             "open": open_ports})


# ── 99: History Viewer ───────────────────────────────────────────────────────

def mod_history_viewer():
    mod_header("HISTORY VIEWER", "Browse saved session history", "📖", LCYN)
    if not HISTORY_DIR.exists():
        status_warn("No history yet — run some modules first.")
        return
    days = sorted([d for d in HISTORY_DIR.iterdir() if d.is_dir()], reverse=True)
    if not days:
        status_warn("History directory is empty.")
        return
    print()
    print(f"  {BOLD}{LCYN}Available dates:{RST}")
    for i, day in enumerate(days[:10], 1):
        count = len(list(day.glob("*.json")))
        print(f"    {LYLW}[{i}]{RST}  {day.name}  {DIM}({count} entries){RST}")
    print()
    choice = ask("Select date number", "1")
    try:
        idx     = int(choice) - 1
        day_dir = days[idx]
    except:
        day_dir = days[0]
    files = sorted(day_dir.glob("*.json"), reverse=True)
    print()
    print(f"  {BOLD}{LCYN}{'TIME':<10}{'ID':<5}{'MODULE':<35}FIRST VALUE{RST}")
    hline("─", DIM, 72)
    for fpath in files[:50]:
        try:
            with open(fpath, encoding="utf-8") as fh:
                entry = json.load(fh)
            ts   = entry.get("timestamp", "")[-8:][:5]
            mid  = entry.get("module_id", "")
            name = entry.get("module_name", "")[:32]
            data = entry.get("data", {})
            inp  = str(list(data.values())[0])[:30] if data else ""
            print(f"  {DIM}{ts:<10}{RST}{LYLW}{str(mid):<5}{RST}{LWHT}{name:<35}{RST}{DIM}{inp}{RST}")
        except:
            pass
    print()
    detail = ask("Enter filename (without .json) to view full entry — or Enter to skip", "")
    if detail:
        target_file = day_dir / (detail + ".json")
        if target_file.exists():
            with open(target_file, encoding="utf-8") as fh:
                content = json.load(fh)
            print()
            print(f"  {LCYN}{json.dumps(content, indent=4, default=str)}{RST}")
        else:
            status_err("File not found")


# ── 100: History Clear ───────────────────────────────────────────────────────

def mod_history_clear():
    mod_header("HISTORY CLEAR", "Permanently delete all history files", "🗑", LRED)
    if not HISTORY_DIR.exists():
        status_warn("No history to clear.")
        return
    total = sum(1 for _ in HISTORY_DIR.rglob("*.json"))
    print()
    status_warn(f"This will permanently delete {total} history file(s) from:")
    print(f"  {LBLU}{HISTORY_DIR}{RST}")
    print()
    confirm = ask("Type YES to confirm deletion", "")
    if confirm.strip().upper() == "YES":
        import shutil
        shutil.rmtree(HISTORY_DIR)
        HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        status_ok("History cleared.")
    else:
        status_info("Aborted — nothing deleted.")


# ════════════════════════════════════════════════════════════════════════════
# MENU DATA  (full 100 modules)
# ════════════════════════════════════════════════════════════════════════════

# ════════════════════════════════════════════════════════════════════════════
# AUTO-UPDATE SYSTEM
# Checks GitHub for a newer version and prompts the user to update.
# ════════════════════════════════════════════════════════════════════════════

CURRENT_VERSION  = "8.2.1"
GITHUB_RAW_VER   = "https://raw.githubusercontent.com/piolunson/koolti-tool/main/version.txt"
GITHUB_REPO_URL  = "https://github.com/piolunson/koolti-tool"

def _version_tuple(v: str):
    try:
        return tuple(int(x) for x in v.strip().split("."))
    except:
        return (0, 0, 0)

def check_for_update(silent: bool = False):
    try:
        r = requests.get(GITHUB_RAW_VER, timeout=4)
        if r.status_code != 200:
            return
        latest = r.text.strip()
        if _version_tuple(latest) > _version_tuple(CURRENT_VERSION):
            print()
            print(f"  {BG_LMAG}{BLK}{BOLD}  UPDATE AVAILABLE  {RST}  "
                  f"{DIM}v{CURRENT_VERSION}{RST} → {LGRN}{BOLD}v{latest}{RST}")
            print(f"  {LBLU}{ULIN}{GITHUB_REPO_URL}/releases{RST}")
            print()
        elif not silent:
            status_ok(f"Already on the latest version (v{CURRENT_VERSION})")
    except:
        if not silent:
            status_warn("Could not reach GitHub to check for updates")

def mod_check_update():
    mod_header("CHECK FOR UPDATE", "Compare current version with GitHub", "🔄", LCYN)
    check_for_update(silent=False)


# ════════════════════════════════════════════════════════════════════════════
# PLUGIN SYSTEM
# Loads external modules from ~/kooltitool/plugins/
# Each plugin is a .py file with a register() function that returns a dict.
#
# Plugin file format (~kooltitool/plugins/my_plugin.py):
#
#   def run():
#       print("Hello from my plugin!")
#
#   def register():
#       return {
#           "name": "My Plugin",
#           "description": "Does something cool",
#           "category": "NET",   # NET / WEB / CRY / SYS / UTL
#           "author": "yourname",
#           "version": "1.0.0",
#           "run": run,
#       }
# ════════════════════════════════════════════════════════════════════════════

PLUGINS_DIR     = Path.home() / "kooltitool" / "plugins"
_loaded_plugins = {}   # { slot_number: plugin_dict }
PLUGIN_SLOT_START = 200


def plugins_init():
    PLUGINS_DIR.mkdir(parents=True, exist_ok=True)
    readme = PLUGINS_DIR / "HOW_TO_WRITE_A_PLUGIN.md"
    if not readme.exists():
        readme.write_text(
            "# How to write a koolti-tool plugin\n\n"
            "Create a .py file in this folder with the following structure:\n\n"
            "```python\n"
            "def run():\n"
            "    print(\'Hello from my plugin!\')\n\n"
            "def register():\n"
            "    return {\n"
            "        \'name\':        \'My Plugin\',\n"
            "        \'description\': \'Does something cool\',\n"
            "        \'category\'   : \'NET\',\n"
            "        \'author\'     : \'yourname\',\n"
            "        \'version\'    : \'1.0.0\',\n"
            "        \'run\'        : run,\n"
            "    }\n"
            "```\n\n"
            "Restart koolti-tool after adding a plugin.\n"
            "Plugins load as module numbers 200, 201, 202...\n\n"
            "Contact piolunson@proton.me if you want your plugin\n"
            "included in the official release.\n",
            encoding="utf-8"
        )


def load_plugins() -> dict:
    global _loaded_plugins
    _loaded_plugins = {}
    plugins_init()
    slot = PLUGIN_SLOT_START
    py_files = sorted(PLUGINS_DIR.glob("*.py"))
    for fpath in py_files:
        if fpath.name.startswith("_"):
            continue
        try:
            import importlib.util
            spec   = importlib.util.spec_from_file_location(fpath.stem, fpath)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            if hasattr(module, "register"):
                plugin = module.register()
                if isinstance(plugin, dict) and callable(plugin.get("run")):
                    plugin["_file"] = fpath.name
                    _loaded_plugins[slot] = plugin
                    slot += 1
        except Exception as e:
            print(f"  {LRED}Plugin load error ({fpath.name}): {e}{RST}")
    return _loaded_plugins


def mod_plugin_list():
    mod_header("PLUGIN MANAGER", "Manage external plugins", "🧩", LCYN)
    plugins = _loaded_plugins
    print()
    if not plugins:
        status_warn("No plugins loaded.")
        status_info(f"Place .py plugin files in:")
        print(f"  {LBLU}{PLUGINS_DIR}{RST}")
        print()
        status_info("See HOW_TO_WRITE_A_PLUGIN.md in that folder for instructions.")
        return
    print(f"  {BOLD}{LCYN}{'SLOT':<6}{'NAME':<28}{'VER':<8}{'AUTHOR':<16}{'CAT':<6}FILE{RST}")
    hline("─", DIM, 80)
    for slot, p in plugins.items():
        print(f"  {LYLW}{slot:<6}{RST}"
              f"{LWHT}{p.get('name','?')[:26]:<28}{RST}"
              f"{DIM}{p.get('version','?'):<8}{RST}"
              f"{LGRN}{p.get('author','?')[:14]:<16}{RST}"
              f"{LCYN}{p.get('category','?'):<6}{RST}"
              f"{DIM}{p.get('_file','?')}{RST}")
    print()
    status_info(f"Run a plugin by typing its slot number (200, 201...)")
    status_info(f"Plugin folder: {PLUGINS_DIR}")


# ── FAVOURITES ───────────────────────────────────────────────────────────────
FAVOURITES_FILE = Path.home() / "kooltitool" / "favourites.json"

def favourites_load() -> list:
    try:
        return json.loads(FAVOURITES_FILE.read_text())
    except:
        return []

def favourites_save(favs: list):
    FAVOURITES_FILE.parent.mkdir(parents=True, exist_ok=True)
    FAVOURITES_FILE.write_text(json.dumps(favs))

def mod_favourites():
    mod_header("FAVOURITES", "Save and run your favourite modules", "⭐", LYLW)
    favs = favourites_load()
    all_mods = {nr: name for nr, name, _, _ in MENU_DATA}
    print()
    if favs:
        print(f"  {BOLD}{LCYN}Your favourites:{RST}\n")
        for i, nr in enumerate(favs, 1):
            name = all_mods.get(nr, f"Module {nr}")
            print(f"  {LYLW}[{i}]{RST}  {LWHT}{nr:>3}. {name}{RST}")
    else:
        status_warn("No favourites saved yet.")
    print()
    print(f"  {DIM}[a] Add   [r] Remove   [run] Run a favourite   [Enter] Back{RST}")
    choice = ask("Action", "")
    if choice == "a":
        raw = ask("Module number to add")
        try:
            nr = int(raw)
            if nr in all_mods and nr not in favs:
                favs.append(nr)
                favourites_save(favs)
                status_ok(f"Added: {all_mods[nr]}")
            elif nr in favs:
                status_warn("Already in favourites")
            else:
                status_err("Module not found")
        except:
            status_err("Invalid number")
    elif choice == "r":
        raw = ask("Module number to remove")
        try:
            nr = int(raw)
            if nr in favs:
                favs.remove(nr)
                favourites_save(favs)
                status_ok(f"Removed: {all_mods.get(nr, nr)}")
            else:
                status_warn("Not in favourites")
        except:
            status_err("Invalid number")
    elif choice == "run":
        raw = ask("Which favourite? (enter number 1-5)")
        try:
            idx = int(raw) - 1
            nr  = favs[idx]
            if nr in ACTIONS:
                ACTIONS[nr]()
        except:
            status_err("Invalid choice")


# ── COMMAND HISTORY ───────────────────────────────────────────────────────────
_CMD_HISTORY: list = []
_CMD_INDEX:   int  = -1
CMD_HISTORY_FILE = Path.home() / "kooltitool" / "cmd_history.json"
CMD_HISTORY_MAX  = 50

def cmd_history_load():
    global _CMD_HISTORY
    try:
        _CMD_HISTORY = json.loads(CMD_HISTORY_FILE.read_text())
    except:
        _CMD_HISTORY = []

def cmd_history_push(cmd: str):
    global _CMD_HISTORY
    if cmd and (not _CMD_HISTORY or _CMD_HISTORY[-1] != cmd):
        _CMD_HISTORY.append(cmd)
        if len(_CMD_HISTORY) > CMD_HISTORY_MAX:
            _CMD_HISTORY = _CMD_HISTORY[-CMD_HISTORY_MAX:]
    try:
        CMD_HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        CMD_HISTORY_FILE.write_text(json.dumps(_CMD_HISTORY))
    except:
        pass

def input_with_history(prompt: str) -> str:
    """
    readline-powered input with arrow key history on Linux/Mac.
    Falls back to plain input() on Windows.
    """
    try:
        import readline
        readline.clear_history()
        for item in _CMD_HISTORY:
            readline.add_history(item)
        val = input(prompt).strip()
        if val:
            cmd_history_push(val)
        return val
    except ImportError:
        val = input(prompt).strip()
        if val:
            cmd_history_push(val)
        return val


# ── MODULE SEARCH ─────────────────────────────────────────────────────────────
def mod_search():
    mod_header("MODULE SEARCH", "Find modules by name or keyword", "🔍", LCYN)
    query = ask("Search (name, keyword, category)").lower().strip()
    if not query:
        return
    results = [(nr, name, cat) for nr, name, cat, _ in MENU_DATA
               if query in name.lower() or query in cat.lower()]
    print()
    if results:
        print(f"  {BOLD}{LCYN}{'#':<6}{'MODULE':<35}CATEGORY{RST}")
        hline("─", DIM, 55)
        for nr, name, cat in results:
            cat_color = CATEGORIES.get(cat, ('', LCYN, ''))[1]
            print(f"  {LYLW}{nr:<6}{RST}{LWHT}{name:<35}{RST}{cat_color}{cat}{RST}")
        print()
        status_info(f"Found {len(results)} module(s)  —  enter a number to run it")
        raw = ask("Run module (Enter to skip)", "")
        if raw:
            try:
                nr = int(raw)
                if nr in ACTIONS:
                    ACTIONS[nr]()
                else:
                    status_err("Module not found")
            except:
                pass
    else:
        status_warn(f"No modules found for '{query}'")
        print()
        status_info("Try: ip, dns, port, hash, ssl, web, crypto, sys, net...")


# ── NEW WEB MODULES ───────────────────────────────────────────────────────────

def mod_xss_scanner():
    mod_header("XSS SCANNER", "Test for reflected XSS vulnerabilities", "💥", LMAG)
    url   = ask("URL (e.g. https://example.com/search?q=test)")
    param = ask("Parameter to test", "q")
    if not url or not param:
        return
    payloads = [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "'\"><script>alert(1)</script>",
        "<svg onload=alert(1)>",
        "javascript:alert(1)",
        "<body onload=alert(1)>",
        "'-alert(1)-'",
        "<iframe src=javascript:alert(1)>",
        "\"><img src=x onerror=alert(1)>",
        "{{7*7}}",
    ]
    indicators = ["<script>alert", "onerror=alert", "onload=alert",
                  "javascript:alert", "<svg onload"]
    print()
    print(f"  {BOLD}{LCYN}{'PAYLOAD':<38}{'STATUS':<8}REFLECTED?{RST}")
    hline("─", DIM, 60)
    for payload in payloads:
        try:
            r   = requests.get(url, params={param: payload}, timeout=6,
                               headers={"User-Agent": "Mozilla/5.0"})
            ref = any(ind.lower() in r.text.lower() for ind in indicators)
            col = LRED if ref else LGRN
            note = "REFLECTED — possible XSS!" if ref else "not reflected"
            print(f"  {col}{payload[:37]:<38}{r.status_code:<8}{note}{RST}")
        except Exception as e:
            print(f"  {DIM}{payload[:37]:<38}{'ERR':<8}{str(e)[:20]}{RST}")
    history_log(106, "XSS Scanner", {"url": url, "param": param})


def mod_directory_brute():
    mod_header("DIRECTORY BRUTEFORCER", "Discover hidden paths on a web server", "📂", LMAG)
    url = ask("Base URL (e.g. https://example.com)")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    url = url.rstrip("/")
    wordlist = [
        "admin","login","dashboard","api","v1","v2","backup","config",
        "test","dev","staging","uploads","files","images","static","assets",
        "css","js","fonts","includes","vendor","lib","src","app","data",
        "db","sql","logs","log","tmp","temp","cache","old","new","www",
        "web","portal","panel","manage","manager","cp","controlpanel",
        "phpmyadmin","pma","mysql","adminer","wp-admin","wp-login",
        "xmlrpc","robots","sitemap","readme","license","changelog",
        ".git","env",".env","composer.json","package.json","config.php",
    ]
    print()
    status_info(f"Bruteforcing {len(wordlist)} paths on {BOLD}{url}{RST}...")
    print()
    found = []
    headers = {"User-Agent": "Mozilla/5.0"}
    for i, path in enumerate(wordlist):
        progress_bar(i, len(wordlist), 38, path)
        try:
            r = requests.get(f"{url}/{path}", timeout=4, headers=headers,
                             allow_redirects=False)
            if r.status_code in (200, 301, 302, 403):
                col = (LGRN if r.status_code == 200
                       else LYLW if r.status_code in (301, 302)
                       else LCYN)
                found.append((path, r.status_code))
                print(f"\r  {col}[{r.status_code}]{RST}  /{path:<35}            ")
        except:
            pass
    progress_bar(len(wordlist), len(wordlist), 38, "Done")
    print("\n")
    status_info(f"Found {len(found)} path(s)")
    history_log(107, "Directory Bruteforcer", {"url": url, "found": found})


def mod_api_fuzzer():
    mod_header("API ENDPOINT FUZZER", "Discover common REST API endpoints", "🔌", LMAG)
    base = ask("Base API URL (e.g. https://api.example.com)")
    if not base:
        return
    if not base.startswith("http"):
        base = "https://" + base
    base = base.rstrip("/")
    endpoints = [
        "/api","/api/v1","/api/v2","/api/v3",
        "/v1","/v2","/v3",
        "/api/users","/api/user","/api/auth","/api/login",
        "/api/register","/api/token","/api/refresh",
        "/api/admin","/api/config","/api/settings",
        "/api/status","/api/health","/api/ping",
        "/api/docs","/api/swagger","/swagger.json",
        "/openapi.json","/.well-known/openid-configuration",
        "/api/keys","/api/data","/api/export",
        "/graphql","/graphiql","/api/graphql",
    ]
    methods = ["GET", "POST"]
    print()
    status_info(f"Scanning {len(endpoints)} endpoints...")
    print()
    print(f"  {BOLD}{LCYN}{'STATUS':<8}{'METHOD':<7}ENDPOINT{RST}")
    hline("─", DIM, 60)
    found = []
    for ep in endpoints:
        for method in methods:
            try:
                r = requests.request(method, base + ep, timeout=4,
                                     headers={"User-Agent": "Mozilla/5.0"},
                                     allow_redirects=False)
                if r.status_code not in (404, 410):
                    col = (LGRN if r.status_code < 300
                           else LYLW if r.status_code < 400
                           else LCYN if r.status_code == 403
                           else LRED)
                    print(f"  {col}{r.status_code:<8}{method:<7}{base+ep}{RST}")
                    found.append({"method": method, "endpoint": ep,
                                  "status": r.status_code})
            except:
                pass
    print()
    status_info(f"Found {len(found)} active endpoint(s)")
    history_log(108, "API Endpoint Fuzzer", {"base": base, "found": found})


def mod_email_harvester():
    mod_header("EMAIL HARVESTER", "Extract email addresses from a web page", "📧", LMAG)
    url = ask("URL")
    if not url:
        return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        r      = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        emails = list(set(re.findall(
            r'[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}', r.text)))
        print()
        if emails:
            status_ok(f"Found {len(emails)} email address(es):")
            print()
            for email in sorted(emails):
                print(f"  {LGRN}→{RST}  {LWHT}{email}{RST}")
        else:
            status_warn("No email addresses found on this page")
        history_log(109, "Email Harvester", {"url": url, "emails": emails})
    except Exception as e:
        status_err(str(e))


def mod_http_smuggling_detector():
    mod_header("HTTP SMUGGLING DETECTOR", "Detect potential HTTP request smuggling", "🚢", LMAG)
    host = ask("Host (e.g. example.com)")
    if not host:
        return
    print()
    status_info("Sending CL.TE and TE.CL probe requests...")
    print()
    results = []
    for name, headers, body in [
        ("CL.TE probe",
         {"Host": host, "Content-Length": "6", "Transfer-Encoding": "chunked",
          "Connection": "keep-alive"},
         "0\r\n\r\nX"),
        ("TE.CL probe",
         {"Host": host, "Content-Length": "3", "Transfer-Encoding": "chunked",
          "Connection": "keep-alive"},
         "1\r\nX\r\n0\r\n\r\n"),
    ]:
        try:
            r = requests.post(f"https://{host}/", headers=headers,
                              data=body, timeout=8)
            col = LYLW if r.status_code in (400, 408, 500, 501) else LGRN
            note = "anomalous response — investigate!" if r.status_code in (400,408,500,501) else "normal"
            print(f"  {col}{name:<20}{RST}  HTTP {r.status_code}  {DIM}{note}{RST}")
            results.append({"probe": name, "status": r.status_code})
        except Exception as e:
            print(f"  {DIM}{name:<20}{RST}  ERR: {str(e)[:35]}")
    print()
    status_warn("This is a passive probe only — manual verification required")
    history_log(110, "HTTP Smuggling Detector", {"host": host})


# ── NEW CRYPTO MODULES ────────────────────────────────────────────────────────

def mod_vigenere_cipher():
    mod_header("VIGENÈRE CIPHER", "Polyalphabetic substitution cipher", "🔑", LYLW)
    print(f"  {LYLW}[1]{RST} Encrypt    {LYLW}[2]{RST} Decrypt\n")
    mode = ask("Mode", "1")
    text = ask("Text")
    key  = ask("Key (letters only, e.g. SECRET)")
    if not text or not key:
        return
    key = re.sub(r'[^a-zA-Z]', '', key).upper()
    if not key:
        status_err("Key must contain at least one letter")
        return
    result = []
    ki = 0
    for ch in text:
        if ch.isalpha():
            shift = ord(key[ki % len(key)]) - ord('A')
            base  = ord('A') if ch.isupper() else ord('a')
            if mode == "2":
                shift = -shift
            result.append(chr((ord(ch) - base + shift) % 26 + base))
            ki += 1
        else:
            result.append(ch)
    out = ''.join(result)
    print()
    label = "Encrypted" if mode == "1" else "Decrypted"
    status_ok(f"{label}: {BOLD}{LYLW}{out}{RST}")
    status_info(f"Key used: {key}")


def mod_atbash_cipher():
    mod_header("ATBASH CIPHER", "Mirror alphabet substitution (A↔Z, B↔Y...)", "🔃", LYLW)
    text = ask("Text")
    if not text:
        return
    result = ''.join(
        chr(ord('Z') - (ord(c) - ord('A'))) if c.isupper() else
        chr(ord('z') - (ord(c) - ord('a'))) if c.islower() else c
        for c in text
    )
    print()
    status_ok(f"Result: {BOLD}{LYLW}{result}{RST}")
    status_info("Atbash is symmetric — apply again to reverse")


def mod_hash_identifier():
    mod_header("HASH IDENTIFIER", "Identify hash type from its length and format", "🔎", LYLW)
    h = ask("Paste hash").strip()
    if not h:
        return
    length = len(h)
    is_hex = bool(re.fullmatch(r'[0-9a-fA-F]+', h))
    is_b64 = bool(re.fullmatch(r'[A-Za-z0-9+/=]+', h))
    print()
    candidates = []
    if is_hex:
        if length == 32:  candidates += ["MD5", "NTLM", "MD4"]
        if length == 40:  candidates += ["SHA-1", "MySQL 4.x"]
        if length == 56:  candidates += ["SHA-224"]
        if length == 64:  candidates += ["SHA-256", "SHA3-256", "BLAKE2s"]
        if length == 96:  candidates += ["SHA-384"]
        if length == 128: candidates += ["SHA-512", "SHA3-512", "Whirlpool"]
        if length == 16:  candidates += ["MD5 (half)", "MySQL 3.x"]
    if h.startswith("$2") and len(h) == 60:
        candidates = ["bcrypt"]
    if h.startswith("$6$"):
        candidates = ["SHA-512 crypt (Linux shadow)"]
    if h.startswith("$1$"):
        candidates = ["MD5 crypt"]
    if h.startswith("$5$"):
        candidates = ["SHA-256 crypt"]
    if is_b64 and not is_hex:
        candidates.append("Base64 encoded hash")
    print(f"  {LCYN}Hash       {RST}  {DIM}{h[:60]}{'...' if len(h)>60 else ''}{RST}")
    print(f"  {LCYN}Length     {RST}  {LWHT}{length} chars{RST}")
    print(f"  {LCYN}Format     {RST}  {LWHT}{'hex' if is_hex else 'base64' if is_b64 else 'other'}{RST}")
    print()
    if candidates:
        print(f"  {BOLD}{LGRN}Likely hash type(s):{RST}")
        for c in candidates:
            print(f"  {LGRN}→{RST}  {LWHT}{c}{RST}")
    else:
        status_warn("Unknown hash type")
        status_info("Could be a custom hash, salted hash, or non-standard encoding")


def mod_password_generator_advanced():
    mod_header("ADVANCED PASSWORD GENERATOR", "Generate passwords with custom rules", "🎲", LYLW)
    print(f"  {DIM}Presets:{RST}")
    print(f"  {LYLW}[1]{RST} PIN (6 digits)")
    print(f"  {LYLW}[2]{RST} WiFi password (12 chars, mixed)")
    print(f"  {LYLW}[3]{RST} API key (32 chars, hex)")
    print(f"  {LYLW}[4]{RST} Passphrase (4 words)")
    print(f"  {LYLW}[5]{RST} Custom\n")
    preset = ask("Choose preset", "5")
    count  = int(ask("How many?", "5"))
    print()
    WORDS = ["correct","horse","battery","staple","dragon","monkey","castle",
             "shadow","hunter","ranger","silver","falcon","thunder","phantom",
             "cobra","viper","storm","blaze","iron","steel","ghost","frost"]
    results = []
    for _ in range(count):
        if preset == "1":
            pwd = ''.join(random.choices(string.digits, k=6))
        elif preset == "2":
            chars = string.ascii_letters + string.digits + "!@#$"
            pwd   = ''.join(random.choices(chars, k=12))
        elif preset == "3":
            pwd = hashlib.md5(str(random.random()).encode()).hexdigest() + \
                  hashlib.md5(str(random.random()).encode()).hexdigest()
            pwd = pwd[:32]
        elif preset == "4":
            pwd = '-'.join(random.choices(WORDS, k=4))
        else:
            length     = int(ask("Length", "16"))
            use_upper  = ask("Uppercase? (y/n)", "y").lower() == 'y'
            use_digits = ask("Digits? (y/n)", "y").lower() == 'y'
            use_spec   = ask("Special chars? (y/n)", "y").lower() == 'y'
            chars = string.ascii_lowercase
            if use_upper:  chars += string.ascii_uppercase
            if use_digits: chars += string.digits
            if use_spec:   chars += "!@#$%^&*_+-="
            pwd = ''.join(random.choices(chars, k=length))
        results.append(pwd)
        print(f"  {LWHT}{pwd}{RST}")
    print()
    save = ask("Save to file? (y/n)", "n").lower()
    if save == 'y':
        fname = Path("generated_passwords.txt")
        fname.write_text('\n'.join(results))
        status_ok(f"Saved to {fname}")


def mod_encoding_detector():
    mod_header("ENCODING DETECTOR", "Detect and decode common encodings automatically", "🧬", LYLW)
    text = ask("Paste encoded text")
    if not text:
        return
    print()
    results = []
    t = text.strip()
    # Base64
    try:
        dec = base64.b64decode(t + '==').decode('utf-8', 'replace')
        if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in dec[:50]):
            results.append(("Base64", dec[:80]))
    except: pass
    # Hex
    try:
        clean = t.replace(' ','').replace(':','')
        dec   = bytes.fromhex(clean).decode('utf-8','replace')
        if all(32 <= ord(c) <= 126 or c in '\n\r\t' for c in dec[:50]):
            results.append(("Hex", dec[:80]))
    except: pass
    # URL encoding
    try:
        from urllib.parse import unquote
        dec = unquote(t)
        if dec != t:
            results.append(("URL encoded", dec[:80]))
    except: pass
    # ROT13
    rot = t.translate(str.maketrans(
        'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz',
        'NOPQRSTUVWXYZABCDEFGHIJKLMnopqrstuvwxyzabcdefghijklm'))
    if rot != t and rot.isprintable():
        results.append(("ROT13", rot[:80]))
    # Binary
    try:
        parts = t.split()
        if all(all(c in '01' for c in p) and len(p) == 8 for p in parts):
            dec = ''.join(chr(int(p, 2)) for p in parts)
            results.append(("Binary", dec[:80]))
    except: pass
    # Caesar brute (only if short and alpha-heavy)
    alpha_ratio = sum(c.isalpha() for c in t) / max(len(t), 1)
    if alpha_ratio > 0.6 and len(t) < 100:
        for shift in range(1, 26):
            dec = ''.join(
                chr((ord(c) - (ord('A') if c.isupper() else ord('a')) + shift) % 26
                    + (ord('A') if c.isupper() else ord('a')))
                if c.isalpha() else c for c in t)
            if any(word in dec.lower() for word in ['the','and','that','have',
                                                      'this','with','from']):
                results.append((f"Caesar shift {shift}", dec[:80]))
                break
    if results:
        print(f"  {BOLD}{LGRN}Detected encoding(s):{RST}\n")
        for enc_type, decoded in results:
            print(f"  {LYLW}{enc_type:<20}{RST}  {LWHT}{decoded}{RST}")
    else:
        status_warn("Could not detect encoding automatically")
        status_info("Try: Base64, Hex, URL, Binary, ROT13, Caesar")







import shutil

# ═══════════════════════════════════════════════════════════════════════════
# TOOL INSTALLER
# ═══════════════════════════════════════════════════════════════════════════

TOOL_CATALOG = {
    "hashcat":    {"desc":"GPU hash cracker ~15B H/s",         "check":"hashcat",      "cat":"CRY", "win":"winget install hashcat",                          "lin":"sudo apt install hashcat"},
    "nmap":       {"desc":"Network mapper & port scanner",     "check":"nmap",         "cat":"NET", "win":"winget install nmap",                             "lin":"sudo apt install nmap"},
    "sqlmap":     {"desc":"Automatic SQL injection tool",      "check":"sqlmap",       "cat":"WEB", "win":"pip install sqlmap",                              "lin":"pip install sqlmap"},
    "nikto":      {"desc":"Web server vulnerability scanner",  "check":"nikto",        "cat":"WEB", "win":"winget install nikto",                            "lin":"sudo apt install nikto"},
    "gobuster":   {"desc":"Directory/DNS bruteforcer in Go",   "check":"gobuster",     "cat":"WEB", "win":"winget install OJ.gobuster",                      "lin":"sudo apt install gobuster"},
    "hydra":      {"desc":"Network login bruteforcer",         "check":"hydra",        "cat":"CRY", "win":"WSL: sudo apt install hydra",                     "lin":"sudo apt install hydra"},
    "subfinder":  {"desc":"Fast passive subdomain discovery",  "check":"subfinder",    "cat":"NET", "win":"go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest", "lin":"go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest"},
    "nuclei":     {"desc":"Fast vuln scanner with templates",  "check":"nuclei",       "cat":"WEB", "win":"go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest",       "lin":"go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest"},
    "ffuf":       {"desc":"Fast web fuzzer written in Go",     "check":"ffuf",         "cat":"WEB", "win":"go install github.com/ffuf/ffuf/v2@latest",        "lin":"sudo apt install ffuf"},
    "masscan":    {"desc":"Mass IP port scanner — very fast",  "check":"masscan",      "cat":"NET", "win":"Build from source or use WSL",                    "lin":"sudo apt install masscan"},
    "wpscan":     {"desc":"WordPress vulnerability scanner",   "check":"wpscan",       "cat":"WEB", "win":"gem install wpscan",                              "lin":"gem install wpscan"},
    "john":       {"desc":"John the Ripper password cracker",  "check":"john",         "cat":"CRY", "win":"winget install openwall.john",                    "lin":"sudo apt install john"},
    "netcat":     {"desc":"TCP/UDP network utility",           "check":"nc",           "cat":"NET", "win":"winget install ncat",                             "lin":"sudo apt install netcat-openbsd"},
    "curl":       {"desc":"HTTP request tool",                 "check":"curl",         "cat":"NET", "win":"winget install curl",                             "lin":"sudo apt install curl"},
    "whois":      {"desc":"WHOIS domain lookup (system)",      "check":"whois",        "cat":"NET", "win":"winget install whois",                            "lin":"sudo apt install whois"},
    "amass":      {"desc":"In-depth attack surface mapper",    "check":"amass",        "cat":"NET", "win":"winget install OWASP.amass",                      "lin":"go install github.com/owasp-amass/amass/v4/...@master"},
    "dirb":       {"desc":"Web content scanner",               "check":"dirb",         "cat":"WEB", "win":"Use WSL",                                         "lin":"sudo apt install dirb"},
    "enum4linux": {"desc":"Windows/Samba enumeration",         "check":"enum4linux",   "cat":"NET", "win":"Use WSL",                                         "lin":"sudo apt install enum4linux"},
    "aircrack-ng":{"desc":"WiFi network security toolkit",     "check":"aircrack-ng",  "cat":"NET", "win":"Download from aircrack-ng.org",                   "lin":"sudo apt install aircrack-ng"},
    "msfconsole": {"desc":"Metasploit penetration framework",  "check":"msfconsole",   "cat":"WEB", "win":"Download from metasploit.com",                    "lin":"curl https://raw.githubusercontent.com/rapid7/metasploit-omnibus/master/config/templates/metasploit-framework-wrappers/msfupdate.erb > msfinstall && chmod 755 msfinstall && ./msfinstall"},
}

TOOLS_STATE_FILE = Path.home() / "kooltitool" / "tools_state.json"

def tools_state_load():
    try:    return json.loads(TOOLS_STATE_FILE.read_text())
    except: return {}

def tools_state_save(s):
    TOOLS_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    TOOLS_STATE_FILE.write_text(json.dumps(s, indent=2))

def tool_installed(name):
    check = TOOL_CATALOG.get(name, {}).get("check", name)
    return shutil.which(check) is not None

def mod_tool_installer():
    mod_header("TOOL INSTALLER", "Install and run external security tools", "🔧", LMAG)
    os_key = "win" if platform.system().lower() == "windows" else "lin"
    while True:
        clear()
        mod_header("TOOL INSTALLER", "Install and run external security tools", "🔧", LMAG)
        print(f"  {BOLD}{LCYN}{'#':<4}{'TOOL':<14}{'CAT':<6}{'STATUS':<14}DESCRIPTION{RST}")
        hline("─", DIM, 72)
        for i, (name, info) in enumerate(TOOL_CATALOG.items(), 1):
            ok  = tool_installed(name)
            col = LGRN if ok else LRED
            tag = f"{LGRN}installed{RST}" if ok else f"{LRED}missing  {RST}"
            print(f"  {LYLW}{i:<4}{RST}{name:<14}{DIM}{info['cat']:<6}{RST}{col}{tag}{RST}  {DIM}{info['desc']}{RST}")
        print()
        print(f"  {DIM}[nr]{RST} show install cmd   {DIM}[run nr]{RST} run tool   {DIM}[all]{RST} show all missing   {DIM}[0]{RST} back")
        print()
        cmd = ask("Choice", "").strip().lower()
        if cmd in ("0", "back", ""):
            return
        if cmd == "all":
            print()
            names = list(TOOL_CATALOG.keys())
            for name in names:
                if not tool_installed(name):
                    print(f"  {LRED}✘{RST}  {BOLD}{name:<14}{RST}  {LWHT}{TOOL_CATALOG[name][os_key]}{RST}")
            print(); pause(); continue
        run_mode = cmd.startswith("run ")
        if run_mode:
            cmd = cmd[4:].strip()
        try:
            idx  = int(cmd) - 1
            name = list(TOOL_CATALOG.keys())[idx]
            info = TOOL_CATALOG[name]
            print()
            print(f"  {BOLD}{name.upper()}{RST}  —  {info['desc']}")
            print(f"\n  {LCYN}Install command ({platform.system()}):{RST}")
            print(f"  {LWHT}{info[os_key]}{RST}\n")
            if tool_installed(name):
                status_ok(f"{name} is already installed")
                target = ask("Target for quick run (Enter to skip)", "")
                if target:
                    run_cmds = {
                        "nmap":     ["nmap", "-sV", target],
                        "sqlmap":   ["sqlmap", "-u", target, "--batch"],
                        "nikto":    ["nikto", "-h", target],
                        "gobuster": ["gobuster", "dir", "-u", target, "-w", "wordlist.txt"],
                        "nuclei":   ["nuclei", "-u", target, "-silent"],
                        "subfinder":["subfinder", "-d", target, "-silent"],
                        "ffuf":     ["ffuf", "-u", target+"/FUZZ", "-w", "wordlist.txt"],
                        "masscan":  ["masscan", target, "-p1-1000", "--rate=500"],
                        "wpscan":   ["wpscan", "--url", target, "--enumerate"],
                        "amass":    ["amass", "enum", "-passive", "-d", target],
                        "dirb":     ["dirb", target],
                        "enum4linux":["enum4linux", "-a", target],
                        "curl":     ["curl", "-s", "-I", target],
                        "whois":    ["whois", target],
                        "nc":       ["nc", "-zv", "-w", "3", target, "80"],
                        "john":     ["john", "--show", target],
                        "hashcat":  ["hashcat", "--help"],
                        "hydra":    ["hydra", "--help"],
                        "aircrack-ng":["aircrack-ng", "--help"],
                        "msfconsole":["msfconsole", "-q", "-x", "version; exit"],
                    }
                    run_cmd = run_cmds.get(name, [name, "--help"])
                    try: subprocess.run(run_cmd)
                    except Exception as e: status_err(str(e))
            else:
                status_warn(f"{name} not installed yet — copy the command above")
            pause()
        except (ValueError, IndexError):
            status_err("Invalid choice"); time.sleep(0.7)


# ═══════════════════════════════════════════════════════════════════════════
# TOOL WRAPPERS — modules 115-134
# ═══════════════════════════════════════════════════════════════════════════

def _need(tool):
    if not tool_installed(tool):
        status_err(f"{tool} not installed — use module [117] Tool Installer")
        return False
    return True

def mod_nmap_wrapper():
    mod_header("NMAP SCANNER", "Run nmap network scan", "🗺", LBLU)
    if not _need("nmap"): return
    target = ask("Target (IP, domain, or CIDR)")
    if not target: return
    print(f"\n  {DIM}[1] Quick(-F)  [2] Services(-sV)  [3] OS(-O)  [4] Full(-sV -O -A)  [5] Custom{RST}")
    p = ask("Preset", "2")
    flags = {
        "1": ["-F"], "2": ["-sV"], "3": ["-O"], "4": ["-sV", "-O", "-A"]
    }.get(p)
    if not flags:
        flags = ask("Flags", "-sV").split()
    print(); subprocess.run(["nmap"] + flags + [target])
    history_log(115, "Nmap", {"target": target})

def mod_sqlmap_wrapper():
    mod_header("SQLMAP", "Automatic SQL injection testing", "💉", LMAG)
    if not _need("sqlmap"): return
    url   = ask("Target URL (e.g. https://site.com/page?id=1)")
    param = ask("Parameter (empty=auto)", "")
    if not url: return
    cmd = ["sqlmap", "-u", url, "--batch", "--level=2"]
    if param: cmd += ["-p", param]
    print(); subprocess.run(cmd)
    history_log(116, "SQLMap", {"url": url})

def mod_gobuster_wrapper():
    mod_header("GOBUSTER", "Directory and DNS bruteforcer", "📂", LMAG)
    if not _need("gobuster"): return
    print(f"  {LYLW}[1]{RST} dir mode   {LYLW}[2]{RST} dns mode")
    mode   = ask("Mode", "1")
    target = ask("URL or domain"); wl = ask("Wordlist", "wordlist.txt")
    if not target: return
    if mode == "1": cmd = ["gobuster", "dir", "-u", target, "-w", wl, "-t", "20"]
    else:           cmd = ["gobuster", "dns", "-d", target, "-w", wl, "-t", "20"]
    print(); subprocess.run(cmd)
    history_log(118, "Gobuster", {"target": target})

def mod_nikto_wrapper():
    mod_header("NIKTO", "Web server vulnerability scanner", "🔍", LMAG)
    if not _need("nikto"): return
    target = ask("Target URL")
    if not target: return
    print(); subprocess.run(["nikto", "-h", target])
    history_log(119, "Nikto", {"target": target})

def mod_wpscan_wrapper():
    mod_header("WPSCAN", "WordPress vulnerability scanner", "🔒", LMAG)
    if not _need("wpscan"): return
    url   = ask("WordPress URL"); token = ask("API token (optional)", "")
    if not url: return
    cmd = ["wpscan", "--url", url, "--enumerate", "u,p,t,cb,dbe"]
    if token: cmd += ["--api-token", token]
    print(); subprocess.run(cmd)
    history_log(120, "WPScan", {"url": url})

def mod_nuclei_wrapper():
    mod_header("NUCLEI", "Fast vulnerability scanner", "⚡", LMAG)
    if not _need("nuclei"): return
    target = ask("Target URL or IP")
    if not target: return
    print(f"  {DIM}[1] default  [2] critical+high  [3] CVE only{RST}")
    p   = ask("Scan type", "1")
    cmd = ["nuclei", "-u", target, "-silent"]
    if p == "2": cmd += ["-severity", "critical,high"]
    if p == "3": cmd += ["-tags", "cve"]
    print(); subprocess.run(cmd)
    history_log(121, "Nuclei", {"target": target})

def mod_subfinder_wrapper():
    mod_header("SUBFINDER", "Passive subdomain discovery", "🔭", LBLU)
    if not _need("subfinder"): return
    domain = ask("Domain")
    if not domain: return
    print(); subprocess.run(["subfinder", "-d", domain, "-silent"])
    history_log(122, "Subfinder", {"domain": domain})

def mod_ffuf_wrapper():
    mod_header("FFUF", "Fast web fuzzer", "🎯", LMAG)
    if not _need("ffuf"): return
    url = ask("URL with FUZZ (e.g. https://site.com/FUZZ)")
    wl  = ask("Wordlist", "wordlist.txt")
    mc  = ask("Match codes", "200,301,302,403")
    if not url: return
    print(); subprocess.run(["ffuf", "-u", url, "-w", wl, "-mc", mc, "-c"])
    history_log(123, "FFUF", {"url": url})

def mod_hydra_wrapper():
    mod_header("HYDRA", "Network login bruteforcer", "🐍", LMAG)
    if not _need("hydra"): return
    target  = ask("Target (IP or domain)")
    service = ask("Service (ssh/ftp/http-post-form/...)", "ssh")
    user    = ask("Username or userlist (.txt)", "admin")
    passw   = ask("Password or passlist (.txt)", "wordlist.txt")
    if not target: return
    uf = "-L" if user.endswith(".txt")  else "-l"
    pf = "-P" if passw.endswith(".txt") else "-p"
    print(); subprocess.run(["hydra", uf, user, pf, passw, target, service])
    history_log(124, "Hydra", {"target": target, "service": service})

def mod_masscan_wrapper():
    mod_header("MASSCAN", "Extremely fast port scanner", "⚡", LBLU)
    if not _need("masscan"): return
    target = ask("Target IP or CIDR")
    ports  = ask("Ports", "1-1000")
    rate   = ask("Rate (packets/sec)", "1000")
    if not target: return
    status_warn("May require root/sudo on Linux")
    print(); subprocess.run(["masscan", target, f"-p{ports}", f"--rate={rate}"])
    history_log(125, "Masscan", {"target": target})

def mod_john_wrapper():
    mod_header("JOHN THE RIPPER", "Password hash cracker", "🔓", LYLW)
    if not _need("john"): return
    hfile = ask("Hash file path"); wl = ask("Wordlist (empty=default)", "")
    if not hfile: return
    cmd = ["john", hfile]
    if wl: cmd += [f"--wordlist={wl}"]
    print(); subprocess.run(cmd)
    subprocess.run(["john", "--show", hfile])
    history_log(126, "John", {"file": hfile})

def mod_curl_wrapper():
    mod_header("CURL TOOL", "HTTP requests via curl", "🌐", LBLU)
    if not _need("curl"): return
    url    = ask("URL"); method = ask("Method", "GET")
    header = ask("Header (e.g. Authorization: Bearer TOKEN)", "")
    data   = ask("POST data (empty=none)", "")
    if not url: return
    cmd = ["curl", "-s", "-i", "-X", method, url]
    if header: cmd += ["-H", header]
    if data:   cmd += ["-d", data]
    print(); subprocess.run(cmd)
    history_log(127, "Curl", {"url": url})

def mod_nc_wrapper():
    mod_header("NETCAT", "TCP/UDP network utility", "🔌", LBLU)
    nc = shutil.which("nc") or shutil.which("ncat") or shutil.which("netcat")
    if not nc: status_err("netcat not installed — use module [117]"); return
    print(f"  {LYLW}[1]{RST} Port check   {LYLW}[2]{RST} Banner grab   {LYLW}[3]{RST} Listen")
    mode = ask("Mode", "1")
    if mode == "3":
        port = ask("Listen port", "4444")
        print(); subprocess.run([nc, "-lvp", port])
    else:
        host = ask("Host"); port = ask("Port", "80")
        if not host: return
        if mode == "2":
            r = subprocess.run([nc, "-w", "3", host, port],
                               input=b"HEAD / HTTP/1.0\r\n\r\n", capture_output=True)
            print(r.stdout.decode("utf-8", "replace")[:500])
        else:
            r = subprocess.run([nc, "-zv", "-w", "3", host, port],
                               capture_output=True, text=True)
            out = r.stdout + r.stderr
            (status_ok if ("open" in out.lower() or "succeeded" in out.lower())
             else status_err)(f"Port {port} on {host}")
    history_log(128, "Netcat", {})

def mod_whois_system():
    mod_header("WHOIS (SYSTEM)", "System whois command", "📋", LBLU)
    if not _need("whois"): return
    target = ask("Domain or IP")
    if not target: return
    print(); subprocess.run(["whois", target])
    history_log(129, "WHOIS System", {"target": target})

def mod_amass_wrapper():
    mod_header("AMASS", "In-depth attack surface mapper", "🗺", LBLU)
    if not _need("amass"): return
    domain = ask("Domain")
    if not domain: return
    print(); subprocess.run(["amass", "enum", "-passive", "-d", domain])
    history_log(130, "Amass", {"domain": domain})

def mod_dirb_wrapper():
    mod_header("DIRB", "Web content scanner", "📁", LMAG)
    if not _need("dirb"): return
    url = ask("Target URL"); wl = ask("Wordlist (empty=default)", "")
    if not url: return
    cmd = ["dirb", url] + ([wl] if wl else [])
    print(); subprocess.run(cmd)
    history_log(131, "DIRB", {"url": url})

def mod_enum4linux_wrapper():
    mod_header("ENUM4LINUX", "Windows/Samba enumeration", "🪟", LBLU)
    if not _need("enum4linux"): return
    target = ask("Target IP")
    if not target: return
    print(); subprocess.run(["enum4linux", "-a", target])
    history_log(132, "Enum4Linux", {"target": target})

def mod_aircrack_wrapper():
    mod_header("AIRCRACK-NG", "WiFi security toolkit", "📡", LBLU)
    if not _need("aircrack-ng"): return
    cap = ask("Capture file (.cap/.pcap)"); wl = ask("Wordlist", "wordlist.txt")
    if not cap: return
    print(); subprocess.run(["aircrack-ng", "-w", wl, cap])
    history_log(133, "Aircrack-ng", {"file": cap})

def mod_metasploit_wrapper():
    mod_header("METASPLOIT", "Penetration testing framework", "💀", LRED)
    if not _need("msfconsole"): return
    status_warn("Launching msfconsole — type 'exit' to return")
    print(); subprocess.run(["msfconsole"])


# ═══════════════════════════════════════════════════════════════════════════
# OSINT & EXTRA MODULES — 135-151
# ═══════════════════════════════════════════════════════════════════════════

def mod_haveibeenpwned():
    mod_header("BREACH CHECK (HIBP)", "Check email/password in data breaches", "🔓", LMAG)
    print(f"  {LYLW}[1]{RST} Email (requires API key)   {LYLW}[2]{RST} Password (free, k-anonymity)\n")
    mode = ask("Mode", "2")
    if mode == "1":
        email   = ask("Email address")
        api_key = ask("HIBP API key (get at haveibeenpwned.com/API/Key)")
        if not email: return
        try:
            r = requests.get(f"https://haveibeenpwned.com/api/v3/breachedaccount/{email}",
                             headers={"hibp-api-key": api_key, "User-Agent": "koolti-tool"}, timeout=10)
            if r.status_code == 200:
                breaches = r.json()
                status_warn(f"Found in {len(breaches)} breach(es)!")
                for b in breaches[:10]:
                    print(f"  {LRED}•{RST}  {b.get('Name','?')}  {DIM}({b.get('BreachDate','?')}){RST}")
            elif r.status_code == 404: status_ok("Not found in any known breaches")
            elif r.status_code == 401: status_warn("Invalid or missing API key")
            else: status_err(f"HTTP {r.status_code}")
        except Exception as e: status_err(str(e))
    else:
        pwd = ask("Password to check")
        if not pwd: return
        try:
            h      = hashlib.sha1(pwd.encode()).hexdigest().upper()
            pre, suf = h[:5], h[5:]
            r = requests.get(f"https://api.pwnedpasswords.com/range/{pre}", timeout=8)
            match = next((l for l in r.text.splitlines() if l.split(":")[0] == suf), None)
            if match: status_warn(f"Found {match.split(':')[1]} times in breach databases!")
            else:     status_ok("Password NOT in known breach databases")
        except Exception as e: status_err(str(e))
    history_log(135, "Breach Check", {"mode": mode})


def mod_username_checker():
    mod_header("USERNAME CHECKER", "Check username across platforms", "👤", LMAG)
    username = ask("Username")
    if not username: return
    platforms = {
        "GitHub":     f"https://github.com/{username}",
        "Twitter/X":  f"https://twitter.com/{username}",
        "Instagram":  f"https://www.instagram.com/{username}",
        "Reddit":     f"https://www.reddit.com/user/{username}",
        "TikTok":     f"https://www.tiktok.com/@{username}",
        "YouTube":    f"https://www.youtube.com/@{username}",
        "Twitch":     f"https://www.twitch.tv/{username}",
        "Steam":      f"https://steamcommunity.com/id/{username}",
        "GitLab":     f"https://gitlab.com/{username}",
        "Medium":     f"https://medium.com/@{username}",
        "Dev.to":     f"https://dev.to/{username}",
        "Pinterest":  f"https://www.pinterest.com/{username}",
        "LinkedIn":   f"https://www.linkedin.com/in/{username}",
        "Pastebin":   f"https://pastebin.com/u/{username}",
        "HackerNews": f"https://news.ycombinator.com/user?id={username}",
    }
    print(); status_info(f"Checking {len(platforms)} platforms...")
    print(); found = []
    for name, url in platforms.items():
        try:
            r = requests.get(url, timeout=5, headers={"User-Agent": "Mozilla/5.0"}, allow_redirects=True)
            if r.status_code == 200 and "not found" not in r.text.lower()[:300]:
                print(f"  {LGRN}✔{RST}  {name:<15}  {LBLU}{url}{RST}"); found.append(name)
            else:
                print(f"  {LRED}✘{RST}  {DIM}{name}{RST}")
        except: print(f"  {LYLW}?{RST}  {DIM}{name}  (timeout){RST}")
    print(); status_info(f"Found on {len(found)}/{len(platforms)} platforms")
    history_log(136, "Username Checker", {"username": username, "found": found})


def mod_cve_lookup():
    mod_header("CVE LOOKUP", "Look up CVE vulnerability details", "⚠", LRED)
    cve = ask("CVE ID (e.g. CVE-2021-44228)").upper().strip()
    if not cve: return
    if not cve.startswith("CVE-"): cve = "CVE-" + cve
    try:
        r = requests.get(f"https://cveawg.mitre.org/api/cve/{cve}", timeout=10)
        if r.status_code == 200:
            d    = r.json()
            meta = d.get("cveMetadata", {})
            cont = d.get("containers", {}).get("cna", {})
            print()
            print(f"  {LCYN}ID          {RST}  {LRED}{BOLD}{cve}{RST}")
            print(f"  {LCYN}State       {RST}  {LWHT}{meta.get('state','N/A')}{RST}")
            print(f"  {LCYN}Published   {RST}  {LWHT}{meta.get('datePublished','N/A')[:10]}{RST}")
            descs = cont.get("descriptions", [])
            if descs: print(f"\n  {LCYN}Description:{RST}\n  {DIM}{descs[0].get('value','')[:300]}{RST}")
            for m in cont.get("metrics", [])[:1]:
                for v in m.values():
                    if isinstance(v, dict) and "baseScore" in v:
                        sc  = v["baseScore"]
                        col = LRED if sc >= 7 else (LYLW if sc >= 4 else LGRN)
                        print(f"\n  {LCYN}CVSS Score  {RST}  {col}{BOLD}{sc}{RST}")
        elif r.status_code == 404: status_err(f"{cve} not found")
        else: status_err(f"HTTP {r.status_code}")
    except Exception as e: status_err(str(e))
    history_log(137, "CVE Lookup", {"cve": cve})


def mod_tech_cve_checker():
    mod_header("TECH CVE CHECKER", "Find CVEs for a technology + version", "⚠", LRED)
    tech    = ask("Technology (e.g. apache, nginx, wordpress)")
    version = ask("Version (e.g. 2.4.49, empty=latest)", "")
    if not tech: return
    query = f"{tech} {version}".strip()
    try:
        r = requests.get("https://services.nvd.nist.gov/rest/json/cves/2.0",
                         params={"keywordSearch": query, "resultsPerPage": 8}, timeout=12)
        if r.status_code == 200:
            d = r.json(); vulns = d.get("vulnerabilities", [])
            print(); status_info(f"Found {d.get('totalResults',0)} CVEs for '{query}'"); print()
            for v in vulns[:6]:
                cve   = v.get("cve", {}); cid = cve.get("id", "")
                desc  = cve.get("descriptions",[{}])[0].get("value","N/A")[:90]
                score = "N/A"
                for mk in ["cvssMetricV31","cvssMetricV30","cvssMetricV2"]:
                    if mk in cve.get("metrics",{}):
                        score = cve["metrics"][mk][0].get("cvssData",{}).get("baseScore","N/A"); break
                col = LRED if isinstance(score,float) and score>=7 else DIM
                print(f"  {LRED}{cid:<22}{RST}  Score: {col}{score}{RST}")
                print(f"  {DIM}{desc}...{RST}\n")
        else: status_err(f"NVD API: HTTP {r.status_code}")
    except Exception as e: status_err(str(e))
    history_log(138, "Tech CVE Checker", {"tech": tech})


def mod_shodan_search():
    mod_header("SHODAN SEARCH", "Search Shodan by keyword or filter", "🔭", LMAG)
    api_key = ask("Shodan API key (free at shodan.io)")
    query   = ask("Query (e.g. apache port:80 country:PL)")
    if not api_key or not query: return
    try:
        r = requests.get("https://api.shodan.io/shodan/host/search",
                         params={"key": api_key, "query": query}, timeout=12)
        if r.status_code == 200:
            d = r.json(); matches = d.get("matches", [])
            print(); status_ok(f"Total: {d.get('total',0)} results"); print()
            for m in matches[:10]:
                ip   = m.get("ip_str",""); port = m.get("port","")
                org  = m.get("org","N/A"); cc   = m.get("location",{}).get("country_code","")
                print(f"  {LGRN}{ip:<18}{RST}:{LYLW}{port:<8}{RST}{DIM}{cc:<5}{org}{RST}")
        elif r.status_code == 401: status_err("Invalid API key")
        else: status_err(f"HTTP {r.status_code}")
    except Exception as e: status_err(str(e))
    history_log(139, "Shodan Search", {"query": query})


def mod_bulk_dns():
    mod_header("BULK DNS RESOLVER", "Resolve multiple domains at once", "📋", LBLU)
    print(f"  {DIM}Enter domains one per line, empty line = done.{RST}\n")
    domains = []
    while True:
        d = input(f"  {LCYN}Domain {len(domains)+1}:{RST} ").strip()
        if not d: break
        domains.append(d)
    if not domains: return
    print(); print(f"  {BOLD}{LCYN}{'DOMAIN':<35}{'IPv4':<18}STATUS{RST}"); hline("─", DIM, 60)
    for d in domains:
        try:
            ip = socket.gethostbyname(d); print(f"  {LWHT}{d:<35}{RST}{LGRN}{ip:<18}{RST}OK")
        except: print(f"  {LWHT}{d:<35}{RST}{LRED}{'N/A':<18}{RST}FAILED")
    history_log(140, "Bulk DNS", {"count": len(domains)})


def mod_ip_blacklist_check():
    mod_header("IP BLACKLIST CHECK", "Check IP against DNSBL blacklists", "🚫", LMAG)
    ip = ask("IP address")
    if not ip: return
    try:
        parts      = ip.split(".")
        rev        = ".".join(reversed(parts))
    except: status_err("Invalid IP"); return
    blacklists = ["zen.spamhaus.org","bl.spamcop.net","dnsbl.sorbs.net",
                  "b.barracudacentral.org","cbl.abuseat.org","dnsbl-1.uceprotect.net",
                  "db.wpbl.info","spam.dnsbl.sorbs.net","ix.dnsbl.manitu.net","dnsbl.inps.de"]
    print(); status_info(f"Checking {len(blacklists)} blacklists..."); print()
    listed = []
    for bl in blacklists:
        try:
            socket.gethostbyname(f"{rev}.{bl}")
            print(f"  {LRED}[LISTED]{RST}  {bl}"); listed.append(bl)
        except: print(f"  {LGRN}[CLEAN] {RST}  {DIM}{bl}{RST}")
    print()
    if listed: status_warn(f"Listed on {len(listed)} blacklist(s)!")
    else:      status_ok("Clean — not on any checked blacklist")
    history_log(141, "IP Blacklist", {"ip": ip, "listed": listed})


def mod_port_service_id():
    mod_header("PORT SERVICE IDENTIFIER", "Look up what service runs on a port", "🔍", LBLU)
    port = ask("Port number")
    if not port: return
    DB = {
        "20":"FTP-data","21":"FTP","22":"SSH","23":"Telnet","25":"SMTP","53":"DNS",
        "67":"DHCP","68":"DHCP","80":"HTTP","110":"POP3","123":"NTP","135":"RPC",
        "137":"NetBIOS","139":"NetBIOS","143":"IMAP","161":"SNMP","389":"LDAP",
        "443":"HTTPS","445":"SMB","465":"SMTPS","514":"Syslog","587":"SMTP-sub",
        "636":"LDAPS","993":"IMAPS","995":"POP3S","1080":"SOCKS","1194":"OpenVPN",
        "1433":"MSSQL","1521":"Oracle","2049":"NFS","2082":"cPanel","3306":"MySQL",
        "3389":"RDP","4444":"Metasploit","5432":"PostgreSQL","5900":"VNC",
        "5985":"WinRM","6379":"Redis","6667":"IRC","8080":"HTTP-Proxy",
        "8443":"HTTPS-alt","8888":"Jupyter","9200":"Elasticsearch","27017":"MongoDB",
    }
    svc = DB.get(str(port), "Unknown service")
    print()
    print(f"  {LCYN}Port    {RST}  {LWHT}{port}/tcp{RST}")
    col = LGRN if svc != "Unknown service" else LYLW
    print(f"  {LCYN}Service {RST}  {col}{BOLD}{svc}{RST}")
    history_log(142, "Port Service ID", {"port": port, "service": svc})


def mod_http_timer():
    mod_header("HTTP RESPONSE TIMER", "Measure server response time", "⏱", LMAG)
    url   = ask("URL"); count = int(ask("Requests", "5"))
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    print(); times = []
    for i in range(count):
        try:
            t0 = time.time()
            requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            ms = round((time.time()-t0)*1000, 1); times.append(ms)
            col = LGRN if ms < 500 else (LYLW if ms < 1500 else LRED)
            print(f"  {DIM}[{i+1}]{RST}  {col}{ms:>8.1f} ms{RST}  {DIM}{'█'*int(ms/100)}{RST}")
        except Exception as e: print(f"  {DIM}[{i+1}]{RST}  {LRED}ERR{RST}")
    if times:
        print()
        print(f"  {LCYN}Min{RST}  {LGRN}{min(times):.1f}ms{RST}   {LCYN}Max{RST}  {LRED}{max(times):.1f}ms{RST}   {LCYN}Avg{RST}  {LWHT}{sum(times)/len(times):.1f}ms{RST}")
    history_log(143, "HTTP Timer", {"url": url})


def mod_network_calculator():
    mod_header("NETWORK CALCULATOR", "Advanced subnet calculations", "🧮", LCYN)
    try: import ipaddress
    except: status_err("ipaddress not available"); return
    cidr = ask("CIDR (e.g. 10.0.0.0/8)")
    if not cidr: return
    try:
        net = ipaddress.IPv4Network(cidr, strict=False)
        print()
        for k, v in [("Network",net.network_address),("Broadcast",net.broadcast_address),
                     ("Netmask",net.netmask),("Wildcard",net.hostmask),("Prefix",f"/{net.prefixlen}"),
                     ("Hosts",f"{net.num_addresses-2:,}"),("Type","Private" if net.is_private else "Public")]:
            print(f"  {LCYN}{k:<12}{RST}  {LWHT}{v}{RST}")
        split = ask("Split into subnets? Enter new prefix (e.g. 24) or Enter to skip", "")
        if split:
            subs = list(net.subnets(new_prefix=int(split)))
            status_info(f"Split into {len(subs)} /{split} subnets:")
            for s in subs[:10]: print(f"  {LGRN}→{RST}  {LWHT}{s}{RST}  {DIM}({s.num_addresses-2} hosts){RST}")
            if len(subs) > 10: status_info(f"... and {len(subs)-10} more")
    except Exception as e: status_err(str(e))
    history_log(144, "Network Calculator", {"cidr": cidr})


def mod_file_strings():
    mod_header("FILE STRINGS EXTRACTOR", "Extract printable strings from any file", "📝", LGRN)
    path    = ask("File path"); min_len = int(ask("Min string length", "4"))
    if not path or not os.path.exists(path): status_err("File not found"); return
    try:
        data = open(path, "rb").read()
        strings = []; cur = []
        for b in data:
            if 32 <= b <= 126: cur.append(chr(b))
            else:
                if len(cur) >= min_len: strings.append("".join(cur))
                cur = []
        if len(cur) >= min_len: strings.append("".join(cur))
        print(); status_ok(f"Found {len(strings)} strings")
        save = ask("Save to file? (y/n)", "n").lower()
        if save == "y":
            out = Path(path).stem + "_strings.txt"
            Path(out).write_text("\n".join(strings)); status_ok(f"Saved: {out}")
        else:
            for s in strings[:40]: print(f"  {DIM}{s}{RST}")
            if len(strings) > 40: status_info(f"... and {len(strings)-40} more")
    except Exception as e: status_err(str(e))
    history_log(145, "File Strings", {"path": path})


def mod_headers_compare():
    mod_header("HEADERS COMPARE", "Compare HTTP headers of two URLs", "🔄", LMAG)
    url1 = ask("First URL"); url2 = ask("Second URL")
    if not url1 or not url2: return
    if not url1.startswith("http"): url1 = "https://" + url1
    if not url2.startswith("http"): url2 = "https://" + url2
    try:
        r1 = requests.get(url1, timeout=8); r2 = requests.get(url2, timeout=8)
        all_keys = sorted(set(list(r1.headers.keys()) + list(r2.headers.keys())))
        print(); print(f"  {BOLD}{LCYN}{'HEADER':<30}{'URL1':<28}URL2{RST}"); hline("─",DIM,75)
        for k in all_keys:
            v1 = r1.headers.get(k, f"{LRED}(missing){RST}")
            v2 = r2.headers.get(k, f"{LRED}(missing){RST}")
            diff = r1.headers.get(k) != r2.headers.get(k)
            col  = LYLW if diff else DIM
            print(f"  {col}{k:<30}{RST}{str(v1)[:26]:<28}{str(v2)[:26]}{'  ◄DIFF' if diff else ''}")
    except Exception as e: status_err(str(e))
    history_log(146, "Headers Compare", {"url1": url1, "url2": url2})


def mod_open_ports_banner():
    mod_header("OPEN PORTS + BANNER", "Scan ports and grab banners", "🏷", LBLU)
    target = ask("Host / IP")
    ports  = ask("Ports (e.g. 22,80,443 or 1-1000)", "21,22,25,80,110,443,3306,8080")
    if not target: return
    port_list = []
    for part in ports.split(","):
        p = part.strip()
        if "-" in p:
            a, b = p.split("-"); port_list.extend(range(int(a), int(b)+1))
        else:
            try: port_list.append(int(p))
            except: pass
    print(); status_info(f"Scanning {len(port_list)} ports...")
    print()
    for port in port_list:
        try:
            s = socket.socket(); s.settimeout(1)
            if s.connect_ex((target, port)) == 0:
                banner = ""
                try:
                    if port in (80, 8080, 443): s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
                    raw = s.recv(128).decode("utf-8","replace").strip()
                    banner = raw.splitlines()[0][:55] if raw else ""
                except: pass
                print(f"  {LGRN}[OPEN]{RST}  {str(port)+'/tcp':<10}  {DIM}{banner}{RST}")
            s.close()
        except: pass
    history_log(147, "Open Ports Banner", {"target": target})


def mod_google_cache():
    mod_header("GOOGLE CACHE CHECKER", "Check if Google has a cached version", "🗃", LMAG)
    url = ask("URL")
    if not url: return
    if not url.startswith("http"): url = "https://" + url
    cache_url = f"https://webcache.googleusercontent.com/search?q=cache:{url}"
    try:
        r = requests.get(cache_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if r.status_code == 200:
            status_ok("Google cache found!")
            print(f"\n  {LBLU}{ULIN}{cache_url}{RST}")
        elif r.status_code == 404: status_warn("No Google cache found")
        else: status_warn(f"HTTP {r.status_code}")
    except Exception as e: status_err(str(e))
    history_log(148, "Google Cache", {"url": url})


def mod_ip_geofence():
    mod_header("IP GEOFENCE CHECKER", "Check if IP is from expected country", "🌍", LBLU)
    ip      = ask("IP address"); country = ask("Expected country code (e.g. PL, US)").upper()
    if not ip or not country: return
    try:
        r = requests.get(f"http://ip-api.com/json/{ip}", timeout=6).json()
        if r.get("status") == "success":
            actual = r.get("countryCode","").upper()
            print()
            print(f"  {LCYN}IP       {RST}  {LWHT}{ip}{RST}")
            print(f"  {LCYN}Actual   {RST}  {LWHT}{r.get('country')} ({actual}){RST}")
            print(f"  {LCYN}Expected {RST}  {LWHT}{country}{RST}")
            print()
            if actual == country: status_ok(f"IP IS from {country}")
            else:                 status_warn(f"IP is NOT from {country} — it is from {actual}")
    except Exception as e: status_err(str(e))
    history_log(149, "IP Geofence", {"ip": ip, "country": country})


def mod_asn_bgp_route():
    mod_header("ASN / BGP ROUTE LOOKUP", "Find BGP routes for an IP or ASN", "🛣", LBLU)
    target = ask("IP address or ASN (e.g. AS15169)")
    if not target: return
    try:
        if target.upper().startswith("AS"):
            r = requests.get(f"https://api.bgpview.io/asn/{target[2:]}/prefixes", timeout=10)
        else:
            r = requests.get(f"https://api.bgpview.io/ip/{target}", timeout=10)
        d = r.json()
        if d.get("status") == "ok":
            data = d.get("data", {}); print()
            if "ipv4_prefixes" in data:
                for p in data["ipv4_prefixes"][:8]:
                    print(f"  {LGRN}→{RST}  {LWHT}{p.get('prefix',''):<22}{RST}  {DIM}{p.get('name','')}{RST}")
            else:
                for prefix in data.get("prefixes",[])[:3]:
                    asn = prefix.get("asn",{})
                    print(f"  {LCYN}ASN {RST}  AS{asn.get('asn','')}  {LWHT}{asn.get('name','')}{RST}  {DIM}{prefix.get('prefix','')}{RST}")
        else: status_err("No data found")
    except Exception as e: status_err(str(e))
    history_log(150, "ASN BGP Route", {"target": target})


# ═══════════════════════════════════════════════════════════════════════════
# BUNDLES
# ═══════════════════════════════════════════════════════════════════════════

def _bs(title):
    print(f"\n  {LYLW}{BOLD}▶  {title}{RST}"); hline("─", DIM, 50)


def bundle_website():
    mod_header("WEBSITE BUNDLE", "Full recon on a domain or IP", "🌐", LCYN)
    target = ask("Domain or IP")
    if not target: return
    if target.startswith("https://"): target = target[8:]
    elif target.startswith("http://"):  target = target[7:]
    target = target.split("/")[0]; url = "https://" + target
    res = {}; print(f"\n  {LCYN}Target:{RST}  {BOLD}{target}{RST}\n"); hline("═", LCYN)

    _bs("IP & GeoIP")
    try:
        ip = socket.gethostbyname(target); res["ip"] = ip; status_ok(f"IP: {ip}")
        d = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        if d.get("status") == "success":
            print(f"  {LCYN}Country{RST}  {d.get('country')}  |  {LCYN}ISP{RST}  {d.get('isp')}")
    except Exception as e: status_err(str(e))

    _bs("DNS")
    try:
        for r in socket.getaddrinfo(target, 80, socket.AF_INET): print(f"  {LGRN}→{RST}  {r[4][0]}  {DIM}IPv4{RST}")
    except Exception as e: status_err(str(e))

    _bs("WHOIS")
    try:
        r = requests.get(f"https://rdap.org/domain/{target}", timeout=7)
        if r.status_code == 200:
            d = r.json(); print(f"  {LCYN}Registrar{RST}  {d.get('port43','N/A')}")
            for ev in d.get("events",[])[:2]: print(f"  {DIM}{ev.get('eventAction',''):<20}  {ev.get('eventDate','')[:10]}{RST}")
    except Exception as e: status_err(str(e))

    _bs("HTTP Headers")
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True)
        res["status"] = r.status_code; res["server"] = r.headers.get("Server","")
        print(f"  {LCYN}Status{RST}  {r.status_code}  |  {LCYN}Server{RST}  {r.headers.get('Server','N/A')}  |  {LCYN}HTTPS{RST}  {'✔' if r.url.startswith('https') else '✘'}")
    except Exception as e: status_err(str(e))

    _bs("SSL Certificate")
    try:
        import ssl as _ssl; ctx = _ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=target) as s:
            s.settimeout(6); s.connect((target, 443)); cert = s.getpeercert()
        subj = dict(x[0] for x in cert.get("subject",[])); print(f"  {LCYN}CN{RST}  {subj.get('commonName','N/A')}")
        try:
            from datetime import datetime as _dt
            exp  = _dt.strptime(cert.get("notAfter",""), "%b %d %H:%M:%S %Y %Z")
            days = (exp - _dt.utcnow()).days
            (status_ok if days > 30 else status_err)(f"Expires in {days} days")
        except: pass
    except Exception as e: status_warn(str(e))

    _bs("CMS / Tech Stack")
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"Mozilla/5.0"}); html = r.text.lower()
        cms = {"WordPress":["wp-content","wp-includes"],"Joomla":["/administrator/"],"Drupal":["Drupal.settings"],"Shopify":["cdn.shopify.com"],"React":["react"],"jQuery":["jquery.min"],"Cloudflare":["cf-ray"]}
        detected = [n for n,sigs in cms.items() if any(s.lower() in html for s in sigs)]
        res["cms"] = detected
        [status_ok(f"Detected: {BOLD}{d}{RST}") for d in detected] if detected else status_warn("No known tech detected")
    except Exception as e: status_err(str(e))

    _bs("Open Ports")
    open_p = []
    for port, svc in {80:"HTTP",443:"HTTPS",21:"FTP",22:"SSH",25:"SMTP",3306:"MySQL",8080:"Alt"}.items():
        s = socket.socket(); s.settimeout(0.8)
        if s.connect_ex((target, port)) == 0: print(f"  {LGRN}[OPEN]{RST}  {port}/{svc}"); open_p.append(port)
        s.close()
    res["open_ports"] = open_p

    _bs("Security Headers")
    try:
        r = requests.get(url, timeout=8); h = {k.lower():v for k,v in r.headers.items()}
        total = 0; scored = {"strict-transport-security":20,"content-security-policy":20,"x-frame-options":15,"x-content-type-options":15,"referrer-policy":10}
        for hh, pts in scored.items():
            present = hh in h; total += pts if present else 0
            print(f"  {'✔' if present else '✘'}  {hh}")
        grade = "A" if total>=70 else "B" if total>=50 else "C" if total>=30 else "F"
        print(f"\n  {BOLD}Score: {total}/80  Grade: {grade}{RST}"); res["sec_score"] = total
    except Exception as e: status_err(str(e))

    _bs("Subdomains")
    subs = []
    for sub in ["www","mail","api","dev","staging","cdn","ftp"]:
        try: ip = socket.gethostbyname(f"{sub}.{target}"); print(f"  {LGRN}✔{RST}  {sub}.{target}  →  {ip}"); subs.append(f"{sub}.{target}")
        except: pass
    res["subdomains"] = subs
    if not subs: status_warn("No subdomains found")

    print(); hline("═",LCYN); print(f"  {BOLD}{LCYN}BUNDLE COMPLETE — {target}{RST}\n")
    for k,v in [("IP",res.get("ip","N/A")),("Status",res.get("status","N/A")),("Server",res.get("server","N/A")),
                ("CMS",", ".join(res.get("cms",[])) or "unknown"),("Open ports",res.get("open_ports",[])),
                ("Subdomains",len(res.get("subdomains",[]))),("Score",f"{res.get('sec_score','N/A')}/80")]:
        print(f"  {LCYN}{k:<14}{RST}  {LWHT}{v}{RST}")
    hline("═",LCYN)
    history_log(901, "Website Bundle", {"target": target})


def bundle_hash():
    mod_header("HASH BUNDLE", "Auto-detect hash → crack it", "🔨", LYLW)
    h = ask("Paste hash").strip().lower()
    if not h: return
    lh = len(h); is_hex = bool(re.fullmatch(r'[0-9a-fA-F]+', h))
    cands = []
    if is_hex:
        if lh==32:  cands += [("MD5","md5"),("NTLM","ntlm")]
        if lh==40:  cands += [("SHA-1","sha1")]
        if lh==64:  cands += [("SHA-256","sha256")]
        if lh==128: cands += [("SHA-512","sha512")]
    if h.startswith("$2") and lh==60: cands = [("bcrypt","bcrypt")]
    if not cands: status_err("Unknown hash type"); return
    print(f"\n  {BOLD}Detected:{RST}")
    [print(f"  {LYLW}[{i}]{RST}  {n}") for i,(n,a) in enumerate(cands,1)]
    idx = int(ask("Which?","1"))-1; name,algo = cands[min(idx,len(cands)-1)]
    if algo == "bcrypt": status_warn("bcrypt — use hashcat"); return

    def mh(w):
        e = w.encode("utf-8","replace")
        if algo=="md5":    return hashlib.md5(e).hexdigest()
        if algo=="sha1":   return hashlib.sha1(e).hexdigest()
        if algo=="sha256": return hashlib.sha256(e).hexdigest()
        if algo=="sha512": return hashlib.sha512(e).hexdigest()
        if algo=="ntlm":
            try: return hashlib.new("md4",w.encode("utf-16le")).hexdigest()
            except: return ""
        return ""

    TOP = ["123456","password","admin","qwerty","letmein","welcome","monkey","dragon","pass123",
           "test123","root","toor","admin123","abc123","iloveyou","shadow","football","1234",
           "12345","123456789","000000","1111","passw0rd","haslo","polska","haslo123","test"]
    found=None; checked=0; t0=time.time()
    print(f"\n  {LCYN}[1/3]{RST} Dictionary...")
    for w in TOP:
        checked+=1
        if mh(w)==h: found=w; break
    if found:
        status_ok(f"FOUND: {LYLW}{BOLD}{found}{RST}  {DIM}(dict, {time.time()-t0:.3f}s, {checked} checked){RST}")
        history_log(902,"Hash Bundle",{"type":name,"found":True}); return

    wl = ask("Wordlist path (Enter to skip)","")
    if wl and Path(wl).exists():
        print(f"\n  {LCYN}[2/3]{RST} Wordlist...")
        with open(wl,encoding="utf-8",errors="replace") as f:
            for line in f:
                w=line.rstrip(); checked+=1
                if checked%100000==0: print(f"\r  {DIM}{checked:,} checked{RST}   ",end="",flush=True)
                if mh(w)==h: found=w; print(); break
        print()
    if found:
        status_ok(f"FOUND: {LYLW}{BOLD}{found}{RST}  {DIM}({checked:,} checked){RST}")
        history_log(902,"Hash Bundle",{"type":name,"found":True}); return

    print(f"\n  {LCYN}[3/3]{RST} Brute force...")
    cs_ch = ask("Charset [1]digits [2]+lower [3]+UPPER","2")
    cs = {"1":string.digits,"2":string.digits+string.ascii_lowercase,"3":string.digits+string.ascii_letters}.get(cs_ch,string.digits+string.ascii_lowercase)
    ml = int(ask("Max length","6")); t0=time.time()
    for ln in range(1,ml+1):
        status_info(f"Length {ln} — {len(cs)**ln:,}")
        for combo in itertools.product(cs,repeat=ln):
            w="".join(combo); checked+=1
            if checked%80000==0: print(f"\r  {DIM}{checked:,}  {checked/max(0.001,time.time()-t0)/1e3:.0f}K/s{RST}   ",end="",flush=True)
            if mh(w)==h: found=w; print(); break
        if found: break
    print()
    elapsed=time.time()-t0
    if found: status_ok(f"FOUND: {LYLW}{BOLD}{found}{RST}  {DIM}({checked:,} checked, {elapsed:.2f}s){RST}")
    else:     status_err(f"Not found  |  {checked:,} checked  |  {elapsed:.1f}s")
    history_log(902,"Hash Bundle",{"type":name,"found":bool(found)})


def bundle_email():
    mod_header("EMAIL BUNDLE", "Full analysis of an email address", "✉", LMAG)
    email = ask("Email address")
    if not email: return
    if not re.match(r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$', email):
        status_err("Invalid email format"); return
    user, domain = email.split("@", 1)
    print(); status_ok("Format valid")
    print(f"  {LCYN}User{RST}  {LWHT}{user}{RST}   {LCYN}Domain{RST}  {LWHT}{domain}{RST}")

    _bs("DNS Check")
    try:
        ip = socket.gethostbyname(domain); status_ok(f"Resolves → {ip}")
    except: status_err("Domain does not resolve"); return

    _bs("Disposable Email")
    disp = ["mailinator.com","tempmail.com","guerrillamail.com","yopmail.com","trashmail.com","maildrop.cc","10minutemail.com"]
    if domain.lower() in disp: status_warn("Known disposable domain!")
    else: status_ok("Not disposable")

    _bs("WHOIS for Domain")
    try:
        r = requests.get(f"https://rdap.org/domain/{domain}", timeout=8)
        if r.status_code == 200:
            d = r.json(); print(f"  {LCYN}Registrar{RST}  {d.get('port43','N/A')}")
    except Exception as e: status_err(str(e))

    _bs("Password Breach Check (k-anonymity)")
    pwd = ask("Check a password for breaches? (Enter to skip)","")
    if pwd:
        try:
            h=hashlib.sha1(pwd.encode()).hexdigest().upper(); pre,suf=h[:5],h[5:]
            r=requests.get(f"https://api.pwnedpasswords.com/range/{pre}",timeout=8)
            match=next((l for l in r.text.splitlines() if l.split(":")[0]==suf),None)
            if match: status_warn(f"Found {match.split(':')[1]} times in breaches!")
            else:     status_ok("Password not in breaches")
        except Exception as e: status_err(str(e))
    history_log(903,"Email Bundle",{"email":email})


def bundle_network_scan():
    mod_header("NETWORK SCAN BUNDLE", "Full network scan on a target", "🌐", LBLU)
    target = ask("IP, domain, or CIDR")
    if not target: return
    if target.startswith("https://"): target=target[8:]
    elif target.startswith("http://"): target=target[7:]
    target=target.split("/")[0]; print()

    _bs("Resolve & GeoIP")
    try:
        ip=socket.gethostbyname(target); status_ok(f"Resolved: {ip}")
        d=requests.get(f"http://ip-api.com/json/{ip}",timeout=5).json()
        if d.get("status")=="success": print(f"  {LCYN}Country{RST}  {d.get('country')}  |  {LCYN}ISP{RST}  {d.get('isp')}")
    except Exception as e: status_err(str(e))

    _bs("Port Scan")
    PORTS={21:"FTP",22:"SSH",23:"Telnet",25:"SMTP",53:"DNS",80:"HTTP",110:"POP3",143:"IMAP",443:"HTTPS",445:"SMB",1433:"MSSQL",3306:"MySQL",3389:"RDP",5432:"Postgres",5900:"VNC",6379:"Redis",8080:"HTTP-Alt",27017:"MongoDB"}
    open_p=[]
    for port,svc in PORTS.items():
        s=socket.socket(); s.settimeout(0.6)
        if s.connect_ex((target,port))==0: print(f"  {LGRN}[OPEN]{RST}  {str(port)+'/tcp':<10}  {svc}"); open_p.append(port)
        s.close()
    if not open_p: status_warn("No open ports found")

    _bs("Banner Grab")
    for port in open_p[:5]:
        try:
            s=socket.socket(); s.settimeout(2); s.connect((target,port))
            if port in(80,8080): s.sendall(b"HEAD / HTTP/1.0\r\n\r\n")
            banner=s.recv(128).decode("utf-8","replace").strip().splitlines()[0][:55]
            print(f"  {LYLW}{port:<8}{RST}  {DIM}{banner}{RST}"); s.close()
        except: pass

    _bs("Reverse DNS")
    try: status_ok(f"Hostname: {socket.gethostbyaddr(target)[0]}")
    except: status_warn("No reverse DNS")

    _bs("Traceroute (10 hops)")
    for ttl in range(1,11):
        try:
            cmd=(["ping","-n","1","-i",str(ttl),"-w","500",target] if platform.system().lower()=="windows"
                 else ["ping","-c","1","-t",str(ttl),"-W","1",target])
            r=subprocess.run(cmd,capture_output=True,text=True,timeout=3)
            m=re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})',r.stdout)
            ip=m.group(1) if m else "*"; print(f"  {LYLW}{ttl:<4}{RST}  {LWHT}{ip}{RST}")
            if ip==target: break
        except: print(f"  {LYLW}{ttl:<4}{RST}  {DIM}*{RST}")
    history_log(904,"Network Scan Bundle",{"target":target,"open":open_p})


def bundle_subdomain():
    mod_header("SUBDOMAIN BUNDLE", "Find all subdomains of a domain", "🕸", LBLU)
    domain = ask("Domain (e.g. example.com)")
    if not domain: return
    SUBS=["www","mail","ftp","smtp","pop","imap","webmail","admin","cpanel","vpn","api","dev",
          "test","staging","blog","shop","store","portal","app","mobile","m","ns1","ns2","dns",
          "mx","autodiscover","remote","cdn","static","media","assets","img","git","gitlab",
          "jira","jenkins","ci","forum","wiki","status","docs","help","support","chat","video",
          "office","beta","demo","old","new","backup","secure","vpn2","mail2","smtp2","cloud",
          "monitor","dashboard","panel","control","manage","admin2","dev2","test2","staging2",
          "pre","prod","uat","qa","integration","portal2","api2","app2","web","shop2"]
    print(); status_info(f"Checking {len(SUBS)} subdomains for {BOLD}{domain}{RST}..."); print()
    found=[]
    for i,sub in enumerate(SUBS):
        progress_bar(i,len(SUBS),38,sub)
        try:
            ip=socket.gethostbyname(f"{sub}.{domain}"); found.append((f"{sub}.{domain}",ip))
        except: pass
    progress_bar(len(SUBS),len(SUBS),38,"Done"); print("\n")
    if found:
        print(f"  {BOLD}{LGRN}{'SUBDOMAIN':<42}IP{RST}"); hline("─",DIM,60)
        for f,ip in found: print(f"  {LGRN}✔{RST}  {LWHT}{f:<40}{RST}  {LCYN}{ip}{RST}")
        print(); status_ok(f"Found {len(found)} subdomain(s)")
        if ask("HTTP check on found? (y/n)","n").lower()=="y":
            print()
            for full,_ in found:
                try:
                    r=requests.get(f"https://{full}",timeout=4,headers={"User-Agent":"Mozilla/5.0"})
                    print(f"  {LGRN if r.status_code<400 else LRED}{r.status_code}{RST}  {full}")
                except: print(f"  {DIM}ERR  {full}{RST}")
    else: status_warn("No subdomains found")
    history_log(905,"Subdomain Bundle",{"domain":domain,"found":[f for f,_ in found]})


def bundle_wordpress():
    mod_header("WORDPRESS BUNDLE", "Full WordPress security audit", "🔒", LMAG)
    url = ask("WordPress URL")
    if not url: return
    if not url.startswith("http"): url="https://"+url
    url=url.rstrip("/"); print()

    _bs("Detection")
    try:
        r=requests.get(url,timeout=8,headers={"User-Agent":"Mozilla/5.0"})
        if any(s in r.text for s in ["wp-content","wp-includes","wordpress"]): status_ok("WordPress detected")
        else: status_warn("WordPress not detected"); return
    except Exception as e: status_err(str(e)); return

    _bs("Version")
    try:
        r=requests.get(f"{url}/readme.html",timeout=6,headers={"User-Agent":"Mozilla/5.0"})
        m=re.search(r'Version (\d+\.\d+\.?\d*)',r.text)
        if m: status_warn(f"Version exposed: {BOLD}{m.group(1)}{RST}")
        else: status_ok("Version not in readme.html")
    except: pass

    _bs("Login Page")
    for path in ["/wp-login.php","/wp-admin","/wp-admin/admin.php"]:
        try:
            r=requests.get(url+path,timeout=6,headers={"User-Agent":"Mozilla/5.0"},allow_redirects=True)
            print(f"  {LYLW if r.status_code==200 else DIM}{r.status_code}  {url+path}{RST}")
        except: pass

    _bs("XML-RPC")
    try:
        r=requests.get(f"{url}/xmlrpc.php",timeout=6)
        if r.status_code==200: status_warn("xmlrpc.php accessible!")
        else: status_ok(f"xmlrpc.php → {r.status_code}")
    except Exception as e: status_err(str(e))

    _bs("User Enumeration")
    users=[]
    for i in range(1,6):
        try:
            r=requests.get(f"{url}/?author={i}",timeout=5,allow_redirects=True,headers={"User-Agent":"Mozilla/5.0"})
            m=re.search(r'/author/([^/]+)/',r.url)
            if m: users.append(m.group(1)); print(f"  {LYLW}#{i}:{RST}  {m.group(1)}")
        except: pass
    if not users: status_ok("No users via author enumeration")

    _bs("Exposed Files")
    for path in ["/.env","/.git/HEAD","/wp-config.php.bak","/wp-config.php.old","/debug.log"]:
        try:
            r=requests.get(url+path,timeout=5,headers={"User-Agent":"Mozilla/5.0"})
            print(f"  {LRED if r.status_code==200 else DIM}{r.status_code}  {path}{RST}")
        except: pass

    if shutil.which("wpscan"):
        if ask("Run WPScan? (y/n)","n").lower()=="y":
            try: subprocess.run(["wpscan","--url",url,"--enumerate","u,p"])
            except Exception as e: status_err(str(e))
    else: status_info("Install wpscan for deeper scan: gem install wpscan")
    history_log(906,"WordPress Bundle",{"url":url})


def bundle_api_security():
    mod_header("API SECURITY BUNDLE", "REST API security assessment", "🔌", LMAG)
    base = ask("Base API URL")
    if not base: return
    if not base.startswith("http"): base="https://"+base
    base=base.rstrip("/"); print()

    _bs("Endpoint Discovery")
    EPS=["/api","/api/v1","/api/v2","/v1","/v2","/swagger.json","/openapi.json",
         "/api/docs","/api/swagger","/graphql","/graphiql","/.well-known/openid-configuration",
         "/api/health","/api/status","/api/ping","/api/users","/api/auth","/api/token",
         "/api/admin","/api/config","/api/keys","/api/export"]
    found_eps=[]
    for ep in EPS:
        try:
            r=requests.get(base+ep,timeout=4,headers={"User-Agent":"koolti-tool"},allow_redirects=False)
            if r.status_code not in(404,410):
                col=LGRN if r.status_code<300 else(LYLW if r.status_code<400 else LCYN)
                print(f"  {col}{r.status_code}{RST}  {ep}"); found_eps.append(ep)
        except: pass

    _bs("Auth Check")
    for ep in found_eps[:3]:
        try:
            r=requests.get(base+ep,timeout=5)
            if r.status_code==401:   print(f"  {LGRN}✔{RST}  {ep}  auth required (401)")
            elif r.status_code==403: print(f"  {LYLW}~{RST}  {ep}  forbidden (403)")
            elif r.status_code==200: print(f"  {LRED}✘{RST}  {ep}  open without auth (200)!")
        except: pass

    _bs("CORS Check")
    for ep in found_eps[:2]:
        try:
            r=requests.options(base+ep,headers={"Origin":"https://evil.com","Access-Control-Request-Method":"GET"},timeout=5)
            acao=r.headers.get("Access-Control-Allow-Origin","not set")
            col=LRED if acao in("*","https://evil.com") else LGRN
            print(f"  {col}ACAO: {acao}{RST}  ({ep})")
        except: pass
    history_log(907,"API Security Bundle",{"base":base,"endpoints":found_eps})


def bundle_password_audit():
    mod_header("PASSWORD AUDIT BUNDLE", "Password strength + breach check", "🔐", LYLW)
    print(f"  {LYLW}[1]{RST} Single password   {LYLW}[2]{RST} File with password list\n")
    mode = ask("Mode","1")

    def analyze(pwd):
        score=0; issues=[]
        if len(pwd)>=8: score+=1
        else: issues.append("Too short (min 8)")
        if len(pwd)>=12: score+=1
        if len(pwd)>=16: score+=1
        if any(c.isupper() for c in pwd): score+=1
        else: issues.append("No uppercase")
        if any(c.islower() for c in pwd): score+=1
        else: issues.append("No lowercase")
        if any(c.isdigit() for c in pwd): score+=1
        else: issues.append("No digits")
        if any(c in "!@#$%^&*()_+-=" for c in pwd): score+=1
        else: issues.append("No special chars")
        if pwd.lower() in ["password","qwerty","123456","admin","letmein"]: score=1; issues.append("Common password!")
        label=("VERY WEAK" if score<=2 else "WEAK" if score<=4 else "MEDIUM" if score<=5 else "STRONG" if score<=6 else "VERY STRONG")
        return score, label, issues

    if mode == "1":
        pwd = ask("Password")
        if not pwd: return
        score, label, issues = analyze(pwd)
        print()
        col = LGRN if score>=6 else(LYLW if score>=4 else LRED)
        print(f"  {BOLD}Score:{RST}  {col}{BOLD}{label}{RST}  {DIM}({score}/8){RST}")
        print(f"  {col}{'█'*score}{DIM}{'░'*(8-score)}{RST}")
        if issues: print(); [status_warn(i) for i in issues]
        if ask("Breach check? (y/n)","y").lower()=="y":
            try:
                h=hashlib.sha1(pwd.encode()).hexdigest().upper(); pre,suf=h[:5],h[5:]
                r=requests.get(f"https://api.pwnedpasswords.com/range/{pre}",timeout=8)
                match=next((l for l in r.text.splitlines() if l.split(":")[0]==suf),None)
                if match: status_warn(f"Found {match.split(':')[1]} times in breaches!")
                else:     status_ok("Not in breach databases")
            except Exception as e: status_err(str(e))
    else:
        path = ask("Password list file")
        if not path or not Path(path).exists(): status_err("File not found"); return
        pwds = Path(path).read_text(encoding="utf-8",errors="replace").splitlines()[:100]
        print(); print(f"  {BOLD}{LCYN}{'PASSWORD':<30}{'SCORE':<8}LABEL{RST}"); hline("─",DIM,55)
        weak=0
        for pwd in pwds:
            s,l,_=analyze(pwd); col=LGRN if s>=6 else(LYLW if s>=4 else LRED)
            print(f"  {DIM}{pwd[:28]:<30}{RST}{col}{s:<8}{l}{RST}")
            if s<=4: weak+=1
        print(); status_info(f"Weak: {weak}  |  Strong: {len(pwds)-weak}  |  Total: {len(pwds)}")
    history_log(908,"Password Audit Bundle",{"mode":mode})


BUNDLES = {
    1: ("Website Bundle",      "IP, DNS, SSL, CMS, ports, headers score",   bundle_website),
    2: ("Hash Bundle",         "Auto-detect hash type → crack it",           bundle_hash),
    3: ("Email Bundle",        "Format, domain, WHOIS, breach check",        bundle_email),
    4: ("Network Scan Bundle", "Ports, banners, GeoIP, traceroute",          bundle_network_scan),
    5: ("Subdomain Bundle",    "Find all subdomains + HTTP check",            bundle_subdomain),
    6: ("WordPress Bundle",    "WP version, users, xmlrpc, exposed files",   bundle_wordpress),
    7: ("API Security Bundle", "Endpoints, auth, CORS, rate limit",          bundle_api_security),
    8: ("Password Audit Bundle","Strength + breach check (single or file)",  bundle_password_audit),
}


# ═══════════════════════════════════════════════════════════════════════════
# MENU DATA & ACTIONS — 151 modules
# ═══════════════════════════════════════════════════════════════════════════

MENU_DATA = [
    (1,"IP Tracker",'NET',False),(2,"DNS Lookup",'NET',False),(3,"Port Scanner",'NET',False),(4,"MAC Lookup",'NET',False),
    (5,"Local Network Info",'NET',False),(6,"Ping Tool",'NET',False),(7,"Subdomain Finder",'NET',False),(8,"Traceroute",'NET',False),
    (9,"Reverse IP Lookup",'NET',False),(10,"GeoIP Info",'NET',False),(11,"Network Interface Stats",'NET',False),(12,"ARP Scanner",'NET',False),
    (13,"Banner Grabber",'NET',False),(14,"HTTP Method Tester",'NET',False),(15,"SMTP Checker",'NET',False),(16,"FTP Checker",'NET',False),
    (17,"SSH Checker",'NET',False),(18,"SNMP Checker",'NET',False),(19,"BGP ASN Lookup",'NET',False),(20,"IP Range Scanner",'NET',False),
    (21,"Network Speed Test",'NET',False),(22,"WiFi SSID Scanner",'NET',False),(23,"mDNS Discovery",'NET',False),(24,"DNS Zone Transfer",'NET',False),
    (25,"Open Redirect Tester",'NET',False),(26,"CORS Policy Checker",'NET',False),(27,"CDN Detector",'NET',False),(28,"IPv6 Checker",'NET',False),
    (29,"Port Knock Detector",'NET',False),(30,"Shodan IP Lookup",'NET',False),(31,"Admin Finder",'WEB',False),(32,"CMS Detector",'WEB',False),
    (33,"WAF Detector",'WEB',False),(34,"HTTP Header Inspector",'WEB',False),(35,"Link Extractor",'WEB',False),(36,"WHOIS Lookup",'WEB',False),
    (37,"Robots.txt Checker",'WEB',False),(38,"URL Scanner",'WEB',False),(39,"Email Validator",'WEB',False),(40,"Wayback Machine",'WEB',False),
    (41,"Tech Stack Detector",'WEB',False),(42,"Broken Link Checker",'WEB',False),(43,"SSL Certificate Info",'WEB',False),(44,"HTTP Status Bulk Check",'WEB',False),
    (45,"Google Dork Generator",'WEB',False),(46,"HTTP Parameter Fuzzer",'WEB',False),(47,"JS File Extractor",'WEB',False),(48,"Form Extractor",'WEB',False),
    (49,"Cookie Inspector",'WEB',False),(50,"IP Reputation Check",'WEB',False),(51,"Path Traversal Tester",'WEB',False),(52,"SQL Error Detector",'WEB',False),
    (53,"Subdomain Takeover Check",'WEB',False),(54,"TLS Version Checker",'WEB',False),(55,"WhatWeb Lite",'WEB',False),(56,"Latency Map",'NET',False),
    (57,"Certificate Transparency",'WEB',False),(58,"HTTP Cache Inspector",'WEB',False),(59,"Security Headers Score",'WEB',False),(60,"DNS History Lookup",'NET',False),
    (61,"Multi-Port Banner Scan",'NET',False),(62,"Network Topology",'NET',False),(63,"Hash Generator",'CRY',False),(64,"Hash Cracker",'CRY',False),
    (65,"Base64 Tool",'CRY',False),(66,"Caesar Cipher",'CRY',False),(67,"Password Strength",'CRY',False),(68,"Wordlist Generator",'CRY',False),
    (69,"ROT13 Cipher",'CRY',False),(70,"XOR Cipher",'CRY',False),(71,"Morse Code",'CRY',False),(72,"Binary Converter",'CRY',False),
    (73,"Hex Converter",'CRY',False),(74,"URL Encoder/Decoder",'CRY',False),(75,"JWT Decoder",'CRY',False),(76,"System Info",'SYS',False),
    (77,"File Analyzer",'SYS',False),(78,"WiFi Passwords (Win)",'SYS',False),(79,"Process Viewer",'SYS',False),(80,"Disk Usage",'SYS',False),
    (81,"Environment Variables",'SYS',False),(82,"Open Connections",'SYS',False),(83,"File Hash Verifier",'SYS',False),(84,"Directory Scanner",'SYS',False),
    (85,"Log File Reader",'SYS',False),(86,"IP Calculator (CIDR)",'UTL',False),(87,"Random Password Gen",'UTL',False),(88,"UUID Generator",'UTL',False),
    (89,"Text Case Converter",'UTL',False),(90,"Lorem Ipsum Generator",'UTL',False),(91,"JSON Formatter",'UTL',False),(92,"Unix Timestamp Converter",'UTL',False),
    (93,"Color Code Converter",'UTL',False),(94,"String Analyzer",'UTL',False),(95,"Number Base Converter",'UTL',False),(96,"Regex Tester",'UTL',False),
    (97,"ASCII Art Generator",'UTL',False),(98,"History Viewer",'UTL',False),(99,"History Clear",'UTL',False),(100,"Network Topology (ext)",'NET',False),
    (101,"Plugin Manager",'UTL',False),(102,"Check for Update",'UTL',False),(103,"Favourites",'UTL',False),(104,"Module Search",'UTL',False),
    (105,"XSS Scanner",'WEB',False),(106,"Directory Bruteforcer",'WEB',False),(107,"API Endpoint Fuzzer",'WEB',False),(108,"Email Harvester",'WEB',False),
    (109,"HTTP Smuggling Detector",'WEB',False),(110,"Vigenère Cipher",'CRY',False),(111,"Atbash Cipher",'CRY',False),(112,"Hash Identifier",'CRY',False),
    (113,"Advanced Password Gen",'CRY',False),(114,"Encoding Detector",'CRY',False),
    (115,"Nmap Scanner",'NET',True),(116,"SQLMap",'WEB',True),(117,"Tool Installer",'UTL',True),(118,"Gobuster",'WEB',True),
    (119,"Nikto",'WEB',True),(120,"WPScan",'WEB',True),(121,"Nuclei",'WEB',True),(122,"Subfinder",'NET',True),
    (123,"FFUF",'WEB',True),(124,"Hydra",'CRY',True),(125,"Masscan",'NET',True),(126,"John the Ripper",'CRY',True),
    (127,"Curl Tool",'NET',True),(128,"Netcat",'NET',True),(129,"WHOIS (System)",'NET',True),(130,"Amass",'NET',True),
    (131,"DIRB",'WEB',True),(132,"Enum4Linux",'NET',True),(133,"Aircrack-ng",'NET',True),(134,"Metasploit",'WEB',True),
    (135,"Breach Check (HIBP)",'WEB',True),(136,"Username Checker",'WEB',True),(137,"CVE Lookup",'WEB',True),(138,"Tech CVE Checker",'WEB',True),
    (139,"Shodan Search",'WEB',True),(140,"Bulk DNS Resolver",'NET',True),(141,"IP Blacklist Check",'NET',True),(142,"Port Service Identifier",'NET',True),
    (143,"HTTP Response Timer",'WEB',True),(144,"Network Calculator",'UTL',True),(145,"File Strings Extractor",'SYS',True),(146,"Headers Compare",'WEB',True),
    (147,"Open Ports + Banner",'NET',True),(148,"Google Cache Checker",'WEB',True),(149,"IP Geofence Checker",'NET',True),(150,"ASN/BGP Route Lookup",'NET',True),
    (151,"IP to ASN",'NET',True),
]

ACTIONS = {
    1:mod_ip_tracker,2:mod_dns_lookup,3:mod_port_scanner,4:mod_mac_lookup,5:mod_local_network,6:mod_ping,
    7:mod_subdomain_finder,8:mod_traceroute,9:mod_reverse_ip,10:mod_geoip,11:mod_net_iface_stats,12:mod_arp_scanner,
    13:mod_banner_grabber,14:mod_http_methods,15:mod_smtp_checker,16:mod_ftp_checker,17:mod_ssh_checker,18:mod_snmp_checker,
    19:mod_asn_lookup,20:mod_ip_range_scanner,21:mod_speed_test,22:mod_wifi_ssid_scanner,23:mod_mdns_discovery,24:mod_dns_zone_transfer,
    25:mod_open_redirect,26:mod_cors_checker,27:mod_cdn_detector,28:mod_ipv6_checker,29:mod_port_knock,30:mod_shodan_lookup,
    31:mod_admin_finder,32:mod_cms_detector,33:mod_waf_detector,34:mod_header_inspector,35:mod_link_extractor,36:mod_whois,
    37:mod_robots_checker,38:mod_url_scanner,39:mod_email_validator,40:mod_wayback,41:mod_tech_stack,42:mod_broken_links,
    43:mod_ssl_info,44:mod_bulk_status,45:mod_dork_generator,46:mod_http_fuzzer,47:mod_js_extractor,48:mod_form_extractor,
    49:mod_cookie_inspector,50:mod_ip_reputation,51:mod_path_traversal,52:mod_sql_error_detector,53:mod_subdomain_takeover,
    54:mod_tls_checker,55:mod_whatweb,56:mod_latency_map,57:mod_cert_transparency,58:mod_cache_inspector,59:mod_security_score,
    60:mod_dns_history,61:mod_banner_scan,62:mod_net_topology,63:mod_hash_generator,64:mod_hash_cracker,65:mod_base64,
    66:mod_caesar,67:mod_password_checker,68:mod_wordlist,69:mod_rot13,70:mod_xor_cipher,71:mod_morse,72:mod_binary,
    73:mod_hex_converter,74:mod_url_encoder,75:mod_jwt_decoder,76:mod_sys_info,77:mod_file_analyzer,78:mod_wifi_passwords,
    79:mod_processes,80:mod_disk_usage,81:mod_env_vars,82:mod_open_connections,83:mod_file_hash_verifier,84:mod_dir_scanner,
    85:mod_log_reader,86:mod_ip_calculator,87:mod_random_password,88:mod_uuid_generator,89:mod_text_case,90:mod_lorem_ipsum,
    91:mod_json_formatter,92:mod_timestamp,93:mod_color_converter,94:mod_string_analyzer,95:mod_number_base,96:mod_regex_tester,
    97:mod_ascii_art,98:mod_history_viewer,99:mod_history_clear,100:mod_net_topology,101:mod_plugin_list,102:mod_check_update,
    103:mod_favourites,104:mod_search,105:mod_xss_scanner,106:mod_directory_brute,107:mod_api_fuzzer,108:mod_email_harvester,
    109:mod_http_smuggling_detector,110:mod_vigenere_cipher,111:mod_atbash_cipher,112:mod_hash_identifier,
    113:mod_password_generator_advanced,114:mod_encoding_detector,
    115:mod_nmap_wrapper,116:mod_sqlmap_wrapper,117:mod_tool_installer,118:mod_gobuster_wrapper,119:mod_nikto_wrapper,
    120:mod_wpscan_wrapper,121:mod_nuclei_wrapper,122:mod_subfinder_wrapper,123:mod_ffuf_wrapper,124:mod_hydra_wrapper,
    125:mod_masscan_wrapper,126:mod_john_wrapper,127:mod_curl_wrapper,128:mod_nc_wrapper,129:mod_whois_system,130:mod_amass_wrapper,
    131:mod_dirb_wrapper,132:mod_enum4linux_wrapper,133:mod_aircrack_wrapper,134:mod_metasploit_wrapper,
    135:mod_haveibeenpwned,136:mod_username_checker,137:mod_cve_lookup,138:mod_tech_cve_checker,
    139:mod_shodan_search,140:mod_bulk_dns,141:mod_ip_blacklist_check,142:mod_port_service_id,
    143:mod_http_timer,144:mod_network_calculator,145:mod_file_strings,146:mod_headers_compare,
    147:mod_open_ports_banner,148:mod_google_cache,149:mod_ip_geofence,150:mod_asn_bgp_route,
151: mod_asn_bgp_route,
}


def draw_bundles_menu():
    w = min(term_width(), 72)
    hline("═", LMAG, w); cprint(f"{BOLD}{LMAG}  BUNDLES{RST}"); hline("═", LMAG, w)
    print(f"\n  {DIM}Bundles run multiple modules automatically on one target.{RST}\n")
    for num,(name,desc,_) in BUNDLES.items():
        print(f"  {LMAG}{BOLD}[{num}]{RST}  {LWHT}{name:<28}{RST}  {DIM}{desc}{RST}")
    print(); hline("─", DIM, w)
    print(f"  {DIM}[0]{RST} Back")


def show_help():
    clear(); w = min(term_width(), 90)
    hline("═", LCYN, w); cprint(f"{BOLD}{LCYN}◈  KOOLTI-TOOL v10.0.0  —  HELP  ◈{RST}"); hline("═", LCYN, w)
    print(f"""
  {BOLD}Navigation:{RST}
    {LYLW}[number]{RST}  Run a module directly
    {LYLW}[b]{RST}       Bundles menu (full workflows)
    {LYLW}[i]{RST}       Tool installer (nmap, sqlmap, hashcat...)
    {LYLW}[/]{RST}       Search modules by keyword
    {LYLW}[fav]{RST}     Favourites
    {LYLW}[u]{RST}       Check for updates
    {LYLW}[h]{RST}       This help page
    {LYLW}[q]{RST}       Quit
    {LYLW}[↑↓]{RST}      Command history (Linux/Mac)

  {BOLD}Bundles:{RST}
    {DIM}Type 'b' to open bundle menu. Bundles accept one target
    and automatically run all relevant modules.{RST}

  {BOLD}Tool Installer (module 117 or 'i'):{RST}
    {DIM}Shows install commands for 20 external tools.
    Checks if already installed. Run tools directly from koolti-tool.{RST}

  {BOLD}Plugin System:{RST}
    {DIM}Drop .py files into ~/kooltitool/plugins/ and restart.
    Plugins load as slot 200, 201, 202...{RST}

  {BOLD}Legal:{RST}
    {LRED}Educational and authorized testing only.{RST}
""")
    hline("─", DIM, w); pause()


def main():
    multiprocessing.freeze_support()
    history_init()
    cmd_history_load()
    load_plugins()
    check_for_update(silent=True)
    while True:
        logo()
        draw_menu()
        print()
        cmd = input_with_history(
            f"  {LGRN}{BOLD}❯{RST}  {DIM}(number / b=bundles / i=installer / /=search / u=update / h=help){RST}\n"
            f"  {LGRN}{BOLD}❯{RST} "
        ).strip().lower()

        if cmd in ("q","0","exit","quit"):
            clear(); print(f"\n  {LGRN}Goodbye!{RST}\n"); sys.exit(0)
        elif cmd in ("h","help","?"):     show_help()
        elif cmd in ("b","bundles"):
            while True:
                logo(); draw_bundles_menu(); print()
                bc = input_with_history(f"  {LGRN}{BOLD}❯{RST} Bundle: ").strip().lower()
                if bc in ("0","back",""): break
                try:
                    bn = int(bc)
                    if bn in BUNDLES:
                        try: BUNDLES[bn][2]()
                        except KeyboardInterrupt: print(f"\n\n  {LYLW}Interrupted{RST}")
                        except Exception as e:    print(f"\n  {LRED}Bundle error: {e}{RST}")
                        pause()
                    else: status_err(f"No bundle #{bn}"); time.sleep(0.7)
                except ValueError: pass
        elif cmd in ("i","installer"):   mod_tool_installer()
        elif cmd in ("/","search","find"): mod_search(); pause()
        elif cmd in ("fav","favourites","favorites"): mod_favourites(); pause()
        elif cmd in ("u","update"):      mod_check_update(); pause()
        else:
            try:
                n = int(cmd)
                if n in ACTIONS:
                    try:
                        ACTIONS[n]()
                        history_log(n, next((name for nr,name,*_ in MENU_DATA if nr==n), str(n)), {})
                    except KeyboardInterrupt: print(f"\n\n  {LYLW}Interrupted{RST}")
                    except Exception as e:    print(f"\n  {LRED}Module {n} error: {e}{RST}")
                    pause()
                elif n in _loaded_plugins:
                    p = _loaded_plugins[n]
                    try:
                        mod_header(p.get("name","Plugin"), p.get("description",""), "🧩", LCYN)
                        p["run"]()
                    except KeyboardInterrupt: print(f"\n\n  {LYLW}Interrupted{RST}")
                    except Exception as e:    print(f"\n  {LRED}Plugin error: {e}{RST}")
                    pause()
                else:
                    print(f"  {LYLW}No module #{n}{RST}"); time.sleep(0.8)
            except ValueError: pass


if __name__ == "__main__":
    main()
