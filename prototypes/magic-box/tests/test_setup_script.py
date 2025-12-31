#!/usr/bin/env python3
"""
Tests for Magic Box setup script.

These are static analysis tests that verify the script structure without
actually running the installer (which requires root and a fresh VM).
"""

import os
import subprocess
import unittest
from pathlib import Path


class TestSetupScript(unittest.TestCase):
    """Test the setup-complete.sh script structure and syntax."""

    @classmethod
    def setUpClass(cls):
        """Get the path to the scripts directory."""
        tests_dir = Path(__file__).parent
        cls.scripts_dir = tests_dir.parent / "scripts"
        cls.setup_script = cls.scripts_dir / "setup-complete.sh"
        cls.provision_script = cls.scripts_dir / "provision.sh"

    def test_setup_script_exists(self):
        """Verify setup-complete.sh exists."""
        self.assertTrue(self.setup_script.exists(), "setup-complete.sh not found")

    def test_provision_script_exists(self):
        """Verify provision.sh exists."""
        self.assertTrue(self.provision_script.exists(), "provision.sh not found")

    def test_setup_script_is_executable(self):
        """Verify setup-complete.sh has execute permission."""
        self.assertTrue(
            os.access(self.setup_script, os.X_OK),
            "setup-complete.sh is not executable"
        )

    def test_provision_script_is_executable(self):
        """Verify provision.sh has execute permission."""
        self.assertTrue(
            os.access(self.provision_script, os.X_OK),
            "provision.sh is not executable"
        )

    def test_setup_script_bash_syntax(self):
        """Verify setup-complete.sh has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(self.setup_script)],
            capture_output=True,
            text=True
        )
        self.assertEqual(
            result.returncode, 0,
            f"Bash syntax error: {result.stderr}"
        )

    def test_provision_script_bash_syntax(self):
        """Verify provision.sh has valid bash syntax."""
        result = subprocess.run(
            ["bash", "-n", str(self.provision_script)],
            capture_output=True,
            text=True
        )
        self.assertEqual(
            result.returncode, 0,
            f"Bash syntax error: {result.stderr}"
        )

    def test_setup_script_has_shebang(self):
        """Verify setup-complete.sh starts with proper shebang."""
        with open(self.setup_script, 'r') as f:
            first_line = f.readline()
        self.assertTrue(
            first_line.startswith("#!/"),
            "setup-complete.sh missing shebang"
        )

    def test_setup_script_uses_strict_mode(self):
        """Verify setup-complete.sh uses set -euo pipefail."""
        content = self.setup_script.read_text()
        self.assertIn(
            "set -euo pipefail",
            content,
            "setup-complete.sh should use strict mode"
        )

    def test_setup_script_has_version(self):
        """Verify setup-complete.sh has a version number."""
        content = self.setup_script.read_text()
        self.assertIn(
            "VERSION=",
            content,
            "setup-complete.sh should define VERSION"
        )

    def test_setup_script_has_usage_function(self):
        """Verify setup-complete.sh has a usage function."""
        content = self.setup_script.read_text()
        self.assertIn(
            "usage()",
            content,
            "setup-complete.sh should have usage function"
        )

    def test_setup_script_checks_root(self):
        """Verify setup-complete.sh checks for root privileges."""
        content = self.setup_script.read_text()
        self.assertIn(
            "EUID",
            content,
            "setup-complete.sh should check for root"
        )

    def test_setup_script_checks_os(self):
        """Verify setup-complete.sh checks OS version."""
        content = self.setup_script.read_text()
        self.assertIn(
            "/etc/os-release",
            content,
            "setup-complete.sh should check OS version"
        )

    def test_setup_script_installs_docker(self):
        """Verify setup-complete.sh installs Docker."""
        content = self.setup_script.read_text()
        self.assertIn(
            "docker-ce",
            content,
            "setup-complete.sh should install Docker"
        )

    def test_setup_script_creates_docker_compose(self):
        """Verify setup-complete.sh creates docker-compose.yml."""
        content = self.setup_script.read_text()
        self.assertIn(
            "docker-compose.yml",
            content,
            "setup-complete.sh should create docker-compose.yml"
        )

    def test_setup_script_binds_localhost_only(self):
        """Verify services bind to localhost only (security)."""
        content = self.setup_script.read_text()
        # Check that ports are bound to 127.0.0.1
        self.assertIn(
            "127.0.0.1:",
            content,
            "Services should bind to 127.0.0.1"
        )
        # Ensure no 0.0.0.0 bindings
        lines_with_ports = [
            line for line in content.split('\n')
            if 'ports:' in line.lower() or '- "' in line and ':' in line
        ]
        for line in lines_with_ports:
            self.assertNotIn(
                '"0.0.0.0:',
                line,
                f"Found 0.0.0.0 binding which exposes service to internet: {line}"
            )

    def test_setup_script_has_error_handling(self):
        """Verify setup-complete.sh has error handling functions."""
        content = self.setup_script.read_text()
        self.assertIn("fail()", content, "Should have fail function")
        self.assertIn("warn()", content, "Should have warn function")
        self.assertIn("log()", content, "Should have log function")

    def test_setup_script_configures_firewall(self):
        """Verify setup-complete.sh configures firewall."""
        content = self.setup_script.read_text()
        self.assertIn(
            "ufw",
            content,
            "setup-complete.sh should configure ufw firewall"
        )

    def test_setup_script_configures_fail2ban(self):
        """Verify setup-complete.sh enables fail2ban."""
        content = self.setup_script.read_text()
        self.assertIn(
            "fail2ban",
            content,
            "setup-complete.sh should configure fail2ban"
        )

    def test_setup_script_hardens_ssh(self):
        """Verify setup-complete.sh hardens SSH configuration."""
        content = self.setup_script.read_text()
        self.assertIn(
            "PasswordAuthentication",
            content,
            "setup-complete.sh should configure SSH"
        )

    def test_setup_script_creates_magic_box_cli(self):
        """Verify setup-complete.sh creates magic-box CLI."""
        content = self.setup_script.read_text()
        self.assertIn(
            "/usr/local/bin/magic-box",
            content,
            "setup-complete.sh should install magic-box CLI"
        )


class TestSetupDocs(unittest.TestCase):
    """Test that setup documentation exists and is complete."""

    @classmethod
    def setUpClass(cls):
        """Get the path to the docs directory."""
        tests_dir = Path(__file__).parent
        cls.docs_dir = tests_dir.parent / "docs"
        cls.setup_doc = cls.docs_dir / "SETUP.md"

    def test_setup_doc_exists(self):
        """Verify SETUP.md exists."""
        self.assertTrue(self.setup_doc.exists(), "docs/SETUP.md not found")

    def test_setup_doc_has_prerequisites(self):
        """Verify SETUP.md documents prerequisites."""
        content = self.setup_doc.read_text()
        self.assertIn(
            "Prerequisites",
            content,
            "SETUP.md should document prerequisites"
        )

    def test_setup_doc_has_quick_install(self):
        """Verify SETUP.md has quick install section."""
        content = self.setup_doc.read_text()
        self.assertIn(
            "Quick Install",
            content,
            "SETUP.md should have quick install section"
        )

    def test_setup_doc_has_troubleshooting(self):
        """Verify SETUP.md has troubleshooting section."""
        content = self.setup_doc.read_text()
        self.assertIn(
            "Troubleshooting",
            content,
            "SETUP.md should have troubleshooting section"
        )


if __name__ == "__main__":
    unittest.main()
