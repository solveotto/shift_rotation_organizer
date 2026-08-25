# Production Readiness Checklist

Run this **before** the October traffic peak — the R27 import and the
registration wave land at the same time, and the failures that matter are the
silent ones: config that falls back to a working-looking default, gitignored
files that only exist where someone put them, and rate limits that lock out a
whole depot.

**Order:** run A–K on **staging (`turnushjelper-2`)** first, then run it again
on **production (`turnushjelper-1`)**.

⚠ = the step writes something. Everything else is read-only and safe to run on
production at any time. Each ⚠ step says whether it is safe on production — one
of them (the restore drill, J) is **staging only**.

Each item says *why* it catches a real failure and gives the command.
**Forventet** is what a healthy result looks like — if you see something else,
stop and investigate rather than continuing.

All commands run from the repo root (`/home/deploy/turnushjelper` on the
servers) with the `venv/bin/` prefix.

**This guide does not cover the R27 import itself** — see
[TESTING_TURNUS_SETS.md](TESTING_TURNUS_SETS.md) Phase B, and the appendix at
the bottom.

---

## A. Before you start

- [ ] **Record the SHA on each host** — deploy status is per-host, and the
      hostnames are near-identical. A PII exposure once survived ten days
      because a fix logged as "done on prod" had only been verified on staging.
      ```bash
      hostname && git rev-parse --short HEAD && git log -1 --format=%cd
      ```
      **Forventet:** you have three written-down pairs (dev / staging / prod).
      Note any gap — production once ran 54 commits behind for two weeks.
      Re-run `hostname` before every ⚠ step.

- [ ] **Test suite green on the dev machine** — pytest is deliberately not in
      `requirements.txt`, so the servers don't have it, and the suite builds its
      own in-memory SQLite DB anyway. Running it on a server would test nothing.
      ```bash
      venv/bin/pytest -q
      ```
      **Forventet:** all green, on the SHA you are about to deploy.

---

## B. Platform & service

- [ ] **Gunicorn timeout is 300 s** — without it, strekliste generation is
      killed at gunicorn's 30 s default partway through (reproducibly at ~269
      images for r26) and the browser shows "En feil oppstod under generering",
      which means *the request died*, not that anything was reported.
      ```bash
      systemctl cat turnushjelper | grep -E 'timeout|workers|gunicorn.conf'
      ```
      **Forventet:** `--timeout 300`, or a `-c deploy/gunicorn.conf.py` that
      supplies it.

- [ ] **Service is active and enabled** — `enabled` is what makes it come back
      after a reboot.
      ```bash
      systemctl is-active turnushjelper && systemctl is-enabled turnushjelper
      ```
      **Forventet:** `active` and `enabled`.

- [ ] **Disk and memory headroom** — each worker is ~150–200 MB, and a forced
      PNG regeneration builds a full second copy in a `.png-gen-*` temp dir
      before swapping it in.
      ```bash
      df -h / && free -h
      ```
      **Forventet:** at least a few GB free and enough RAM to add a worker if
      you need to scale under load.

- [ ] **No leftover `.png-gen-*` directory** — one of these is the fingerprint
      of a strekliste run that was killed mid-way.
      ```bash
      ls -d turnusdata/*/streklister/.png-gen-* 2>/dev/null || echo "clean"
      ```
      **Forventet:** `clean`.

- [ ] **TLS certificate is not about to expire** — an expiry mid-October takes
      the entire site down for everyone at once.
      ```bash
      sudo certbot certificates 2>/dev/null | grep -E 'Certificate Name|Expiry'
      ```
      **Forventet:** expiry comfortably past October, and the renewal timer
      active (`systemctl is-active certbot.timer`).

- [ ] **Log destinations exist and are writable** — gunicorn worker timeouts
      land in `error.log`, **not** journald, so this is where the evidence goes.
      ```bash
      ls -la /var/log/turnushjelper/ && ls -la app/logs/
      ```
      **Forventet:** `access.log`, `error.log`, plus `app.log` and
      `turnus_import.log`, all owned by the service user.

---

## C. Config truth

The theme of this section: **wrong config here fails silently**, not loudly.

