# Focus by Kraliki - Script Usage Guide

This guide explains how to start and stop the Focus by Kraliki application correctly to avoid port conflicts.

## Development Mode

### Starting Development Servers

```bash
./dev-start.sh
```

This script will:
- Automatically clear any processes on ports 8000 and 5173
- Start the backend server (FastAPI) on port 8000 with hot reload
- Start the frontend server (Vite) on port 5173 with hot reload
- Save process IDs to `.backend.pid` and `.frontend.pid`
- Display logs at `backend.log` and `frontend.log`

### Stopping Development Servers

```bash
./dev-stop.sh
```

This script will:
- Read PIDs from `.backend.pid` and `.frontend.pid`
- Gracefully kill both processes
- Force-kill any remaining processes on ports 8000 and 5173
- Clean up PID files

## Production Mode

### Starting Production Servers

```bash
./prod-start.sh
```

This script will:
- Clear ports 8000 and 4173
- Build the frontend production bundle
- Start backend with 4 workers (optimized for production)
- Start frontend preview server on port 4173
- Save PIDs to `.backend-prod.pid` and `.frontend-prod.pid`
- Display logs at `backend-prod.log` and `frontend-prod.log`

### Stopping Production Servers

```bash
./prod-stop.sh
```

This script will:
- Read PIDs from production PID files
- Gracefully stop both services
- Force-kill any lingering processes on ports 8000 and 4173
- Clean up production PID files

## Quick Reference

| Mode        | Start Command      | Stop Command      | Backend Port | Frontend Port |
|-------------|-------------------|-------------------|--------------|---------------|
| Development | `./dev-start.sh`  | `./dev-stop.sh`   | 8000        | 5173          |
| Production  | `./prod-start.sh` | `./prod-stop.sh`  | 8000        | 4173          |

## Troubleshooting

### Port Already in Use

If you see "port already in use" errors:

1. **Quick fix**: Run the stop script for your mode:
   ```bash
   ./dev-stop.sh    # for development
   ./prod-stop.sh   # for production
   ```

2. **Manual cleanup** (if stop script doesn't work):
   ```bash
   # Check what's using the ports
   lsof -ti:8000
   lsof -ti:5173  # or 4173 for production

   # Kill specific processes
   kill -9 $(lsof -ti:8000)
   kill -9 $(lsof -ti:5173)  # or 4173
   ```

### Can't Find Scripts

Make sure the scripts are executable:
```bash
chmod +x dev-start.sh dev-stop.sh prod-start.sh prod-stop.sh
```

### Logs Not Showing

View logs in real-time:
```bash
# Development
tail -f backend.log
tail -f frontend.log

# Production
tail -f backend-prod.log
tail -f frontend-prod.log
```

## Best Practices

1. **Always use the stop scripts** before starting again to avoid port conflicts
2. **Check logs** if services fail to start
3. **Don't manually kill processes** - use the stop scripts instead
4. **Run stop script before switching modes** (dev ↔ prod)

## Process Management

The scripts automatically:
- ✅ Clear ports before starting
- ✅ Save PIDs for clean shutdown
- ✅ Verify services are ready before completing
- ✅ Provide detailed status messages
- ✅ Force-kill stuck processes

This ensures you'll never have port conflicts when starting the application.
