#!/usr/bin/env python3
"""
Lab by Kraliki Provisioning API Client

Python wrapper for automated VM provisioning via Hetzner Cloud API.
Useful for integration with n8n, webhooks, or custom automation.

Usage:
    from provision_api import MagicBoxProvisioner

    provisioner = MagicBoxProvisioner(hcloud_token="your-token")
    result = provisioner.provision(
        customer_name="acme-corp",
        ssh_key_name="admin-key",
        size="cpx31",
        location="nbg1"
    )

    print(f"VM IP: {result['ip']}")
    print(f"SSH: {result['ssh_command']}")
"""

import os
import sys
import time
import json
import base64
import logging
from dataclasses import dataclass
from typing import Optional
import urllib.request
import urllib.error

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ProvisionResult:
    """Result of a provisioning operation."""
    status: str
    vm_name: str
    vm_id: str
    ip: str
    ssh_user: str
    ssh_command: str
    size: str
    location: str
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            'status': self.status,
            'vm_name': self.vm_name,
            'vm_id': self.vm_id,
            'ip': self.ip,
            'ssh_user': self.ssh_user,
            'ssh_command': self.ssh_command,
            'size': self.size,
            'location': self.location,
            'error': self.error
        }


class HetznerAPIError(Exception):
    """Error from Hetzner Cloud API."""
    pass


