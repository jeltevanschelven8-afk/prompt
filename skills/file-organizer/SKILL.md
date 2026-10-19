---
name: file-organizer
description: >-
  Sort, rename and deduplicate files in a folder safely - photos, downloads, scans, documents or
  project archives. Analyses the folder first, proposes a structure and naming scheme, shows a preview
  and dry run, moves files instead of deleting them and writes an undo log so every change can be
  reversed. Use this skill whenever the user says "clean up my downloads", "organise my photos by
  date", "find duplicate files", "rename these files consistently", "my desktop is a mess", or "ruim
  mijn downloads op", "sorteer mijn foto's op datum" or "zoek dubbele bestanden".
license: "MIT"
metadata:
  author: "prompt"
  category: "automation"
  tags: "files, organize, duplicates, rename, photos, opruimen, bestanden, downloads, sorteren"
  version: "1.0.0"
  summary_nl: "Sorteert, hernoemt en ontdubbelt bestanden in een map veilig, met voorbeeld, proefdraai en een log om terug te draaien."
---

# File organizer

Messy folders are personal: one person's clutter is another's working archive. So this skill never
reorganises blindly. It looks first, proposes a plan, shows exactly what would happen, and makes every
change reversible: files are moved, not deleted, and each move is written to an undo log.

## Workflow

### 1. Analyse the folder (read-only)

Summarise what is there before suggesting anything:

```powershell
Get-ChildItem "$HOME\Downloads" -File -Recurse |
  Group-Object Extension | Sort-Object Count -Descending |
  Select-Object Count, Name, @{n='MB';e={[math]::Round(($_.Group | Measure-Object Length -Sum).Sum/1MB,1)}}
```

```bash
find ~/Downloads -type f | sed 's/.*\.//' | sort | uniq -c | sort -rn | head -20
```

Report file count, total size, top file types, date range, and obvious patterns such as
`IMG_1234.JPG`, `scan0001.pdf` or `invoice (3).pdf`. Ask which subfolders are off limits (synced
folders, app data, project repositories).

### 2. Propose a structure

Offer one or two concrete layouts that fit what was found, for example:

| Content | Destination | Naming |
|---|---|---|
| Photos and videos | `Photos/2026/2026-08/` | `2026-08-14_153012.jpg` from EXIF date |
| PDFs and office files | `Documents/<type>/` | keep name, strip ` (1)` suffixes |
| Installers (`.exe`, `.msi`, `.dmg`) | `_Review/Installers/` | unchanged |
| Archives | `_Review/Archives/` | unchanged |
| Duplicates | `_Duplicates/<date>/` | original relative path kept |

Use the photo's EXIF capture date when available and fall back to the file's modified date, saying
which one was used, because copied files often carry the copy date.

### 3. Find duplicates reliably

Group by size first (cheap), then compare a SHA-256 hash only within same-size groups. Identical
names are not duplicates and different names can be:

```powershell
Get-ChildItem $src -File -Recurse | Group-Object Length | Where-Object Count -gt 1 |
  ForEach-Object { $_.Group | Get-FileHash -Algorithm SHA256 } |
  Group-Object Hash | Where-Object Count -gt 1
```

Keep the copy with the best path or oldest date as the original and move the others to `_Duplicates`.
Treat near-duplicates (resized photos, re-saved PDFs) as a separate, optional review list.

### 4. Dry run, then apply

Write the plan as a CSV with `action, source, destination, reason` and show a summary plus the first
rows. Resolve name collisions in the plan (`report.pdf` becomes `report_2.pdf`) rather than overwriting.
Only after the user approves, execute the moves and append each completed move to `undo-log.csv` in the
target folder. A script for this follows the script-automator conventions: dry run by default and an
explicit apply flag.

### 5. Verify and offer undo

Count files before and after (they should match, since nothing is deleted), list any errors such as
locked files, and explain how to reverse it: read `undo-log.csv` bottom-up and move each file back.
Emptying `_Duplicates` is the user's own decision once they have checked it; suggest the recycle bin
over permanent deletion.

## Output format

```text
Folder: C:\Users\sam\Downloads - 2,314 files, 18.6 GB, 2019-2026

Plan (dry run)
  Move   1,102 photos/videos -> Photos\YYYY\YYYY-MM\   (renamed by capture date)
  Move     486 documents      -> Documents\<type>\
  Move      97 installers     -> _Review\Installers\
  Move     211 duplicates     -> _Duplicates\2026-10-17\  (frees 3.4 GB once you empty it)
  Leave    418 files untouched (unknown types, in use, or in excluded folders)

Collisions resolved: 23 - Errors expected: 0
Full plan: plan-2026-10-17.csv. Shall I apply it? An undo log will be written.
```

## Pitfalls and when to stop

- Do not reorganise folders managed by applications (photo libraries, OneDrive or iCloud roots, game
  saves, code repositories); moving files there can break the app or trigger mass re-syncing.
- Keep sidecar files together with their originals (`.xmp`, `.aae`, `.srt`).
- Long paths and special characters on Windows can fail; report them instead of skipping silently.
- Ask before touching more than a few thousand files at once; offer to start with one subfolder.

## Scope

Sorting, renaming and deduplicating files on a local or network drive. Ongoing automation of other
repetitive tasks belongs to script-automator; cleaning up a git repository belongs to git-helper.
