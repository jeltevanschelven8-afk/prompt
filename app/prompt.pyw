"""Prompt - alle Claude Code slash-commands met 1 klik te kopieren, plus een marktplaats met skills.

Draait met pythonw.exe en gebruikt alleen de standaardbibliotheek. Zie README.md.
"""
import ctypes
import json
import math
import os
import re
import shutil
import plistlib
import shlex
import socket
import subprocess
import sys
import tempfile
import threading
import time
import tkinter as tk
from tkinter import simpledialog
import unicodedata
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path
from tkinter import font as tkfont
from tkinter import messagebox, ttk

try:
    import winreg
except ImportError:  # niet-Windows (bijvoorbeeld tests in CI)
    winreg = None

HOME = Path.home()
CLAUDE_DIR = HOME / ".claude"
SKILLS_DIR = CLAUDE_DIR / "skills"
# Skills die uit staan: buiten de skills-map, zodat Claude ze niet laadt. Aanzetten = terugzetten.
LIBRARY_DIR = CLAUDE_DIR / "skills-uit"
COMMANDS_DIR = CLAUDE_DIR / "commands"
PROJECTS_DIR = CLAUDE_DIR / "projects"
CLAUDE_JSON = HOME / ".claude.json"
FROZEN = bool(getattr(sys, "frozen", False))
# HOSTED: gestart als bin\Prompt.exe (kopie van pythonw.exe die via sitecustomize dit script laadt).
HOSTED = Path(sys.executable).stem.lower() == "prompt"
if FROZEN:
    APP_DIR = Path(sys.executable).resolve().parent
elif HOSTED:
    APP_DIR = Path(sys.prefix).resolve()  # de Prompt-map (daar staat pyvenv.cfg)
else:
    APP_DIR = Path(__file__).resolve().parent
APP_NAME = "Prompt"
APP_VERSION = "2.0.1"
BUILTIN_FILE = APP_DIR / "builtin_commands.json"
UITLEG_FILE = APP_DIR / "uitleg.json"
STATE_FILE = APP_DIR / "state.json"
SETTINGS_FILE = APP_DIR / "settings.json"
REGISTRY_FILE = APP_DIR / "registry.json"
SYNONYMS_FILE = APP_DIR / "synonyms.json"
MARKET_CACHE = APP_DIR / "market_cache.json"
MARKET_STATE = APP_DIR / "market_state.json"
CATALOG_DIR = APP_DIR / "catalog"

# PROMPT_PORT: alleen om een tweede (test)exemplaar naast het gewone te kunnen draaien.
PORT = int(os.environ.get("PROMPT_PORT") or 47631)
POLL_MS = 2000
WATCH_MS = 2500
RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
RUN_VALUE = "Prompt"
CLAUDE_PROCESSES = {"claude.exe", "claude"}  # Claude-app en Claude Code (Windows, macOS, Linux)
IS_WINDOWS = os.name == "nt"
IS_MAC = sys.platform == "darwin"
IS_LINUX = sys.platform.startswith("linux")

CAT_SKILLS = "Mijn skills"
CAT_COMMANDS = "Mijn commands"
CAT_PROJECT = "Project"
CAT_PLUGINS = "Plugins"
CAT_BUILTIN = "Ingebouwd"
CATEGORY_ORDER = [CAT_SKILLS, CAT_COMMANDS, CAT_PROJECT, CAT_PLUGINS, CAT_BUILTIN]
FILTER_ALL = "Alles"


# --------------------------------------------------------------------------- #
# Kleine hulpfuncties
# --------------------------------------------------------------------------- #
MAX_DESC = 150


def shorten(text, limit=MAX_DESC):
    """Eerste zin, of afgekapt op een woordgrens, zodat elke rij kort blijft."""
    text = re.sub(r"\s+", " ", (text or "")).strip()
    if len(text) <= limit:
        return text
    m = re.match(r"^(.{20,%d}?[.!?])(\s|$)" % limit, text)
    if m:
        return m.group(1)
    cut = text[:limit].rsplit(" ", 1)[0]
    return cut.rstrip(",;:") + "…"


def read_text(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig", errors="replace")
    except OSError:
        return ""


def save_json(path, data):
    try:
        Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError:
        pass


def nice_date(iso):
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", iso or "")
    return f"{int(m.group(3))}-{int(m.group(2))}-{m.group(1)}" if m else ""


# --------------------------------------------------------------------------- #
# Instellingen
# --------------------------------------------------------------------------- #
ACCENTS = {  # naam: (licht, licht donkerder, donker thema, donker thema lichter)
    "terracotta": ("#c2562b", "#a3461f", "#ec8a5f", "#f4a27e"),
    "blauw": ("#2f66d0", "#2453ad", "#6b9cf2", "#8db3f5"),
    "groen": ("#2b7d50", "#21653f", "#5cc48a", "#7fd3a3"),
    "paars": ("#7447c6", "#5e37a6", "#a586ec", "#bba3f1"),
    "roze": ("#c73d73", "#a4305d", "#ee79a4", "#f398b9"),
    "grafiet": ("#2f2f2f", "#111111", "#e8e4dc", "#ffffff"),
}
TEXT_SIZES = {"klein": 0.9, "normaal": 1.0, "groot": 1.15}
DEFAULT_SETTINGS = {
    "theme": "system",
    "accent": "terracotta",
    "text_size": "normaal",
    "start_view": "local",
    "open_with_claude": False,
    "always_on_top": False,
    "minimize_after_copy": False,
    "check_updates": True,
    "show_plugins": True,
    "show_builtin": True,
    "hide_hint_shown": False,
    "pick_on_claude_start": True,
    "new_skills_active": True,
    "skill_sets": {},
}
MAX_SETS = 30
CHOICES = {
    "theme": ("system", "light", "dark"),
    "accent": tuple(ACCENTS),
    "text_size": tuple(TEXT_SIZES),
    "start_view": ("local", "market"),
}


def load_settings(path=None):
    settings = dict(DEFAULT_SETTINGS)
    try:
        data = json.loads(read_text(path or SETTINGS_FILE) or "{}")
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        return settings
    for key, default in DEFAULT_SETTINGS.items():
        value = data.get(key, default)
        if isinstance(default, bool):
            settings[key] = value if isinstance(value, bool) else default
        elif key in CHOICES:
            settings[key] = value if value in CHOICES[key] else default
        elif key == "skill_sets":
            settings[key] = clean_sets(value)
    return settings


def clean_sets(value):
    """{"Setnaam": ["skill", ...]}; alles wat daar niet op lijkt valt weg."""
    if not isinstance(value, dict):
        return {}
    out = {}
    for name, skills in list(value.items())[:MAX_SETS]:
        if isinstance(name, str) and name.strip() and isinstance(skills, list):
            out[name.strip()[:40]] = sorted({x for x in skills if isinstance(x, str) and x})
    return out


# --------------------------------------------------------------------------- #
# Kleuren
# --------------------------------------------------------------------------- #
LIGHT = {
    "bg": "#f4f2ee", "surface": "#ffffff", "surface2": "#ebe7e0", "hover": "#f8f5f0", "border": "#e2ddd5",
    "text": "#1d1c1a", "muted": "#6b665f", "faint": "#8d877e", "ok": "#2e7d4f", "warn": "#8a5a00",
    "danger": "#b3261e", "field": "#ffffff",
}
DARK = {
    "bg": "#161513", "surface": "#211f1c", "surface2": "#2d2a25", "hover": "#28251f", "border": "#38332d",
    "text": "#f1ece4", "muted": "#aaa297", "faint": "#857e74", "ok": "#6cc28c", "warn": "#e6b75c",
    "danger": "#f2867c", "field": "#1b1a17",
}
C = {}  # de actieve kleuren, gevuld door set_palette()


def _rgb(hex_color):
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """Meng kleur a met b; t=0 is a, t=1 is b."""
    ra, rb = _rgb(a), _rgb(b)
    return "#%02x%02x%02x" % tuple(round(x + (y - x) * t) for x, y in zip(ra, rb))


def luminance(hex_color):
    def chan(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = (chan(c) for c in _rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def set_palette(dark, accent):
    C.clear()
    C.update(DARK if dark else LIGHT)
    a = ACCENTS.get(accent, ACCENTS["terracotta"])
    C["accent"], C["accent_hover"] = (a[2], a[3]) if dark else (a[0], a[1])
    C["accent_text"] = a[2] if dark else a[1]  # iets donkerder in licht thema: beter contrast voor tekst
    C["on_accent"] = "#1d1c1a" if luminance(C["accent"]) > 0.4 else "#ffffff"
    C["accent_soft"] = mix(C["accent"], C["surface"], 0.86)


def run_quiet(cmd, timeout=5):
    """Voer een klein systeemcommando uit; geeft de uitvoer terug, of "" als het niet lukt."""
    try:
        kwargs = {"creationflags": 0x08000000} if IS_WINDOWS else {}  # CREATE_NO_WINDOW
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, **kwargs).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def system_prefers_dark():
    if IS_WINDOWS:
        if not winreg:
            return False
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize") as key:
                return winreg.QueryValueEx(key, "AppsUseLightTheme")[0] == 0
        except OSError:
            return False
    if IS_MAC:
        return "dark" in run_quiet(["defaults", "read", "-g", "AppleInterfaceStyle"]).lower()
    scheme = run_quiet(["gsettings", "get", "org.gnome.desktop.interface", "color-scheme"]).lower()
    if "dark" in scheme:
        return True
    if "light" in scheme:
        return False
    return "dark" in run_quiet(["gsettings", "get", "org.gnome.desktop.interface", "gtk-theme"]).lower()


def apply_titlebar(root, dark):
    """Donkere of lichte Windows-titelbalk, passend bij het thema. (macOS en Linux doen dat zelf.)"""
    if not IS_WINDOWS:
        return
    try:
        root.update_idletasks()
        hwnd = ctypes.windll.user32.GetParent(root.winfo_id())
        value = ctypes.c_int(1 if dark else 0)
        for attribute in (20, 19):  # DWMWA_USE_IMMERSIVE_DARK_MODE (nieuw, oud)
            if ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, attribute, ctypes.byref(value),
                                                          ctypes.sizeof(value)) == 0:
                break
    except Exception:  # noqa: BLE001 - puur cosmetisch
        pass


def open_path(path):
    """Open een map of bestand in Verkenner, Finder of de bestandsbeheerder van Linux."""
    path = str(path)
    if IS_WINDOWS:
        os.startfile(path)
    elif IS_MAC:
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path], start_new_session=True,
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def set_window_icon(root):
    try:
        if IS_WINDOWS and (APP_DIR / "icon.ico").exists():
            root.iconbitmap(default=str(APP_DIR / "icon.ico"))
        elif (APP_DIR / "icon.png").exists():
            root._icon_image = tk.PhotoImage(file=str(APP_DIR / "icon.png"))  # referentie vasthouden
            root.iconphoto(True, root._icon_image)
    except tk.TclError:
        pass


# --------------------------------------------------------------------------- #
# Opstarten met Claude
# --------------------------------------------------------------------------- #
def running_process_names():
    """Namen (kleine letters) van alle draaiende processen."""
    names = set()
    if IS_LINUX:
        try:
            for pid in os.listdir("/proc"):
                if pid.isdigit():
                    try:
                        names.add(Path("/proc", pid, "comm").read_text(errors="replace").strip().lower())
                    except OSError:
                        pass
        except OSError:
            pass
        return names
    if IS_MAC:
        for line in run_quiet(["ps", "-A", "-o", "comm="]).splitlines():
            if line.strip():
                names.add(Path(line.strip()).name.lower())
        return names
    if not IS_WINDOWS:
        return names

    class PROCESSENTRY32W(ctypes.Structure):
        _fields_ = [("dwSize", ctypes.c_ulong), ("cntUsage", ctypes.c_ulong),
                    ("th32ProcessID", ctypes.c_ulong), ("th32DefaultHeapID", ctypes.c_size_t),
                    ("th32ModuleID", ctypes.c_ulong), ("cntThreads", ctypes.c_ulong),
                    ("th32ParentProcessID", ctypes.c_ulong), ("pcPriClassBase", ctypes.c_long),
                    ("dwFlags", ctypes.c_ulong), ("szExeFile", ctypes.c_wchar * 260)]

    k32 = ctypes.windll.kernel32
    k32.CreateToolhelp32Snapshot.restype = ctypes.c_void_p
    snapshot = k32.CreateToolhelp32Snapshot(0x2, 0)  # TH32CS_SNAPPROCESS
    if not snapshot or snapshot == ctypes.c_void_p(-1).value:
        return names
    try:
        entry = PROCESSENTRY32W()
        entry.dwSize = ctypes.sizeof(entry)
        ok = k32.Process32FirstW(ctypes.c_void_p(snapshot), ctypes.byref(entry))
        while ok:
            names.add(entry.szExeFile.lower())
            ok = k32.Process32NextW(ctypes.c_void_p(snapshot), ctypes.byref(entry))
    finally:
        k32.CloseHandle(ctypes.c_void_p(snapshot))
    return names


def claude_is_running():
    return bool(CLAUDE_PROCESSES & running_process_names())


def find_claude_app():
    """Waar de Claude-app staat: AppID (Windows Store), pad naar Claude.app (macOS) of een programma (Linux)."""
    if IS_WINDOWS:
        out = run_quiet(["powershell", "-NoProfile", "-Command",
                         "(Get-StartApps | Where-Object { $_.Name -eq 'Claude' } | Select-Object -First 1).AppID"],
                        timeout=15)
        return out.strip() or None
    if IS_MAC:
        for app in (Path("/Applications/Claude.app"), HOME / "Applications" / "Claude.app"):
            if app.is_dir():
                return str(app)
        return None
    for name in ("claude-desktop", "claude-desktop-bin"):  # community-builds voor Linux
        found = shutil.which(name)
        if found:
            return found
    return None