- [ ] **The app is really on MySQL** — if `DB_TYPE` falls back to `sqlite`, the
      app comes up against an empty `./dummy.db` that looks like a perfectly
      working site with no users. This script prints `DB_TYPE=` as its first
      line precisely because a prod script once gave a clean bill of health for
      a stray local SQLite file.
      ```bash
      venv/bin/python scripts/check_rullenummer_duplicates.py | head -1
      ```
      **Forventet:** `DB_TYPE=mysql`.

- [ ] **`TRUSTED_PROXY_COUNT` matches the real hop count** — too low and rate
      limiting keys on nginx's own IP (so one blocked IP blocks everyone) and
      emailed links come out `http://` with the wrong host; too high and a
      client can spoof its IP with a forged `X-Forwarded-For`.
      ```bash
      grep -E '^TRUSTED_PROXY_COUNT|^DB_TYPE' .env
      ```
      **Forventet:** `1` behind a single nginx, `2` if Cloudflare sits in front.
      Unset is fine — it defaults to 1 when `DB_TYPE=mysql`.

- [ ] **Session cookie flags** — `Secure` is defaulted on only because
      `DB_TYPE == "mysql"`; verify it actually arrives that way.
      ```bash
      curl -sI https://<host>/login | grep -i set-cookie
      ```
      **Forventet:** `Secure`, `HttpOnly` and `SameSite=Lax` all present.

- [ ] **Mailgun is configured** — the whole registration wave depends on it.
      ```bash
      grep -E '^MAILGUN_|^SENDER_' .env | sed 's/=.*KEY.*/=<set>/'
      ```
      **Forventet:** API key set, `MAILGUN_REGION=eu`, sender on
      `mail.turnushjelper.no`.

- [ ] **No bootstrap admin password left behind, and prod is not running
      `run.py`** — `DEFAULT_ADMIN_PASSWORD` is a one-time bootstrap value, and
      `run.py` is the dev server.
      ```bash
      grep -E '^DEFAULT_ADMIN_PASSWORD' .env; ps aux | grep -c '[r]un.py'
      ```
      **Forventet:** the password blank or absent, and `0` run.py processes.

---

## D. Database & migrations

> `check_db.py` and `db_check_orphaned_favorites.py` **always exit 0** — read
> their output, don't script them as pass/fail gates. The other two do set
> exit codes.

- [ ] **Alembic is at head** — a pending migration after a pull means the
      running code and the schema disagree.
      ```bash
      venv/bin/alembic current
      ```
      **Forventet:** a revision id with no `(head)` mismatch, matching
      `venv/bin/alembic heads`.

- [ ] **Database connects and the counts are sane** — the cheapest proof that
      the app is talking to the database you think it is.
      ```bash
      venv/bin/python scripts/check_db.py
      ```
      **Forventet:** `Database connection successful` and user/favorite/shift
      counts in the right ballpark for production. A few hundred users, not 0.

- [ ] **No duplicate rullenummer** — innplassering rows join to users on the
      rullenummer *string*, so two users sharing one means one sees the other's
      turnus. Especially worth re-running after any member-list import.
      ```bash
      venv/bin/python scripts/check_rullenummer_duplicates.py
      ```
      **Forventet:** `SAFE to add the unique index` (exit 0). Whitespace/case
      variants are reported as warnings — normalize them before October.

- [ ] **No orphaned favorites — run this BEFORE the import** so pre-existing
      rows don't get blamed on it.
      ```bash
      venv/bin/python scripts/db_check_orphaned_favorites.py
      ```
      **Forventet:** `Database is clean`. If not, note the rows now.

- [ ] **`TurnusSet` paths point at real files** — the rows store **absolute**
      paths, so any relocation strands them. The app falls back to the
      conventional location and only logs a warning, so this fails quietly.
      ```bash
      venv/bin/python scripts/repoint_turnus_paths.py --dry-run
      ```
      **Forventet:** every set `OK, left alone`, `0 row(s) would change`.
      If rows would change, re-run without `--dry-run` (⚠ safe and idempotent).

---

## E. Data files only the server has

`turnusdata/**/*.pdf`, `**/*.png` and everything under `instance/` are
gitignored — they exist **only where someone put them**, and `git pull` never
restores them. "Works on dev" proves nothing here.

