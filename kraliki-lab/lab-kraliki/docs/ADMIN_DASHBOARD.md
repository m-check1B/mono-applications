# Lab by Kraliki Admin Dashboard

Admin dashboard for managing Lab by Kraliki VM fleet and customer infrastructure.

> **SECURITY WARNING**: This dashboard currently has NO authentication. Do NOT expose via Traefik or any reverse proxy until security controls are implemented. See [SECURITY_TODO.md](./SECURITY_TODO.md) for required implementation steps.

## Features

### 1. VM Status Overview
- Real-time VM status (online/offline/provisioning/error)
- Health monitoring (healthy/unhealthy/unknown)
- Resource usage tracking:
  - CPU percentage
  - Memory percentage
  - Disk usage with percentage
- Version tracking per VM
- IP address management

### 2. Resource Usage Monitoring
- CPU usage per VM
- Memory usage per VM
- Disk usage with alert thresholds (80GB warning)
- Network traffic tracking

### 3. Alert System
- **Disk Space Alerts**: Auto-generated when disk > 80GB
- **API Quota Alerts**: Triggered when customer exceeds $50/week API spend
- **Unusual Activity**: Placeholder for custom alerts
- Alert severity levels: high, medium, low
- Alert resolution tracking

### 4. Fleet-Wide Metrics
- Total customers count
- Active VMs count
- Monthly revenue calculation (based on tier)
- Monthly costs (VMs + API usage)
- Gross margin percentage

### 5. Customer Management
- Customer listing with VM associations
- Customer details view
- Billing status tracking
- Support ticket association

### 6. VM Actions
- **Restart VM**: Restarts magic-box-stack service
- **Rebuild VM**: Schedules VM rebuild (Hetzner API integration pending)
- One-click actions from dashboard

### 7. Update Management
- Version tracking per VM
- Update rollout status (pending/deployed)
- Release notes storage

### 8. Support Ticket Integration
- Ticket creation with priority levels
- Ticket assignment tracking
- Status management (open/resolved)
- Customer/VM association

## Architecture

### Database Schema

#### `vms` table
```sql
- id (TEXT PRIMARY KEY): VM identifier
- customer_id (TEXT): Associated customer
- status (TEXT): online, offline, provisioning, error
- health (TEXT): healthy, unhealthy, unknown
- last_check (DATETIME): Last health check timestamp
- version (TEXT): Lab by Kraliki version running
- ip_address (TEXT): VM IP address
- region (TEXT): Deployment region (eu/us)
- tier (TEXT): Customer tier (starter/pro/enterprise)
```

#### `alerts` table
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- timestamp (DATETIME): Alert creation time
- vm_id (TEXT): Associated VM
- alert_type (TEXT): disk_space, api_quota, etc.
- severity (TEXT): high, medium, low
- message (TEXT): Alert description
- resolved (BOOLEAN): Resolution status
- resolved_at (DATETIME): Resolution timestamp
```

#### `support_tickets` table
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- timestamp (DATETIME): Ticket creation time
- customer_id (TEXT): Customer identifier
- vm_id (TEXT): Associated VM (optional)
- subject (TEXT): Ticket subject
- description (TEXT): Full description
- status (TEXT): open, in_progress, resolved
- priority (TEXT): low, medium, high
- assigned_to (TEXT): Support agent
- resolved_at (DATETIME): Resolution timestamp
```

#### `updates` table
```sql
- id (INTEGER PRIMARY KEY AUTOINCREMENT)
- version (TEXT): Update version
- released_at (DATETIME): Release date
- rollout_status (TEXT): pending, deployed, failed
- deployed_to (TEXT): Target VMs/groups
- notes (TEXT): Update description
```

### API Endpoints

#### Dashboard
- `GET /`: Main dashboard view
- `GET /vms`: VM fleet overview
- `GET /vms/<vm_id>`: VM detail view
- `GET /customers`: Customer management
- `GET /alerts`: Active alerts list
- `GET /tickets`: Support tickets
- `GET /tickets/new`: New ticket form

#### REST API
- `GET /api/metrics`: Fleet-wide metrics (JSON)
- `GET /api/vms`: All VMs (JSON)
- `GET /api/alerts`: All alerts (JSON)
- `POST /api/vms/<vm_id>/restart`: Restart VM
- `POST /api/vms/<vm_id>/rebuild`: Rebuild VM

## Installation

1. Install dependencies:
```bash
pip install flask
```

2. Start dashboard:
```bash
cd /home/adminmatej/github/applications/kraliki-lab/lab-kraliki/scripts
python3 admin_dashboard.py
```

3. Access at: `http://127.0.0.1:8002`

## Configuration

### Default Settings
- Host: `127.0.0.1` (security: only localhost)
- Port: `8002`
- Database: `/var/lib/magic-box/admin.db`
- Usage Database: `/var/lib/magic-box/usage.db`