def launch_claude_app(app_id):
    if IS_WINDOWS:
        if "!" in app_id:  # Store-app
            subprocess.Popen(["explorer.exe", "shell:AppsFolder\\" + app_id])
        else:
            os.startfile(app_id)
    elif IS_MAC:
        subprocess.Popen(["open", app_id])
    else:
        subprocess.Popen([app_id], start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


TERMINALS = (  # Linux: de eerste die bestaat wordt gebruikt
    ("x-terminal-emulator", "-e"), ("gnome-terminal", "--"), ("konsole", "-e"), ("xfce4-terminal", "-x"),
    ("kitty", None), ("alacritty", "-e"), ("tilix", "-e"), ("xterm", "-e"),
)


def launch_claude_code():
    """Claude Code in een nieuw terminalvenster, in je gebruikersmap."""
    if IS_WINDOWS:
        wt = shutil.which("wt")
        cmd = [wt, "claude"] if wt else ["cmd.exe", "/c", "start", "cmd.exe", "/k", "claude"]
        subprocess.Popen(cmd, cwd=str(HOME))
        return
    if IS_MAC:
        subprocess.Popen(["osascript", "-e", 'tell application "Terminal" to do script "claude"',
                          "-e", 'tell application "Terminal" to activate'])
        return
    for term, flag in TERMINALS:
        if shutil.which(term):
            subprocess.Popen([term] + ([flag] if flag else []) + ["claude"], cwd=str(HOME), start_new_session=True,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return
    raise OSError("Geen terminalprogramma gevonden om Claude Code in te starten.")


LINUX_AUTOSTART = Path(os.environ.get("XDG_CONFIG_HOME") or HOME / ".config") / "autostart" / "prompt.desktop"
MAC_AGENT = HOME / "Library" / "LaunchAgents" / "nl.prompt.app.plist"


def autostart_args():
    """Wat bij het aanmelden start: Prompt op de achtergrond, wachtend op Claude."""
    if HOSTED:
        return [sys.executable, "-X", "detach", "-X", "watch"]
    exe = Path(sys.executable)
    if IS_WINDOWS:
        pythonw = exe.with_name("pythonw.exe")
        return [str(pythonw if pythonw.exists() else exe), str(Path(__file__).resolve()), "--detach", "--watch"]
    return [str(exe), str(Path(__file__).resolve()), "--watch"]


def desktop_exec(args):
    """Exec-regel voor een .desktop-bestand (freedesktop-regels voor aanhalingstekens)."""
    def quote(a):
        if re.search(r'[\s"`$\\]', a):
            return '"' + re.sub(r'(["`$\\])', r"\\\1", a) + '"'
        return a
    return " ".join(quote(a) for a in args)


def autostart_command():
    args = autostart_args()
    if IS_WINDOWS:
        return " ".join(f'"{a}"' if i < 2 or " " in a else a for i, a in enumerate(args))
    return " ".join(shlex.quote(a) if i else f'"{a}"' for i, a in enumerate(args))


def set_autostart(enabled):
    try:
        if IS_WINDOWS:
            if not winreg:
                return False
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, RUN_KEY, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, RUN_VALUE, 0, winreg.REG_SZ, autostart_command())
                else:
                    try:
                        winreg.DeleteValue(key, RUN_VALUE)
                    except FileNotFoundError:
                        pass
            return True
        if IS_MAC:
            if enabled:
                MAC_AGENT.parent.mkdir(parents=True, exist_ok=True)
                MAC_AGENT.write_bytes(plistlib.dumps({
                    "Label": "nl.prompt.app", "ProgramArguments": autostart_args(), "RunAtLoad": True,
                    "ProcessType": "Interactive"}))
            elif MAC_AGENT.exists():
                MAC_AGENT.unlink()
            return True
        if enabled:
            LINUX_AUTOSTART.parent.mkdir(parents=True, exist_ok=True)
            LINUX_AUTOSTART.write_text(
                "[Desktop Entry]\nType=Application\nName=Prompt\n"
                "Comment=Prompt op de achtergrond; komt naar voren als Claude opent\n"
                f"Exec={desktop_exec(autostart_args())}\nIcon={APP_DIR / 'icon.png'}\n"
                "NoDisplay=true\nX-GNOME-Autostart-enabled=true\n", encoding="utf-8")
        elif LINUX_AUTOSTART.exists():
            LINUX_AUTOSTART.unlink()
        return True
    except OSError:
        return False


# --------------------------------------------------------------------------- #
# Bronnen scannen
# --------------------------------------------------------------------------- #
class Cmd:
    __slots__ = ("command", "description", "full", "uitleg", "wanneer", "voorbeeld", "category", "source", "_fields",
                 "active")

    def __init__(self, command, description, category, source="", uitleg="", wanneer="", voorbeeld=""):
        self.command = command
        self.full = re.sub(r"\s+", " ", (description or "")).strip()
        self.description = shorten(description)
        self.uitleg = (uitleg or "").strip()
        self.wanneer = (wanneer or "").strip()
        self.voorbeeld = (voorbeeld or "").strip()
        self.category = category
        self.source = source
        self._fields = None
        self.active = True

    @property
    def key(self):
        return f"{self.category}|{self.command}"

    @property
    def toggleable(self):
        """Eigen skills en marktplaats-skills kun je aan/uit zetten; ingebouwde commands en plugins niet."""
        return self.category == CAT_SKILLS and self.source.endswith("SKILL.md")

    @property
    def skill_name(self):
        return Path(self.source).parent.name

    def base_name(self):
        """'/anthropic-skills:design-first' -> '/design-first' (voor uitleg-overrides)."""
        return "/" + self.command.lstrip("/").split(":")[-1]


def parse_frontmatter(text):
    """Kleine YAML-subset: key: value, meerregelige >- / | blokken, ingesprongen vervolgregels."""
    meta = {}
    body = text
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        end = None
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                end = i
                break
        if end is not None:
            key = None
            quoted = {}  # sleutel -> aanhalingsteken waarmee de waarde begon
            for line in lines[1:end]:
                m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
                if m and not line[:1].isspace():
                    key = m.group(1)
                    val = m.group(2).strip()
                    if val in (">", ">-", "|", "|-", ">+", "|+"):
                        val = ""
                    if val[:1] in ("'", '"'):
                        quoted[key] = val[0]
                        val = val[1:]
                    meta[key] = val
                elif key and line.strip():
                    meta[key] = (meta[key] + " " + line.strip()).strip()
            for key, q in quoted.items():
                val = meta[key]
                if val.endswith(q):
                    val = val[:-1]
                # YAML: '' binnen enkele quotes is één ', \" binnen dubbele quotes is één "
                meta[key] = val.replace("''", "'") if q == "'" else val.replace('\\"', '"')
            body = "\n".join(lines[end + 1:])
    return meta, body


def first_text_line(body):
    for line in body.splitlines():
        s = line.strip()
        if s and not s.startswith("#") and s != "---":
            return s
    return ""


def scan_skills(directory, category, active=True):
    items = []
    directory = Path(directory)
    if not directory.is_dir():
        return items
    for d in sorted(directory.iterdir(), key=lambda p: p.name.lower()):
        f = d / "SKILL.md"
        if d.is_dir() and f.is_file():
            meta, body = parse_frontmatter(read_text(f))
            name = meta.get("name") or d.name
            desc = meta.get("description") or first_text_line(body)
            item = Cmd("/" + name, desc, category, str(f))
            item.active = active
            items.append(item)
    return items


def scan_commands(directory, category):
    items = []
    directory = Path(directory)
    if not directory.is_dir():
        return items
    for f in sorted(directory.rglob("*.md"), key=lambda p: str(p).lower()):
        rel = f.relative_to(directory).with_suffix("")
        name = ":".join(rel.parts)
        meta, body = parse_frontmatter(read_text(f))
        desc = meta.get("description") or first_text_line(body)
        items.append(Cmd("/" + name, desc, category, str(f)))
    return items


def decode_project_dir(encoded):
    """Zet een mapnaam uit ~/.claude/projects (bv. C--Users-naam-Desktop-mijn-app) om naar een echt pad."""
    m = re.match(r"^([A-Za-z])--(.*)$", encoded)
    if not m:
        return None
    rest = m.group(2)
    current = Path(m.group(1) + ":\\")

    def enc(name):
        return re.sub(r"[^A-Za-z0-9]", "-", name)

    def walk(path, remaining):
        if not remaining:
            return path
        try:
            entries = [e for e in os.scandir(path) if e.is_dir()]
        except OSError:
            return None
        for e in sorted(entries, key=lambda x: -len(x.name)):
            en = enc(e.name)
            if remaining == en:
                return Path(e.path)
            if remaining.startswith(en + "-"):
                found = walk(Path(e.path), remaining[len(en) + 1:])
                if found:
                    return found
        return None

    return walk(current, rest)


def project_paths():
    """Echte projectmappen: eerst uit ~/.claude.json, daarna gedecodeerd uit ~/.claude/projects."""
    paths = {}
    try:
        data = json.loads(read_text(CLAUDE_JSON) or "{}")
        for p in (data.get("projects") or {}).keys():
            paths[os.path.normcase(p)] = Path(p)
    except (ValueError, AttributeError):
        pass
    if PROJECTS_DIR.is_dir():
        for d in PROJECTS_DIR.iterdir():
            if not d.is_dir() or "scratch-workspaces" in d.name:
                continue
            real = decode_project_dir(d.name)
            if real and real.is_dir():
                paths.setdefault(os.path.normcase(str(real)), real)
    result = []
    for p in paths.values():
        if "scratch-workspaces" in str(p).lower():
            continue
        if (p / ".claude").is_dir():
            result.append(p)
    return sorted(result, key=lambda p: p.name.lower())


def claude_app_dirs():
    """Datamappen van de Claude-desktopapp (daar staan de plugins die je in de app hebt aangezet)."""
    if IS_WINDOWS:
        dirs = [Path(os.environ["APPDATA"]) / "Claude"] if os.environ.get("APPDATA") else []
        if os.environ.get("LOCALAPPDATA"):
            dirs += [p / "LocalCache" / "Roaming" / "Claude"
                     for p in Path(os.environ["LOCALAPPDATA"], "Packages").glob("Claude_*")]
        return dirs
    if IS_MAC:
        return [HOME / "Library" / "Application Support" / "Claude"]
    return [HOME / ".config" / "Claude"]


_PLUGIN_CACHE = {"time": 0.0, "names": None}


def installed_plugin_skills():
    """Namen van skills en commands uit plugins die echt op deze computer staan: Claude Code
    (~/.claude/plugins) en de Claude-app. Vijf minuten bewaard, want zoeken op schijf kost tijd."""
    if _PLUGIN_CACHE["names"] is not None and time.time() - _PLUGIN_CACHE["time"] < 300:
        return _PLUGIN_CACHE["names"]
    names = set()

    def collect(folder):
        try:
            for child in folder.iterdir():
                if folder.name == "skills" and (child / "SKILL.md").is_file():
                    names.add(child.name)
                elif folder.name == "commands" and child.suffix == ".md":
                    names.add(child.stem)
        except OSError:
            pass

    patterns = []
    for d in claude_app_dirs():
        patterns += [(d / "local-agent-mode-sessions" / "skills-plugin", "*/*/skills"),
                     (d / "rpm", "*/*/*/skills"), (d / "rpm", "*/*/*/commands")]
    for root, pattern in patterns:
        if root.is_dir():
            for folder in root.glob(pattern):
                collect(folder)
    plugins = CLAUDE_DIR / "plugins"
    if plugins.is_dir():
        for path, dirs, _files in os.walk(plugins):
            depth = len(Path(path).relative_to(plugins).parts)
            if depth >= 7:
                dirs[:] = []
            for d in ("skills", "commands"):
                if d in dirs:
                    collect(Path(path) / d)
    _PLUGIN_CACHE.update(time=time.time(), names=names)
    return names


def load_builtin():
    items = []
    try:
        data = json.loads(read_text(BUILTIN_FILE) or "{}")
    except ValueError:
        return items
    plugins = None
    for group in data.get("groups", []):
        cat = group.get("category") or CAT_BUILTIN
        for c in group.get("commands", []):
            cmd = c.get("command", "").strip()
            if ":" in cmd:
                # Plugin-command (/plugin:skill): alleen tonen als die plugin hier geïnstalleerd is.
                if plugins is None:
                    plugins = installed_plugin_skills()
                if cmd.rsplit(":", 1)[1] not in plugins:
                    continue
            if cmd:
                items.append(Cmd(cmd, c.get("description", ""), cat, str(BUILTIN_FILE),
                                 uitleg=c.get("uitleg", ""), wanneer=c.get("wanneer", ""),
                                 voorbeeld=c.get("voorbeeld", "")))
    return items


def load_uitleg():
    """Nederlandse uitleg per command uit uitleg.json: {"/naam": {"kort": .., "uitleg": .., "wanneer": .., "voorbeeld": ..}}."""
    try:
        data = json.loads(read_text(UITLEG_FILE) or "{}")
    except ValueError:
        return {}
    return {k: v for k, v in data.items() if isinstance(v, dict) and k.startswith("/")}


def apply_uitleg(items, uitleg):
    """Vul uitleg/wanneer/voorbeeld aan voor gescande commands; exacte naam wint, anders de naam zonder prefix."""
    for it in items:
        extra = uitleg.get(it.command) or uitleg.get(it.base_name())
        if not extra:
            continue
        if extra.get("kort"):
            it.description = shorten(extra["kort"])
        it.uitleg = it.uitleg or (extra.get("uitleg") or "").strip()
        it.wanneer = it.wanneer or (extra.get("wanneer") or "").strip()
        it.voorbeeld = it.voorbeeld or (extra.get("voorbeeld") or "").strip()
    return items


def apply_market_summaries(items, skills):
    """Skills uit de marktplaats krijgen in Mijn commands de korte Nederlandse samenvatting."""
    by_name = {s["name"]: s for s in skills if s.get("summary_nl")}
    for it in items:
        s = by_name.get(it.base_name().lstrip("/"))
        if s and it.category == CAT_SKILLS and not it.uitleg:
            it.description = shorten(s["summary_nl"])
            it._fields = None
    return items


def scan_all():
    items = []
    active = scan_skills(SKILLS_DIR, CAT_SKILLS)
    names = {Path(it.source).parent.name for it in active}
    inactive = [it for it in scan_skills(LIBRARY_DIR, CAT_SKILLS, active=False)
                if Path(it.source).parent.name not in names]
    items += sorted(active + inactive, key=lambda it: it.command.lower())
    items += scan_commands(COMMANDS_DIR, CAT_COMMANDS)
    for proj in project_paths():
        cat = f"{CAT_PROJECT}: {proj.name}"
        items += scan_skills(proj / ".claude" / "skills", cat)
        items += scan_commands(proj / ".claude" / "commands", cat)
    items += load_builtin()
    return apply_uitleg(items, load_uitleg())


def fingerprint():
    """Snapshot van mtimes van alles wat we scannen; verandert => opnieuw scannen."""
    roots = [SKILLS_DIR, LIBRARY_DIR, COMMANDS_DIR, BUILTIN_FILE, UITLEG_FILE, CLAUDE_JSON, PROJECTS_DIR]
    for proj in project_paths():
        roots.append(proj / ".claude" / "skills")
        roots.append(proj / ".claude" / "commands")
    parts = []
    for root in roots:
        try:
            st = root.stat()
        except OSError:
            parts.append((str(root), None))
            continue
        parts.append((str(root), st.st_mtime_ns))
        if root.is_dir() and root != PROJECTS_DIR:
            base_depth = len(root.parts)
            for dirpath, dirnames, filenames in os.walk(root):
                if len(Path(dirpath).parts) - base_depth >= 3:
                    dirnames[:] = []
                for n in dirnames + filenames:
                    p = os.path.join(dirpath, n)
                    try:
                        parts.append((p, os.stat(p).st_mtime_ns))
                    except OSError:
                        pass
    return hash(tuple(parts))


def category_sort_key(cat):
    for i, c in enumerate(CATEGORY_ORDER):
        if cat == c or cat.startswith(c + ":"):
            return (i, cat.lower())
    return (len(CATEGORY_ORDER), cat.lower())


def group_of(category):
    return CAT_PROJECT if category.startswith(CAT_PROJECT + ":") else category


# --------------------------------------------------------------------------- #
# Zoeken: Nederlands en Engels door elkaar, synoniemen en typefouten
# --------------------------------------------------------------------------- #
STOPWORDS = {
    "de", "het", "een", "en", "of", "van", "voor", "met", "op", "in", "aan", "om", "te", "naar", "bij", "uit",
    "ik", "wil", "mijn", "je", "jij", "me", "mij", "hoe", "wat", "kan", "iets", "die", "dat", "dit", "is",
    "the", "a", "an", "and", "or", "for", "with", "on", "to", "my", "i", "how", "can", "want", "it",
    "this", "that", "please", "graag", "even", "laten", "doen",
}
# Te algemene woorden: tellen alleen mee als ze in de naam of tags staan, niet in elke beschrijving.
WEAK_WORDS = {"skill", "skills", "claude", "code", "use", "gebruik", "gebruiken", "user", "help", "helpen", "whenever",
              "maken", "make", "create", "nieuw", "nieuwe", "new", "schrijven", "write", "bouwen", "build"}
_SYNONYMS = None


def norm(text):
    text = unicodedata.normalize("NFKD", str(text or "").lower())
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def load_synonyms(path=None):
    """{woord: {alle woorden uit dezelfde groep}}"""
    mapping = {}
    try:
        data = json.loads(read_text(path or SYNONYMS_FILE) or "{}")
    except ValueError:
        data = {}
    groups = data.get("groups") if isinstance(data, dict) else None
    for group in groups if isinstance(groups, list) else []:
        if not isinstance(group, list):
            continue
        words = {w for member in group if isinstance(member, str) for w in norm(member).split()}
        for w in words:
            mapping.setdefault(w, set()).update(words)
    return mapping


def synonyms():
    global _SYNONYMS
    if _SYNONYMS is None:
        _SYNONYMS = load_synonyms()
    return _SYNONYMS


MAX_QUERY_CHARS = 200
MAX_QUERY_TERMS = 10


def query_terms(query):
    """Zoekwoorden zonder stopwoorden, ontdubbeld en begrensd: een geplakte lap tekst mag niets laten vastlopen."""
    words = list(dict.fromkeys(norm(str(query or "")[:MAX_QUERY_CHARS]).split()))
    terms = [w for w in words if w not in STOPWORDS]
    return (terms or words)[:MAX_QUERY_TERMS]


def within_one_edit(a, b):
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) > len(b):
        a, b = b, a
    i = j = edits = 0
    while i < len(a) and j < len(b):
        if a[i] == b[j]:
            i += 1
            j += 1
            continue
        edits += 1
        if edits > 1:
            return False
        if len(a) == len(b):
            i += 1
        j += 1
    return edits + (len(b) - j) + (len(a) - i) <= 1


def match_quality(term, words, loose=True):
    """loose=False voor synoniemen: alleen hele woorden en woordbegin, geen toevalstreffers midden in een woord."""
    best = 0.0
    for w in words:
        if w == term:
            return 1.0
        if len(term) >= 3 and w.startswith(term):
            best = max(best, 0.85)
        elif not loose:
            continue
        elif len(w) >= 4 and term.startswith(w):
            best = max(best, 0.7)  # "testen" vindt "test"
        elif len(term) >= 5 and within_one_edit(term, w):
            best = max(best, 0.7)  # typefout
        elif len(term) >= 4 and term in w:
            best = max(best, 0.5)  # deel van een samenstelling
    return best


def term_variants(term):
    syn = synonyms()
    variants = {term: 1.0}
    groups = set()
    if term in syn:
        groups |= syn[term]
    elif len(term) >= 4:  # half getypt woord: "vertaa" -> groep van "vertalen"
        for word, group in syn.items():
            if word.startswith(term):
                groups |= group
    for w in groups:
        variants.setdefault(w, 0.8)
    return variants