- [ ] **Schedule and stats JSON per year** — every user-facing shift page reads
      these.
      ```bash
      ls turnusdata/*/turnus_schedule_*.json turnusdata/*/turnus_stats_*.json
      ```
      **Forventet:** one pair per active rutetermin. (These two *are* tracked
      in git, unlike the rest of the directory.)

- [ ] **Strekliste PNG count** — missing PNGs mean "Ingen tidslinje
      tilgjengelig" on every single shift popup, the most visible failure on
      this list.
      ```bash
      ls turnusdata/r26/streklister/png | wc -l
      ```
      **Forventet:** **423** for r26. 492 means the wrong PDF edition (the
      correct one is md5 `9091cf5ee5b1fd5db797a6dc3ccf6888`).

- [ ] **Turnusnøkkel Excel present with the Norwegian `ø` intact** — this is
      the only calendar-date source in the system. A filename encoding mismatch
      on the server silently blanks every kompdag badge to `–`.
      ```bash
      ls turnusdata/*/turnusnøkkel_*_org.xlsx
      ```
      **Forventet:** `turnusnøkkel_R26_org.xlsx` (uppercase year, `_org`
      suffix) listed without mojibake.

- [ ] **PII files in `instance/protected/`, and nowhere else** — nothing under
      `app/static/` is authenticated.
      ```bash
      ls -R instance/protected/
      ```
      **Forventet:** `medlemsliste.xlsx`, `ansinitet.pdf`, and
      `{rxx}/innplassering_{RXX}.pdf` per year.

- [ ] **PDF download directory is not empty** — if it is, the navbar download
      dropdown simply disappears with no error.
      ```bash
      ls turnusdata/*/pdf/
      ```
      **Forventet:** `turnuser_{RXX}.pdf` and any other published PDFs.

---

## F. Registration wave

The least-covered area in the existing guides, and the one October will stress
hardest.

- [ ] **The member list is loaded** — self-registration matches against
      pre-seeded stub users keyed on NLF medlemsnummer. No stubs, no
      registrations.
      ```bash
      venv/bin/python scripts/check_db.py
      ```
      Then open `/admin/employees` and compare against the roster you expect.
      **Forventet:** stub count matches the number of people you expect to sign
      up.

- [ ] ⚠ **Register one genuinely new test account, end to end** — form →
      verification email → `/verify/<token>` → auto-login. This is the single
      highest-value test on the page; it exercises Mailgun, the token, the
      stub match and the login path in one pass.
      **Forventet:** the email arrives within a minute and the link logs you
      straight in.

- [ ] **The emailed link is `https://` and the right host** — links are built
      with `url_for(_external=True)`, so this is the visible symptom of a wrong
      `TRUSTED_PROXY_COUNT`.
      **Forventet:** `https://<prod host>/verify/...`. An `http://` link or a
      wrong host means go back to section C.

- [ ] ⚠ **Decide the `/register` rate limit before October — this is a real
      risk, not just a check.** The limit is `10 per hour` **per IP**
      (`app/routes/registration.py:17`), and the limiter uses
      `storage_uri="memory://"` (`app/extensions.py:31`), so it is per-worker
      and resets on restart. **A depot behind one NAT can lock out a whole
      shift's worth of signups.**

      Test it **in the browser**, submitting the real form repeatedly. A `curl`
      loop does **not** work: `csrf.init_app()` runs before `limiter.init_app()`
      in `app/__init__.py`, so a token-less POST is redirected by CSRF and never
      reaches the limiter — verified, 13 bare POSTs returned 302 every time and
      never once 429.

      **Forventet:** submissions 1–10 go through and the **11th** returns
      `429`. That is the limiter working correctly — the real question is
      whether 10/hour/IP is the right number for a depot on one NAT. If it
      isn't, raise it before October.

- [ ] **Email throttles and windows** — `/resend-verification` is where users
      land when the first email fails, and the cleanup cron must not delete
      people who are mid-signup.
      ```bash
      grep -E '^MAX_VERIFICATION_EMAILS_PER_DAY|^TOKEN_EXPIRY_HOURS|^UNVERIFIED_CLEANUP_DAYS' .env
      crontab -l | grep cleanup
      ```
      **Forventet:** resend cap `3`, expiry 48 h, cleanup 14 days — cleanup must
      stay much longer than expiry. Test one resend on staging.

