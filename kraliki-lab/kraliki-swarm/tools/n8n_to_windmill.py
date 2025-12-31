#!/usr/bin/env python3
"""
n8n to Windmill Workflow Converter
==================================
Converts n8n workflow JSON exports to Windmill scripts/flows.

For clients migrating from n8n to Windmill.

Usage:
    python3 n8n_to_windmill.py input.json output/
    python3 n8n_to_windmill.py --help

Supports:
    - HTTP Request nodes → Python/TypeScript scripts
    - Code nodes → Direct script conversion
    - Webhook triggers → Windmill webhook triggers
    - Schedule triggers → Windmill schedules
    - Basic flow structure
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional


def convert_http_node(node: Dict[str, Any]) -> str:
    """Convert n8n HTTP Request node to Windmill Python script."""
    params = node.get('parameters', {})
    method = params.get('method', 'GET')
    url = params.get('url', '')

    script = f'''"""
Converted from n8n HTTP Request node: {node.get('name', 'http_request')}
"""
import requests

def main(
    url: str = "{url}",
    method: str = "{method}",
    headers: dict = {{}},
    body: dict = None
) -> dict:
    """
    Make HTTP request.

    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE)
        headers: Request headers
        body: Request body (for POST/PUT)

    Returns:
        Response data
    """
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=body
    )
    return {{
        "status": response.status_code,
        "data": response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
    }}
'''
    return script


def convert_code_node(node: Dict[str, Any]) -> str:
    """Convert n8n Code/Function node to Windmill script."""
    params = node.get('parameters', {})
    code = params.get('jsCode', params.get('functionCode', '// No code found'))

    script = f'''"""
Converted from n8n Code node: {node.get('name', 'code')}

Original JavaScript:
{code}
"""

def main(items: list = []) -> list:
    """
    Process items.

    Note: This is a placeholder. The original JavaScript code needs manual conversion.

    Args:
        items: Input items from previous node

    Returns:
        Processed items
    """
    # TODO: Convert JavaScript logic to Python
    # Original code is preserved in docstring above

    return items
'''
    return script


def convert_webhook_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """Convert n8n Webhook trigger to Windmill webhook config."""
    params = node.get('parameters', {})

    return {
        "type": "webhook",
        "path": params.get('path', '/webhook'),
        "method": params.get('httpMethod', 'POST'),
        "description": f"Converted from n8n webhook: {node.get('name', 'webhook')}"
    }


def convert_schedule_node(node: Dict[str, Any]) -> Dict[str, Any]:
    """Convert n8n Schedule trigger to Windmill schedule config."""
    params = node.get('parameters', {})

    # n8n uses cron-like expressions
    cron = params.get('rule', {}).get('interval', [{}])[0]

    return {
        "type": "schedule",
        "cron": "0 * * * *",  # Default hourly, needs manual adjustment
        "description": f"Converted from n8n schedule: {node.get('name', 'schedule')}",
        "note": "Cron expression may need adjustment from n8n format"
    }


def convert_workflow(n8n_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert complete n8n workflow to Windmill structure."""
    workflow_name = n8n_data.get('name', 'converted_workflow')
    nodes = n8n_data.get('nodes', [])

    result = {
        "name": workflow_name,
        "converted_at": datetime.now().isoformat(),
        "source": "n8n",
        "scripts": [],
        "triggers": [],
        "flow": {
            "summary": f"Converted from n8n: {workflow_name}",
            "description": f"Auto-converted workflow. Manual review recommended.",
            "steps": []
        }
    }

    for node in nodes:
        node_type = node.get('type', '')
        node_name = node.get('name', 'unnamed')

        if 'httpRequest' in node_type.lower():
            script = convert_http_node(node)
            result["scripts"].append({
                "name": f"{node_name}.py",
                "content": script,
                "type": "python"
            })
            result["flow"]["steps"].append({
                "name": node_name,
                "type": "script",
                "script": f"{node_name}.py"
            })

        elif 'code' in node_type.lower() or 'function' in node_type.lower():
            script = convert_code_node(node)
            result["scripts"].append({
                "name": f"{node_name}.py",
                "content": script,
                "type": "python"
            })
            result["flow"]["steps"].append({
                "name": node_name,
                "type": "script",
                "script": f"{node_name}.py"
            })

        elif 'webhook' in node_type.lower():
            trigger = convert_webhook_node(node)
            result["triggers"].append(trigger)

        elif 'schedule' in node_type.lower() or 'cron' in node_type.lower():
            trigger = convert_schedule_node(node)
            result["triggers"].append(trigger)

        else:
            # Unsupported node type - add as TODO
            result["flow"]["steps"].append({
                "name": node_name,
                "type": "manual",
                "note": f"Unsupported n8n node type: {node_type}. Manual conversion required."
            })

    return result


def write_output(result: Dict[str, Any], output_dir: Path):
    """Write converted workflow to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write main flow definition
    flow_file = output_dir / "flow.json"
    with open(flow_file, 'w') as f:
        json.dump(result["flow"], f, indent=2)
    print(f"Created: {flow_file}")

    # Write trigger configs
    if result["triggers"]:
        triggers_file = output_dir / "triggers.json"
        with open(triggers_file, 'w') as f:
            json.dump(result["triggers"], f, indent=2)
        print(f"Created: {triggers_file}")

    # Write individual scripts
    scripts_dir = output_dir / "scripts"
    scripts_dir.mkdir(exist_ok=True)

    for script in result["scripts"]:
        script_file = scripts_dir / script["name"]
        with open(script_file, 'w') as f:
            f.write(script["content"])
        print(f"Created: {script_file}")

    # Write summary
    summary_file = output_dir / "CONVERSION_SUMMARY.md"
    with open(summary_file, 'w') as f:
        f.write(f"# n8n to Windmill Conversion\n\n")
        f.write(f"**Workflow:** {result['name']}\n")
        f.write(f"**Converted:** {result['converted_at']}\n\n")
        f.write(f"## Scripts ({len(result['scripts'])})\n\n")
        for s in result["scripts"]:
            f.write(f"- `{s['name']}` ({s['type']})\n")
        f.write(f"\n## Triggers ({len(result['triggers'])})\n\n")
        for t in result["triggers"]:
            f.write(f"- {t['type']}: {t.get('description', '')}\n")
        f.write(f"\n## Manual Review Required\n\n")
        f.write("- [ ] Verify script logic (especially JavaScript → Python conversions)\n")
        f.write("- [ ] Check cron expressions for schedules\n")
        f.write("- [ ] Test webhook paths\n")
        f.write("- [ ] Review unsupported node conversions\n")
    print(f"Created: {summary_file}")


def main():
    if len(sys.argv) < 3 or '--help' in sys.argv:
        print(__doc__)
        print("\nUsage: python3 n8n_to_windmill.py <input.json> <output_dir>")
        sys.exit(0 if '--help' in sys.argv else 1)

    input_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])

    if not input_file.exists():
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    print(f"Converting: {input_file}")

    with open(input_file) as f:
        n8n_data = json.load(f)

    result = convert_workflow(n8n_data)
    write_output(result, output_dir)

    print(f"\nConversion complete! Output: {output_dir}")
    print("Review CONVERSION_SUMMARY.md for next steps.")


if __name__ == "__main__":
    main()
