# Prompt: your Claude Code commands, skills and a skill marketplace

**Prompt** is a free, open-source desktop app for **Windows, macOS and Linux** that sits next to Claude. It lists every slash command and skill Claude Code knows, each one click to copy, lets you choose which skills Claude loads, and comes with a marketplace of 55 ready-made skills.

*Nederlandse uitleg: [LEESMIJ.md](LEESMIJ.md). The app itself is in Dutch.*

- **One-click copy** of every command: your own skills and commands, project skills, plugins and Claude Code's built-in commands, each with an explanation and an example.
- **Choose your skills before you start Claude.** Every skill has an on/off switch. Skills that are off are moved to `~/.claude/skills-uit`, so Claude does not load them; switch them on again with one click. Save a selection as a **set** ("Web development", "Writing") and switch sets in one click. **Start Claude** opens Claude with your choice.
- **Marketplace** with 55 skills in 12 categories: install, update, switch on/off, remove, or copy a skill as a prompt and paste it straight into Claude. Works offline too: the catalogue ships with the app.
- **Smart search** in plain Dutch or English with synonyms and typo tolerance: "skill maken", "excel formula", "why doesn't this work".
- **Safety check:** every skill is scanned for risky patterns (download-and-run, deleting files, credentials, "ignore previous instructions"). Prompt shows the notes and asks before installing.
- **Opens with Claude** (optional): Prompt waits in the background and comes forward with your skill list as soon as Claude starts.
- **Light and dark theme**, six accent colours, three text sizes.
- No account, no tracking, no AI inside the app. Everything stays on your computer.

## Download

Get Prompt from the **[Releases page](https://github.com/jeltevanschelven8-afk/prompt/releases/latest)**.

| Your computer | Download |
|---|---|
| Windows 10 / 11 | `Prompt-…-windows.zip` |
| macOS 12 or newer (Apple silicon and Intel) | `Prompt-…-macos.zip` |
| Linux (Ubuntu, Debian, Mint, Fedora, openSUSE, Arch, …) | `Prompt-…-linux.tar.gz` |

**Step-by-step installation and troubleshooting: [INSTALL.md](INSTALL.md)** (also in Dutch).

Prompt is a Python program. It needs **Python 3.9 or newer with Tk**, which the installer finds by itself and tells you how to get if it is missing.

## Supported operating systems

| Operating system | Versions | Notes |
|---|---|---|
| **Windows** | 10 and 11 (x64, ARM64) | Python from [python.org](https://www.python.org/downloads/) |
| **macOS** | 12 Monterey and newer (Apple silicon, Intel) | Python from [python.org](https://www.python.org/downloads/macos/) (includes Tk) or Homebrew `python-tk` |
| **Ubuntu / Debian / Linux Mint / Pop!_OS** | Ubuntu 22.04+, Debian 12+ | `sudo apt install python3-tk` |
| **Fedora** | 39 and newer | `sudo dnf install python3-tkinter` |
| **openSUSE** | Tumbleweed, Leap 15.6 | `sudo zypper install python3-tk` |
| **Arch / Manjaro / EndeavourOS** | rolling | `sudo pacman -S python tk` |

Every change is tested automatically on Windows, macOS and Linux (unit, stress and real-window tests).

## Skill marketplace

The marketplace is this repository: every skill is a folder in [`skills/`](skills) with a `SKILL.md`. GitHub builds the catalogue and the website from it:

**Website:** https://jeltevanschelven8-afk.github.io/prompt/ (browse, search, copy as prompt, or install without the app)

**Add your own skill:** in the app, open a skill under *Mijn commands* and click **Deel op marktplaats**. GitHub opens with your skill filled in; click *Commit changes* and *Create pull request*. After review it appears in everyone's marketplace. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Project structure

```
prompt/
├── app/                    The desktop app
│   ├── prompt.pyw          The whole program (Python + Tk, standard library only)
│   ├── install.ps1/.cmd    Windows installer
│   ├── install.sh          macOS and Linux installer (uninstall.sh to remove)
│   ├── synonyms.json       Search synonyms (Dutch and English)
│   └── catalog-index.json  The bundled marketplace catalogue
├── skills/                 The 55 marketplace skills (one folder each, with SKILL.md)
├── site/                   Marketplace website (plain HTML, CSS, JavaScript)
├── scripts/                build.mjs (validate skills, build catalogue and website), serve.mjs
├── test/                   Unit, stress and window tests (Python and Node)
└── .github/workflows/      CI on Windows, macOS and Linux; releases; website
```

## Technical info

- **One Python file, no dependencies.** `app/prompt.pyw` uses only the Python standard library and Tk, so it runs anywhere Python with Tk runs.
- **Windows:** `Prompt.exe` is a copy of the signed `pythonw.exe`, so Smart App Control does not block it. Start menu and desktop shortcuts; "opens with Claude" uses the Run key.
- **macOS:** installed as `~/Applications/Prompt.app`; "opens with Claude" uses a LaunchAgent.
- **Linux:** a menu entry and a `prompt-app` command in `~/.local/bin`; "opens with Claude" uses `~/.config/autostart`.
- **Skills** live where Claude Code reads them: `~/.claude/skills` (on) and `~/.claude/skills-uit` (off). Prompt only moves folders; it never deletes your own skills without asking.
- **Marketplace:** `npm run build` validates every skill (name, description, file types, size, no links), runs the safety scan and writes the catalogue. A pull request runs the same checks.
- **Tests:** `npm test` (website and build) and `npm run test:app` (app logic, stress tests and a real-window smoke test).

## Develop

```bash
npm run dev        # build the website + catalogue and serve http://localhost:4321
npm test           # website, build and safety-scan tests (Node 22+)
npm run test:app   # app tests (Python)
python app/prompt.pyw --market   # run the app from source
```

## License

MIT, see [LICENSE](LICENSE). Each skill has its own license (MIT by default). Prompt is not affiliated with Anthropic.