- [ ] **Password reset — verify by log, not by screen.** `/forgot-password`
      always shows the success modal even when Mailgun fails, deliberately, so
      the page cannot be used to enumerate accounts. The screen tells you
      nothing.
      ```bash
      tail -f app/logs/app.log     # then trigger a reset in the browser
      ```
      **Forventet:** the reset email arrives and **no** Mailgun error in the log.

---

## G. Logged-in smoke path

One pass in a real browser as a normal (non-admin) test user. Fast, and it
catches everything sections D–E can only infer.

- [ ] **`/login` → `/turnusliste` renders with data.**
      **Forventet:** the full shift table, and kompdag badges showing
      **numbers, not `–`**, that **differ between linjer**. All-zero or
      all-identical means the counting never saw the schedule.

- [ ] **Open a shift popup — the strekliste image loads.**
      **Forventet:** a timeline image, not "Ingen tidslinje tilgjengelig".
      Spot-check that the hour ruler lines up with the bars against the source
      PDF; stale PNGs from a previous edition look perfectly correct alone.

- [ ] **Favorites: add, reorder, reload — then reload ~20 times.** The repeat
      is only meaningful on a real two-worker host: an order that alternates
      between two values means a per-user page cache has been reintroduced,
      which caused two shipped bugs and was deliberately removed.
      **Forventet:** pills numbered `1, 2, 3 …` with no gap after removing one
      from the middle, and the same order on every one of the ~20 reloads.

- [ ] **`/mintur` shows that user's own shift.**
      **Forventet:** their own turnus. A user not in the innplassering must see
      no Min tur at all — **never someone else's**. Allow up to a minute after
      an activation; the nav flag is cached 60 s per user.

- [ ] **`/mintur/export_ical` downloads a valid `.ics`.**
      **Forventet:** a file that opens in a calendar app. A 404 JSON
      "Turnusnøkkel-mal ikke funnet" means section E's Excel check failed.

- [ ] **`/soknadsskjema` generates both DOCX and PDF, `/oversikt` renders, and
      a PDF downloads from the navbar dropdown.**
      **Forventet:** all four work. `/oversikt` is the heaviest page — note how
      long it takes.

---

## H. Security invariants

- [ ] **Data files are not reachable without a session** — nginx must not serve
      `turnusdata/` or `instance/`. The identical bytes were once fetchable at
      `/static/turnusfiler/…` with no session while the route was
      `@login_required` — protection that didn't protect.
      ```bash
      curl -s -o /dev/null -w "%{http_code}\n" https://<host>/static/turnusfiler/r26/streklister/png/1201.png
      curl -s -o /dev/null -w "%{http_code}\n" https://<host>/turnusdata/r26/streklister/png/1201.png
      curl -s -o /dev/null -w "%{http_code}\n" https://<host>/instance/protected/medlemsliste.xlsx
      ```
      **Forventet:** `404` for all three.

- [ ] **Admin routes reject a normal user.**
      ```bash
      curl -s -o /dev/null -w "%{http_code}\n" https://<host>/admin/dashboard
      ```
      **Forventet:** a redirect to login (302) when logged out; a flash +
      redirect as a normal user, and 403 JSON for an XHR request.

- [ ] **PII invariant test passes** (dev machine — it shells out to git).
      ```bash
      venv/bin/pytest tests/test_protected_files.py -q
      ```
      **Forventet:** green. Note the PII half is a filename denylist and fails
      open on unanticipated names; the structural half can't.

> **Not a bug:** login flash messages revealing stub/NLF/unverified state are
> settled and intentional — they only appear after a correct password.

---

## I. Load

- [ ] **Run the remote load test against staging** (never point it at
      production during business hours).
      ```bash
      LOAD_TEST_URL=https://<staging host> LOAD_TEST_WORKERS=20 \
        LOAD_TEST_REQUESTS=100 venv/bin/pytest tests/test_load.py -v -s
      ```
      **Forventet:** zero 5xx, p95 under the test's own assertions (2 s on
      `/login`, 3 s on mixed waves). For reference, `/turnusliste` renders in
      ~33 ms and `/oversikt` in ~17 ms with the data caches warm.

- [ ] **Watch the error log while it runs** — worker timeouts land here, not in
      journald.
      ```bash
      sudo tail -f /var/log/turnushjelper/error.log
      ```
      **Forventet:** no worker timeouts, no restarts. If the site struggles,
      [HIGH_TRAFFIC_MODE.md](HIGH_TRAFFIC_MODE.md) is the runbook for scaling
      workers.

