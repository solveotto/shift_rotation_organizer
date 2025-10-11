# Daily MySQL Backup System for PythonAnywhere

This directory contains scripts for automated MySQL database backups on PythonAnywhere.

## Files

1. **`daily_mysql_backup.py`** - Main backup script (run daily by scheduled task)
2. **`restore_backup.py`** - Interactive restore tool
3. **`test_backup_system.py`** - Pre-deployment test script
4. **`README.md`** - This file

## Features

- ✅ Creates daily backups with timestamps
- ✅ Keeps last 7 days of backups automatically
- ✅ Logs all operations to `app/logs/backup.log`
- ✅ Handles PythonAnywhere MySQL limitations
- ✅ Automatic cleanup of old backups

## Quick Start

### Step 1: Test the System (on PythonAnywhere)

```bash
cd ~/shift_rotation_organizer
python app/utils/backup/test_backup_system.py
```

This verifies:
- MySQL configuration is correct
- mysqldump command is available
- Database connection works
- Directories are writable
- Backup script is ready

### Step 2: Test Manual Backup

```bash
python app/utils/backup/daily_mysql_backup.py
```

This creates a backup in `backups/backup_YYYYMMDD_HHMMSS.sql`

### Step 3: Set Up Scheduled Task

1. Go to **PythonAnywhere Dashboard** → **Tasks** tab
2. Click **"Create a new scheduled task"**
3. Enter:
   - **Command**: 
     ```
     /home/solveottooren/shift_rotation_organizer/venv/bin/python /home/solveottooren/shift_rotation_organizer/app/utils/backup/daily_mysql_backup.py
     ```
   - **Hour**: `2` (2 AM UTC)
   - **Minute**: `0`
4. Click **Create**

## Configuration

Edit `daily_mysql_backup.py` to adjust:

```python
BACKUP_DIR = os.path.join(project_root, 'backups')  # Where backups are stored
KEEP_DAYS = 7  # Number of days to keep backups
LOG_FILE = os.path.join(project_root, 'app', 'logs', 'backup.log')
```

## Monitoring

### Check Backup Logs

```bash
tail -50 ~/shift_rotation_organizer/app/logs/backup.log
```

### List Backups

```bash
ls -lh ~/shift_rotation_organizer/backups/
```

### Check Disk Usage

```bash
du -sh ~/shift_rotation_organizer/backups/
```

## Restoring from Backup

### Interactive Restore

```bash
python app/utils/backup/restore_backup.py
```

This will:
1. Show all available backups
2. Let you choose which one to restore
3. Ask for confirmation (type `RESTORE`)
4. Restore the database

### Manual Restore

```bash
cd ~/shift_rotation_organizer/backups

# List available backups
ls -lh backup_*.sql

# Restore a specific backup
mysql -h solveottooren.mysql.pythonanywhere-services.com \
      -u solveottooren \
      -p \
      solveottooren\$turnuser < backup_20251011_020000.sql
```

## Backup Retention

Default: **7 days** of backups

To change retention, edit `daily_mysql_backup.py`:
```python
KEEP_DAYS = 30  # Keep 30 days instead
```

## Backup File Format

Backups are named: `backup_YYYYMMDD_HHMMSS.sql`

Example:
- `backup_20251011_020000.sql` = Backup from October 11, 2025 at 2:00 AM

## Troubleshooting

### "mysqldump: command not found"
- Script must run on PythonAnywhere server, not locally
- Use PythonAnywhere's scheduled tasks

### "Access denied" errors
- Check password in `config.ini` is correct
- Verify database name includes `$` character

### "Error: 'Access denied; you need (at least one of) the PROCESS privilege(s)'"
- Add `--no-tablespaces` flag (already included in script)

### No backups created
- Check scheduled task logs in PythonAnywhere
- Check `app/logs/backup.log` for errors
- Try running manually to test

### Disk space issues
- Check total size: `du -sh ~/shift_rotation_organizer/backups/`
- Reduce `KEEP_DAYS` if needed
- PythonAnywhere free accounts have disk limits

## Best Practices

1. **Test restores periodically** - Verify backups work
2. **Download critical backups** - Keep local copies
3. **Monitor logs regularly** - Check backup.log weekly
4. **Adjust retention** - Based on needs and disk space
5. **Choose low-traffic time** - 2-4 AM recommended

## Security Notes

- Backups stored on same server as database
- Passwords in `config.ini` - keep it secure
- Consider downloading for off-site storage
- Backups contain all user data - protect appropriately

## Manual Download

Download backups via PythonAnywhere's Files tab:
1. Go to **Files** tab
2. Navigate to `/home/solveottooren/shift_rotation_organizer/backups/`
3. Click on a backup file
4. Click **Download** button

Store locally as an additional backup layer!

## Support

For issues:
1. Check logs: `app/logs/backup.log`
2. Run test script: `python app/utils/backup/test_backup_system.py`
3. Review this README for troubleshooting
4. Check PythonAnywhere scheduled task logs