def score_fields(terms, fields):
    """fields: [(gewicht, woorden, algemene_woorden_tellen)]. 0 = geen match."""
    if not terms:
        return 1.0
    total = 0.0
    matched = 0
    strong_terms = [t for t in terms if t not in WEAK_WORDS]
    for term in terms:
        best = 0.0
        variants = term_variants(term)
        weak = term in WEAK_WORDS
        for weight, words, weak_ok in fields:
            if weak and not weak_ok:
                continue
            for variant, factor in variants.items():
                q = match_quality(variant, words, loose=(factor == 1.0))
                if q:
                    best = max(best, weight * q * factor * (0.6 if weak else 1.0))
        if best:
            total += best
            if not weak or not strong_terms:
                matched += 1
    # Algemene woorden ('maken', 'skill') zijn optioneel; tellen alleen mee als er niets anders is.
    counted = len(strong_terms) or len(terms)
    needed = 1 if counted <= 2 else math.ceil(counted * 0.6)
    if matched < needed:
        return 0.0
    return total * (0.5 + 0.5 * matched / counted)


def rank(results, terms, keep=0.25):
    """Houd alleen resultaten die in de buurt van de beste score komen."""
    if not terms or not results:
        return results
    top = max(score for score, _ in results)
    return [r for r in results if r[0] >= top * keep]


def cmd_fields(it):
    if it._fields is None:
        it._fields = [
            (10, norm(it.command).split(), True),
            (4, norm(it.full + " " + it.description).split(), False),
            (3, norm(it.uitleg + " " + it.wanneer).split(), False),
            (2, norm(it.category).split(), True),
        ]
    return it._fields


def skill_fields(s):
    return [
        (10, norm(s["name"]).split(), True),
        (7, norm(" ".join(s["tags"])).split(), True),
        (5, norm(s.get("summary_nl", "")).split(), False),
        (4, norm(CATEGORY_NL.get(s["category"], "") + " " + s["category"]).split(), True),
        (3, norm(s["description"]).split(), False),
        (2, norm(s["author"]).split(), True),
    ]


# --------------------------------------------------------------------------- #
# Marktplaats
# --------------------------------------------------------------------------- #
# De marktplaats is een GitHub-repository met skills; GitHub Pages serveert data/index.json en de
# skillbestanden. Zonder online marktplaats gebruikt Prompt de ingebouwde catalogus (map catalog\).
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFE_PATH_RE = re.compile(r"^[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*$")
MAX_DOWNLOAD = 2_000_000
GITHUB_URL_LIMIT = 7800

CATEGORY_NL = {
    "code": "Code", "testing": "Testen", "design": "Design", "writing": "Schrijven", "data": "Data",
    "automation": "Automatisering", "devops": "DevOps", "security": "Veiligheid", "productivity": "Productiviteit",
    "learning": "Leren", "workflow": "Workflow", "other": "Overig",
}
SAFETY_NL = {
    "pipe-shell": "Script downloaden en direct uitvoeren",
    "iex": "PowerShell-code direct uitvoeren",
    "rm-rf": "Recursief verwijderen",
    "skip-perms": "Rechten- of veiligheidschecks overslaan",
    "secrets": "Noemt wachtwoorden, sleutels of tokens",
    "override": "Probeert eerdere instructies te overschrijven",
    "encoded": "Verborgen (base64) inhoud",
    "exfil": "Stuurt mogelijk data naar een externe dienst",
}
SORTS = {"relevance": "Relevantie", "name": "Naam (A–Z)", "newest": "Nieuwste", "category": "Categorie"}


def load_registry_config():
    """registry.json naast de app: {"url": site met data/index.json, "repo": "eigenaar/naam", "branch": "main"}.
    PROMPT_REGISTRY overschrijft de url (handig om een lokale testsite te gebruiken)."""
    cfg = {"url": "", "repo": "", "branch": "main"}
    try:
        data = json.loads(read_text(REGISTRY_FILE) or "{}")
        if isinstance(data, dict):
            cfg.update({k: v for k, v in data.items() if k in cfg and isinstance(v, str) and v})
    except ValueError:
        pass
    url = (os.environ.get("PROMPT_REGISTRY") or cfg["url"]).strip()
    if url and not url.endswith("/"):
        url += "/"
    cfg["url"] = url if url.startswith(("https://", "http://")) and "OWNER" not in url else ""
    repo = cfg["repo"].strip()
    cfg["repo"] = repo if re.match(r"^[\w.-]+/[\w.-]+$", repo) and not repo.startswith("OWNER/") else ""
    branch = cfg["branch"].strip()
    valid = re.match(r"^[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*$", branch) and ".." not in branch
    cfg["branch"] = branch if valid else "main"
    return cfg


def http_get(url, timeout=15):
    if not url.startswith(("https://", "http://")):
        raise ValueError(f"Geen webadres: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Prompt-app"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise ValueError("Bestand is te groot")
    return data.decode("utf-8")


def safe_rel(rel):
    return isinstance(rel, str) and bool(SAFE_PATH_RE.match(rel)) and ".." not in rel.split("/")


def safe_files(skill):
    """Geldige, unieke bestandspaden. Windows ziet SKILL.md en skill.md als hetzelfde bestand, en een bestand
    kan niet dezelfde naam hebben als een map; zulke dubbelingen vallen weg."""
    files = skill.get("files")
    if not isinstance(files, list):
        return []
    out, seen = [], set()
    for f in files:
        if safe_rel(f) and f.lower() not in seen:
            seen.add(f.lower())
            out.append(f)
    dirs = {"/".join(f.lower().split("/")[:i]) for f in out for i in range(1, f.count("/") + 1)}
    return [f for f in out if f.lower() not in dirs]


def file_url(base, name, rel="SKILL.md"):
    return f"{base}skills/{urllib.parse.quote(name)}/" + "/".join(urllib.parse.quote(p) for p in rel.split("/"))


def clean_index(data):
    """Houd alleen skills met een geldige naam, een SKILL.md en de velden die we gebruiken."""
    def as_list(value):
        return value if isinstance(value, list) else []

    def as_text(value, default=""):
        return value if isinstance(value, str) else (str(value) if isinstance(value, (int, float)) else default)

    out = []
    skills = data.get("skills") if isinstance(data, dict) else None
    for s in as_list(skills):
        if not isinstance(s, dict) or not isinstance(s.get("name"), str) or not NAME_RE.match(s["name"]):
            continue
        files = safe_files(s)
        if "SKILL.md" not in files:
            continue
        safety = s.get("safety") if isinstance(s.get("safety"), dict) else {}
        category = s.get("category")
        out.append({
            "name": s["name"],
            "description": as_text(s.get("description")),
            "summary_nl": as_text(s.get("summary_nl")),
            "author": as_text(s.get("author"), "onbekend") or "onbekend",
            "category": category if isinstance(category, str) and category in CATEGORY_NL else "other",
            "tags": [t for t in as_list(s.get("tags")) if isinstance(t, str)][:10],
            "version": as_text(s.get("version"), "1.0.0") or "1.0.0",
            "updated": as_text(s.get("updated")),
            "files": files,
            "hits": [h for h in as_list(safety.get("hits") or s.get("hits")) if isinstance(h, dict)],
            "hosts": [h for h in as_list(safety.get("hosts") or s.get("hosts")) if isinstance(h, str)],
        })
    return out


class HttpSource:
    """Online marktplaats (GitHub Pages of een andere site met dezelfde indeling)."""

    def __init__(self, url):
        self.url = url
        self.key = url
        self.label = "online"

    def index(self):
        return clean_index(json.loads(http_get(self.url + "data/index.json")))

    def text(self, name, rel="SKILL.md"):
        return http_get(file_url(self.url, name, rel))


class LocalSource:
    """Ingebouwde catalogus: dezelfde skills, meegeleverd met de app."""

    def __init__(self, index_file, skills_dir):
        self.index_file = Path(index_file)
        self.skills_dir = Path(skills_dir)
        self.key = "local:" + str(self.index_file)
        self.label = "ingebouwd"

    def index(self):
        return clean_index(json.loads(self.index_file.read_text(encoding="utf-8")))

    def text(self, name, rel="SKILL.md"):
        if not NAME_RE.match(name) or not safe_rel(rel):
            raise ValueError(f"Ongeldig pad: {name}/{rel}")
        return self.skills_dir.joinpath(name, *rel.split("/")).read_text(encoding="utf-8")


def market_source(cfg):
    if cfg.get("url"):
        return HttpSource(cfg["url"])
    return bundled_source()


def bundled_source():
    """De catalogus die met de app is meegeleverd (ook bruikbaar als de online marktplaats niet bereikbaar is)."""
    candidates = [
        (CATALOG_DIR / "data" / "index.json", CATALOG_DIR / "skills"),  # geïnstalleerde app
        (APP_DIR / "catalog-index.json", APP_DIR.parent / "skills"),    # vanuit de broncode
    ]
    for index_file, skills_dir in candidates:
        if index_file.is_file() and skills_dir.is_dir():
            return LocalSource(index_file, skills_dir)
    return None


# Installeren, aan/uit en verwijderen raken dezelfde mappen; nooit twee tegelijk.
FILE_LOCK = threading.RLock()


def check_folder(name):
    """Eigen skills mogen elke gewone mapnaam hebben; padtrucs en lege namen niet."""
    if (not isinstance(name, str) or not name.strip() or name != name.strip() or name in (".", "..")
            or len(name) > 200 or any(c in name for c in '/\\:*?"<>|\0')):
        raise ValueError(f"Ongeldige mapnaam: {name!r}")
    return name


def skill_dirs(skills_dir=None, library_dir=None):
    """(aan-map, uit-map). Geef je alleen een eigen aan-map op, dan ligt de uit-map daar naast; we vallen dan
    nooit terug op de echte ~/.claude/skills-uit."""
    on_dir = Path(skills_dir) if skills_dir else SKILLS_DIR
    if library_dir:
        off_dir = Path(library_dir)
    elif skills_dir:
        off_dir = on_dir.parent / "skills-uit"
    else:
        off_dir = LIBRARY_DIR
    return on_dir, off_dir


def skill_state(name, skills_dir=None, library_dir=None):
    """'on' (Claude laadt hem), 'off' (staat in skills-uit) of None (niet aanwezig)."""
    on_dir, off_dir = skill_dirs(skills_dir, library_dir)
    if (on_dir / name / "SKILL.md").is_file():
        return "on"
    if (off_dir / name / "SKILL.md").is_file():
        return "off"
    return None


def is_installed(name, skills_dir=None, library_dir=None):
    return skill_state(name, skills_dir, library_dir) is not None


def set_skill_active(name, active, skills_dir=None, library_dir=None):
    """Zet een skill aan (naar ~/.claude/skills) of uit (naar ~/.claude/skills-uit). Verplaatsen, nooit wissen."""
    check_folder(name)
    on_dir, off_dir = skill_dirs(skills_dir, library_dir)
    src, dst = (off_dir / name, on_dir / name) if active else (on_dir / name, off_dir / name)
    with FILE_LOCK:
        if not src.is_dir():
            if dst.is_dir():
                return dst  # staat al goed
            raise FileNotFoundError(f"/{name} niet gevonden")
        if dst.exists():
            raise FileExistsError(f"/{name} staat al in {dst.parent}")
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return dst


def install_skill(source, skill, skills_dir=None, library_dir=None, active=True):
    """Haal alle bestanden eerst op; pas als alles binnen is komt de map in ~/.claude/skills (of skills-uit)."""
    on_dir, off_dir = skill_dirs(skills_dir, library_dir)
    skills_dir = on_dir if active else off_dir
    name = skill["name"]
    if not NAME_RE.match(name):
        raise ValueError(f"Ongeldige naam: {name}")
    files = safe_files(skill)
    if "SKILL.md" not in files:
        raise ValueError("Deze skill heeft geen SKILL.md")
    contents = {rel: source.text(name, rel) for rel in files}  # eerst alles binnen, buiten het slot

    with FILE_LOCK:
        work = skills_dir.parent / ".prompt-installing"
        work.mkdir(parents=True, exist_ok=True)
        tmp = Path(tempfile.mkdtemp(prefix=f"{name}-", dir=work))
        try:
            staging = tmp / "new"
            for rel, text in contents.items():
                dest = staging.joinpath(*rel.split("/"))
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text(text, encoding="utf-8", newline="")
            skills_dir.mkdir(parents=True, exist_ok=True)
            target = skills_dir / name
            # Oude versie (aan of uit) eerst opzij zetten; pas weggooien als de nieuwe er staat.
            parked = []
            for i, old in enumerate((on_dir / name, off_dir / name)):
                if old.exists():
                    spot = tmp / f"old{i}"
                    shutil.move(str(old), str(spot))
                    parked.append((old, spot))
            try:
                shutil.move(str(staging), str(target))
            except BaseException:
                for old, spot in parked:
                    shutil.move(str(spot), str(old))
                raise
            return target
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
            try:
                work.rmdir()
            except OSError:
                pass


def remove_skill(name, skills_dir=None, library_dir=None):
    check_folder(name)
    with FILE_LOCK:
        for base in skill_dirs(skills_dir, library_dir):
            target = base / name
            if target.resolve().parent != base.resolve():
                raise ValueError(f"Onveilig pad: {target}")
            if target.is_dir():
                shutil.rmtree(target)


def build_prompt(items, task=""):
    """items: [(naam, volledige SKILL.md-tekst)]. Plak het resultaat in Claude Code; Claude volgt de skill meteen."""
    if len(items) == 1:
        head = ("Gebruik de skill hieronder voor de rest van dit gesprek. Pas hem toe zodra een taak "
                "erbij past; je hoeft hem niet te installeren.")
    else:
        head = (f"Gebruik de {len(items)} skills hieronder voor de rest van dit gesprek. Pas elke skill toe "
                "zodra een taak erbij past; je hoeft ze niet te installeren.")
    def fence(text):
        # Een skill die zelf </skill> of <skill bevat, kan zijn blok niet doorbreken.
        return text.strip().replace("</skill", "<\\/skill").replace("<skill", "<\\skill")

    blocks = "\n\n".join(f'<skill name="{str(name).replace(chr(34), "")}">\n{fence(text)}\n</skill>'
                           for name, text in items)
    tail = f"\n\nMijn taak: {task.strip()}" if task and task.strip() else ""
    return f"{head}\n\n{blocks}{tail}\n"


def github_share_url(repo, branch, name, text):
    """Link naar GitHub 'nieuw bestand' met de skill al ingevuld; GitHub maakt zo nodig een fork en een PR."""
    url = (f"https://github.com/{repo}/new/{urllib.parse.quote(branch)}?"
           + urllib.parse.urlencode({"filename": f"skills/{name}/SKILL.md", "value": text}, quote_via=urllib.parse.quote))
    return url if len(url) <= GITHUB_URL_LIMIT else None


def load_market_state():
    try:
        data = json.loads(read_text(MARKET_STATE) or "{}")
        return {k: v for k, v in data.items() if NAME_RE.match(k) and isinstance(v, dict)}
    except (ValueError, AttributeError):
        return {}


# --------------------------------------------------------------------------- #
# Een instantie tegelijk
# --------------------------------------------------------------------------- #
def try_signal_existing(signal=True):
    """Draait er al een instantie? Geef True terug; met signal=True vraag je die ook naar voren te komen."""
    try:
        with socket.create_connection(("127.0.0.1", PORT), timeout=0.5) as s:
            s.sendall(b"SHOW\n" if signal else b"PING\n")
        return True
    except OSError:
        return False


def claim_port():
    """Claim de poort van Prompt meteen bij het opstarten. Lukt dat niet, dan draait er al een Prompt.
    Op Windows exclusief: anders kunnen twee programma's dezelfde poort openen en krijg je twee vensters."""
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if IS_WINDOWS:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("127.0.0.1", PORT))
        srv.listen(5)
    except OSError:
        srv.close()
        raise
    return srv


def start_server(on_show, srv=None):
    srv = srv or claim_port()

    def loop():
        while True:
            try:
                conn, _ = srv.accept()
            except OSError:
                return
            with conn:
                try:
                    conn.settimeout(1)
                    data = conn.recv(64)
                except OSError:
                    data = b""
            if b"SHOW" in data:
                on_show()

    threading.Thread(target=loop, daemon=True).start()
    return srv


# --------------------------------------------------------------------------- #
# Widgets
# --------------------------------------------------------------------------- #
ICON_GLYPHS = {  # Segoe Fluent Icons / Segoe MDL2 Assets
    "search": "", "settings": "", "copy": "", "download": "", "delete": "",
    "refresh": "", "folder": "", "check": "", "share": "", "open": "",
    "chevron": "", "doc": "", "close": "", "filter": "", "update": "",
}
# Zonder Windows-iconenlettertype: alleen tekens die vrijwel elk lettertype heeft; de rest zonder icoon.
ICON_FALLBACK = {
    "search": "⌕", "settings": "⚙", "copy": "", "download": "↓", "delete": "✕", "refresh": "⟳",
    "folder": "", "check": "✓", "share": "↗", "open": "↗", "chevron": "▾", "doc": "", "close": "✕",
    "filter": "", "update": "↑",
}


