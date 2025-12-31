#!/bin/bash
#
# Lab by Kraliki Usage Metering - Cron Job Setup
#
# This script configures automated collection of usage metrics.
#

MAGIC_BOX_SCRIPTS="/opt/magic-box/scripts"
CUSTOMER_ID="${CUSTOMER_ID:-magicbox-default}"
VM_ID="${VM_ID:-$(hostname)}"
LOG_DIR="/var/log/magic-box"

echo "Setting up Lab by Kraliki usage metering cron jobs..."
echo "Customer ID: $CUSTOMER_ID"
echo "VM ID: $VM_ID"

# Create log directory
mkdir -p "$LOG_DIR"
chmod 755 "$LOG_DIR"

# Remove existing cron job
crontab -l 2>/dev/null | grep -v "magic-box" | crontab -

# Add new cron jobs
(crontab -l 2>/dev/null; cat <<EOF

# Lab by Kraliki Usage Metering
# Collect resource usage every 5 minutes
*/5 * * * * root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 usage_metering.py --customer-id $CUSTOMER_ID --vm-id $VM_ID --collect >> $LOG_DIR/metering.log 2>&1

# Parse API logs every hour
0 * * * * root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 parse_cliproxy_logs.py --log-file /var/log/cliproxy/access.log --customer-id $CUSTOMER_ID --vm-id $VM_ID --store >> $LOG_DIR/parser.log 2>&1

# Start dashboard on boot
@reboot root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 usage_dashboard.py --port 8080 --host 127.0.0.1 >> $LOG_DIR/dashboard.log 2>&1 &

# Generate daily usage report
0 0 * * * root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 usage_metering.py --customer-id $CUSTOMER_ID --vm-id $VM_ID --period day --export-csv $LOG_DIR/usage-daily-$(date +\%Y\%m\%d).csv >> $LOG_DIR/reports.log 2>&1

# Generate weekly usage report (Monday 0:00)
0 0 * * 1 root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 usage_metering.py --customer-id $CUSTOMER_ID --vm-id $VM_ID --period week --export-csv $LOG_DIR/usage-weekly-$(date +\%Y\%W).csv >> $LOG_DIR/reports.log 2>&1

# Generate monthly usage report (1st of month 0:00)
0 0 1 * * root cd $MAGIC_BOX_SCRIPTS && /usr/bin/python3 usage_metering.py --customer-id $CUSTOMER_ID --vm-id $VM_ID --period month --export-csv $LOG_DIR/usage-monthly-$(date +\%Y\%m).csv >> $LOG_DIR/reports.log 2>&1

EOF
) | crontab -

echo "Cron jobs installed successfully!"
echo ""
echo "To view cron jobs: crontab -l"
echo "To edit cron jobs: crontab -e"
echo ""
echo "Log files:"
echo "  - $LOG_DIR/metering.log"
echo "  - $LOG_DIR/parser.log"
echo "  - $LOG_DIR/dashboard.log"
echo "  - $LOG_DIR/reports.log"