class MagicBoxProvisioner:
    """
    Automated provisioner for Lab by Kraliki VMs.

    Creates and configures Hetzner Cloud VMs with the Lab by Kraliki stack.
    """

    HCLOUD_API = "https://api.hetzner.cloud/v1"
    DEFAULT_SIZE = "cpx31"
    DEFAULT_LOCATION = "nbg1"
    DEFAULT_IMAGE = "ubuntu-22.04"
    DEFAULT_ADMIN_USER = "magicbox"

    # Cloud-init template for VM initialization
    CLOUD_INIT_TEMPLATE = """#cloud-config
package_update: true
package_upgrade: true

packages:
  - ca-certificates
  - curl
  - git
  - gnupg
  - jq
  - lsb-release
  - ufw
  - fail2ban
  - htop
  - vim
  - tmux

write_files:
  - path: /opt/magic-box-init.sh
    permissions: '0755'
    content: |
      #!/bin/bash
      set -e

      # Install Docker
      install -m 0755 -d /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      chmod a+r /etc/apt/keyrings/docker.gpg

      CODENAME=$(. /etc/os-release && echo ${{VERSION_CODENAME}})
      echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu ${{CODENAME}} stable" > /etc/apt/sources.list.d/docker.list

      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
      systemctl enable docker

      # Configure firewall
      ufw default deny incoming
      ufw default allow outgoing
      ufw allow OpenSSH
      ufw --force enable

      # Enable fail2ban
      systemctl enable fail2ban
      systemctl start fail2ban

      # Harden SSH
      sed -i 's/^#\\?PasswordAuthentication .*/PasswordAuthentication no/' /etc/ssh/sshd_config
      sed -i 's/^#\\?PermitRootLogin .*/PermitRootLogin prohibit-password/' /etc/ssh/sshd_config
      systemctl reload ssh

      touch /var/lib/cloud/instance/magic-box-init-done

runcmd:
  - /opt/magic-box-init.sh
"""

    def __init__(self, hcloud_token: Optional[str] = None):
        """
        Initialize the provisioner.

        Args:
            hcloud_token: Hetzner Cloud API token. Falls back to HCLOUD_TOKEN env var.
        """
        self.token = hcloud_token or os.environ.get('HCLOUD_TOKEN')
        if not self.token:
            raise ValueError("Hetzner Cloud token required. Set HCLOUD_TOKEN or pass hcloud_token.")

    def _api_request(self, method: str, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make a request to the Hetzner Cloud API."""
        url = f"{self.HCLOUD_API}{endpoint}"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        body = json.dumps(data).encode('utf-8') if data else None

        req = urllib.request.Request(url, data=body, headers=headers, method=method)

        try:
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            try:
                error_data = json.loads(error_body)
                msg = error_data.get('error', {}).get('message', str(e))
            except json.JSONDecodeError:
                msg = str(e)
            raise HetznerAPIError(f"API error: {msg}")
        except urllib.error.URLError as e:
            raise HetznerAPIError(f"Network error: {e}")

    def get_ssh_key_id(self, key_name: str) -> Optional[str]:
        """Get SSH key ID by name."""
        response = self._api_request('GET', f'/ssh_keys?name={key_name}')
        keys = response.get('ssh_keys', [])
        return str(keys[0]['id']) if keys else None

    def check_vm_exists(self, vm_name: str) -> bool:
        """Check if a VM with the given name exists."""
        response = self._api_request('GET', f'/servers?name={vm_name}')
        return len(response.get('servers', [])) > 0

    def create_vm(
        self,
        name: str,
        ssh_key_id: str,
        size: str = DEFAULT_SIZE,
        location: str = DEFAULT_LOCATION,
        image: str = DEFAULT_IMAGE,
        labels: Optional[dict] = None
    ) -> dict:
        """Create a new VM."""
        payload = {
            'name': name,
            'server_type': size,
            'location': location,
            'image': image,
            'ssh_keys': [int(ssh_key_id)],
            'user_data': self.CLOUD_INIT_TEMPLATE,
            'labels': labels or {},
            'start_after_create': True
        }

        return self._api_request('POST', '/servers', payload)

    def get_server_status(self, server_id: str) -> str:
        """Get server status."""
        response = self._api_request('GET', f'/servers/{server_id}')
        return response.get('server', {}).get('status', 'unknown')

    def wait_for_running(self, server_id: str, timeout: int = 300) -> bool:
        """Wait for server to be in running state."""
        start = time.time()
        while time.time() - start < timeout:
            status = self.get_server_status(server_id)
            if status == 'running':
                return True
            logger.debug(f"Server status: {status}")
            time.sleep(5)
        return False

    def provision(
        self,
        customer_name: str,
        ssh_key_name: str,
        size: str = DEFAULT_SIZE,
        location: str = DEFAULT_LOCATION,
        admin_user: str = DEFAULT_ADMIN_USER,
        wait_for_ready: bool = True,
        timeout: int = 600
    ) -> ProvisionResult:
        """
        Provision a complete Lab by Kraliki environment.

        Args:
            customer_name: Customer identifier (used in VM naming)
            ssh_key_name: Name of SSH key registered in Hetzner Cloud
            size: VM size (cpx11, cpx21, cpx31, cpx41, cpx51)
            location: Datacenter location (nbg1, fsn1, hel1, ash, hil)
            admin_user: Admin username to create
            wait_for_ready: Wait for VM to be fully initialized
            timeout: Maximum wait time in seconds

        Returns:
            ProvisionResult with VM details and connection info
        """
        vm_name = f"magicbox-{customer_name}"

        logger.info(f"Starting provisioning for {customer_name}")

        # Check if VM exists
        if self.check_vm_exists(vm_name):
            return ProvisionResult(
                status='error',
                vm_name=vm_name,
                vm_id='',
                ip='',
                ssh_user=admin_user,
                ssh_command='',
                size=size,
                location=location,
                error=f"VM '{vm_name}' already exists"
            )

        # Get SSH key ID
        ssh_key_id = self.get_ssh_key_id(ssh_key_name)
        if not ssh_key_id:
            return ProvisionResult(
                status='error',
                vm_name=vm_name,
                vm_id='',
                ip='',
                ssh_user=admin_user,
                ssh_command='',
                size=size,
                location=location,
                error=f"SSH key '{ssh_key_name}' not found"
            )

        logger.info(f"Creating VM: {vm_name}")

        # Create VM
        labels = {
            'product': 'magic-box',
            'customer': customer_name,
            'managed': 'auto-provision'
        }

        try:
            response = self.create_vm(
                name=vm_name,
                ssh_key_id=ssh_key_id,
                size=size,
                location=location,
                labels=labels
            )
        except HetznerAPIError as e:
            return ProvisionResult(
                status='error',
                vm_name=vm_name,
                vm_id='',
                ip='',
                ssh_user=admin_user,
                ssh_command='',
                size=size,
                location=location,
                error=str(e)
            )

        server = response.get('server', {})
        server_id = str(server.get('id', ''))
        ip = server.get('public_net', {}).get('ipv4', {}).get('ip', '')

        logger.info(f"VM created: ID={server_id}, IP={ip}")

        # Wait for VM to be running
        if wait_for_ready:
            logger.info("Waiting for VM to be running...")
            if not self.wait_for_running(server_id, timeout=timeout):
                logger.warning("VM did not reach running state within timeout")

        return ProvisionResult(
            status='success',
            vm_name=vm_name,
            vm_id=server_id,
            ip=ip,
            ssh_user=admin_user,
            ssh_command=f"ssh {admin_user}@{ip}",
            size=size,
            location=location
        )


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='Lab by Kraliki Provisioning API')
    parser.add_argument('--customer', required=True, help='Customer name')
    parser.add_argument('--ssh-key', required=True, help='SSH key name in Hetzner')
    parser.add_argument('--size', default='cpx31', help='VM size')
    parser.add_argument('--location', default='nbg1', help='Datacenter location')
    parser.add_argument('--output', choices=['json', 'text'], default='text', help='Output format')

    args = parser.parse_args()

    try:
        provisioner = MagicBoxProvisioner()
        result = provisioner.provision(
            customer_name=args.customer,
            ssh_key_name=args.ssh_key,
            size=args.size,
            location=args.location
        )

        if args.output == 'json':
            print(json.dumps(result.to_dict(), indent=2))
        else:
            if result.status == 'success':
                print(f"\nProvisioning complete!")
                print(f"  VM Name: {result.vm_name}")
                print(f"  IP: {result.ip}")
                print(f"  SSH: {result.ssh_command}")
            else:
                print(f"\nProvisioning failed: {result.error}")
                sys.exit(1)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
