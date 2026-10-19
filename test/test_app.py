"""Tests voor de logica van app/prompt.pyw (zonder venster).

    python -m unittest discover -s test -p "test_*.py"
"""
import http.server
import importlib.machinery
import importlib.util
import json
import tempfile
import threading
import unittest
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
loader = importlib.machinery.SourceFileLoader("prompt_app", str(ROOT / "app" / "prompt.pyw"))
spec = importlib.util.spec_from_loader("prompt_app", loader)
app = importlib.util.module_from_spec(spec)
loader.exec_module(app)

# Zandbak: alle standaardmappen van de app wijzen naar een tijdelijke map, zodat geen enkele test (ook niet
# per ongeluk, via een vergeten parameter) je echte ~/.claude kan raken.
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

SKILL_MD = "---\nname: demo\ndescription: Demo skill. Use when testing.\n---\n\n# Demo\nDo things.\n"
FILES = {"skills/demo/SKILL.md": SKILL_MD, "skills/demo/scripts/run.py": "print('hi')\n"}


class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        body = FILES.get(urllib.parse.unquote(self.path.lstrip("/")))
        if body is None:
            self.send_response(404)
            self.end_headers()
            return
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body.encode("utf-8"))

    def log_message(self, *args):
        pass


class MarketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=cls.server.serve_forever, daemon=True).start()
        cls.source = app.HttpSource(f"http://127.0.0.1:{cls.server.server_port}/")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.skills = Path(self.tmp.name) / ".claude" / "skills"

    def tearDown(self):
        self.tmp.cleanup()

    def test_clean_index_drops_unsafe_entries(self):
        data = {"skills": [
            {"name": "good", "files": ["SKILL.md", "a/b.py", "../evil.md", "x;rm.md"], "category": "design",
             "summary_nl": "Goed."},
            {"name": "../evil", "files": ["SKILL.md"]},
            {"name": "nofile", "files": ["README.md"]},
            "nonsense",
        ]}
        skills = app.clean_index(data)
        self.assertEqual([s["name"] for s in skills], ["good"])
        self.assertEqual(skills[0]["files"], ["SKILL.md", "a/b.py"])
        self.assertEqual(skills[0]["summary_nl"], "Goed.")
        self.assertEqual(app.clean_index({"skills": [{"name": "x", "files": ["SKILL.md"], "category": "bogus"}]})[0]["category"], "other")
        self.assertEqual(app.clean_index(None), [])

    def test_install_and_remove(self):
        skill = {"name": "demo", "files": ["SKILL.md", "scripts/run.py"]}
        target = app.install_skill(self.source, skill, self.skills)
        self.assertEqual((target / "SKILL.md").read_text(encoding="utf-8"), SKILL_MD)
        self.assertTrue((target / "scripts" / "run.py").is_file())
        self.assertTrue(app.is_installed("demo", self.skills))
        self.assertFalse((self.skills.parent / ".prompt-installing").exists())
        (target / "stale.txt").write_text("old")
        app.install_skill(self.source, skill, self.skills)
        self.assertFalse((target / "stale.txt").exists())
        app.remove_skill("demo", self.skills)
        self.assertFalse(target.exists())

    def test_failed_download_leaves_existing_skill_alone(self):
        (self.skills / "demo").mkdir(parents=True)
        (self.skills / "demo" / "SKILL.md").write_text("mine")
        with self.assertRaises(Exception):
            app.install_skill(self.source, {"name": "demo", "files": ["SKILL.md", "missing.md"]}, self.skills)
        self.assertEqual((self.skills / "demo" / "SKILL.md").read_text(), "mine")

    def test_rejects_bad_names(self):
        # Installeren uit de marktplaats volgt de strenge naamregels.
        for bad in ("../x", "A", "a b", "a--b", ""):
            with self.assertRaises(ValueError):
                app.install_skill(self.source, {"name": bad, "files": ["SKILL.md"]}, self.skills)
        # Verwijderen mag elke gewone mapnaam (eigen skills), maar nooit een padtruc.
        for bad in ("../x", "", "a/b", ".."):
            with self.assertRaises(ValueError):
                app.remove_skill(bad, self.skills)

    def test_local_catalog_installs_and_blocks_traversal(self):
        local = app.LocalSource(ROOT / "app" / "catalog-index.json", ROOT / "skills")
        skills = local.index()
        self.assertGreaterEqual(len(skills), 55)
        builder = next(s for s in skills if s["name"] == "skill-builder")
        target = app.install_skill(local, builder, self.skills)
        self.assertIn("name: skill-builder", (target / "SKILL.md").read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            local.text("skill-builder", "../design-first/SKILL.md")
        with self.assertRaises(ValueError):
            local.text("..", "SKILL.md")

    def test_build_prompt(self):
        one = app.build_prompt([("demo", SKILL_MD)], "  maak het mooi ")
        self.assertIn('<skill name="demo">\n---\nname: demo', one)
        self.assertTrue(one.rstrip().endswith("Mijn taak: maak het mooi"))
        two = app.build_prompt([("a", "x"), ("b", "y")])
        self.assertIn("de 2 skills", two)
        self.assertNotIn("Mijn taak", two)

    def test_github_share_url(self):
        url = app.github_share_url("me/prompt", "main", "demo", SKILL_MD)
        parsed = urllib.parse.urlparse(url)
        q = urllib.parse.parse_qs(parsed.query)
        self.assertEqual(parsed.path, "/me/prompt/new/main")
        self.assertEqual(q["filename"], ["skills/demo/SKILL.md"])
        self.assertEqual(q["value"], [SKILL_MD])
        self.assertIsNone(app.github_share_url("me/prompt", "main", "demo", "x" * 9000))

    def test_registry_config_placeholders_are_ignored(self):
        old = app.REGISTRY_FILE
        try:
            app.REGISTRY_FILE = Path(self.tmp.name) / "registry.json"
            app.REGISTRY_FILE.write_text(json.dumps({"url": "https://OWNER.github.io/prompt/", "repo": "OWNER/prompt"}))
            cfg = app.load_registry_config()
            self.assertEqual((cfg["url"], cfg["repo"]), ("", ""))
            app.REGISTRY_FILE.write_text(json.dumps({"url": "https://me.github.io/prompt", "repo": "me/prompt"}))
            cfg = app.load_registry_config()
            self.assertEqual((cfg["url"], cfg["repo"]), ("https://me.github.io/prompt/", "me/prompt"))
            app.REGISTRY_FILE.write_text(json.dumps({"url": "file:///C:/x"}))
            self.assertEqual(app.load_registry_config()["url"], "")
        finally:
            app.REGISTRY_FILE = old

    def test_frontmatter_of_all_skills(self):
        for f in (ROOT / "skills").glob("*/SKILL.md"):
            meta, _ = app.parse_frontmatter(f.read_text(encoding="utf-8"))
            self.assertEqual(meta.get("name"), f.parent.name)
            self.assertTrue(meta.get("description"))
        meta, _ = app.parse_frontmatter("---\nname: a\ndescription: 'what''s up'\n---\n")
        self.assertEqual(meta["description"], "what's up")


class ToggleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name) / ".claude"
        self.on, self.off = base / "skills", base / "skills-uit"
        (self.on / "demo").mkdir(parents=True)
        (self.on / "demo" / "SKILL.md").write_text(SKILL_MD, encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_toggle_moves_between_folders(self):
        self.assertEqual(app.skill_state("demo", self.on, self.off), "on")
        app.set_skill_active("demo", False, self.on, self.off)
        self.assertFalse((self.on / "demo").exists())
        self.assertEqual(app.skill_state("demo", self.on, self.off), "off")
        self.assertTrue(app.is_installed("demo", self.on, self.off))
        app.set_skill_active("demo", False, self.on, self.off)  # al uit: geen fout
        app.set_skill_active("demo", True, self.on, self.off)
        self.assertEqual((self.on / "demo" / "SKILL.md").read_text(encoding="utf-8"), SKILL_MD)

    def test_toggle_never_overwrites(self):
        (self.off / "demo").mkdir(parents=True)
        (self.off / "demo" / "SKILL.md").write_text("other", encoding="utf-8")
        with self.assertRaises(FileExistsError):
            app.set_skill_active("demo", False, self.on, self.off)
        self.assertEqual((self.on / "demo" / "SKILL.md").read_text(encoding="utf-8"), SKILL_MD)
        with self.assertRaises(ValueError):
            app.set_skill_active("../demo", False, self.on, self.off)
        with self.assertRaises(FileNotFoundError):
            app.set_skill_active("missing", True, self.on, self.off)

    def test_scan_marks_inactive_skills(self):
        app.set_skill_active("demo", False, self.on, self.off)
        items = app.scan_skills(self.off, app.CAT_SKILLS, active=False)
        self.assertEqual([(i.command, i.active, i.toggleable) for i in items], [("/demo", False, True)])

    def test_install_inactive_and_remove_everywhere(self):
        local = app.LocalSource(ROOT / "app" / "catalog-index.json", ROOT / "skills")
        builder = next(s for s in local.index() if s["name"] == "skill-builder")
        app.install_skill(local, builder, self.on, self.off, active=False)
        self.assertEqual(app.skill_state("skill-builder", self.on, self.off), "off")
        app.install_skill(local, builder, self.on, self.off, active=True)  # opnieuw: oude kopie verdwijnt
        self.assertEqual(app.skill_state("skill-builder", self.on, self.off), "on")
        self.assertFalse((self.off / "skill-builder").exists())
        app.set_skill_active("demo", False, self.on, self.off)
        app.remove_skill("demo", self.on, self.off)
        app.remove_skill("skill-builder", self.on, self.off)
        self.assertIsNone(app.skill_state("demo", self.on, self.off))
        self.assertIsNone(app.skill_state("skill-builder", self.on, self.off))


class SearchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.skills = app.LocalSource(ROOT / "app" / "catalog-index.json", ROOT / "skills").index()

    def top(self, query, n=3):
        terms = app.query_terms(query)
        results = [(app.score_fields(terms, app.skill_fields(s)), s["name"]) for s in self.skills]
        results = app.rank([r for r in results if r[0] > 0], terms)
        return [name for _, name in sorted(results, key=lambda r: (-r[0], r[1]))[:n]]

    def test_natural_dutch_queries_find_the_right_skill(self):
        cases = {
            "skill maken": "skill-builder",
            "ik wil een nieuwe skill maken": "skill-builder",
            "excel formule": "excel-formula-helper",
            "vertaal naar het engels": "translator-nl-en",
            "mijn code nakijken": "code-review-buddy",
            "waarom werkt dit niet": "debug-detective",
            "website mooier maken": ("ui-polish", "design-first", "landing-page-builder"),
            "sollicitatiebrief": "cv-and-cover-letter",
            "commit bericht schrijven": "commit-message-writer",
            "spelling controleren": "proofreader",
            "downloads opruimen": "file-organizer",
        }
        for query, expected in cases.items():
            accepted = expected if isinstance(expected, tuple) else (expected,)
            with self.subTest(query=query):
                found = self.top(query)
                self.assertTrue(set(accepted) & set(found), f"{query!r} -> {found}")

    def test_typo_and_partial_words(self):
        self.assertIn("refactor-safely", self.top("refactr"))
        self.assertIn("regex-helper", self.top("rege"))

    def test_generic_word_alone_does_not_match_everything(self):
        self.assertIn("skill-builder", self.top("skill", n=5))
        self.assertLess(len(self.top("skill", n=99)), 20)

    def test_nonsense_finds_nothing(self):
        self.assertEqual(self.top("qqqzzz"), [])

    def test_edit_distance(self):
        self.assertTrue(app.within_one_edit("refactr", "refactor"))
        self.assertTrue(app.within_one_edit("formule", "formula"))
        self.assertFalse(app.within_one_edit("abc", "xyz"))


class SettingsTests(unittest.TestCase):
    def test_defaults_and_bad_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "settings.json"
            self.assertEqual(app.load_settings(p), app.DEFAULT_SETTINGS)
            p.write_text(json.dumps({"theme": "dark", "accent": "neon", "open_with_claude": "yes",
                                     "always_on_top": True, "unknown": 1}))
            s = app.load_settings(p)
            self.assertEqual(s["theme"], "dark")
            self.assertEqual(s["accent"], "terracotta")
            self.assertFalse(s["open_with_claude"])
            self.assertTrue(s["always_on_top"])
            self.assertNotIn("unknown", s)

    def test_palette_contrast(self):
        for dark in (False, True):
            for accent in app.ACCENTS:
                app.set_palette(dark, accent)
                self.assertIn(app.C["on_accent"], ("#ffffff", "#1d1c1a"))

    def test_autostart_command_starts_in_watch_mode(self):
        cmd = app.autostart_command()
        self.assertIn("watch", cmd)
        self.assertTrue(cmd.startswith('"'))


if __name__ == "__main__":
    unittest.main()