def round_rect(canvas, x1, y1, x2, y2, r, **kw):
    r = max(0, min(r, (x2 - x1) / 2, (y2 - y1) / 2))
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
           x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return canvas.create_polygon(pts, smooth=True, **kw)


class ScrollArea(tk.Frame):
    """Scrollbaar gebied zonder Canvas: de inhoud (self.inner) wordt met place() verschoven binnen dit frame,
    dat hem afknipt. Een Canvas met een venster-item op volle breedte liet Tk 9 op macOS het hele venster
    honderden keren hertekenen (30 s bij het starten); dit doet hetzelfde met één verschuiving per ronde."""

    def __init__(self, master, scrollbar, inset=0, **kw):
        super().__init__(master, **kw)
        self.sb = scrollbar
        self.top = 0
        self._job = None
        self._when_sized = []
        self.inner = tk.Frame(self, bg=kw.get("bg"))
        self.inner.place(x=0, y=0, relwidth=1, width=-inset)
        self.bind("<Configure>", self._changed)
        self.inner.bind("<Configure>", self._changed)

    def _sizes(self):
        return max(1, self.inner.winfo_reqheight()), max(1, self.winfo_height())

    def _changed(self, _=None):
        if self._job is None:
            self._job = self.after_idle(self._apply)

    def when_sized(self, callback):
        """Roep callback aan zodra de inhoud een echte breedte heeft (meteen, als dat al zo is)."""
        if self.inner.winfo_width() > 1:
            callback()
        elif callback not in self._when_sized:
            self._when_sized.append(callback)

    def _apply(self):
        self._job = None
        if self._when_sized and self.inner.winfo_width() > 1:
            callbacks, self._when_sized = self._when_sized, []
            for callback in callbacks:
                callback()
        try:
            total, view = self._sizes()
            self.top = min(max(0, int(self.top)), max(0, total - view))
            if str(-self.top) != self.inner.place_info().get("y"):
                self.inner.place_configure(y=-self.top)
            self.sb.set(self.top / total, min(1.0, (self.top + view) / total))
        except tk.TclError:
            pass

    def can_scroll(self):
        total, view = self._sizes()
        return total > view

    def yview(self, *args):
        """Zelfde aanroep als Canvas.yview: zonder argumenten de positie, anders vanuit de scrollbalk."""
        if not args:
            total, view = self._sizes()
            return self.top / total, min(1.0, (self.top + view) / total)
        if args[0] == "moveto":
            self.yview_moveto(float(args[1]))
        elif args[0] == "scroll":
            self.yview_scroll(int(args[1]), args[2])

    def yview_moveto(self, fraction):
        self.top = float(fraction) * self._sizes()[0]
        self._apply()

    def yview_scroll(self, number, what="units"):
        view = self._sizes()[1]
        step = {"pages": view * 0.9, "pixels": 1}.get(what, max(20, view / 10))
        self.top += number * step
        self._apply()


class Pill(tk.Canvas):
    """Afgeronde knop. kind: primary | secondary | ghost | chip | nav | ok"""

    def __init__(self, parent, app, text="", command=None, kind="secondary", icon=None, selected=False,
                 small=False, bg=None):
        self.app, self.text, self.command, self.kind = app, text, command, kind
        self.icon, self.selected, self.small = icon, selected, small
        self.hover = False
        self.parent_bg = bg or C["bg"]
        super().__init__(parent, highlightthickness=0, bd=0, bg=self.parent_bg, cursor="hand2", takefocus=1)
        self.bind("<Enter>", lambda e: self._set_hover(True))
        self.bind("<Leave>", lambda e: self._set_hover(False))
        self.bind("<ButtonRelease-1>", self._click)
        self.bind("<Return>", self._click)
        self.bind("<space>", self._click)
        self.draw()

    def _set_hover(self, value):
        self.hover = value
        self.draw()

    def _click(self, _event=None):
        if self.command:
            self.app.root.after(0, self.command)  # na de klik: de knop mag dan al vervangen zijn

    def colors(self):
        k, h, sel = self.kind, self.hover, self.selected
        if k == "primary":
            fill = C["accent_hover"] if h else C["accent"]
            return fill, C["on_accent"], fill
        if k == "ok":
            return C["ok"], C["surface"], C["ok"]
        if k == "secondary":
            return (C["hover"] if h else C["surface"]), C["accent_text"], C["border"]
        if k == "ghost":
            fill = C["surface2"] if h else self.parent_bg
            return fill, C["accent_text"], fill
        if sel:  # chip of nav, geselecteerd
            return C["text"], C["bg"], C["text"]
        if k == "chip":
            return (C["surface2"] if h else C["surface"]), C["text"], C["border"]
        fill = C["surface2"] if h else self.parent_bg  # nav
        return fill, (C["text"] if h else C["muted"]), fill

    def draw(self):
        try:
            self.delete("all")
        except tk.TclError:
            return
        app = self.app
        font = app.font(app.f_btn_b if self.kind in ("primary", "ok") else app.f_btn)
        ifont = app.font(app.f_icon) if app.icon_font else font
        icon = self.icon_char() if self.icon else ""
        gap = app.s(6) if (icon and self.text) else 0
        tw = font.measure(self.text) if self.text else 0
        iw = ifont.measure(icon) if icon else 0
        padx = app.s(9 if self.small else 13)
        pady = app.s(4 if self.small else 6)
        h = max(font.metrics("linespace"), ifont.metrics("linespace") if icon else 0) + 2 * pady
        w = tw + iw + gap + 2 * padx
        if not self.text:
            w = h  # alleen een icoon: rond
        self.configure(width=w, height=h, bg=self.parent_bg)
        fill, fg, outline = self.colors()
        radius = h / 2 if self.kind in ("chip", "nav") or not self.text else app.s(8)
        round_rect(self, 1, 1, w - 1, h - 1, radius, fill=fill, outline=outline)
        x = (w - tw - iw - gap) / 2
        if icon:
            self.create_text(x, h / 2, text=icon, font=ifont, fill=fg, anchor="w")
            x += iw + gap
        if self.text:
            self.create_text(x, h / 2, text=self.text, font=font, fill=fg, anchor="w")

    def icon_char(self):
        return (ICON_GLYPHS if self.app.icon_font else ICON_FALLBACK).get(self.icon, self.icon)

    def set(self, text=None, kind=None, selected=None, bg=None):
        if text is not None:
            self.text = text
        if kind is not None:
            self.kind = kind
        if selected is not None:
            self.selected = selected
        if bg is not None:
            self.parent_bg = bg
        self.draw()


class Switch(tk.Canvas):
    def __init__(self, parent, app, value, command, bg=None):
        self.app, self.value, self.command = app, bool(value), command
        self.parent_bg = bg or C["surface"]
        w, h = app.s(40), app.s(22)
        super().__init__(parent, width=w, height=h, highlightthickness=0, bd=0, bg=self.parent_bg,
                         cursor="hand2", takefocus=1)
        self.w, self.h = w, h
        self.bind("<ButtonRelease-1>", self.toggle)
        self.bind("<space>", self.toggle)
        self.draw()

    def toggle(self, _event=None):
        self.value = not self.value
        self.draw()
        self.app.root.after(0, lambda: self.command(self.value))

    def draw(self):
        self.delete("all")
        track = C["accent"] if self.value else C["border"]
        round_rect(self, 1, 1, self.w - 1, self.h - 1, self.h / 2, fill=track, outline=track)
        d = self.h - self.app.s(6)
        x = self.w - d - self.app.s(3) if self.value else self.app.s(3)
        knob = C["on_accent"] if self.value else C["muted"]
        self.create_oval(x, self.app.s(3), x + d, self.app.s(3) + d, fill=knob, outline=knob)


