#!/bin/bash
#
# Magic Box Usage Metering Installation Script
# ========================================
# Installs usage tracking service on Magic Box VMs
#

set -e

INSTALL_DIR="/opt/magic-box-usage"
DB_PATH="/opt/magic-box/usage.db"
SERVICE_FILE="/etc/systemd/system/magic-box-usage.service"

echo "📊 Installing Magic Box Usage Metering..."

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"
cd "$INSTALL_DIR"

# Copy files
echo "Installing service files..."
sudo cp usage_tracker.py "$INSTALL_DIR/"
sudo cp api.py "$INSTALL_DIR/"
sudo cp dashboard.html "$INSTALL_DIR/"
sudo cp schema.sql "$INSTALL_DIR/"

# Create database
echo "Initializing database..."
sudo python3 "$INSTALL_DIR/usage_tracker.py" --init --db "$DB_PATH"

# Prompt for customer registration
if [ ! -f "/opt/magic-box/customer-info.txt" ]; then
    echo ""
    echo "Customer Registration"
    echo "===================="
    read -p "Customer ID: " CUSTOMER_ID
    read -p "Customer Name: " CUSTOMER_NAME
    read -p "Customer Email (optional): " CUSTOMER_EMAIL

    # Register customer in database
    sudo python3 "$INSTALL_DIR/usage_tracker.py" \
        --register "$CUSTOMER_ID" "$CUSTOMER_NAME" "$CUSTOMER_EMAIL" \
        --db "$DB_PATH"

    # Save customer info for future reference
    cat > /tmp/customer-info.txt <<EOF
CUSTOMER_ID=$CUSTOMER_ID
CUSTOMER_NAME=$CUSTOMER_NAME
CUSTOMER_EMAIL=$CUSTOMER_EMAIL
EOF
    sudo mv /tmp/customer-info.txt "/opt/magic-box/customer-info.txt"
    echo "Customer registered successfully!"
fi

# Create systemd service for API server
echo "Creating systemd service..."
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=Magic Box Usage Metering API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/api.py --port 8585 --db $DB_PATH
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Create systemd service for collector
COLLECTOR_SERVICE="/etc/systemd/system/magic-box-usage-collector.service"
sudo tee "$COLLECTOR_SERVICE" > /dev/null <<EOF
[Unit]
Description=Magic Box Usage Collector
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=$INSTALL_DIR
ExecStart=/usr/bin/python3 $INSTALL_DIR/usage_tracker.py --collect --db $DB_PATH
Restart=always
RestartSec=300

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start services
echo "Starting services..."
sudo systemctl daemon-reload
sudo systemctl enable magic-box-usage.service
sudo systemctl enable magic-box-usage-collector.service
sudo systemctl start magic-box-usage.service
sudo systemctl start magic-box-usage-collector.service

# Add cron job for hourly collection
echo "Setting up cron jobs..."
(sudo crontab -l 2>/dev/null; echo "0 * * * * python3 $INSTALL_DIR/usage_tracker.py --collect --db $DB_PATH") | sudo crontab -

# Configure Traefik (if exists)
if command -v traefik &> /dev/null || [ -f "/etc/traefik/traefik.yml" ]; then
    echo "Configuring Traefik..."
    sudo tee -a /etc/traefik/traefik.yml > /dev/null <<EOF

http:
  routers:
    usage-metering:
      rule: "Host(\`usage.magicbox.local\`)"
      service: usage-metering

  services:
    usage-metering:
      loadBalancer:
        servers:
          - url: "http://localhost:8585"
EOF

    sudo systemctl reload traefik 2>/dev/null || true
    echo "Traefik configured: http://usage.magicbox.local"
fi

# Success message
echo ""
echo "✅ Installation complete!"
echo ""
echo "📍 Usage Dashboard:"
echo "   Local:  http://localhost:8585/dashboard.html"
if [ -f "/etc/traefik/traefik.yml" ]; then
    echo "   Traefik: http://usage.magicbox.local"
fi
echo ""
echo "🔧 API Endpoints:"
echo "   Health:      http://localhost:8585/api/health"
echo "   Usage:       http://localhost:8585/api/usage/summary"
echo "   Resources:   http://localhost:8585/api/usage/resources"
echo "   Billing:     http://localhost:8585/api/billing/report"
echo ""
echo "💾 Database: $DB_PATH"
echo ""
echo "📊 CLI Usage:"
echo "   View summary:  python3 $INSTALL_DIR/usage_tracker.py --summary"
echo "   Generate report: python3 $INSTALL_DIR/usage_tracker.py --report YYYY-MM"
echo "   Export data:    python3 $INSTALL_DIR/usage_tracker.py --export json"
echo ""
