---
name: secrets-scanner
description: >-
  Find credentials that were accidentally committed to the user's own repository, in current files and
  in git history, explain the real risk, and walk through remediation in the right order - rotate or
  revoke first, then clean up the code and history, then prevent it happening again. Use this skill
  whenever the user says "I committed a secret", "is there anything sensitive in my repo", "scan for
  leaked keys", "GitHub warned me about a token", "clean my .env from git", or asks "heb ik
  wachtwoorden in mijn repo gezet", "ik heb per ongeluk een sleutel gepusht" or "controleer mijn repo
  op geheimen".
license: "MIT"
metadata:
  author: "prompt"
  category: "security"
  tags: "secrets, credentials, gitleaks, leak, git history, rotatie, beveiliging, geheimen"
  version: "1.0.0"
  summary_nl: "Vindt per ongeluk gecommitte inloggegevens in je repo en geschiedenis en legt uit hoe je ze intrekt en opruimt."
---

# Secrets scanner

A credential that reached a git remote should be treated as compromised: clones, forks, CI caches and
bots may already have it, and deleting the file does not remove it from history. That is why the order
matters - make the leaked credential useless first, clean up second. This skill finds leaks in the
user's own repository and guides that remediation.

## Workflow

### 1. Scan

Prefer a dedicated scanner when it is installed, because it knows hundreds of credential formats and
checks history:

```bash
gitleaks detect --source . --report-path gitleaks.json        # history + working tree
gitleaks detect --source . --no-git                             # working tree only
trufflehog git file://. --only-verified                          # alternative
```

If neither is available, do a careful manual pass and say it is less complete:

```bash
git ls-files | grep -Ei '(\.env|\.pem|\.p12|\.key|id_rsa|credentials|secrets?\.(json|ya?ml))$'
git grep -nIE '(api[_-]?key|secret|token|password)\s*[:=]\s*[^ ]{8,}'
git grep -nI 'BEGIN (RSA|EC|OPENSSH) PRIVATE KEY'
git log --all -p -S 'AKIA' --oneline        # search history for a known prefix
```

Look in config files, test fixtures, notebooks, Docker and CI files, and committed `.env` files.

### 2. Triage each finding

For every hit, decide and record: real or false positive (example values, test fixtures, public
keys), what system it grants access to, whether it is in a pushed commit, and whether the repository is
public. Show only a masked form such as `sk_live_****9f2a`; repeating the full value in chat or reports
spreads the leak further.

### 3. Remediate in order

1. **Rotate or revoke** the credential at the provider (cloud console, payment dashboard, database).
   This is the only step that actually stops misuse. Check the provider's access logs for unexpected use
   since the commit date.
2. **Remove it from the code**: load it from an environment variable or a secret manager, add the file
   to `.gitignore`, and commit a `.env.example` with placeholder values.
3. **Clean history** only if needed (public repo, compliance, or the credential cannot be rotated).
   This rewrites history, so confirm with the user and explain the consequences first:

   ```bash
   git clone --mirror <repo-url> repo-backup.git                   # backup first
   git filter-repo --replace-text replacements.txt                  # or --path config/.env --invert-paths
   git push --force-with-lease --all && git push --force-with-lease --tags
   ```

   Every collaborator must re-clone afterwards, open PRs may break, and GitHub may keep cached views;
   contact GitHub support for sensitive data removal if the repo is public.
4. **Prevent recurrence**: add a pre-commit hook with gitleaks, enable GitHub secret scanning and push
   protection, and keep secrets out of example configs.

Do not run history rewriting or force pushes without an explicit yes from the user.

## Output format

```text
Secrets scan - repo: shop-api (public) - scanner: gitleaks 8.x, full history

| # | Where                          | Type              | Value        | Pushed | Risk   |
|---|--------------------------------|-------------------|--------------|--------|--------|
| 1 | config/prod.env (commit a1b2c3)| Payment live key  | sk_live_**9f | yes    | HIGH   |
| 2 | tests/fixtures/user.json       | Example token     | test_****    | yes    | none (fake) |

Do now:
  1. Revoke key #1 in the payment dashboard and create a new one; check recent API logs.
  2. Move it to an environment variable (patch below) and ignore config/*.env.
Then (needs your OK): rewrite history to remove config/prod.env - plan and impact below.
```

## Pitfalls and when to stop

- Rotation can break production; suggest updating the new value in deployments before revoking the old
  one when downtime matters, and let the user choose the timing.
- Do not test whether a found credential still works by logging in with it; checking via the
  provider's own dashboard is the safe route.
- Scan only repositories the user owns or is responsible for.
- Encrypted files (SOPS, git-crypt, sealed secrets) are usually fine; note them rather than flag them.

## Scope

This skill handles leaked credentials. Broader code vulnerabilities are covered by
security-review-lite, and general git history repair by git-helper.
