"""Smoke test of the real window on this operating system: build the UI, load the marketplace, visit every
tab, switch theme and accent, toggle a skill, then close. Skipped when there is no display.

    python -m unittest discover -s test -p "test_gui_smoke.py"
"""
import importlib.machinery
import importlib.util
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("prompt_app_gui", str(ROOT / "app" / "prompt.pyw"))
spec = importlib.util.spec_from_loader("prompt_app_gui", loader)
app = importlib.util.module_from_spec(spec)
loader.exec_module(app)

# Sandbox: never touch the real ~/.claude or the app's own settings files.
SANDBOX = Path(tempfile.mkdtemp(prefix="prompt-test-home-"))
app.HOME = SANDBOX
app.CLAUDE_DIR = SANDBOX / ".claude"
app.SKILLS_DIR = app.CLAUDE_DIR / "skills"
app.LIBRARY_DIR = app.CLAUDE_DIR / "skills-uit"
app.COMMANDS_DIR = app.CLAUDE_DIR / "commands"
app.PROJECTS_DIR = app.CLAUDE_DIR / "projects"
app.CLAUDE_JSON = SANDBOX / ".claude.json"
app.SETTINGS_FILE = SANDBOX / "settings.json"
app.MARKET_STATE = SANDBOX / "market_state.json"
app.MARKET_CACHE = SANDBOX / "market_cache.json"
app.STATE_FILE = SANDBOX / "state.json"
app.REGISTRY_FILE = SANDBOX / "registry.json"  # no online marketplace: use the bundled catalogue
app.find_claude_app = lambda: None             # don't start PowerShell/ps during the test

try:
    import tkinter as tk
    _root = tk.Tk()
    _root.destroy()
    HAS_DISPLAY = True
except Exception:  # noqa: BLE001 - no display, no Tk
    HAS_DISPLAY = False


def pump(root, seconds):
    end = time.time() + seconds
    while time.time() < end:
        root.update()
        time.sleep(0.02)


@unittest.skipUnless(HAS_DISPLAY, "no display available")
class GuiSmoke(unittest.TestCase):
    def test_full_tour(self):
        skill = app.SKILLS_DIR / "demo"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text("---\nname: demo\ndescription: Demo skill. Use when testing.\n---\n\n# Demo\n",
                                        encoding="utf-8")
        root = tk.Tk()
        try:
            ui = app.App(root)
            pump(root, 1.5)
            self.assertTrue(ui.items)
            self.assertGreaterEqual(len(ui.market_skills), 55)  # bundled catalogue loaded
            for view in ("market", "settings", "local"):
                ui.show_view(view)
                pump(root, 0.3)
            ui.search_var.set("skill maken")
            pump(root, 0.3)
            ui.m_search_var.set("excel formule")
            pump(root, 0.3)
            for theme in ("dark", "light"):
                ui.change_setting("theme", theme, rebuild=True)
                pump(root, 0.3)
            ui.change_setting("accent", "blauw", rebuild=True)
            demo = next(it for it in ui.items if it.command == "/demo")
            ui.toggle_skill(demo, False)
            self.assertEqual(app.skill_state("demo"), "off")
            ui.toggle_skill(next(it for it in ui.items if it.command == "/demo"), True)
            self.assertEqual(app.skill_state("demo"), "on")
            ui.toast("smoke test")
            pump(root, 0.3)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