### Command Line Options
```bash
python3 admin_dashboard.py --host 127.0.0.1 --port 8002 --debug
```

## Alert Thresholds

### Disk Space
- **Warning**: > 80GB
- **Critical**: > 90GB (to be implemented)

### API Quota
- **Warning**: > $50/week
- **Critical**: > $100/week (to be implemented)

### Unusual Activity
- **CPU spike**: > 90% for 5+ minutes (to be implemented)
- **Memory spike**: > 90% for 5+ minutes (to be implemented)

## Fleet Management

### Register New VM
```python
from admin_dashboard import AdminDatabase

db = AdminDatabase()
db.register_vm(
    vm_id="mb-12345",
    customer_id="cust-67890",
    ip_address="1.2.3.4",
    region="eu"
)
```

### Update VM Status
```python
db.update_vm_status(
    vm_id="mb-12345",
    status="online",
    health="healthy",
    version="1.0.1"
)
```

### Create Alert
```python
db.create_alert(
    vm_id="mb-12345",
    alert_type="disk_space",
    severity="high",
    message="Disk usage at 85GB (threshold: 80GB)"
)
```

### Create Support Ticket
```python
db.create_support_ticket(
    customer_id="cust-67890",
    vm_id="mb-12345",
    subject="VM not responding",
    description="Cannot access VM via SSH",
    priority="high"
)
```

## Security Considerations

**Current Status: PROTOTYPE - NO AUTHENTICATION**

See [SECURITY_TODO.md](./SECURITY_TODO.md) for complete implementation guide.

| Control | Status | Priority |
|---------|--------|----------|
| Localhost Binding | Implemented | - |
| JWT Authentication | NOT IMPLEMENTED | Critical |
| HTTPS Enforcement | NOT IMPLEMENTED (Traefik) | High |
| Rate Limiting | NOT IMPLEMENTED | High |
| CSRF Protection | NOT IMPLEMENTED | Medium |
| Audit Logging | NOT IMPLEMENTED | Medium |
| Zitadel Integration | NOT IMPLEMENTED | Future |

**WARNING:** Do NOT expose via Traefik until JWT auth and rate limiting are implemented.

## Integration Points

### Hetzner API
- VM creation (TODO)
- VM rebuild (TODO)
- VM deletion (TODO)
- Image management (TODO)

### Stripe Integration
- Customer tier validation (TODO)
- Billing sync (TODO)
- Subscription management (TODO)

### Notification System
- Email alerts (TODO)
- Slack integration (TODO)
- PagerDuty integration (TODO)

## Monitoring & Logging

### Log Location
- Application logs: stdout/stderr
- Database logs: SQLite journal files

### Health Checks
Run periodic health checks via cron:
```bash
*/5 * * * * cd /path/to/magic-box/scripts && python3 -c "from admin_dashboard import AdminDatabase; AdminDatabase().check_disk_alerts()"
```

## Troubleshooting

### Dashboard Won't Start
```bash
# Check if port is in use
lsof -i :8002

# Check database permissions
ls -la /var/lib/magic-box/

# View logs
python3 admin_dashboard.py --debug
```

### No VMs Showing
```bash
# Check if vms table exists
sqlite3 /var/lib/magic-box/admin.db ".schema vms"

# Insert test VM
sqlite3 /var/lib/magic-box/admin.db "INSERT INTO vms (id, customer_id, status, last_check) VALUES ('test-vm', 'test-customer', 'online', datetime('now'))"
```

### Alerts Not Creating
```bash
# Check resource usage data
sqlite3 /var/lib/magic-box/usage.db "SELECT * FROM resource_usage ORDER BY timestamp DESC LIMIT 5"

# Run alert check manually
python3 -c "from admin_dashboard import AdminDatabase; AdminDatabase().check_disk_alerts()"
```

## Roadmap

### Phase 1 (Current)
- [x] Basic VM status tracking
- [x] Resource usage monitoring
- [x] Alert system (disk, API quota)
- [x] Support tickets
- [x] Fleet metrics
- [x] VM actions (restart/rebuild)

### Phase 2 (Next)
- [ ] Hetzner API integration
- [ ] SMTP email alerts
- [ ] Slack webhook integration
- [ ] JWT authentication
- [ ] Role-based access control
- [ ] Customer self-service portal
- [ ] Billing integration (Stripe)
- [ ] Automated backups

### Phase 3 (Future)
- [ ] Predictive scaling
- [ ] Cost optimization recommendations
- [ ] Multi-region deployment
- [ ] Custom alert rules
- [ ] Integration marketplace
- [ ] White-label branding

## Support

For issues or questions, contact the Lab by Kraliki team or create a support ticket via the dashboard.