---

## J. Backups

- [ ] **Run the backup self-test** — the single best "is this server healthy"
      script: MySQL config, `mysqldump` on PATH, live connection, backup and
      log dirs writable, B2 credentials and bucket access.
      ```bash
      venv/bin/python scripts/backup/test_backup_system.py
      ```
      **Forventet:** all checks pass (exit 0). It prompts before doing anything
      that writes — **answer `no` to both prompts** for a read-only pass.

- [ ] **A recent dump actually exists, and the cron entries are there.**
      ```bash
      ls -la ../backups/ | tail -5
      crontab -l
      ```
      **Forventet:** a dump from last night with a plausible size. Prod runs
      `daily_mysql_backup.py` at 02:00 and `offsite_backup.py` at 02:10;
      staging runs `restore_from_offsite.py --yes` at 03:00.

- [ ] ⚠ **Restore drill — staging only.** A backup that has never been restored
      is not a backup.
      ```bash
      venv/bin/python scripts/backup/restore_from_offsite.py
      ```
      **Forventet:** the restore completes and staging still works afterwards.
      Never run this on production.

---

## K. Finish

- [ ] **Read the logs for anything recurring** — not just errors from today.
      ```bash
      sudo tail -100 /var/log/turnushjelper/error.log
      tail -100 app/logs/app.log
      tail -50 app/logs/turnus_import.log
      ```
      **Forventet:** nothing repeating. `app.log` is WARNING-level only, so
      anything in it is worth reading.

- [ ] **Write down host + SHA + date for each host.** Not just the date.

---

## Appendix: the R27 import

**Do not improvise the import from this page.** Follow
[TESTING_TURNUS_SETS.md](TESTING_TURNUS_SETS.md) Phase B (Parts 0–7) — it has
the dry run, the favorites snapshots, the activation steps and the rollback
path. [CREATING_TURNUS_SETS.md](CREATING_TURNUS_SETS.md) is the how-to.

Three things from it are worth repeating here because they are the ones that
cause outages:

1. **Create the set inactive.** A set with no innplassering, no turnusnøkkel
   and no strekliste PNGs breaks Min tur, kompdag badges and shift images for
   every user at once, from the moment it goes active.
2. **Generate strekliste PNGs from the CLI, not the admin button.** The admin
   route runs synchronously inside the request, occupying one of two workers
   for ~35 s (so the site runs at half capacity), and it **discards** the
   per-shift error list that this form prints:
   ```bash
   nohup venv/bin/python -c "import app.utils.pdf.strekliste_generator as sg; r=sg.generate_all_images('r27', force=True); print(r['total'], len(r['generated']), r['errors'][:5])" > /tmp/strekliste.log 2>&1 &
   ```
   An interrupted run leaves the existing images untouched — generation builds
   into a sibling temp dir and swaps in only when complete.
3. **Restart after any import.** `SimpleCache` is per-process and production
   runs two workers, so an invalidation triggered by your admin request only
   ever reaches the worker that served it.
   ```bash
   sudo systemctl restart turnushjelper
   ```

**Order of operations for the whole October window:** pull → run the migration
pre-flight checks → `alembic upgrade head` → restart. A migration's pre-flight
script can ship inside the very pull that gates it; the pull touches no
database state and running workers keep the old code in memory until restart.

---

## Related guides

- [TESTING_TURNUS_SETS.md](TESTING_TURNUS_SETS.md) — the turnus import checklist
- [CREATING_TURNUS_SETS.md](CREATING_TURNUS_SETS.md) — import how-to
- [HIGH_TRAFFIC_MODE.md](HIGH_TRAFFIC_MODE.md) — what to do *during* a slowdown
- [BACKUP_SETUP.md](BACKUP_SETUP.md) — backup and off-site configuration
- [PROTECTED_FILES.md](PROTECTED_FILES.md) — where PII lives and why
- [ADMIN_BOOTSTRAP.md](ADMIN_BOOTSTRAP.md) — creating the first admin
- [SERVER_RESTORE_GUIDE.md](SERVER_RESTORE_GUIDE.md) — full disaster recovery