# --------------------------------------------------------------------------- #
# UI
# --------------------------------------------------------------------------- #
class App:
    def __init__(self, root, start_view=None, hidden=False):
        self.root = root
        self.settings = load_settings()
        self.items = []
        self.fp = None
        self.expanded = set()
        self.local_filter = FILTER_ALL
        self.search_text = ""
        self.view = start_view or self.settings["start_view"]

        self.market_cfg = load_registry_config()
        self.source = market_source(self.market_cfg)
        self.market_skills = []
        self.market_loaded = False
        self.market_loading = False
        self.market_note = ""
        self.market_state = load_market_state()
        self.market_texts = {}
        self.market_expanded = set()
        self.m_search_text = ""
        self.m_task_text = ""
        self.m_category = "all"
        self.m_sort = "relevance"
        self.m_only_installed = False
        self.m_only_updates = False
        self.m_hide_notes = False
        self.m_fields = {}

        self.claude_running = False if hidden else claude_is_running()
        self.claude_app = None
        self._wrap_known, self._wrap_pending, self._wrap_job = {}, {}, None
        self.claude_cli = shutil.which("claude")
        self._show_requested = False
        self._save_job = None
        self._fonts = {}
        self.flash_jobs = {}
        self.ui_built = False

        root.title(APP_NAME)
        set_window_icon(root)
        self.load_state()
        root.minsize(self.s(440), self.s(420))
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Alleen het venster zelf, niet elk kindwidget: een binding op root geldt in Tk ook voor alle widgets
        # erin, en dan riep elke maatverandering Python aan (duizenden keren bij het starten, 27 s op macOS).
        root.bindtags(("PromptWindow",) + root.bindtags())
        root.bind_class("PromptWindow", "<Configure>", self.on_configure)
        root.bind_all("<MouseWheel>", self.on_mousewheel)
        root.bind_all("<Button-4>", lambda e: self.scroll_active(-3))  # Linux: wieltje omhoog
        root.bind_all("<Button-5>", lambda e: self.scroll_active(3))   # Linux: wieltje omlaag
        mod = "Command" if IS_MAC else "Control"
        root.bind_all(f"<{mod}-f>", lambda e: self.focus_search())
        root.bind_all(f"<{mod}-comma>", lambda e: self.show_view("settings"))

        self.items = scan_all()
        self.fp = fingerprint()
        self.build_ui()
        if hidden:
            root.withdraw()
        root.after(POLL_MS, self.poll)
        root.after(300, self.check_show_request)
        root.after(WATCH_MS, self.watch_claude)
        if self.source and (self.view == "market" or self.settings["check_updates"]):
            root.after(600, self.load_market)
        self.run_bg(find_claude_app, self.on_claude_app_found, lambda e: None)

    def on_claude_app_found(self, app_id):
        if app_id == self.claude_app:
            return  # niets veranderd: de lijst niet voor niets opnieuw opbouwen
        self.claude_app = app_id
        self.rebuild()

    # -- maten en lettertypes ---------------------------------------------- #
    def s(self, px):
        return int(round(px * self.scale))

    def font(self, spec):
        f = self._fonts.get(spec)
        if f is None:
            f = self._fonts[spec] = tkfont.Font(root=self.root, font=spec)
        return f

    def make_fonts(self):
        families = set(tkfont.families(self.root))

        def pick(options, fallback):
            return next((f for f in options if f in families), fallback)

        default = tkfont.nametofont("TkDefaultFont", root=self.root).actual("family")
        fixed = tkfont.nametofont("TkFixedFont", root=self.root).actual("family")
        ui = pick(("Segoe UI Variable Text", "Segoe UI", ".AppleSystemUIFont", "SF Pro Text", "Helvetica Neue",
                   "Ubuntu", "Cantarell", "Noto Sans", "DejaVu Sans"), default)
        display = pick(("Segoe UI Variable Display", ".AppleSystemUIFont", "SF Pro Display"), ui)
        mono = pick(("Cascadia Mono", "Cascadia Code", "Consolas", "SF Mono", "Menlo", "Ubuntu Mono",
                     "DejaVu Sans Mono", "Liberation Mono"), fixed)
        self.icon_font = pick(("Segoe Fluent Icons", "Segoe MDL2 Assets"), None) if IS_WINDOWS else None
        # macOS rekent lettergroottes in schermpunten van 72 dpi: iets groter maken, zodat het even groot oogt.
        k = TEXT_SIZES[self.settings["text_size"]] * (1.3 if IS_MAC else 1.0)

        def size(n):
            return max(7, round(n * k))

        self.f_title = (display, size(15), "bold")
        self.f_h2 = (display, size(12), "bold")
        self.f_body = (ui, size(10))
        self.f_body_b = (ui, size(10), "bold")
        self.f_small = (ui, size(9))
        self.f_tiny = (ui, size(8))
        self.f_badge = (ui, size(8), "bold")
        self.f_head = (ui, size(8), "bold")
        self.f_cmd = (mono, size(11), "bold")
        self.f_mono = (mono, size(10))
        self.f_btn = (ui, size(9))
        self.f_btn_b = (ui, size(9), "bold")
        self.f_icon = (self.icon_font or ui, size(10))

    # -- opbouw ------------------------------------------------------------- #
    def is_dark(self):
        theme = self.settings["theme"]
        return theme == "dark" or (theme == "system" and system_prefers_dark())

    def build_ui(self):
        dark = self.is_dark()
        set_palette(dark, self.settings["accent"])
        self.make_fonts()
        self.flash_jobs = {}
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg=C["bg"])
        self.root.attributes("-topmost", self.settings["always_on_top"])
        apply_titlebar(self.root, dark)

        style = ttk.Style(self.root)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("Prompt.Vertical.TScrollbar", troughcolor=C["bg"], background=C["surface2"],
                        bordercolor=C["bg"], lightcolor=C["surface2"], darkcolor=C["surface2"],
                        arrowcolor=C["muted"], gripcount=0, relief="flat")
        style.map("Prompt.Vertical.TScrollbar", background=[("active", C["border"])])

        self.build_header()
        self.status = tk.Label(self.root, text="", anchor="w", bg=C["bg"], fg=C["faint"], font=self.f_tiny)
        self.status.pack(side="bottom", fill="x", padx=self.s(16), pady=(self.s(2), self.s(8)))
        self.content = tk.Frame(self.root, bg=C["bg"])
        self.content.pack(fill="both", expand=True)
        self.views = {
            "local": self.build_local_view(),
            "market": self.build_market_view(),
            "settings": self.build_settings_view(),
        }
        self.ui_built = True
        self.show_view(self.view)
        self.rebuild()
        self.rebuild_market()

    def build_header(self):
        top = tk.Frame(self.root, bg=C["bg"])
        top.pack(fill="x", padx=self.s(14), pady=(self.s(12), self.s(10)))
        size = self.s(28)
        logo = tk.Canvas(top, width=size, height=size, bg=C["bg"], highlightthickness=0)
        round_rect(logo, 0, 0, size, size, self.s(8), fill=C["accent"], outline=C["accent"])
        logo.create_text(size / 2, size / 2, text="/", font=(self.f_cmd[0], self.f_cmd[1] + 1, "bold"),
                         fill=C["on_accent"])
        logo.pack(side="left")
        tk.Label(top, text=APP_NAME, font=self.f_title, bg=C["bg"], fg=C["text"]).pack(
            side="left", padx=(self.s(8), self.s(14)))
        self.nav = {}
        for key, label in (("local", "Mijn commands"), ("market", "Marktplaats")):
            p = Pill(top, self, label, kind="nav", command=lambda k=key: self.show_view(k))
            p.pack(side="left", padx=(0, self.s(4)))
            self.nav[key] = p
        self.nav["settings"] = Pill(top, self, "", icon="settings", kind="nav",
                                    command=lambda: self.show_view("settings"))
        self.nav["settings"].pack(side="right")

    def update_nav(self):
        if not getattr(self, "nav", None):
            return
        updates = sum(1 for s in self.market_skills if self.market_status(s) == "update")
        for key, pill in self.nav.items():
            text = None
            if key == "market":
                text = "Marktplaats" + (f"  ·  {updates}" if updates else "")
            try:
                pill.set(text=text, selected=(key == self.view))
            except tk.TclError:
                pass

    def show_view(self, view):
        self.view = view
        for key, frame in self.views.items():
            if key != view:
                frame.pack_forget()
        self.views[view].pack(fill="both", expand=True)
        self.update_nav()
        if view == "market":
            if not self.market_loaded:
                self.load_market()
            if getattr(self, "market_dirty", False):
                self.rebuild_market()
            self.update_market_info()
            self.m_entry.focus_set()
        elif view == "local":
            self.set_status(f"{len(self.visible_items())} commands")
            self.entry.focus_set()
        else:
            self.set_status(f"Prompt {APP_VERSION}  ·  instellingen worden meteen bewaard")

    def focus_search(self):
        if self.view == "settings":
            self.show_view("local")
        (self.m_entry if self.view == "market" else self.entry).focus_set()

    def set_status(self, text):
        try:
            self.status.configure(text=text)
        except (tk.TclError, AttributeError):
            pass

    # -- gedeelde bouwstenen ------------------------------------------------- #
    def make_scroll(self, parent):
        body = tk.Frame(parent, bg=C["bg"])
        body.pack(fill="both", expand=True, padx=(self.s(14), self.s(4)))
        sb = ttk.Scrollbar(body, orient="vertical", style="Prompt.Vertical.TScrollbar")
        sb.pack(side="right", fill="y")
        area = ScrollArea(body, sb, inset=self.s(8), bg=C["bg"])
        sb.configure(command=area.yview)
        area.pack(side="left", fill="both", expand=True)
        return area, area.inner

    def search_box(self, parent, var, placeholder, on_change, on_enter=None):
        box = tk.Frame(parent, bg=C["field"], highlightthickness=1, highlightbackground=C["border"],
                       highlightcolor=C["accent"])
        box.pack(fill="x", padx=self.s(14), pady=(0, self.s(8)))
        icon = ICON_GLYPHS["search"] if self.icon_font else ICON_FALLBACK["search"]
        tk.Label(box, text=icon, font=self.f_icon, bg=C["field"], fg=C["muted"]).pack(
            side="left", padx=(self.s(12), self.s(6)))
        entry = tk.Entry(box, textvariable=var, relief="flat", bd=0, bg=C["field"], fg=C["text"],
                         insertbackground=C["text"], font=self.f_body, highlightthickness=0)
        entry.pack(side="left", fill="x", expand=True, ipady=self.s(8), padx=(0, self.s(10)))
        hint = tk.Label(box, text=placeholder, bg=C["field"], fg=C["faint"], font=self.f_body, anchor="w")

        def placeholder_update():
            if var.get():
                hint.place_forget()
            else:
                hint.place(in_=entry, x=0, rely=0.5, anchor="w")

        var.trace_add("write", lambda *_: (placeholder_update(), on_change()))
        placeholder_update()
        hint.bind("<Button-1>", lambda e: entry.focus_set())
        entry.bind("<Escape>", lambda e: var.set(""))
        if on_enter:
            entry.bind("<Return>", lambda e: on_enter())
        entry.bind("<FocusIn>", lambda e: box.configure(highlightbackground=C["accent"]))
        entry.bind("<FocusOut>", lambda e: box.configure(highlightbackground=C["border"]))
        return entry

    def field_entry(self, parent, var, width=None):
        frame = tk.Frame(parent, bg=C["field"], highlightthickness=1, highlightbackground=C["border"],
                         highlightcolor=C["accent"])
        entry = tk.Entry(frame, textvariable=var, relief="flat", bd=0, bg=C["field"], fg=C["text"],
                         insertbackground=C["text"], font=self.f_small, width=width or 20,
                         highlightthickness=0)
        entry.pack(fill="x", ipady=self.s(5), padx=self.s(8))
        entry.bind("<FocusIn>", lambda e: frame.configure(highlightbackground=C["accent"]))
        entry.bind("<FocusOut>", lambda e: frame.configure(highlightbackground=C["border"]))
        return frame, entry

    def flow(self, frame, widgets, gap=None):
        """Zet widgets naast elkaar en begint een nieuwe regel als ze niet meer passen."""
        gap = self.s(6) if gap is None else gap

        def layout(_=None):
            width = frame.winfo_width()
            if width <= 1:
                return
            x = y = line_h = 0
            for w in widgets:
                try:
                    ww, wh = w.winfo_reqwidth(), w.winfo_reqheight()
                except tk.TclError:
                    return
                if x and x + ww > width:
                    x, y, line_h = 0, y + line_h + gap, 0
                w.place(x=x, y=y)
                x += ww + gap
                line_h = max(line_h, wh)
            if int(frame.cget("height")) != max(1, y + line_h):
                frame.configure(height=max(1, y + line_h))

        # Geen update_idletasks() hier: Tk 9 op macOS crasht daarop als het scherm nog niet zichtbaar is.
        # De opmaak volgt vanzelf zodra het frame een breedte krijgt (<Configure>) of Tk tijd heeft (after_idle).
        frame.bind("<Configure>", layout)
        frame.after_idle(layout)

    def restore_scroll(self, area, position):
        """De scrollpositie terugzetten zodra Tk de nieuwe lijst heeft opgemeten."""
        area.after_idle(lambda: area.yview_moveto(position))

    def wrap_to(self, label, container, minus=0, key=None, guess=None):
        """Laat de tekst afbreken op de breedte van de container.

        Een nieuwe afbreekbreedte laat Tk de hele lijst opnieuw opmeten, en dat is op macOS met Tk 9 traag (seconden
        voor een lange lijst). Daarom krijgt een label meteen een goede breedte (`guess`, of de laatst bekende voor
        `key`), wordt hij alleen aangepast als de tekst echt niet past of er flink meer ruimte is, en gaan alle
        aanpassingen samen in één ronde (after_idle)."""
        last = [None]
        start = guess if guess and guess > 1 else (self._wrap_known.get(key) if key else None)
        if start:
            start = max(120, int(start))
            last[0] = start
            label.configure(wraplength=start)

        def on_configure(event):
            width = max(120, event.width - minus)
            if last[0] is not None and 0 <= width - last[0] < self.s(40):
                return  # past al; een paar pixels extra ruimte is het opnieuw opmeten niet waard
            last[0] = width
            if key:
                self._wrap_known[key] = width
            self._wrap_pending[label] = width
            if self._wrap_job is None:
                self._wrap_job = self.root.after_idle(self._apply_wraps)

        container.bind("<Configure>", on_configure, add="+")

    def _apply_wraps(self):
        self._wrap_job = None
        pending, self._wrap_pending = self._wrap_pending, {}
        for label, width in pending.items():
            try:
                label.configure(wraplength=width)
            except tk.TclError:
                pass  # label is intussen weggegooid

    def card(self, parent):
        row = tk.Frame(parent, bg=C["surface"], highlightbackground=C["border"], highlightthickness=1)
        row.pack(fill="x", pady=self.s(4), padx=self.s(2))
        return row

    def hoverable(self, widgets, on_click=None):
        def paint(color):
            for w in widgets:
                try:
                    if isinstance(w, Pill):
                        w.set(bg=color)
                    else:
                        w.configure(bg=color)
                except tk.TclError:
                    pass

        for w in widgets:
            if isinstance(w, (Pill, Switch)):
                continue
            w.bind("<Enter>", lambda e: paint(C["hover"]))
            w.bind("<Leave>", lambda e: paint(C["surface"]))
            if on_click:
                w.bind("<Button-1>", lambda e: on_click())
                w.configure(cursor="hand2")

    def badge(self, parent, text, color):
        return tk.Label(parent, text=text, font=self.f_badge, bg=C["surface"], fg=color)

    def section(self, parent, kop, tekst, color=None, mono=False):
        tk.Label(parent, text=kop.upper(), font=self.f_head, bg=C["surface"], fg=C["faint"], anchor="w").pack(
            anchor="w", pady=(self.s(4), 0))
        lbl = tk.Label(parent, text=tekst, font=self.f_mono if mono else self.f_small, bg=C["surface"],
                       fg=color or C["text"], anchor="w", justify="left")
        lbl.pack(anchor="w", fill="x", pady=(self.s(2), self.s(8)))
        self.wrap_to(lbl, parent)
        return lbl

    def empty_state(self, parent, title, text, action=None):
        box = tk.Frame(parent, bg=C["bg"])
        box.pack(fill="x", pady=self.s(40))
        tk.Label(box, text=title, font=self.f_h2, bg=C["bg"], fg=C["text"]).pack()
        lbl = tk.Label(box, text=text, font=self.f_small, bg=C["bg"], fg=C["muted"], justify="center")
        lbl.pack(pady=(self.s(4), self.s(12)))
        self.wrap_to(lbl, box, self.s(40))
        if action:
            Pill(box, self, action[0], command=action[1], kind="primary").pack()

    def run_bg(self, work, done, fail):
        """Werk in een achtergrondthread; done/fail draaien weer op de tkinter-thread."""
        box = {}

        def target():
            try:
                box["ok"] = work()
            except Exception as e:  # noqa: BLE001 - elke fout moet in de UI terechtkomen
                box["err"] = e

        thread = threading.Thread(target=target, daemon=True)
        thread.start()

        def check():
            if thread.is_alive():
                self.root.after(100, check)
            elif "err" in box:
                fail(box["err"])
            else:
                done(box.get("ok"))

        self.root.after(100, check)

    # -- meldingen ------------------------------------------------------------ #
    def toast(self, text, kind="ok"):
        """Korte melding onderin het venster; verdwijnt vanzelf."""
        old = getattr(self, "_toast", None)
        if old is not None:
            try:
                self.root.after_cancel(old[1])
                old[0].destroy()
            except (tk.TclError, ValueError):
                pass
        color = {"ok": C["text"], "warn": C["warn"], "error": C["danger"]}.get(kind, C["text"])
        box = tk.Frame(self.root, bg=color)
        tk.Label(box, text=text, bg=color, fg=C["bg"], font=self.f_small, padx=self.s(14), pady=self.s(8),
                 wraplength=self.s(420), justify="left").pack()
        box.place(relx=0.5, rely=1.0, anchor="s", y=-self.s(34))
        box.lift()
        self._toast = (box, self.root.after(2600, box.destroy))

    # -- kopiëren -------------------------------------------------------------- #
    def copy_text(self, text, pill=None, status=None):
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.set_status(status or f"Gekopieerd: {text}")
        self.toast(status or f"Gekopieerd: {shorten(text, 60)}")
        if pill is not None:
            self.flash(pill, "Gekopieerd")
        if self.settings["minimize_after_copy"]:
            self.root.after(500, self.root.iconify)

    def flash(self, pill, text):
        old = self.flash_jobs.pop(pill, None)
        if old:
            self.root.after_cancel(old[0])
            original = old[1]
        else:
            original = (pill.text, pill.kind, pill.icon)
        pill.icon = "check"
        pill.set(text=text, kind="ok")

        def restore():
            self.flash_jobs.pop(pill, None)
            try:
                pill.icon = original[2]
                pill.set(text=original[0], kind=original[1])
            except tk.TclError:
                pass

        self.flash_jobs[pill] = (self.root.after(1500, restore), original)

    # -- tab Mijn commands ---------------------------------------------------- #
    def build_local_view(self):
        v = tk.Frame(self.content, bg=C["bg"])
        self.search_var = tk.StringVar(value=self.search_text)
        self.entry = self.search_box(v, self.search_var, "Zoek een command, of beschrijf wat je wilt doen…",
                                     self.on_local_search, on_enter=self.copy_top_result)
        self.skill_bar = tk.Frame(v, bg=C["bg"])
        self.skill_bar.pack(fill="x", padx=self.s(14), pady=(0, self.s(8)))
        self.filter_bar = tk.Frame(v, bg=C["bg"], height=1)
        self.filter_bar.pack(fill="x", padx=self.s(14), pady=(0, self.s(6)))
        self.canvas, self.list_frame = self.make_scroll(v)
        return v

    def build_skill_bar(self, items):
        """Bovenaan Mijn commands: hoeveel skills aan staan, alles aan/uit, en Claude starten."""
        for w in self.skill_bar.winfo_children():
            w.destroy()
        skills = [it for it in items if it.toggleable]
        if not skills:
            return
        on = sum(1 for it in skills if it.active)
        card = tk.Frame(self.skill_bar, bg=C["surface"], highlightbackground=C["border"], highlightthickness=1)
        card.pack(fill="x")
        inner = tk.Frame(card, bg=C["surface"])
        inner.pack(fill="x", padx=self.s(12), pady=self.s(10))
        tk.Label(inner, text=f"{on} van {len(skills)} skills aan", font=self.f_body_b, bg=C["surface"],
                 fg=C["text"], anchor="w").pack(anchor="w")
        hint = tk.Label(inner, text="Kies welke skills Claude gebruikt. Alleen skills die aan staan worden geladen "
                                    "in een nieuwe Claude-sessie; ingebouwde commands en plugins werken altijd.",
                        font=self.f_small, bg=C["surface"], fg=C["muted"], anchor="w", justify="left")
        hint.pack(anchor="w", fill="x", pady=(self.s(2), self.s(8)))
        self.wrap_to(hint, inner)
        buttons = tk.Frame(inner, bg=C["surface"], height=1)
        buttons.pack(fill="x")
        widgets = []
        if self.claude_app or self.claude_cli:
            widgets.append(Pill(buttons, self, "Start Claude", icon="open", kind="primary", small=True,
                                bg=C["surface"], command=self.start_claude))
        widgets += [
            Pill(buttons, self, "Kies skills", kind="chip", small=True, bg=C["surface"],
                 selected=self.local_filter == CAT_SKILLS, command=lambda: self.set_local_filter(CAT_SKILLS)),
            Pill(buttons, self, "Alles aan", kind="ghost", small=True, bg=C["surface"],
                 command=lambda: self.set_all_skills(True)),
            Pill(buttons, self, "Alles uit", kind="ghost", small=True, bg=C["surface"],
                 command=lambda: self.set_all_skills(False)),
        ]
        sets_pill = Pill(buttons, self, f"Sets  {len(self.settings['skill_sets'])}  ▾", kind="chip", small=True,
                         bg=C["surface"])
        sets_pill.command = lambda: self.open_menu(sets_pill, self.sets_menu_items())
        widgets.insert(2 if (self.claude_app or self.claude_cli) else 1, sets_pill)
        self.flow(buttons, widgets)

    # -- skill-sets ----------------------------------------------------------- #
    def sets_menu_items(self):
        sets = self.settings["skill_sets"]
        active = sorted(it.skill_name for it in self.items if it.toggleable and it.active)
        items = []
        for name, skills in sorted(sets.items(), key=lambda kv: kv[0].lower()):
            items.append((f"{name}  ({len(skills)})", sorted(skills) == active, lambda n=name: self.apply_set(n)))
        if items:
            items.append(None)
        items.append((f"Huidige keuze opslaan als set…  ({len(active)} aan)", False, self.save_set))
        for name in sorted(sets, key=str.lower):
            items.append((f"Set verwijderen: {name}", False, lambda n=name: self.delete_set(n)))
        return items

    def save_set(self):
        name = simpledialog.askstring(APP_NAME, "Naam voor deze set, bijvoorbeeld 'Webontwikkeling':",
                                      parent=self.root)
        if not name or not name.strip():
            return
        name = name.strip()[:40]
        sets = dict(self.settings["skill_sets"])
        if name not in sets and len(sets) >= MAX_SETS:
            messagebox.showwarning(APP_NAME, f"Je kunt maximaal {MAX_SETS} sets bewaren.", parent=self.root)
            return
        if name in sets and not messagebox.askyesno(APP_NAME, f"Set '{name}' bestaat al. Overschrijven?",
                                                    parent=self.root):
            return
        sets[name] = sorted(it.skill_name for it in self.items if it.toggleable and it.active)
        self.change_setting("skill_sets", sets)
        self.rebuild()
        self.toast(f"Set '{name}' bewaard met {len(sets[name])} skills.")

    def apply_set(self, name):
        wanted = set(self.settings["skill_sets"].get(name, []))
        changed, errors = 0, []
        for it in self.items:
            if it.toggleable and it.active != (it.skill_name in wanted):
                try:
                    set_skill_active(it.skill_name, it.skill_name in wanted)
                    changed += 1
                except (OSError, ValueError) as e:
                    errors.append(f"/{it.skill_name}: {e}")
        present = {it.skill_name for it in self.items if it.toggleable}
        missing = sorted(wanted - present)
        self.refresh(force=True)
        note = f" ({len(missing)} niet meer aanwezig)" if missing else ""
        self.toast(f"Set '{name}' staat aan: {len(wanted & present)} skills{note}.")
        if errors:
            messagebox.showwarning(APP_NAME, "Niet alles lukte:\n\n" + "\n".join(errors[:10]), parent=self.root)

    def delete_set(self, name):
        if not messagebox.askyesno(APP_NAME, f"Set '{name}' verwijderen? De skills zelf blijven staan.",
                                   parent=self.root):
            return
        sets = dict(self.settings["skill_sets"])
        sets.pop(name, None)
        self.change_setting("skill_sets", sets)
        self.rebuild()
        self.toast(f"Set '{name}' verwijderd.")

    def copy_top_result(self):
        """Enter in het zoekveld: kopieer het bovenste resultaat."""
        _, shown = self.filtered(self.visible_items())
        if shown:
            self.copy_text(shown[0].command, status=f"Gekopieerd: {shown[0].command}")

    def toggle_skill(self, it, active):
        try:
            set_skill_active(it.skill_name, active)
        except (OSError, ValueError) as e:
            word = "aanzetten" if active else "uitzetten"
            messagebox.showerror(APP_NAME, f"Kon /{it.skill_name} niet {word}.\n\n{e}", parent=self.root)
        self.refresh(force=True)
        msg = f"/{it.skill_name} staat {'aan' if active else 'uit'}. Dit geldt vanaf een nieuwe Claude-sessie."
        self.set_status(msg)
        self.toast(msg)

    def set_all_skills(self, active):
        changed, errors = 0, []
        for it in self.items:
            if it.toggleable and it.active != active:
                try:
                    set_skill_active(it.skill_name, active)
                    changed += 1
                except (OSError, ValueError) as e:
                    errors.append(f"/{it.skill_name}: {e}")
        self.refresh(force=True)
        self.set_status(f"{changed} skills {'aangezet' if active else 'uitgezet'}.")
        self.toast(f"{changed} skills {'aangezet' if active else 'uitgezet'}.")
        if errors:
            messagebox.showwarning(APP_NAME, "Niet alles lukte:\n\n" + "\n".join(errors[:10]), parent=self.root)

    def start_claude(self):
        on = sum(1 for it in self.items if it.toggleable and it.active)
        try:
            if self.claude_app:
                launch_claude_app(self.claude_app)
                what = "De Claude-app"
            else:
                launch_claude_code()
                what = "Claude Code"
        except OSError as e:
            messagebox.showerror(APP_NAME, f"Kon Claude niet starten.\n\n{e}", parent=self.root)
            return
        self.claude_running = True  # niet nog eens naar voren springen door de eigen start
        self.set_status(f"{what} wordt gestart met {on} skills aan. Draaide Claude al, begin dan een nieuwe sessie.")

    def on_local_search(self):
        self.search_text = self.search_var.get()
        self.rebuild()

    def visible_items(self):
        hidden = set()
        if not self.settings["show_plugins"]:
            hidden.add(CAT_PLUGINS)
        if not self.settings["show_builtin"]:
            hidden.add(CAT_BUILTIN)
        return [it for it in self.items if group_of(it.category) not in hidden]

    def build_filter_bar(self, items):
        counts = {}
        for it in items:
            g = group_of(it.category)
            counts[g] = counts.get(g, 0) + 1
        groups = [FILTER_ALL] + [c for c in CATEGORY_ORDER if c in counts]
        if self.local_filter not in groups:
            self.local_filter = FILTER_ALL
        for w in self.filter_bar.winfo_children():
            w.destroy()
        widgets = []
        for g in groups:
            n = len(items) if g == FILTER_ALL else counts[g]
            widgets.append(Pill(self.filter_bar, self, f"{g}  {n}", kind="chip", small=True,
                                selected=(g == self.local_filter), command=lambda g=g: self.set_local_filter(g)))
        self.flow(self.filter_bar, widgets)

    def set_local_filter(self, group):
        self.local_filter = group
        self.rebuild()

    def filtered(self, items):
        terms = query_terms(self.search_text)
        results = []
        for it in items:
            if self.local_filter != FILTER_ALL and group_of(it.category) != self.local_filter:
                continue
            score = score_fields(terms, cmd_fields(it)) if terms else 1.0
            if score > 0:
                results.append((score, it))
        results = rank(results, terms)
        if terms:
            results.sort(key=lambda r: (-r[0], r[1].command))
        return terms, [it for _, it in results]

    def rebuild(self):
        if not hasattr(self, "list_frame"):
            return
        if self.list_frame.winfo_width() <= 1:
            # Pas opbouwen als de lijst zijn breedte kent: dan krijgt elke beschrijving meteen de goede
            # afbreekbreedte en hoeft Tk de lijst niet nog eens op te meten.
            self.canvas.when_sized(self.rebuild)
            return
        items = self.visible_items()
        self.build_skill_bar(items)
        self.build_filter_bar(items)
        y = self.canvas.yview()[0]
        for w in self.list_frame.winfo_children():
            w.destroy()
        terms, shown = self.filtered(items)
        if not shown:
            self.empty_state(self.list_frame, "Niets gevonden",
                             "Probeer een ander woord. Zoeken werkt in het Nederlands en Engels en kijkt ook in de uitleg.",
                             ("Zoek in de marktplaats", self.search_market_for_local) if terms else None)
        elif terms:
            tk.Label(self.list_frame, text=f"{len(shown)} RESULTATEN", bg=C["bg"], fg=C["faint"],
                     font=self.f_head).pack(anchor="w", pady=(self.s(4), self.s(2)), padx=self.s(2))
            for it in shown:
                self.make_row(it, show_category=True)
        else:
            cats = {}
            for it in shown:
                cats.setdefault(it.category, []).append(it)
            for cat in sorted(cats, key=category_sort_key):
                tk.Label(self.list_frame, text=cat.upper(), bg=C["bg"], fg=C["faint"], font=self.f_head).pack(
                    anchor="w", pady=(self.s(14), self.s(2)), padx=self.s(2))
                for it in cats[cat]:
                    self.make_row(it)
        self.restore_scroll(self.canvas, 0 if terms else y)

    def search_market_for_local(self):
        self.m_search_var.set(self.search_text)
        self.show_view("market")

    def make_row(self, it, show_category=False):
        is_open = it.key in self.expanded
        row = self.card(self.list_frame)
        head = tk.Frame(row, bg=C["surface"])
        head.pack(fill="x", padx=self.s(12), pady=self.s(9))
        btn = Pill(head, self, "Kopieer", icon="copy", kind="primary" if it.active else "secondary", small=True,
                   bg=C["surface"])
        btn.command = lambda: self.copy_text(it.command, btn)
        btn.pack(side="right", padx=(self.s(8), 0))
        hover = [row, head, btn]
        if it.toggleable:
            sw = Switch(head, self, it.active, lambda v: self.toggle_skill(it, v), bg=C["surface"])
            sw.pack(side="right", padx=(self.s(8), 0))
            hover.append(sw)
        text_col = tk.Frame(head, bg=C["surface"])
        text_col.pack(side="left", fill="both", expand=True)
        right = sum(w.winfo_reqwidth() + self.s(8) for w in hover[2:])
        text_w = self.list_frame.winfo_width() - 2 * self.s(2) - 2 - 2 * self.s(12) - right - self.s(4)
        title = tk.Frame(text_col, bg=C["surface"])
        title.pack(anchor="w", fill="x")
        cmd_lbl = tk.Label(title, text=it.command, font=self.f_cmd, bg=C["surface"],
                           fg=C["accent_text"] if it.active else C["faint"], anchor="w")
        cmd_lbl.pack(side="left")
        hover += [text_col, title, cmd_lbl]
        if not it.active:
            off = self.badge(title, "UIT", C["faint"])
            off.pack(side="left", padx=(self.s(10), 0))
            hover.append(off)
        if show_category:
            b = self.badge(title, group_of(it.category).upper(), C["faint"])
            b.pack(side="left", padx=(self.s(10), 0))
            hover.append(b)
        if it.description:
            desc = tk.Label(text_col, text=it.description, font=self.f_small, bg=C["surface"], fg=C["muted"],
                            anchor="w", justify="left")
            desc.pack(anchor="w", fill="x", pady=(self.s(2), 0))
            self.wrap_to(desc, text_col, key="row", guess=text_w)
            hover.append(desc)
        self.hoverable(hover, lambda: self.toggle(it))
        if is_open:
            self.make_detail(row, it)

    def make_detail(self, row, it):
        detail = tk.Frame(row, bg=C["surface"])
        detail.pack(fill="x", padx=self.s(12), pady=(0, self.s(10)))
        tk.Frame(detail, bg=C["border"], height=1).pack(fill="x", pady=(0, self.s(8)))
        self.section(detail, "Wat het doet", it.uitleg or it.full or "Geen beschrijving gevonden in het bestand.")
        if it.wanneer:
            self.section(detail, "Wanneer gebruiken", it.wanneer)
        if it.voorbeeld:
            self.section(detail, "Voorbeeld", it.voorbeeld, mono=True)
        actions = tk.Frame(detail, bg=C["surface"])
        if it.voorbeeld:
            vb = Pill(actions, self, "Kopieer voorbeeld", icon="copy", small=True, bg=C["surface"])
            vb.command = lambda: self.copy_text(it.voorbeeld, vb)
            vb.pack(side="left", padx=(0, self.s(6)))
        if it.source.endswith("SKILL.md"):
            pb = Pill(actions, self, "Kopieer als prompt", icon="doc", small=True, bg=C["surface"])
            pb.command = lambda: self.copy_local_prompt(it, pb)
            pb.pack(side="left", padx=(0, self.s(6)))
            Pill(actions, self, "Deel op marktplaats", icon="share", small=True, bg=C["surface"],
                 command=lambda: self.share_skill(it)).pack(side="left", padx=(0, self.s(6)))
        if actions.winfo_children():
            actions.pack(anchor="w", pady=(0, self.s(6)))
        if it.source and not it.source.endswith(".json"):
            tk.Label(detail, text=it.source, font=self.f_tiny, bg=C["surface"], fg=C["faint"],
                     anchor="w", justify="left").pack(anchor="w")

    def toggle(self, it):
        if it.key in self.expanded:
            self.expanded.discard(it.key)
        else:
            self.expanded.add(it.key)
        self.rebuild()

    # -- data verversen -------------------------------------------------------- #
    def refresh(self, force=False):
        fp = fingerprint()
        if force or fp != self.fp:
            self.fp = fp
            self.items = apply_market_summaries(scan_all(), self.market_skills)
            self.rebuild()
            if self.market_skills:
                self.rebuild_market()  # geïnstalleerd-labels kloppen weer als er iets veranderde
            if self.view == "local":
                self.set_status(f"{len(self.visible_items())} commands  ·  bijgewerkt {time.strftime('%H:%M:%S')}")

    def poll(self):
        try:
            self.refresh()
        finally:
            self.root.after(POLL_MS, self.poll)

    # -- tab Marktplaats ------------------------------------------------------- #
    def build_market_view(self):
        v = tk.Frame(self.content, bg=C["bg"])
        self.m_search_var = tk.StringVar(value=self.m_search_text)
        self.m_entry = self.search_box(v, self.m_search_var,
                                       "Zoek of beschrijf wat je wilt, bijv. skill maken of excel formule…",
                                       self.on_market_search)

        bar = tk.Frame(v, bg=C["bg"])
        bar.pack(fill="x", padx=self.s(14), pady=(0, self.s(6)))
        self.m_cat_btn = Pill(bar, self, "Alle categorieën", kind="chip", small=True, icon="filter")
        self.m_cat_btn.command = lambda: self.open_menu(self.m_cat_btn, self.category_menu_items())
        self.m_cat_btn.pack(side="left", padx=(0, self.s(6)))
        self.m_sort_btn = Pill(bar, self, "Sorteren", kind="chip", small=True)
        self.m_sort_btn.command = lambda: self.open_menu(self.m_sort_btn, [
            (label, key == self.m_sort, lambda k=key: self.set_market_sort(k)) for key, label in SORTS.items()])
        self.m_sort_btn.pack(side="left")
        Pill(bar, self, "", icon="refresh", kind="ghost", small=True, command=self.reload_market).pack(side="right")

        self.m_toggle_bar = tk.Frame(v, bg=C["bg"], height=1)
        self.m_toggle_bar.pack(fill="x", padx=self.s(14), pady=(0, self.s(6)))

        task = tk.Frame(v, bg=C["bg"])
        task.pack(fill="x", padx=self.s(14), pady=(0, self.s(6)))
        tk.Label(task, text="Je taak bij de prompt", bg=C["bg"], fg=C["muted"], font=self.f_small).pack(
            side="left", padx=(0, self.s(8)))
        self.m_task_var = tk.StringVar(value=self.m_task_text)
        self.m_task_var.trace_add("write", lambda *_: setattr(self, "m_task_text", self.m_task_var.get()))
        frame, _ = self.field_entry(task, self.m_task_var)
        frame.pack(side="left", fill="x", expand=True)

        self.m_info = tk.Label(v, text="", bg=C["bg"], fg=C["faint"], font=self.f_tiny, anchor="w")
        self.m_info.pack(fill="x", padx=self.s(16), pady=(0, self.s(2)))
        self.m_canvas, self.m_list = self.make_scroll(v)
        return v

    def on_market_search(self):
        self.m_search_text = self.m_search_var.get()
        self.rebuild_market()

    def open_menu(self, pill, entries):
        menu = tk.Menu(self.root, tearoff=0, bg=C["surface"], fg=C["text"], activebackground=C["accent"],
                       activeforeground=C["on_accent"], font=self.f_small, bd=0, relief="flat")
        for entry in entries:
            if entry is None:
                menu.add_separator()
                continue
            label, selected, command = entry
            menu.add_command(label=("✓  " if selected else "     ") + label, command=command)
        try:
            menu.tk_popup(pill.winfo_rootx(), pill.winfo_rooty() + pill.winfo_height() + self.s(2))
        finally:
            menu.grab_release()

    def category_menu_items(self):
        counts = {}
        for s in self.market_skills:
            counts[s["category"]] = counts.get(s["category"], 0) + 1
        items = [(f"Alle categorieën  ({len(self.market_skills)})", self.m_category == "all",
                  lambda: self.set_market_category("all"))]
        for key, label in sorted(CATEGORY_NL.items(), key=lambda kv: kv[1]):
            if counts.get(key):
                items.append((f"{label}  ({counts[key]})", self.m_category == key,
                              lambda k=key: self.set_market_category(k)))
        return items

    def set_market_category(self, key):
        self.m_category = key
        self.rebuild_market()

    def set_market_sort(self, key):
        self.m_sort = key
        self.rebuild_market()

    def toggle_market_flag(self, flag):
        setattr(self, flag, not getattr(self, flag))
        self.rebuild_market()

    def clear_market_filters(self):
        self.m_category = "all"
        self.m_only_installed = self.m_only_updates = self.m_hide_notes = False
        self.m_search_var.set("")
        self.rebuild_market()

    def build_market_toolbar(self):
        cat = "Alle categorieën" if self.m_category == "all" else CATEGORY_NL[self.m_category]
        self.m_cat_btn.set(text=f"{cat}  ▾", selected=self.m_category != "all")
        self.m_sort_btn.set(text=f"Sorteren: {SORTS[self.m_sort]}  ▾")
        for w in self.m_toggle_bar.winfo_children():
            w.destroy()
        if not self.market_skills:
            self.m_toggle_bar.configure(height=1)
            return
        installed = sum(1 for s in self.market_skills if self.market_status(s) != "new")
        updates = sum(1 for s in self.market_skills if self.market_status(s) == "update")
        widgets = [
            Pill(self.m_toggle_bar, self, f"Geïnstalleerd  {installed}", kind="chip", small=True,
                 selected=self.m_only_installed, command=lambda: self.toggle_market_flag("m_only_installed")),
            Pill(self.m_toggle_bar, self, f"Updates  {updates}", kind="chip", small=True,
                 selected=self.m_only_updates, command=lambda: self.toggle_market_flag("m_only_updates")),
            Pill(self.m_toggle_bar, self, "Zonder notities", kind="chip", small=True,
                 selected=self.m_hide_notes, command=lambda: self.toggle_market_flag("m_hide_notes")),
        ]
        if (self.m_category != "all" or self.m_only_installed or self.m_only_updates or self.m_hide_notes
                or self.m_search_text):
            widgets.append(Pill(self.m_toggle_bar, self, "Wis filters", icon="close", kind="ghost", small=True,
                                command=self.clear_market_filters))
        self.flow(self.m_toggle_bar, widgets)

    def reload_market(self):
        self.market_cfg = load_registry_config()
        self.load_market()

    def load_market(self):
        if self.market_loading:
            return
        self.market_loaded = True
        self.source = market_source(self.market_cfg)
        if not self.source:
            self.market_note = ("Geen marktplaats gevonden. Vul het webadres in bij Instellingen → Marktplaats, "
                                "of installeer Prompt opnieuw voor de ingebouwde catalogus.")
            self.rebuild_market()
            return
        source = self.source
        if not self.market_skills and isinstance(source, HttpSource):
            try:
                cached = json.loads(read_text(MARKET_CACHE) or "{}")
                if cached.get("key") == source.key:
                    self.market_skills = clean_index(cached)
                    self.market_note = f"opgeslagen lijst van {cached.get('saved', '?')}"
            except (ValueError, AttributeError):
                pass
        self.market_loading = True
        self.update_market_info("Marktplaats laden…")
        self.rebuild_market()

        def done(skills):
            self.market_loading = False
            self.market_skills = skills
            self.m_fields = {}
            self.market_texts = {}
            label = "ingebouwde catalogus" if isinstance(source, LocalSource) else "online"
            self.market_note = f"{label}  ·  bijgewerkt {time.strftime('%H:%M')}"
            if isinstance(source, HttpSource):
                save_json(MARKET_CACHE, {"key": source.key, "saved": time.strftime("%d-%m-%Y %H:%M"), "skills": skills})
            before = [it.description for it in self.items]
            self.items = apply_market_summaries(self.items, skills)
            if [it.description for it in self.items] != before:
                self.rebuild()
            self.rebuild_market()

        def fail(err):
            self.market_loading = False
            fallback = bundled_source() if isinstance(source, HttpSource) and not self.market_skills else None
            if fallback:
                try:
                    skills = fallback.index()
                except (OSError, ValueError):
                    skills = []
                if skills:
                    self.source = fallback
                    self.market_skills = skills
                    self.m_fields = {}
                    self.market_note = "online niet bereikbaar  ·  ingebouwde catalogus"
                    self.rebuild_market()
                    return
            self.market_note = (f"Kon de marktplaats niet bereiken ({err}). "
                                + ("Je ziet de opgeslagen lijst." if self.market_skills else "Controleer je internet."))
            self.rebuild_market()

        self.run_bg(source.index, done, fail)

    def update_market_info(self, text=None):
        if text is None:
            n = len(self.market_skills)
            text = f"{n} skills" + (f"  ·  {self.market_note}" if self.market_note else "")
            if not n and self.market_note:
                text = self.market_note
        try:
            self.m_info.configure(text=text)
        except (tk.TclError, AttributeError):
            pass
        if self.view == "market":
            self.set_status(f"Installeert in {SKILLS_DIR}")

    def market_status(self, s):
        """'new' | 'installed' | 'update' | 'local' (eigen skill met dezelfde naam)"""
        name = s["name"]
        if not is_installed(name):
            return "new"
        known = self.market_state.get(name)
        if not known:
            return "local"
        return "update" if known.get("version") != s["version"] else "installed"

    def fields_for(self, s):
        f = self.m_fields.get(s["name"])
        if f is None:
            f = self.m_fields[s["name"]] = skill_fields(s)
        return f

    def market_filtered(self):
        terms = query_terms(self.m_search_text)
        results = []
        for s in self.market_skills:
            state = self.market_status(s)
            if self.m_category != "all" and s["category"] != self.m_category:
                continue
            if self.m_only_installed and state == "new":
                continue
            if self.m_only_updates and state != "update":
                continue
            if self.m_hide_notes and s["hits"]:
                continue
            score = score_fields(terms, self.fields_for(s)) if terms else 1.0
            if score > 0:
                results.append((score, s))
        results = rank(results, terms)
        order = list(CATEGORY_NL)
        if self.m_sort == "relevance" and terms:
            results.sort(key=lambda r: (-r[0], r[1]["name"]))
        elif self.m_sort == "newest":
            results.sort(key=lambda r: (r[1]["updated"], r[1]["name"]), reverse=True)
        elif self.m_sort == "category":
            results.sort(key=lambda r: (order.index(r[1]["category"]), r[1]["name"]))
        else:
            results.sort(key=lambda r: r[1]["name"])
        return terms, [s for _, s in results]

    def rebuild_market(self):
        if not hasattr(self, "m_list"):
            return
        self.update_nav()
        if self.view != "market":
            # Pas opbouwen als de tab te zien is: dat scheelt honderden widgets bij het starten.
            self.market_dirty = True
            return
        if self.m_list.winfo_width() <= 1:
            self.m_canvas.when_sized(self.rebuild_market)
            return
        self.market_dirty = False
        self.build_market_toolbar()
        y = self.m_canvas.yview()[0]
        for w in self.m_list.winfo_children():
            w.destroy()
        terms, items = self.market_filtered()
        if not items:
            if self.market_loading:
                self.empty_state(self.m_list, "Laden…", "De marktplaats wordt opgehaald.")
            elif self.market_skills:
                self.empty_state(self.m_list, "Niets gevonden",
                                 "Probeer andere woorden of wis de filters. Mis je een skill? Maak hem zelf met "
                                 "/skill-builder en deel hem.", ("Wis filters", self.clear_market_filters))
            else:
                self.empty_state(self.m_list, "Nog geen skills", self.market_note or "De marktplaats is leeg.",
                                 ("Naar instellingen", lambda: self.show_view("settings")))
        for s in items:
            self.make_market_row(s)
        self.restore_scroll(self.m_canvas, 0 if terms else y)
        self.update_market_info()

    def make_market_row(self, s):
        name = s["name"]
        state = self.market_status(s)
        is_open = name in self.market_expanded
        row = self.card(self.m_list)
        head = tk.Frame(row, bg=C["surface"])
        head.pack(fill="x", padx=self.s(12), pady=self.s(10))

        buttons = tk.Frame(head, bg=C["surface"])
        buttons.pack(side="right", padx=(self.s(8), 0), anchor="n")
        hover_extra = []
        if state in ("installed", "update"):
            # Geïnstalleerd: aan/uit-schakelaar hier; verwijderen staat in de details.
            on = skill_state(name) == "on"
            sw = Switch(buttons, self, on, lambda v: self.toggle_market_skill(name, v), bg=C["surface"])
            sw.pack(side="right")
            hover_extra.append(sw)
        if state != "installed":
            label, icon = {"new": ("Installeer", "download"), "update": ("Bijwerken", "update"),
                           "local": ("Vervang", "download")}[state]
            act = Pill(buttons, self, label, icon=icon, kind="primary", small=True, bg=C["surface"])
            act.command = lambda: self.market_action(s)
            act.pack(side="right", padx=(0, self.s(8) if hover_extra else 0))
            hover_extra.append(act)
        cp = Pill(buttons, self, "Prompt", icon="copy", kind="secondary", small=True, bg=C["surface"])
        cp.command = lambda: self.market_copy_prompt(s, cp)
        cp.pack(side="right", padx=(0, self.s(8)))

        text_col = tk.Frame(head, bg=C["surface"])
        text_col.pack(side="left", fill="both", expand=True)
        right = sum(w.winfo_reqwidth() + self.s(8) for w in buttons.winfo_children()) + self.s(8)
        text_w = self.m_list.winfo_width() - 2 * self.s(2) - 2 - 2 * self.s(12) - right - self.s(4)
        title = tk.Label(text_col, text="/" + name, font=self.f_cmd, bg=C["surface"], fg=C["accent_text"],
                         anchor="w")
        title.pack(anchor="w")
        summary = s["summary_nl"] or shorten(s["description"])
        desc = tk.Label(text_col, text=summary, font=self.f_small, bg=C["surface"], fg=C["muted"], anchor="w",
                        justify="left")
        desc.pack(anchor="w", fill="x", pady=(self.s(2), self.s(4)))
        self.wrap_to(desc, text_col, key="market-row", guess=text_w)
        meta = tk.Frame(text_col, bg=C["surface"])
        meta.pack(anchor="w")
        badges = [(CATEGORY_NL[s["category"]].upper(), C["faint"])]
        if state in ("installed", "update"):
            on = skill_state(name) == "on"
            badges.append(("✓ AAN" if on else "GEÏNSTALLEERD · UIT", C["ok"] if on else C["faint"]))
        if state == "update":
            badges.append(("UPDATE " + s["version"], C["accent_text"]))
        elif state == "local":
            badges.append(("EIGEN VERSIE", C["muted"]))
        if s["hits"]:
            n = len(s["hits"])
            badges.append((f"! {n} NOTITIE{'S' if n > 1 else ''}", C["warn"]))
        hover = [row, head, text_col, title, desc, meta, buttons, cp] + hover_extra
        for i, (text, color) in enumerate(badges):
            b = self.badge(meta, text, color)
            b.pack(side="left", padx=(0 if i == 0 else self.s(10), 0))
            hover.append(b)
        self.hoverable(hover, lambda: self.toggle_market(name))
        if is_open:
            self.make_market_detail(row, s)

    def make_market_detail(self, row, s):
        detail = tk.Frame(row, bg=C["surface"])
        detail.pack(fill="x", padx=self.s(12), pady=(0, self.s(10)))
        tk.Frame(detail, bg=C["border"], height=1).pack(fill="x", pady=(0, self.s(8)))
        self.section(detail, "Wat het doet en wanneer", s["description"] or "Geen beschrijving.")
        meta = f"{s['author']}  ·  versie {s['version']}"
        if s["updated"]:
            meta += f"  ·  bijgewerkt {nice_date(s['updated'])}"
        self.section(detail, "Door", meta)
        if s["tags"]:
            tk.Label(detail, text="TAGS", font=self.f_head, bg=C["surface"], fg=C["faint"]).pack(anchor="w")
            tags = tk.Frame(detail, bg=C["surface"], height=1)
            tags.pack(fill="x", pady=(self.s(4), self.s(8)))
            self.flow(tags, [Pill(tags, self, "#" + t, kind="chip", small=True, bg=C["surface"],
                                  command=lambda t=t: self.m_search_var.set(t)) for t in s["tags"]])
        if s["hits"]:
            lines = [f"• {SAFETY_NL.get(h.get('id'), h.get('id'))} (regel {h.get('line')}): "
                     f"{str(h.get('excerpt', ''))[:120]}" for h in s["hits"]]
            self.section(detail, "Veiligheid  ·  lees dit na voordat je installeert", "\n".join(lines), C["warn"])
        else:
            self.section(detail, "Veiligheid", "Geen opvallende patronen gevonden. Lees een skill toch even door.",
                         C["ok"])
        if s["hosts"]:
            self.section(detail, "Genoemde websites", ", ".join(s["hosts"]))
        actions = tk.Frame(detail, bg=C["surface"])
        actions.pack(anchor="w")
        Pill(actions, self, "Bekijk SKILL.md", icon="doc", small=True, bg=C["surface"],
             command=lambda: self.view_skill_text(s)).pack(side="left", padx=(0, self.s(6)))
        if self.market_status(s) in ("installed", "update"):
            Pill(actions, self, "Verwijder", icon="delete", small=True, bg=C["surface"],
                 command=lambda: self.market_remove(s)).pack(side="left", padx=(0, self.s(6)))
        if self.market_cfg["repo"]:
            Pill(actions, self, "Open op GitHub", icon="open", small=True, bg=C["surface"],
                 command=lambda: webbrowser.open(f"https://github.com/{self.market_cfg['repo']}/blob/"
                                                 f"{self.market_cfg['branch']}/skills/{s['name']}/SKILL.md")).pack(
                side="left")

    def toggle_market_skill(self, name, active):
        try:
            set_skill_active(name, active)
        except (OSError, ValueError) as e:
            messagebox.showerror(APP_NAME, f"Kon /{name} niet {'aanzetten' if active else 'uitzetten'}.\n\n{e}",
                                 parent=self.root)
        self.refresh(force=True)
        self.rebuild_market()
        self.toast(f"/{name} staat {'aan' if active else 'uit'}. Dit geldt vanaf een nieuwe Claude-sessie.")

    def toggle_market(self, name):
        if name in self.market_expanded:
            self.market_expanded.discard(name)
        else:
            self.market_expanded.add(name)
        self.rebuild_market()

    # -- marktplaats: acties ------------------------------------------------- #
    def with_skill_text(self, s, then):
        name = s["name"]
        if name in self.market_texts:
            then(self.market_texts[name])
            return
        source = self.source
        self.set_status(f"/{name} ophalen…")

        def done(text):
            self.market_texts[name] = text
            then(text)

        self.run_bg(lambda: source.text(name), done, lambda e: self.market_error(f"Kon /{name} niet ophalen", e))

    def market_copy_prompt(self, s, pill):
        name = s["name"]
        self.with_skill_text(s, lambda text: self.copy_text(
            build_prompt([(name, text)], self.m_task_text), pill,
            f"Prompt met /{name} gekopieerd. Plak hem in Claude Code; Claude gaat er meteen mee aan de slag."))

    def view_skill_text(self, s):
        self.with_skill_text(s, lambda text: self.show_text_window(f"/{s['name']}  ·  SKILL.md", text))

    def show_text_window(self, title, text):
        win = tk.Toplevel(self.root)
        win.title(title)
        win.configure(bg=C["bg"])
        win.geometry(f"{self.s(640)}x{self.s(720)}")
        apply_titlebar(win, self.is_dark())
        frame = tk.Frame(win, bg=C["bg"])
        frame.pack(fill="both", expand=True, padx=self.s(10), pady=self.s(10))
        txt = tk.Text(frame, wrap="word", font=self.f_mono, bg=C["surface"], fg=C["text"], relief="flat",
                      highlightthickness=1, highlightbackground=C["border"], padx=self.s(12), pady=self.s(10),
                      insertbackground=C["text"], selectbackground=C["accent"], selectforeground=C["on_accent"])
        sb = ttk.Scrollbar(frame, orient="vertical", command=txt.yview, style="Prompt.Vertical.TScrollbar")
        txt.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        txt.pack(side="left", fill="both", expand=True)
        txt.insert("1.0", text)
        txt.configure(state="disabled")
        self.set_status("")

    def market_action(self, s):
        state = self.market_status(s)
        if state == "installed":
            self.market_remove(s)
        else:
            self.market_install(s, replacing_local=(state == "local"))

    def market_install(self, s, replacing_local=False):
        name = s["name"]
        if s["hits"]:
            lines = "\n".join(f"• {SAFETY_NL.get(h.get('id'), h.get('id'))} (regel {h.get('line')})"
                              for h in s["hits"][:8])
            if not messagebox.askyesno(
                    APP_NAME, f"/{name} heeft {len(s['hits'])} veiligheidsnotitie(s):\n\n{lines}\n\n"
                              "Dit is een automatische scan, geen oordeel. Klik op de regel en dan op "
                              "'Bekijk SKILL.md' om het na te lezen.\n\nToch installeren?",
                    icon="warning", parent=self.root):
                return
        if replacing_local and not messagebox.askyesno(
                APP_NAME, f"Je hebt al een eigen skill /{name} in\n{SKILLS_DIR / name}\n\n"
                          "Die wordt vervangen door de versie uit de marktplaats. Doorgaan?",
                icon="warning", parent=self.root):
            return
        self.set_status(f"/{name} installeren…")
        source = self.source

        def done(target):
            self.market_state[name] = {"version": s["version"], "installed": time.strftime("%Y-%m-%d %H:%M")}
            save_json(MARKET_STATE, self.market_state)
            self.refresh(force=True)
            self.rebuild_market()
            msg = f"/{name} geïnstalleerd" + (". Hij staat aan vanaf een nieuwe Claude-sessie." if active
                                              else " en staat uit. Zet hem aan met de schakelaar.")
            self.set_status(msg)
            self.toast(msg)

        active = self.settings["new_skills_active"]
        self.run_bg(lambda: install_skill(source, s, active=active), done,
                    lambda e: self.market_error(f"Installeren van /{name} mislukt", e))

    def market_remove(self, s):
        name = s["name"]
        where = SKILLS_DIR if skill_state(name) == "on" else LIBRARY_DIR
        if not messagebox.askyesno(APP_NAME, f"/{name} verwijderen uit\n{where / name}?", parent=self.root):
            return
        try:
            remove_skill(name)
        except (OSError, ValueError) as e:
            self.market_error(f"Verwijderen van /{name} mislukt", e)
            return
        self.market_state.pop(name, None)
        save_json(MARKET_STATE, self.market_state)
        self.refresh(force=True)
        self.rebuild_market()
        self.set_status(f"/{name} verwijderd.")
        self.toast(f"/{name} verwijderd.")

    def market_error(self, what, err):
        self.set_status(f"{what}: {err}")
        messagebox.showerror(APP_NAME, f"{what}.\n\n{err}", parent=self.root)

    # -- eigen skills: prompt en delen -------------------------------------- #
    def copy_local_prompt(self, it, pill):
        text = read_text(it.source)
        name = it.command.lstrip("/").split(":")[-1]
        self.copy_text(build_prompt([(name, text)], self.m_task_text), pill,
                       f"Prompt met /{name} gekopieerd. Plak hem in Claude Code.")

    def share_skill(self, it):
        path = Path(it.source)
        text = read_text(path)
        meta, _ = parse_frontmatter(text)
        name = meta.get("name") or path.parent.name
        if not NAME_RE.match(name):
            messagebox.showwarning(APP_NAME, f"De naam \"{name}\" kan niet op de marktplaats: gebruik alleen kleine "
                                             "letters, cijfers en streepjes (bijvoorbeeld mijn-skill).", parent=self.root)
            return
        if not meta.get("description"):
            messagebox.showwarning(APP_NAME, "Deze skill heeft geen description in de frontmatter. Die is nodig zodat "
                                             "Claude (en anderen) weten wanneer hij gebruikt moet worden.", parent=self.root)
            return
        repo, branch = self.market_cfg["repo"], self.market_cfg["branch"]
        if not repo:
            if messagebox.askyesno(APP_NAME, "De marktplaats is nog niet gekoppeld aan een GitHub-repository.\n\n"
                                             "Wil je dat nu instellen?", parent=self.root):
                self.show_view("settings")
            return
        extra_files = [p for p in path.parent.rglob("*") if p.is_file() and p != path]
        url = None if extra_files else github_share_url(repo, branch, name, text)
        if url:
            webbrowser.open(url)
            self.set_status("GitHub is geopend met je skill ingevuld. Klik op 'Commit changes' en daarna "
                            "'Create pull request'.")
        else:
            webbrowser.open(f"https://github.com/{repo}/upload/{branch}")
            open_path(path.parent)
            messagebox.showinfo(APP_NAME, f"Deze skill is te groot of heeft meerdere bestanden.\n\nGitHub en de map "
                                          f"zijn geopend. Sleep de map \"{name}\" naar de pagina, zet er skills/ voor "
                                          "in het pad en maak een pull request.", parent=self.root)

    # -- tab Instellingen ------------------------------------------------------ #
    def build_settings_view(self):
        v = tk.Frame(self.content, bg=C["bg"])
        self.settings_canvas, inner = self.make_scroll(v)

        def group(title, subtitle=None):
            tk.Label(inner, text=title, font=self.f_h2, bg=C["bg"], fg=C["text"], anchor="w").pack(
                anchor="w", pady=(self.s(14), self.s(2)), padx=self.s(2))
            if subtitle:
                lbl = tk.Label(inner, text=subtitle, font=self.f_small, bg=C["bg"], fg=C["muted"], anchor="w",
                               justify="left")
                lbl.pack(anchor="w", fill="x", padx=self.s(2), pady=(0, self.s(4)))
                self.wrap_to(lbl, inner, self.s(10))
            return self.card(inner)

        def row(card, title, desc, make_control, last=False):
            r = tk.Frame(card, bg=C["surface"])
            r.pack(fill="x", padx=self.s(14), pady=self.s(10))
            control = make_control(r)
            control.pack(side="right", anchor="center", padx=(self.s(12), 0))
            col = tk.Frame(r, bg=C["surface"])
            col.pack(side="left", fill="x", expand=True)
            tk.Label(col, text=title, font=self.f_body_b, bg=C["surface"], fg=C["text"], anchor="w").pack(anchor="w")
            if desc:
                d = tk.Label(col, text=desc, font=self.f_small, bg=C["surface"], fg=C["muted"], anchor="w",
                             justify="left")
                d.pack(anchor="w", fill="x")
                self.wrap_to(d, col)
            if not last:
                tk.Frame(card, bg=C["border"], height=1).pack(fill="x", padx=self.s(14))

        def segmented(key, options):
            def make(parent):
                f = tk.Frame(parent, bg=C["surface"])
                for value, label in options:
                    Pill(f, self, label, kind="chip", small=True, bg=C["surface"],
                         selected=self.settings[key] == value,
                         command=lambda v=value: self.change_setting(key, v, rebuild=True)).pack(
                        side="left", padx=(self.s(4), 0))
                return f
            return make

        def switch(key, on_change=None):
            def make(parent):
                handler = on_change or (lambda val: self.change_setting(key, val))
                return Switch(parent, self, self.settings[key], handler, bg=C["surface"])
            return make

        def swatches(parent):
            f = tk.Frame(parent, bg=C["surface"])
            dark = self.is_dark()
            for name, colors in ACCENTS.items():
                size = self.s(22)
                c = tk.Canvas(f, width=size + self.s(8), height=size + self.s(8), bg=C["surface"],
                              highlightthickness=0, cursor="hand2")
                color = colors[2] if dark else colors[0]
                if self.settings["accent"] == name:
                    c.create_oval(1, 1, size + self.s(7), size + self.s(7), outline=C["text"], width=self.s(2))
                c.create_oval(self.s(4), self.s(4), size + self.s(4), size + self.s(4), fill=color, outline=color)
                c.bind("<Button-1>", lambda e, n=name: self.change_setting("accent", n, rebuild=True))
                c.pack(side="left", padx=(self.s(2), 0))
            return f

        card = group("Uiterlijk")
        row(card, "Thema", "Systeem volgt het licht of donker thema van je computer.",
            segmented("theme", [("system", "Systeem"), ("light", "Licht"), ("dark", "Donker")]))
        row(card, "Accentkleur", None, swatches)
        row(card, "Tekstgrootte", None,
            segmented("text_size", [("klein", "Klein"), ("normaal", "Normaal"), ("groot", "Groot")]), last=True)

        card = group("Opstarten")
        row(card, "Openen als Claude start",
            "Prompt start dan op de achtergrond als je je aanmeldt en komt naar voren zodra je de Claude-app of "
            "Claude Code opent. Sluiten verbergt Prompt dan; helemaal afsluiten kan onderaan bij Over.",
            switch("open_with_claude", self.change_open_with_claude))
        row(card, "Openen op tabblad", None,
            segmented("start_view", [("local", "Mijn commands"), ("market", "Marktplaats")]), last=True)

        card = group("Skills kiezen", "Skills die uit staan bewaart Prompt in " + str(LIBRARY_DIR) +
                     "; Claude laadt ze dan niet.")
        row(card, "Skills kiezen als Claude opent",
            "Prompt opent bij Mijn skills zodra Claude start (samen met Openen als Claude start).",
            switch("pick_on_claude_start"))
        row(card, "Nieuwe skills meteen aanzetten",
            "Uit: skills uit de marktplaats komen eerst uitgeschakeld binnen en zet je zelf aan.",
            switch("new_skills_active"), last=True)

        card = group("Gedrag")
        row(card, "Altijd bovenop", "Prompt blijft boven andere vensters, handig naast de terminal.",
            switch("always_on_top", self.change_always_on_top))
        row(card, "Minimaliseren na kopiëren", "Na Kopieer gaat Prompt uit beeld, zodat je meteen kunt plakken.",
            switch("minimize_after_copy"))
        row(card, "Bij opstarten op updates controleren",
            "Kijkt of er nieuwere versies zijn van skills die je via de marktplaats hebt geïnstalleerd.",
            switch("check_updates"), last=True)

        card = group("Lijst Mijn commands")
        row(card, "Plugins tonen", None,
            switch("show_plugins", lambda val: self.change_setting("show_plugins", val, rebuild=True)))
        row(card, "Ingebouwde commands tonen", None,
            switch("show_builtin", lambda val: self.change_setting("show_builtin", val, rebuild=True)), last=True)

        card = group("Marktplaats", "Laat beide velden leeg om de ingebouwde catalogus te gebruiken.")
        url_var = tk.StringVar(value=self.market_cfg["url"])
        repo_var = tk.StringVar(value=self.market_cfg["repo"])

        def entry_control(var):
            def make(parent):
                frame, _ = self.field_entry(parent, var, width=26)
                return frame
            return make

        row(card, "Webadres", "Waar data/index.json staat, bijv. https://jouw-naam.github.io/prompt/",
            entry_control(url_var))
        row(card, "GitHub-repository", "Voor Deel op marktplaats, bijv. jouw-naam/prompt", entry_control(repo_var),
            last=True)
        r = tk.Frame(card, bg=C["surface"])
        r.pack(fill="x", padx=self.s(14), pady=(0, self.s(12)))
        in_use = ("ingebouwde catalogus" if isinstance(self.source, LocalSource)
                  else "online marktplaats" if self.source else "geen")
        tk.Label(r, text=f"Nu in gebruik: {in_use}", font=self.f_small, bg=C["surface"], fg=C["muted"]).pack(
            side="left")
        Pill(r, self, "Opslaan", kind="primary", small=True, bg=C["surface"],
             command=lambda: self.save_registry(url_var.get(), repo_var.get())).pack(side="right")

        card = group("Over")
        info = tk.Frame(card, bg=C["surface"])
        info.pack(fill="x", padx=self.s(14), pady=self.s(12))
        tk.Label(info, text=f"Prompt {APP_VERSION}", font=self.f_body_b, bg=C["surface"], fg=C["text"]).pack(anchor="w")
        tk.Label(info, text=f"Skills: {SKILLS_DIR}", font=self.f_tiny, bg=C["surface"], fg=C["muted"]).pack(anchor="w")
        tk.Label(info, text=f"Programma: {APP_DIR}", font=self.f_tiny, bg=C["surface"], fg=C["muted"]).pack(anchor="w")
        buttons = tk.Frame(info, bg=C["surface"], height=1)
        buttons.pack(fill="x", pady=(self.s(10), 0))
        self.flow(buttons, [
            Pill(buttons, self, "Open skills-map", icon="folder", small=True, bg=C["surface"],
                 command=self.open_skills_dir),
            Pill(buttons, self, "Open Prompt-map", icon="folder", small=True, bg=C["surface"],
                 command=lambda: open_path(APP_DIR)),
            Pill(buttons, self, "Prompt afsluiten", icon="close", small=True, bg=C["surface"], command=self.quit_app),
        ])
        tk.Frame(inner, bg=C["bg"], height=self.s(16)).pack()
        return v

    def change_setting(self, key, value, rebuild=False):
        self.settings[key] = value
        save_json(SETTINGS_FILE, self.settings)
        if rebuild:
            self.rebuild_keep_scroll()

    def rebuild_keep_scroll(self):
        y = self.settings_canvas.yview()[0] if self.view == "settings" else None
        self.build_ui()
        if y is not None:
            self.root.after(60, lambda: self.settings_canvas.yview_moveto(y))

    def change_open_with_claude(self, value):
        if not set_autostart(value):
            messagebox.showerror(APP_NAME, "Kon Prompt niet aan het opstarten van Windows toevoegen.", parent=self.root)
            self.rebuild_keep_scroll()
            return
        self.settings["open_with_claude"] = value
        save_json(SETTINGS_FILE, self.settings)
        self.claude_running = claude_is_running()
        self.set_status("Prompt komt nu naar voren als je Claude opent." if value else "Openen met Claude staat uit.")

    def change_always_on_top(self, value):
        self.change_setting("always_on_top", value)
        self.root.attributes("-topmost", value)

    def save_registry(self, url, repo):
        data = {"url": url.strip(), "repo": repo.strip(), "branch": self.market_cfg.get("branch") or "main"}
        save_json(REGISTRY_FILE, data)
        self.market_cfg = load_registry_config()
        if url.strip() and not self.market_cfg["url"]:
            messagebox.showwarning(APP_NAME, "Dat webadres is niet geldig; het moet beginnen met https://.",
                                   parent=self.root)
        self.market_skills = []
        self.market_loaded = False
        self.source = market_source(self.market_cfg)
        self.rebuild_keep_scroll()
        self.load_market()
        self.set_status("Marktplaats opgeslagen.")

    def open_skills_dir(self):
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)
        open_path(SKILLS_DIR)

    # -- venster, achtergrond en Claude ---------------------------------------- #
    def load_state(self):
        try:
            self.scale = max(1.0, self.root.winfo_fpixels("1i") / 96.0)
        except tk.TclError:
            self.scale = 1.0
        geo = f"{self.s(560)}x{self.s(780)}"
        try:
            st = json.loads(read_text(STATE_FILE) or "{}")
            if isinstance(st.get("geometry"), str):
                geo = st["geometry"]
        except ValueError:
            pass
        self.root.geometry(geo)

    def save_state(self):
        self._save_job = None
        try:
            if self.root.state() == "normal":
                save_json(STATE_FILE, {"geometry": self.root.geometry()})
        except tk.TclError:
            pass

    def on_configure(self, event):
        if event.widget is not self.root:
            return
        if self._save_job:
            self.root.after_cancel(self._save_job)
        self._save_job = self.root.after(800, self.save_state)

    def on_close(self):
        self.save_state()
        if self.settings["open_with_claude"]:
            if not self.settings["hide_hint_shown"]:
                messagebox.showinfo(APP_NAME, "Prompt blijft op de achtergrond en komt terug zodra je Claude opent.\n\n"
                                              "Helemaal afsluiten kan via Instellingen → Over → Prompt afsluiten.",
                                    parent=self.root)
                self.settings["hide_hint_shown"] = True
                save_json(SETTINGS_FILE, self.settings)
            self.root.withdraw()
        else:
            self.quit_app()

    def quit_app(self):
        self.save_state()
        self.root.destroy()

    def bring_to_front(self):
        self.root.deiconify()
        if IS_WINDOWS:
            # Door Windows geminimaliseerd (bijv. via de taakbalk): Tk weet dat niet altijd, dus vraag Windows
            # zelf om het venster te herstellen.
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                if ctypes.windll.user32.IsIconic(hwnd):
                    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
            except Exception:  # noqa: BLE001 - herstellen is een gemak, geen voorwaarde
                pass
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.after(250, lambda: self.root.attributes("-topmost", self.settings["always_on_top"]))
        self.root.focus_force()

    def watch_claude(self):
        try:
            if self.settings["open_with_claude"]:
                running = claude_is_running()
                if running and not self.claude_running:
                    if self.settings["pick_on_claude_start"]:
                        self.local_filter = CAT_SKILLS
                        self.show_view("local")
                        self.rebuild()
                        self.set_status("Claude is geopend. Kies welke skills aan staan en begin dan een nieuwe sessie.")
                    self.bring_to_front()
                self.claude_running = running
        finally:
            self.root.after(WATCH_MS, self.watch_claude)

    def on_mousewheel(self, event):
        if IS_MAC and abs(event.delta) < 120:
            self.scroll_active(-event.delta * 6, "pixels")  # trackpad op macOS: kleine, vloeiende stappen
        else:
            self.scroll_active(int(-event.delta / 120) or (-1 if event.delta > 0 else 1))

    def scroll_active(self, step, what="units"):
        area = {"market": getattr(self, "m_canvas", None), "local": getattr(self, "canvas", None),
                "settings": getattr(self, "settings_canvas", None)}.get(self.view)
        try:
            if step and area and area.can_scroll():
                area.yview_scroll(step, what)
        except tk.TclError:
            pass

    def request_show(self):
        """Wordt vanuit de server-thread aangeroepen; raakt tkinter niet aan (niet thread-safe)."""
        self._show_requested = True

    def check_show_request(self):
        if self._show_requested:
            self._show_requested = False
            trace(f"SHOW ontvangen; state={self.root.state()}")
            self.bring_to_front()
            trace(f"na bring_to_front; state={self.root.state()}")
        self.root.after(300, self.check_show_request)


