---
name: scheduled-task-setup
description: >-
  Make a script or command run automatically on a schedule, with Windows Task Scheduler
  (schtasks or PowerShell ScheduledTasks), cron on Linux, or launchd on macOS. Covers picking the
  trigger, wrapping the job so it logs output, running it once by hand to test, and showing how to
  pause or remove it. Use this skill whenever the user says "run this every night", "schedule a
  backup", "cron job", "start this at login", "taak inplannen", "elke dag automatisch draaien" or
  "geplande taak maken", or asks why a scheduled job silently does nothing.
license: "MIT"
metadata:
  author: "prompt"
  category: "automation"
  tags: "schedule, cron, launchd, task scheduler, schtasks, automatisering, planning, logging"
  version: "1.0.0"
  summary_nl: "Laat een script automatisch op vaste tijden draaien via Taakplanner, cron of launchd, met logging en een test."
---

# Scheduled task setup

A scheduled job runs when nobody is watching, so the hard part is not the trigger line but making sure
the job works without your interactive shell, leaves a trace when it fails, and can be switched off
easily. This skill walks through those steps for each operating system.

## Workflow

1. **Pin down the job.** Ask what should run, how often, and on which machine. Get the exact command
   that works today in a terminal. If it does not work by hand, scheduling it will only hide the error.
2. **Detect the platform.** Windows uses Task Scheduler, Linux uses cron (or systemd timers), macOS
   uses launchd. Check rather than assume, for example `uname` or `$PSVersionTable`.
3. **Write a wrapper script.** Schedulers start with a minimal environment: a different working
   directory, a short PATH, no profile. A wrapper fixes this in one place and adds logging.
4. **Create the schedule** with the commands below. Show the command to the user before running it,
   because it changes system state that persists after the session.
5. **Test by triggering it once** instead of waiting for the real time, then read the log.
6. **Hand over the off-switch**: how to list, disable, and remove the job.

## Wrapper with logging

Windows (`C:\jobs\backup.ps1`):

```powershell
$ErrorActionPreference = 'Stop'
$log = "C:\jobs\logs\backup-$(Get-Date -Format yyyy-MM-dd).log"
Start-Transcript -Path $log -Append
try {
  Set-Location 'C:\data'
  robocopy C:\data D:\backup\data /MIR /R:2 /W:5
} finally { Stop-Transcript }
```

Linux/macOS (`~/jobs/backup.sh`, then `chmod +x`):

```bash
#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/data"
exec >>"$HOME/jobs/logs/backup.log" 2>&1
echo "== $(date -Is) start"
rsync -a "$HOME/data/" /mnt/backup/data/
echo "== $(date -Is) done"
```

Use absolute paths everywhere; relative paths are the most common reason a job works by hand but not on schedule.

## Creating the schedule

**Windows, schtasks** (daily at 02:00, runs as the current user):

```powershell
schtasks /Create /TN "Prompt\NightlyBackup" /SC DAILY /ST 02:00 /TR "powershell.exe -NoProfile -File C:\jobs\backup.ps1"
```

**Windows, PowerShell** (more options, such as running only when on AC power):

```powershell
$action  = New-ScheduledTaskAction -Execute 'powershell.exe' -Argument '-NoProfile -File C:\jobs\backup.ps1'
$trigger = New-ScheduledTaskTrigger -Daily -At 2am
Register-ScheduledTask -TaskName 'NightlyBackup' -TaskPath '\Prompt\' -Action $action -Trigger $trigger
```

Putting tasks in a `\Prompt\` folder keeps them easy to find and separate from system tasks.

**Linux, cron** (`crontab -e`):

```
# m h dom mon dow  command
0 2 * * * /home/ana/jobs/backup.sh
```

Explain the five fields when you show the line; `*/15 * * * *` means every 15 minutes, `0 9 * * 1-5` weekdays at 09:00.

**macOS, launchd** (`~/Library/LaunchAgents/com.prompt.backup.plist`):

```xml
<plist version="1.0"><dict>
  <key>Label</key><string>com.prompt.backup</string>
  <key>ProgramArguments</key><array><string>/Users/ana/jobs/backup.sh</string></array>
  <key>StartCalendarInterval</key><dict><key>Hour</key><integer>2</integer><key>Minute</key><integer>0</integer></dict>
</dict></plist>
```

Load with `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.prompt.backup.plist`.

## Test, inspect, disable

| Action | Windows | cron | launchd |
|---|---|---|---|
| Run now | `schtasks /Run /TN "Prompt\NightlyBackup"` | run the script directly | `launchctl kickstart gui/$(id -u)/com.prompt.backup` |
| Status | `schtasks /Query /TN "Prompt\NightlyBackup" /V /FO LIST` | `crontab -l`, `grep CRON /var/log/syslog` | `launchctl print gui/$(id -u)/com.prompt.backup` |
| Pause | `schtasks /Change /TN "Prompt\NightlyBackup" /DISABLE` | comment out the line | `launchctl bootout gui/$(id -u)/com.prompt.backup` |
| Remove | `schtasks /Delete /TN "Prompt\NightlyBackup"` | delete the line | bootout, then delete the plist |

After a test run, read the log and the "Last Result" field (0 means success on Windows) before calling it done.

## What the user receives

```markdown
**Job:** nightly backup of C:\data to D:\backup
**Schedule:** daily 02:00 (Task Scheduler, \Prompt\NightlyBackup)
**Script:** C:\jobs\backup.ps1  **Log:** C:\jobs\logs\backup-<date>.log
**Tested:** ran once at 14:12, Last Result 0, log shows 1,204 files copied
**Pause:** schtasks /Change /TN "Prompt\NightlyBackup" /DISABLE
**Remove:** schtasks /Delete /TN "Prompt\NightlyBackup"
```

## Pitfalls and when to ask

- The laptop is asleep at 02:00: on Windows set "run as soon as possible after a missed start"
  (`New-ScheduledTaskSettingsSet -StartWhenAvailable`); on macOS launchd catches up after wake; cron does not.
- The job needs to run while the user is logged out or with admin rights: ask first, since that
  means storing account credentials in Task Scheduler or editing the system crontab.
- Overlapping runs: if a job can take longer than its interval, add a lock (`flock` on Linux) so runs do not pile up.
- Time zones and daylight saving: say which clock the schedule uses.
- Never report a job as working until a test run and its log confirm it.

## Scope

This skill is for jobs on the user's own machine or server. For cloud schedules (GitHub Actions cron,
cloud functions) or recurring Claude agents, use the tool built for that platform instead.
