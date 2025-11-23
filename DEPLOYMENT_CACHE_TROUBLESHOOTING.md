# Deployment & Cache Troubleshooting Guide

When deploying to production or updating the live site, you may encounter caching/state issues where `git pull` and file deletions don't seem to take effect. This guide covers common causes and solutions.

## Common Issues & Solutions

### Issue 1: Old Python Process Still Running
When you delete the database and restart, if old Python processes are still running, they may still be using the old database file.

**Solution:**
```bash
# Kill all uvicorn/Python processes on port 8000
lsof -i :8000 | grep -v COMMAND | awk '{print $2}' | xargs kill -9

# Or kill all uvicorn processes system-wide
pkill -f uvicorn

# Or kill specific processes
ps aux | grep uvicorn
kill -9 <PID>

# Wait a moment
sleep 2

# Then start fresh
python -m uvicorn app.main:app --reload
```

### Issue 2: Python Import Caching (`.pyc` files)
Python caches bytecode in `__pycache__` directories. If you update models or enums but don't clear the cache, Python may load old bytecode.

**Solution:**
```bash
# Remove all Python cache directories
find . -type d -name __pycache__ -exec rm -r {} +

# Or remove .pyc files
find . -name "*.pyc" -delete

# Remove pip cache (if dependencies haven't updated properly)
pip cache purge

# Re-create the virtual environment if issues persist
rm -rf .venv
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue 3: Database File Lock
SQLite databases can be locked by processes if they don't close connections properly. This prevents deletion/recreation.

**Solution:**
```bash
# Check what has the database file open
lsof | grep ai_exchange.db

# Kill the processes holding the lock
kill -9 <PID>

# Now safely delete
rm -f ai_exchange.db

# Verify it's gone
ls -la ai_exchange.db  # Should show "No such file or directory"
```

### Issue 4: Node.js/Frontend Caching
Frontend may be serving cached bundles or stale JavaScript.

**Solution:**
```bash
cd frontend

# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Remove build artifacts
rm -rf dist/ .next/

# Hard reload in browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows/Linux)
```

### Issue 5: Browser Cache
Browser caching can cause old UI code to be loaded.

**Solution:**
```
- Open DevTools (F12 / Cmd+Opt+I)
- Go to Application > Cache Storage and clear all
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
- Or use Private/Incognito mode which doesn't cache
```

### Issue 6: Docker/Container Caching
If using Docker, images and containers may have stale data.

**Solution:**
```bash
# Stop all containers
docker compose down

# Remove unused images/volumes
docker system prune -a --volumes

# Rebuild from scratch
docker compose up --build

# Or clean rebuild
docker compose down -v  # Remove volumes too
docker system prune -a --volumes
docker compose up --build
```

## Complete "Nuclear Reset" Script

When all else fails, here's a complete reset for development:

```bash
#!/bin/bash
echo "🧹 Starting complete reset..."

# Kill all processes
echo "Killing processes..."
pkill -f uvicorn || true
pkill -f "npm run" || true

# Backend cleanup
echo "Cleaning backend..."
cd backend
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find . -name "*.pyc" -delete 2>/dev/null || true
rm -f ai_exchange.db ai_exchange.db-shm ai_exchange.db-wal
rm -rf .venv/

# Reinstall backend
echo "Reinstalling backend..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend cleanup
echo "Cleaning frontend..."
cd ../frontend
rm -rf node_modules package-lock.json
npm cache clean --force
rm -rf dist/ .next/

# Reinstall frontend
echo "Reinstalling frontend..."
npm install

echo "✅ Reset complete! You can now start fresh:"
echo "  Backend:  cd backend && source .venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "  Frontend: cd frontend && npm run dev"
```

## Prevention for Production

### Strategy 1: Use Health Checks
Add an endpoint to verify the database schema is up-to-date:

```python
@router.get("/health/db")
def health_check_db(session: Session = Depends(get_session)):
    """Verify database schema is current."""
    try:
        # Check that professional_role column exists on User table
        result = session.exec(
            text("PRAGMA table_info(user)")
        ).all()
        columns = [row[1] for row in result]

        if "professional_role" not in columns:
            raise HTTPException(
                status_code=500,
                detail="Database schema is outdated. Run migrations."
            )

        return {"status": "healthy", "database": "current"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}, 500
```

### Strategy 2: Automated Health Checks on Deploy
```bash
#!/bin/bash
# deploy.sh

# Pull latest code
git pull origin main

# Kill old processes
pkill -f uvicorn

# Clean cache
find . -type d -name __pycache__ -exec rm -r {} + 2>/dev/null
find . -name "*.pyc" -delete 2>/dev/null

# Restart backend
cd backend && python -m uvicorn app.main:app --reload &
sleep 5

# Health check
HEALTH=$(curl -s http://localhost:8000/health/db | jq -r '.status')
if [ "$HEALTH" != "healthy" ]; then
  echo "❌ Deployment failed: Database schema mismatch"
  exit 1
fi

echo "✅ Deployment successful"
```

### Strategy 3: Database Migrations (Future)
For production, consider using Alembic for migrations instead of auto-recreating:

```python
# Instead of: SQLModel.metadata.create_all(engine)
# Use: alembic upgrade head
```

This ensures:
- Schema changes are tracked
- Rollbacks are possible
- Existing data is preserved
- Clear audit trail

## Checklist for Production Deployment

- [ ] Kill all running processes before updating code
- [ ] Clear Python cache directories (`__pycache__`, `.pyc` files)
- [ ] Clear pip cache if dependency issues occur
- [ ] Delete database file ONLY if schema changed
- [ ] Verify database exists and has correct schema
- [ ] Clear npm/Node cache before frontend rebuild
- [ ] Hard refresh browser (not just F5)
- [ ] Test health check endpoints
- [ ] Check server logs for errors
- [ ] Monitor for 5-10 minutes after deploy

## Resources

- [Python Import System](https://docs.python.org/3/reference/import_system.html)
- [SQLite File Format](https://www.sqlite.org/fileformat.html)
- [Node.js Cache Best Practices](https://docs.npmjs.com/cli/v8/commands/npm-cache)
- [Docker Prune Documentation](https://docs.docker.com/config/pruning/)