def enable_dpi_awareness():
    """Scherpe tekst op schermen met schaling (Windows)."""
    try:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except (AttributeError, OSError):
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:  # noqa: BLE001
        pass


def spawn_detached(watch=False):
    """Start een losgekoppelde kopie van dit programma en keer direct terug."""
    if FROZEN or HOSTED:
        cmd = [sys.executable] + (["-X", "watch"] if watch else [])
    else:
        exe = Path(sys.executable)
        pythonw = exe.with_name("pythonw.exe")
        cmd = [str(pythonw if pythonw.exists() else exe), str(Path(__file__).resolve())] + (["--watch"] if watch else [])
    if IS_WINDOWS:
        extra = {"creationflags": 0x00000008 | 0x00000200}  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        extra = {"start_new_session": True}
    subprocess.Popen(cmd, close_fds=True, stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                     stderr=subprocess.DEVNULL, cwd=str(APP_DIR), **extra)


def trace(msg):
    """Alleen met omgevingsvariabele PROMPT_DEBUG=1: schrijf stappen naar debug.log (voor foutopsporing)."""
    if os.environ.get("PROMPT_DEBUG") == "1":
        try:
            with open(APP_DIR / "debug.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%H:%M:%S')} pid={os.getpid()} {msg}\n")
        except OSError:
            pass


