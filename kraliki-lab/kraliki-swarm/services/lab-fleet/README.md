# Lab by Kraliki Fleet Management

Admin dashboard for managing Lab by Kraliki VM fleet, customers, and monitoring.

## Features

- **VM Management**: View, monitor, restart, and rebuild VMs
- **Customer Management**: Track customers, billing status, and subscriptions
- **Fleet Metrics**: Aggregate statistics across all VMs (revenue, costs, usage)
- **Alert System**: Track and resolve issues (disk space, offline VMs, unusual activity)
- **Resource Monitoring**: CPU, memory, disk usage per VM
- **One-Click Actions**: Restart or rebuild VMs directly from dashboard

## Architecture

```
┌─────────────────────────────────────────────────────┐
│              Fleet Management API                  │
│              (Python HTTP Server)                 │
├─────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌──────────────┐           │
│  │   VMs       │  │  Customers   │           │
│  │  Table      │  │   Table      │           │
│  └─────────────┘  └──────────────┘           │
│  ┌─────────────┐  ┌──────────────┐           │
│  │  Metrics    │  │   Alerts     │           │
│  │  Table      │  │   Table      │           │
│  └─────────────┘  └──────────────┘           │
│  ┌─────────────┐                                │
│  │  Updates    │                                │
│  │  Table      │                                │
│  └─────────────┘                                │
└─────────────────────────────────────────────────────┘
         ▲                    ▲
         │                    │
    HTTP JSON            HTTP JSON
         │                    │
┌────────┴────────┐  ┌─────┴──────────┐
│   Svelte UI     │  │   VM Agents    │
│   Dashboard     │  │   (Heartbeat)  │
└─────────────────┘  └────────────────┘
```

## Database Schema

### customers
- `id`: Customer ID (primary key)
- `name`: Customer name
- `email`: Customer email (unique)
- `company`: Company name (optional)
- `tier`: Subscription tier (starter/pro/enterprise)
- `billing_status`: Billing status (active/inactive/overdue)
- `monthly_fee`: Monthly subscription fee
- `created_at`: Creation timestamp

### vms
- `id`: VM ID (primary key)
- `hostname`: VM hostname
- `ip_address`: VM IP address (unique)
- `customer_id`: Customer ID (foreign key)
- `tier`: VM tier
- `status`: VM status (online/offline/maintenance/error)
- `created_at`: Creation timestamp
- `last_heartbeat`: Last heartbeat timestamp
- `cpu_cores`: Number of CPU cores
- `memory_gb`: Memory in GB
- `disk_gb`: Disk size in GB
- `version`: Lab by Kraliki version

### vm_metrics
- `id`: Metric ID (auto-increment)
- `vm_id`: VM ID (foreign key)
- `cpu_percent`: CPU usage percentage
- `memory_percent`: Memory usage percentage
- `disk_percent`: Disk usage percentage
- `disk_used_gb`: Disk used in GB
- `timestamp`: Metric timestamp

### alerts
- `id`: Alert ID (primary key)
- `vm_id`: VM ID (optional, foreign key)
- `customer_id`: Customer ID (optional, foreign key)
- `type`: Alert type (vm_offline, disk_space, api_quota, etc.)
- `severity`: Severity (high/warning/info)
- `message`: Alert message
- `created_at`: Alert timestamp
- `resolved`: Resolution status

### updates
- `id`: Update ID (primary key)
- `version`: Version number
- `description`: Update description
- `rollout_status`: Rollout status (pending/in_progress/completed)
- `created_at`: Creation timestamp
- `completed_at`: Completion timestamp

## API Endpoints

### Health
- `GET /` - Service info
- `GET /api/health` - Health check

### VMs
- `GET /api/vms` - List all VMs
- `GET /api/vms?status=online` - Filter by status
- `GET /api/vms/{vm_id}` - Get VM details
- `POST /api/vms` - Create new VM
- `PUT /api/vms/{vm_id}/status` - Update VM status
- `POST /api/vms/{vm_id}/restart` - Restart VM
- `POST /api/vms/{vm_id}/rebuild` - Rebuild VM
- `PUT /api/vms/{vm_id}/heartbeat` - VM heartbeat with metrics
- `GET /api/vms/{vm_id}/metrics?hours=24` - Get VM metrics

### Customers
- `GET /api/customers` - List all customers
- `GET /api/customers/{customer_id}` - Get customer details
- `GET /api/customers/{customer_id}/vms` - Get customer VMs
- `POST /api/customers` - Create new customer

### Metrics
- `GET /api/metrics/fleet` - Get fleet-wide metrics

### Alerts
- `GET /api/alerts` - List all alerts
- `GET /api/alerts?resolved=false` - Filter unresolved alerts
- `POST /api/alerts` - Create alert
- `PUT /api/alerts/{alert_id}/resolve` - Resolve alert

### Updates
- `GET /api/updates` - List updates

### Development
- `POST /api/seed-test-data` - Seed test data

## Deployment

### Local Development

1. Start the API server:
```bash
cd /home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/services/lab-fleet
./api.py --port 8686
```

2. Access dashboard:
   - Development: http://localhost:5173/lab
   - Production: https://kraliki.com/lab

### Production Deployment

1. Copy service to production:
```bash
mkdir -p /opt/lab-fleet
cp api.py /opt/lab-fleet/
chmod +x /opt/lab-fleet/api.py
```

2. Create systemd service:
```bash
cat > /etc/systemd/system/lab-fleet.service << EOF
[Unit]
Description=Lab by Kraliki Fleet Management API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/lab-fleet
ExecStart=/usr/bin/python3 /opt/lab-fleet/api.py --port 8686
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable lab-fleet
systemctl start lab-fleet
```

3. Configure Traefik reverse proxy (optional):
```yaml
# Example file provider snippet
http:
  routers:
    lab-fleet:
      rule: "PathPrefix(`/api/fleet`)"
      service: lab-fleet
  services:
    lab-fleet:
      loadBalancer:
        servers:
          - url: "http://127.0.0.1:8686"
```

## VM Agent Integration

VMs should send heartbeats with metrics:

```bash
curl -X PUT http://fleet-api:8686/api/vms/{vm_id}/heartbeat \
  -H "Content-Type: application/json" \
  -d '{
    "cpu_percent": 25.5,
    "memory_percent": 45.2,
    "disk_percent": 65.0,
    "disk_used_gb": 32.5
  }'
```

## Alert Generation

Alerts can be generated:

1. **Manually** via POST to `/api/alerts`
2. **Automatically** by monitoring script (to be implemented):
   - Check offline VMs (> 24h)
   - Check disk usage (> 80%)
   - Check API quota limits
   - Detect unusual activity patterns

## Future Enhancements

- SSH key management for VM access
- Automated alert generation daemon
- Historical metrics visualization with charts
- Customer billing integration
- Support ticket integration
- Update rollout automation
- Backup/snapshot management
- Cost optimization recommendations

## Troubleshooting

### API not responding
```bash
systemctl status lab-fleet
journalctl -u lab-fleet -n 50
```

### Database locked
```bash
rm /opt/lab-fleet/fleet.db
systemctl restart lab-fleet
# Database will be recreated
```

### Frontend not loading API
- Check CORS headers
- Verify API_BASE in frontend matches backend URL
- Check browser console for errors
