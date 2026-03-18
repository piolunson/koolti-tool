# KOOLTI-TOOL v8.1.1

![Version](https://img.shields.io/badge/version-v8.1.1-blue)
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

### Sadly I cannot give full module list as for now. ):


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

### v8.1.1
- Fixed import issues in several modules

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