def main():
    args = sys.argv[1:]
    watch = "--watch" in args
    if os.environ.get("PROMPT_DEBUG") == "1":
        # Loopt Prompt vast, dan staat na 20 seconden in debug-trace.log waar elke thread op dat moment was.
        import faulthandler
        try:
            faulthandler.dump_traceback_later(20, file=open(APP_DIR / "debug-trace.log", "w", encoding="utf-8"))
        except OSError:
            pass
    trace(f"main start exe={sys.executable} argv={sys.argv} hosted={HOSTED} app_dir={APP_DIR}")
    if "--detach" in args:
        # Snelkoppeling of opstarten: starten, of het bestaande venster naar voren halen; keert direct terug.
        # Bij het opstarten van Windows (--watch) laten we een draaiend venster met rust.
        if not try_signal_existing(signal=not watch):
            spawn_detached(watch)
        return 0
    if try_signal_existing(signal=not watch):
        trace("andere instantie draait al; stoppen")
        return 0
    try:
        srv = claim_port()  # vóór het opbouwen van het venster, zodat een tweede start dit meteen ziet
    except OSError as e:
        trace(f"poort bezet ({e}); andere instantie naar voren halen")
        try_signal_existing(signal=not watch)
        return 0
    enable_dpi_awareness()
    root = tk.Tk()
    start_view = next((v for v in ("market", "settings") if f"--{v}" in args), None)
    app = App(root, start_view=start_view, hidden=watch)
    app._server = start_server(app.request_show, srv)
    root.after(2000, lambda: trace(
        f"venster: tk={tk.TkVersion} state={root.state()} mapped={root.winfo_ismapped()} "
        f"viewable={root.winfo_viewable()} geometry={root.geometry()} "
        f"scherm={root.winfo_screenwidth()}x{root.winfo_screenheight()} items={len(app.items)}"))
    root.mainloop()
    return 0


def install_error_log():
    """Onder pythonw is stderr None; schrijf fouten dan naar error.log naast de app."""
    if sys.stderr is None or sys.stdout is None:
        try:
            log = open(APP_DIR / "error.log", "a", encoding="utf-8", buffering=1)
            if sys.stderr is None:
                sys.stderr = log
            if sys.stdout is None:
                sys.stdout = log
        except OSError:
            pass


if __name__ == "__main__":
    install_error_log()
    try:
        code = main()
    except Exception:
        import traceback
        traceback.print_exc()
        code = 1
    sys.exit(code)
