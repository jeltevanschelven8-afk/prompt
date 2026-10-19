# Installation guide

*Nederlandse uitleg staat onderaan.*

All downloads are on the **[Releases page](https://github.com/jeltevanschelven8-afk/prompt/releases/latest)**.

- [Windows 10 / 11](#windows-10--11)
- [macOS](#macos)
- [Linux](#linux)
- [First use](#first-use)
- [Updating and removing](#updating-and-removing)
- [Problems?](#problems)

Prompt needs **Python 3.9 or newer with Tk**. The installer looks for it and tells you exactly what to install if it is missing.

## Windows 10 / 11

1. Install Python from **[python.org](https://www.python.org/downloads/)** if you don't have it. Leave **"tcl/tk and IDLE"** ticked (it is by default).
2. Download `Prompt-…-windows.zip`.
3. Right-click the ZIP › **Properties**. If there is an **Unblock** checkbox at the bottom, tick it and click **OK**.
4. Right-click the ZIP › **Extract All…**
5. Open the extracted `Prompt` folder and double-click **`Install Prompt.cmd`**.
6. Start **Prompt** from the Start menu or the desktop shortcut.

**"Windows protected your PC"?** The installer is not signed with a paid certificate. Click **More info** › **Run anyway**.

## macOS

1. Install Python from **[python.org](https://www.python.org/downloads/macos/)** (recommended, it includes Tk). With Homebrew instead: `brew install python python-tk`.
   *Apple's built-in `/usr/bin/python3` has an old Tk that draws badly; the installer skips it.*
2. Download `Prompt-…-macos.zip` and double-click it to unpack.
3. In the `Prompt` folder, **right-click** `Install Prompt.command` › **Open** › **Open**. (The first time macOS asks because the file is not from the App Store.)
   Or in Terminal:
   ```bash
   cd ~/Downloads/Prompt
   bash app/install.sh
   ```
4. Start **Prompt** from Launchpad or `~/Applications`.

## Linux

1. Install Python with Tk:
   ```bash
   sudo apt install python3 python3-tk          # Ubuntu, Debian, Linux Mint, Pop!_OS
   sudo dnf install python3 python3-tkinter     # Fedora
   sudo zypper install python3 python3-tk       # openSUSE
   sudo pacman -S python tk                     # Arch, Manjaro, EndeavourOS
   ```
2. Download and install Prompt:
   ```bash
   tar xzf Prompt-*-linux.tar.gz
   cd prompt
   ./install.sh
   ```
3. Start **Prompt** from your applications menu, or run `prompt-app`.

Nothing is installed system-wide and no `sudo` is needed for Prompt itself: it goes into `~/.local/share/prompt`, with a menu entry and the `prompt-app` command in `~/.local/bin`.

## From source (any system)

```bash
git clone https://github.com/jeltevanschelven8-afk/prompt.git
cd prompt
bash app/install.sh          # macOS / Linux
app\install.cmd              # Windows
```

## First use

- **Mijn commands** lists everything you can type after `/` in Claude. Click **Kopieer** to copy a command.
- **Choose your skills:** use the switch next to each skill (on = Claude loads it). Save a selection under **Sets**. Then click **Start Claude**. Changes apply to the next new Claude session.
- **Marktplaats:** search for what you need, click **Installeer**, or **Prompt** to copy a skill as a prompt without installing it.
- **Settings** (gear icon, top right): theme, accent colour, text size, and **Openen als Claude start** to let Prompt come forward whenever you open Claude.

## Updating and removing

- **Update:** download the new version and run the installer again. Your settings and skills are kept.
- **Remove:**
  - Windows: delete `%LOCALAPPDATA%\Programs\Prompt` and the Prompt shortcuts.
  - macOS / Linux: `bash app/uninstall.sh` from the downloaded folder.

Your skills in `~/.claude/skills` and `~/.claude/skills-uit` are never removed by uninstalling.

## Problems?

| Problem | Solution |
|---|---|
| "Python 3 with tkinter was not found" | Install Python with Tk (step 1 for your system) and run the installer again |
| macOS: "cannot be opened because it is from an unidentified developer" | Right-click the file › **Open** › **Open** |
| macOS: window looks wrong or blurry | Use Python from python.org instead of `/usr/bin/python3` |
| Linux: `prompt-app: command not found` | Add `~/.local/bin` to your PATH, or start Prompt from the applications menu |
| Linux: **Start Claude** says no terminal was found | Install a terminal such as `gnome-terminal`, `konsole` or `xterm` |
| Windows: "Windows protected your PC" | **More info** › **Run anyway** |
| Marketplace says "online niet bereikbaar" | No internet: you see the bundled catalogue, which works fine offline |

---

## Nederlands

Alle downloads staan op de **[Releases-pagina](https://github.com/jeltevanschelven8-afk/prompt/releases/latest)**. Prompt heeft **Python 3.9 of nieuwer met Tk** nodig; het installatieprogramma zoekt dat zelf en zegt wat je moet installeren als het ontbreekt.

**Windows 10 / 11**
1. Installeer Python van [python.org](https://www.python.org/downloads/) (laat "tcl/tk and IDLE" aangevinkt).
2. Download `Prompt-…-windows.zip`, rechtsklik › **Eigenschappen** › vink **Blokkering opheffen** aan (als dat er staat) › **OK**.
3. Rechtsklik › **Alles uitpakken…** en dubbelklik in de map `Prompt` op **`Install Prompt.cmd`**.
4. Start **Prompt** vanuit het Startmenu. Zegt Windows "Uw pc is beschermd"? **Meer info** › **Toch uitvoeren**.

**macOS**
1. Installeer Python van [python.org](https://www.python.org/downloads/macos/) (of `brew install python python-tk`).
2. Download `Prompt-…-macos.zip` en pak hem uit.
3. **Rechtsklik** op `Install Prompt.command` › **Open** › **Open**.
4. Start **Prompt** vanuit Launchpad of `~/Applications`.

**Linux**
1. Installeer Python met Tk: `sudo apt install python3-tk` (Ubuntu/Debian/Mint), `sudo dnf install python3-tkinter` (Fedora), `sudo pacman -S python tk` (Arch).
2. `tar xzf Prompt-*-linux.tar.gz && cd prompt && ./install.sh`
3. Start **Prompt** vanuit het menu, of typ `prompt-app`.

**Gebruik:** zet bij **Mijn commands** de skills aan die je wilt gebruiken (of kies een **Set**), klik op **Start Claude** en begin een nieuwe sessie. In de **Marktplaats** installeer je nieuwe skills of kopieer je ze als prompt.
