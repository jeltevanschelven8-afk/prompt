---
name: security-review-lite
description: >-
  Review the user's own code for the most common security mistakes - SQL and command injection, XSS,
  path traversal, unsafe deserialisation, SSRF, missing authentication or authorisation checks, weak
  crypto and risky defaults - and propose concrete fixes ranked by severity. Defensive only. Use this
  skill whenever the user asks "is this code secure", "review this for vulnerabilities", "check my API
  for security issues", "OWASP check", "can this be hacked", or says "is mijn code veilig", "controleer
  op beveiligingslekken" or "zitten er kwetsbaarheden in". Works on a file, a diff or a small project.
license: "MIT"
metadata:
  author: "prompt"
  category: "security"
  tags: "security, owasp, code review, injection, xss, authorization, kwetsbaarheden, beveiliging"
  version: "1.0.0"
  summary_nl: "Controleert je eigen code op veelvoorkomende beveiligingsfouten zoals injectie en XSS en stelt concrete fixes voor."
---

# Security review lite

Most real-world vulnerabilities come from a short list of mistakes: untrusted input reaching a
dangerous function, or an action that never checks who is asking. This skill traces input through the
user's code to those dangerous spots and proposes the smallest fix that closes each gap. It is a
focused review, not a penetration test.

## Workflow

### 1. Map the attack surface

Identify where untrusted data enters: HTTP handlers, query and path parameters, request bodies,
headers, cookies, file uploads, message queues, CLI arguments, environment and files from users. Note
the framework, because it decides which protections already exist (ORMs parameterise, React escapes by
default, Django has CSRF middleware).

### 2. Trace input to sinks

For each entry point, follow the data to these sinks and check the matching defence:

| Risk | Look for | Safe pattern |
|---|---|---|
| SQL injection | string-built queries, f-strings in `execute` | parameterised queries or the ORM |
| Command injection | `os.system`, `shell=True`, `exec` with input | argument arrays, no shell, allow-list |
| XSS | `innerHTML`, React raw-HTML props, the Jinja `safe` filter, unescaped templates | auto-escaping, sanitiser such as DOMPurify |
| Path traversal | `open(base + name)`, user-chosen file paths | resolve, then check it stays inside the base |
| Unsafe deserialisation | `pickle.loads`, `yaml.load`, Java `ObjectInputStream`, `BinaryFormatter` | JSON, `yaml.safe_load`, schema validation |
| SSRF | server fetches a URL the user supplies | allow-list hosts, block internal ranges |
| Missing authz | handlers that load objects by id without checking the owner | check ownership or role on every request |
| Weak crypto | MD5/SHA1 for credentials, `Math.random` for tokens, ECB | bcrypt or argon2, `crypto.randomBytes`, AEAD |
| Risky defaults | debug mode on, permissive CORS, verbose errors, no rate limit | production config, explicit origins |

Also glance at dependencies (`npm audit`, `pip-audit`, `dotnet list package --vulnerable`) and report
only advisories that affect code paths in use.

### 3. Confirm each finding

Before reporting, check that the input is actually attacker-controlled and that no upstream layer
already validates it. Rate severity by impact and reachability: an unauthenticated SQL injection is
critical; an XSS in an admin-only debug page is low. Mark anything uncertain as "needs verification"
rather than overstating it.

### 4. Propose fixes

Give a minimal patch per finding, in the project's own style, plus a test that would catch a
regression where practical. Example:

```python
# Before - path traversal: name="../../etc/hosts" escapes the uploads folder
return send_file(os.path.join(UPLOAD_DIR, name))

# After
target = (UPLOAD_DIR / name).resolve()
if not target.is_relative_to(UPLOAD_DIR.resolve()):
    abort(404)
return send_file(target)
```

Apply changes only when the user asks; otherwise deliver them as suggestions.

## Output format

```text
Security review - src/api (Flask, 14 files) - 4 findings

[HIGH] Missing authorisation - routes/invoices.py:42
  GET /invoices/<id> returns any invoice to any logged-in user.
  Fix: filter by current_user.id (patch below). Test: user B gets 404 for user A's invoice.

[MEDIUM] Path traversal - routes/files.py:18  (patch below)
[LOW] Debug mode enabled via FLASK_DEBUG default - config.py:5
[INFO] Dependency: werkzeug 2.x has an advisory, but the affected debugger is not used in production.

Not reviewed: infrastructure, auth provider configuration, client-side bundle.
```

Order findings by severity and always list what was not covered, so nobody mistakes the review for a
full audit.

## Pitfalls and when to stop

- Review only code the user owns or is authorised to assess. Describe how a weakness could be abused
  in one sentence; do not write working exploits or attack tooling.
- Do not report a theoretical issue as confirmed without tracing it.
- If you see credentials in the code, mask them in the report and point to secrets-scanner.
- Large codebases: agree on a scope (one service, the auth flow, the upload path) instead of skimming
  everything shallowly.

## Scope

A quick, defensive code review. It does not replace a professional penetration test, threat modelling
for high-risk systems, or compliance audits. Personal data handling is covered by privacy-checker.
