# Production Deployment Plan: claude-code-update → main

> **Action:** After approval, save this guide to `docs/DEPLOYMENT.md` for future reference.

## Summary of Changes

The `claude-code-update` branch adds these major features:
- **User self-registration** with email verification (48-hour tokens)
- **Authorized emails management** (admin whitelists email+rullenummer combinations)
- **Strekliste PDF→PNG conversion** (shift timeline image generation)
- **Favorites import** from previous turnus years with statistical matching

### Database Changes
| Change | Description |
|--------|-------------|
| New table | `authorized_emails` - stores whitelisted email/rullenummer pairs |
| New table | `email_verification_tokens` - stores verification tokens |
| Modified | `users` table - added: `email`, `email_verified`, `name`, `rullenummer`, `created_at`, `verification_sent_at` |

### New Dependencies
- Flask-Mail 0.9.1, email-validator 2.2.0
- PyMuPDF, pdfplumber 0.11.0, Pillow
- numpy 1.26.4, pandas 2.2.2

---

## Deployment Checklist

### Phase 1: Pre-Deployment (Before Merge)

- [ ] **1.1 Backup production database**
  ```bash
  # On PythonAnywhere console
  cd /home/solveottooren/shift_rotation_organizer
  python app/utils/backup/daily_mysql_backup.py
  ```

- [ ] **1.2 Document current production state**
  ```bash
  git log --oneline -3
  ```

- [ ] **1.3 Prepare email configuration** (have SMTP credentials ready)

### Phase 2: Merge & Pull Code

- [ ] **2.1 Merge branch locally**
  ```bash
  git checkout main
  git pull origin main
  git merge claude-code-update
  git push origin main
  ```

- [ ] **2.2 Pull on PythonAnywhere**
  ```bash
  cd /home/solveottooren/shift_rotation_organizer
  git stash              # Preserve local config
  git pull origin main
  git stash pop          # Restore local config
  ```

### Phase 3: Install Dependencies

- [ ] **3.1 Install new packages**
  ```bash
  pip install Flask-Mail==0.9.1 email-validator==2.2.0 PyMuPDF pdfplumber==0.11.0 Pillow numpy==1.26.4 pandas==2.2.2
  ```

### Phase 4: Update Configuration

- [ ] **4.1 Add email section to production config.ini**
  ```ini
  [email]
  smtp_server = smtp.gmail.com
  smtp_port = 587
  smtp_use_tls = True
  smtp_username = YOUR_EMAIL
  smtp_password = YOUR_APP_PASSWORD
  sender_email = noreply@yourdomain.com
  sender_name = Shift Rotation System
  ```

- [ ] **4.2 Create upload directory**
  ```bash
  mkdir -p app/static/turnusfiler
  ```

### Phase 5: Run Database Migrations (ORDER MATTERS)

- [ ] **5.1 First migration** (email verification)
  ```bash
  python app/utils/migrate_add_email_verification.py
  ```

- [ ] **5.2 Second migration** (name & rullenummer)
  ```bash
  python app/utils/migrate_add_name_and_rullenummer.py
  ```

### Phase 6: Reload & Verify

- [ ] **6.1 Reload web app** (PythonAnywhere Web tab → Reload)

- [ ] **6.2 Verify deployment**
  - Application loads without errors
  - Existing users can still log in
  - Existing users show `email_verified=1`
  - Admin panel shows new "Authorized Emails" section
  - Registration page (`/register`) displays correctly

---

## Rollback Procedure

If issues occur:
```bash
# Revert code
git checkout main~1

# Restore database (if needed)
python app/utils/backup/restore_backup.py
```

---

## Verification Steps

| Test | How to Verify |
|------|---------------|
| App loads | Visit production URL |
| Login works | Log in with existing account |
| Admin features | Check Admin → Authorized Emails menu |
| Registration | Visit /register (form should display) |
| Email sending | Complete test registration (optional) |

---

## Critical Files

- `app/utils/migrate_add_email_verification.py` - First migration
- `app/utils/migrate_add_name_and_rullenummer.py` - Second migration
- `config.ini` - Needs email settings added
- `app/utils/backup/daily_mysql_backup.py` - Backup script

---

## Email Setup Guide (SendGrid)

### Step 1: Get SendGrid API Key
1. Log in to https://sendgrid.com
2. Go to Settings → API Keys
3. Click "Create API Key"
4. Choose "Restricted Access" → enable "Mail Send"
5. Copy the API key (starts with `SG.`)

### Step 2: Verify Sender Identity
1. Go to Settings → Sender Authentication
2. Either verify a single sender email OR set up domain authentication
3. Single sender is faster for testing

### Step 3: Add to production config.ini
```ini
[email]
smtp_server = smtp.sendgrid.net
smtp_port = 587
smtp_use_tls = True
smtp_username = apikey
smtp_password = SG.xxxxxxxxxxxxxxxxxxxx    # Your full API key
sender_email = verified-sender@yourdomain.com
sender_name = Shift Rotation System
```

**Important:** The `smtp_username` must be literally `apikey` (not your email), and `smtp_password` is your SendGrid API key.

### SendGrid Benefits
- Better deliverability than Gmail
- Works well with PythonAnywhere
- Free tier: 100 emails/day
