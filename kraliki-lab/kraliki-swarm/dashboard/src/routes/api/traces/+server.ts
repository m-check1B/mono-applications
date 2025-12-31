import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

const ARENA_DIR = '/home/adminmatej/github/applications/kraliki-lab/kraliki-swarm/arena';

interface TraceQuery {
	agent_id?: string;
	decision_type?: string;
	linear_issue?: string;
	limit?: number;
}

async function getTraces(query: TraceQuery): Promise<any[]> {
	try {
		let cmd = `python3 ${ARENA_DIR}/decision_trace.py query`;
		if (query.agent_id) cmd += ` -a "${query.agent_id}"`;
		if (query.decision_type) cmd += ` -t "${query.decision_type}"`;
		if (query.linear_issue) cmd += ` -i "${query.linear_issue}"`;
		cmd += ` -l ${query.limit || 50}`;

		// Use Python to get JSON output instead of CLI
		const pythonCmd = `python3 -c "
import json
import sys
sys.path.insert(0, '${ARENA_DIR}')
from decision_trace import get_traces, get_stats
traces = get_traces(
    agent_id=${query.agent_id ? `'${query.agent_id}'` : 'None'},
    decision_type=${query.decision_type ? `'${query.decision_type}'` : 'None'},
    linear_issue=${query.linear_issue ? `'${query.linear_issue}'` : 'None'},
    limit=${query.limit || 50}
)
print(json.dumps(traces))
"`;

		const { stdout } = await execAsync(pythonCmd);
		return JSON.parse(stdout.trim());
	} catch (error) {
		console.error('Error getting traces:', error);
		return [];
	}
}

async function getStats(): Promise<any> {
	try {
		const pythonCmd = `python3 -c "
import json
import sys
sys.path.insert(0, '${ARENA_DIR}')
from decision_trace import get_stats
print(json.dumps(get_stats()))
"`;

		const { stdout } = await execAsync(pythonCmd);
		return JSON.parse(stdout.trim());
	} catch (error) {
		console.error('Error getting stats:', error);
		return {
			total_traces: 0,
			by_type: {},
			by_agent: {},
			by_outcome: {},
			by_genome: {}
		};
	}
}

export const GET: RequestHandler = async ({ url }) => {
	const agent_id = url.searchParams.get('agent_id') || undefined;
	const decision_type = url.searchParams.get('type') || undefined;
	const linear_issue = url.searchParams.get('issue') || undefined;
	const limit = parseInt(url.searchParams.get('limit') || '50');
	const statsOnly = url.searchParams.get('stats') === 'true';

	if (statsOnly) {
		const stats = await getStats();
		return json(stats);
	}

	const [traces, stats] = await Promise.all([
		getTraces({ agent_id, decision_type, linear_issue, limit }),
		getStats()
	]);

	return json({
		traces,
		stats,
		timestamp: new Date().toISOString()
	});
};
