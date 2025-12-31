#!/usr/bin/env python3
"""
CLIProxyAPI Usage Parser

Parses CLIProxyAPI logs to extract API usage metrics for billing.
Integrates with usage_metering.py to store metrics.

Usage:
    python -m parse_cliproxy_logs --log-file /var/log/cliproxy/access.log
"""

import os
import sys
import re
import json
import logging
import argparse
from datetime import datetime
from typing import Dict, Optional, Iterator
from dataclasses import dataclass

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class APIRequest:
    """Parsed API request from CLIProxyAPI log."""

    timestamp: datetime
    customer_id: str
    vm_id: str
    provider: str
    model: str
    tokens_in: int
    tokens_out: int
    cost_usd: float


class LogParser:
    """Parse CLIProxyAPI access logs."""

    COMMON_LOG_PATTERN = re.compile(
        r"(?P<ip>\S+) \S+ \S+ \[(?P<timestamp>[^\]]+)\] "
        r'"(?P<method>\S+) (?P<path>\S+) \S+" '
        r"(?P<status>\d+) (?P<size>\d+) "
        r'"(?P<referer>[^"]*)" "(?P<user_agent>[^"]*)"'
    )

    JSON_LOG_PATTERN = re.compile(r"\{.*\}")

    PROVIDER_PATTERNS = {
        "anthropic": {
            "prefix": "/v1/messages",
            "model_field": "model",
            "tokens_in": "input_tokens",
            "tokens_out": "output_tokens",
        },
        "openai": {
            "prefix": "/v1/chat/completions",
            "model_field": "model",
            "tokens_in": "prompt_tokens",
            "tokens_out": "completion_tokens",
        },
        "google": {
            "prefix": "/v1beta/models",
            "model_field": "model",
            "tokens_in": "promptTokenCount",
            "tokens_out": "candidatesTokenCount",
        },
    }

    PRICING = {
        "anthropic": {
            "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
            "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
            "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
        },
        "openai": {
            "gpt-4-turbo": {"input": 0.01, "output": 0.03},
            "gpt-4": {"input": 0.03, "output": 0.06},
            "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
        },
        "google": {
            "gemini-1.5-pro": {"input": 0.000125, "output": 0.0005},
            "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
            "gemini-1.0-pro": {"input": 0.00025, "output": 0.0005},
        },
    }

    def __init__(self, customer_id: str, vm_id: str):
        self.customer_id = customer_id
        self.vm_id = vm_id

    def parse_line(self, line: str) -> Optional[APIRequest]:
        """
        Parse a single log line.

        Args:
            line: Log line string

        Returns:
            APIRequest if line contains valid API request, None otherwise
        """
        try:
            if self.JSON_LOG_PATTERN.search(line):
                return self._parse_json_line(line)
            else:
                return self._parse_common_line(line)
        except Exception as e:
            logger.debug(f"Failed to parse line: {e}")
            return None

    def _parse_common_line(self, line: str) -> Optional[APIRequest]:
        """Parse common log format."""
        match = self.COMMON_LOG_PATTERN.match(line)
        if not match:
            return None

        groups = match.groupdict()
        path = groups.get("path", "")

        for provider, config in self.PROVIDER_PATTERNS.items():
            if path.startswith(config["prefix"]):
                return self._extract_from_path(path, provider, groups["timestamp"])

        return None

    def _parse_json_line(self, line: str) -> Optional[APIRequest]:
        """Parse JSON log format."""
        try:
            data = json.loads(line)

            timestamp_str = data.get("timestamp") or data.get("time")
            if not timestamp_str:
                return None

            timestamp = self._parse_timestamp(timestamp_str)
            path = data.get("path") or data.get("uri") or data.get("url", "")

            for provider, config in self.PROVIDER_PATTERNS.items():
                if path.startswith(config["prefix"]):
                    return self._extract_from_json(data, provider, timestamp)

            return None

        except json.JSONDecodeError:
            return None

    def _extract_from_path(
        self, path: str, provider: str, timestamp_str: str
    ) -> Optional[APIRequest]:
        """Extract API info from request path."""
        try:
            timestamp = self._parse_timestamp(timestamp_str)

            query_params = {}
            if "?" in path:
                path, query = path.split("?", 1)
                for param in query.split("&"):
                    if "=" in param:
                        key, value = param.split("=", 1)
                        query_params[key] = value

            model = query_params.get("model", "unknown")
            max_tokens = int(query_params.get("max_tokens", 0))

            return APIRequest(
                timestamp=timestamp,
                customer_id=self.customer_id,
                vm_id=self.vm_id,
                provider=provider,
                model=model,
                tokens_in=max_tokens,
                tokens_out=0,
                cost_usd=0.0,
            )

        except Exception as e:
            logger.debug(f"Failed to extract from path: {e}")
            return None

    def _extract_from_json(
        self, data: Dict, provider: str, timestamp: datetime
    ) -> Optional[APIRequest]:
        """Extract API info from JSON log data."""
        try:
            config = self.PROVIDER_PATTERNS[provider]

            model = data.get(config["model_field"], "unknown")
            tokens_in = data.get(config["tokens_in"], 0)
            tokens_out = data.get(config["tokens_out"], 0)

            cost = self._calculate_cost(provider, model, tokens_in, tokens_out)

            return APIRequest(
                timestamp=timestamp,
                customer_id=self.customer_id,
                vm_id=self.vm_id,
                provider=provider,
                model=model,
                tokens_in=tokens_in,
                tokens_out=tokens_out,
                cost_usd=cost,
            )

        except Exception as e:
            logger.debug(f"Failed to extract from JSON: {e}")
            return None

    def _calculate_cost(
        self, provider: str, model: str, tokens_in: int, tokens_out: int
    ) -> float:
        """Calculate cost based on pricing."""
        try:
            pricing = self.PRICING.get(provider, {})
            model_pricing = pricing.get(model, {})

            input_price = model_pricing.get("input", 0.0)
            output_price = model_pricing.get("output", 0.0)

            cost = (tokens_in / 1000.0) * input_price + (
                tokens_out / 1000.0
            ) * output_price

            return round(cost, 6)

        except Exception as e:
            logger.debug(f"Failed to calculate cost: {e}")
            return 0.0

    def _parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse timestamp string to datetime."""
        formats = [
            "%d/%b/%Y:%H:%M:%S %z",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%SZ",
        ]

        for fmt in formats:
            try:
                return datetime.strptime(timestamp_str, fmt)
            except ValueError:
                continue

        logger.warning(f"Could not parse timestamp: {timestamp_str}")
        return datetime.now()

    def parse_file(self, file_path: str) -> Iterator[APIRequest]:
        """
        Parse log file and yield API requests.

        Args:
            file_path: Path to log file

        Yields:
            APIRequest objects
        """
        if not os.path.exists(file_path):
            logger.error(f"Log file not found: {file_path}")
            return

        with open(file_path, "r") as f:
            for line in f:
                request = self.parse_line(line.strip())
                if request:
                    yield request


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="CLIProxyAPI Log Parser")
    parser.add_argument(
        "--log-file", required=True, help="Path to CLIProxyAPI log file"
    )
    parser.add_argument("--customer-id", required=True, help="Customer ID")
    parser.add_argument("--vm-id", required=True, help="VM ID")
    parser.add_argument(
        "--output", choices=["json", "summary"], default="summary", help="Output format"
    )
    parser.add_argument(
        "--store", action="store_true", help="Store to usage_metering database"
    )

    args = parser.parse_args()

    try:
        parser = LogParser(args.customer_id, args.vm_id)

        if args.store:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            sys.path.insert(0, script_dir)

            from usage_metering import UsageDatabase, APIUsageRecord

            db = UsageDatabase()

            for request in parser.parse_file(args.log_file):
                record = APIUsageRecord(
                    timestamp=request.timestamp,
                    customer_id=request.customer_id,
                    vm_id=request.vm_id,
                    provider=request.provider,
                    model=request.model,
                    tokens_in=request.tokens_in,
                    tokens_out=request.tokens_out,
                    cost_usd=request.cost_usd,
                )
                db.record_api_usage(record)

            logger.info(f"Stored API usage from {args.log_file}")
            db.close()

        else:
            requests = list(parser.parse_file(args.log_file))

            if args.output == "json":
                print(json.dumps([r.__dict__ for r in requests], indent=2, default=str))
            else:
                print(f"\nParsed {len(requests)} API requests from {args.log_file}")

                total_cost = sum(r.cost_usd for r in requests)
                total_tokens_in = sum(r.tokens_in for r in requests)
                total_tokens_out = sum(r.tokens_out for r in requests)

                print(f"\nTotal Cost: ${total_cost:.4f}")
                print(f"Total Tokens In: {total_tokens_in:,}")
                print(f"Total Tokens Out: {total_tokens_out:,}")

                by_provider = {}
                for req in requests:
                    if req.provider not in by_provider:
                        by_provider[req.provider] = {
                            "count": 0,
                            "cost": 0.0,
                            "tokens_in": 0,
                            "tokens_out": 0,
                        }
                    by_provider[req.provider]["count"] += 1
                    by_provider[req.provider]["cost"] += req.cost_usd
                    by_provider[req.provider]["tokens_in"] += req.tokens_in
                    by_provider[req.provider]["tokens_out"] += req.tokens_out

                print("\nBy Provider:")
                for provider, data in by_provider.items():
                    print(f"  {provider}:")
                    print(f"    Requests: {data['count']}")
                    print(f"    Cost: ${data['cost']:.4f}")
                    print(f"    Tokens: {data['tokens_in'] + data['tokens_out']:,}")

    except Exception as e:
        logger.error(f"Error: {e}")
        import sys

        sys.exit(1)


if __name__ == "__main__":
    main()
