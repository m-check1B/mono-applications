import { json } from "@sveltejs/kit";
const LINEAR_API_URL = "https://api.linear.app/graphql";
const KRALIKI_ENV = (process.env.KRALIKI_ENV || "").trim().toUpperCase();
function getEnvValue(baseKey) {
  const direct = (process.env[baseKey] || "").trim();
  if (direct) {
    return direct;
  }
  if (KRALIKI_ENV) {
    const envKey = `${baseKey}_${KRALIKI_ENV}`;
    const envValue = (process.env[envKey] || "").trim();
    if (envValue) {
      return envValue;
    }
  }
  return "";
}
function getEnvSuffixFile(baseName) {
  if (!KRALIKI_ENV) {
    return null;
  }
  return `${baseName}_${KRALIKI_ENV.toLowerCase()}.txt`;
}
async function resolveLinearApiKey() {
  let apiKey = getEnvValue("LINEAR_API_KEY");
  if (apiKey) {
    return apiKey;
  }
  try {
    const fs = await import("fs/promises");
    const candidates = [
      getEnvSuffixFile("/home/adminmatej/github/secrets/linear_api_key"),
      "/home/adminmatej/github/secrets/linear_api_key.txt"
    ].filter(Boolean);
    for (const candidate of candidates) {
      try {
        apiKey = (await fs.readFile(candidate, "utf-8")).trim();
        if (apiKey) {
          return apiKey;
        }
      } catch {
      }
    }
  } catch {
  }
  return "";
}
function resolveLinearTeamKey() {
  return getEnvValue("LINEAR_TEAM_KEY") || "VD";
}
async function linearGraphql(apiKey, query, variables) {
  const response = await fetch(LINEAR_API_URL, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Authorization": apiKey
    },
    body: JSON.stringify({ query, variables })
  });
  if (!response.ok) {
    const text = await response.text();
    throw new Error(`Linear API error: ${response.status} ${text}`);
  }
  return response.json();
}
function normalizeLabelNames(labels) {
  if (!Array.isArray(labels)) {
    return [];
  }
  const cleaned = labels.filter((label) => typeof label === "string").map((label) => label.trim()).filter(Boolean);
  return Array.from(new Set(cleaned));
}
const GET = async () => {
  const apiKey = await resolveLinearApiKey();
  const teamKey = resolveLinearTeamKey();
  if (!apiKey) {
    return json({ issues: [], error: "Linear API key not configured" });
  }
  const query = `
		query {
			issues(
				filter: {
					team: { key: { eq: "${teamKey}" } }
					state: { type: { nin: ["completed", "canceled"] } }
				}
				first: 50
				orderBy: updatedAt
			) {
				nodes {
					id
					identifier
					title
					priority
					createdAt
					updatedAt
					state {
						name
						color
					}
					labels {
						nodes {
							name
						}
					}
					assignee {
						name
					}
				}
			}
		}
	`;
  try {
    const response = await fetch(LINEAR_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": apiKey
      },
      body: JSON.stringify({ query })
    });
    if (!response.ok) {
      throw new Error(`Linear API error: ${response.status}`);
    }
    const data = await response.json();
    const issues = (data.data?.issues?.nodes || []).map((issue) => ({
      ...issue,
      labels: issue.labels?.nodes || []
    }));
    return json({ issues });
  } catch (e) {
    console.error("Linear API error:", e);
    return json({ issues: [], error: "Failed to fetch from Linear" });
  }
};
const POST = async ({ request }) => {
  const body = await request.json();
  const { action, title, description, priority, labels } = body;
  if (action !== "create") {
    return json({ error: "Unknown action" }, { status: 400 });
  }
  const apiKey = await resolveLinearApiKey();
  const teamKey = resolveLinearTeamKey();
  if (!apiKey) {
    return json({ error: "Linear API key not configured" }, { status: 500 });
  }
  const teamQuery = `
		query {
			teams(filter: { key: { eq: "${teamKey}" } }) {
				nodes {
					id
				}
			}
		}
	`;
  try {
    const teamData = await linearGraphql(apiKey, teamQuery);
    const teamId = teamData.data?.teams?.nodes?.[0]?.id;
    if (!teamId) {
      return json({ error: `Team ${teamKey} not found` }, { status: 500 });
    }
    const labelNames = normalizeLabelNames(labels);
    const labelIds = [];
    if (labelNames.length > 0) {
      const labelsQuery = `
				query {
					issueLabels(first: 250) {
						nodes {
							id
							name
							team { id }
						}
					}
				}
			`;
      const labelsData = await linearGraphql(apiKey, labelsQuery);
      const availableLabels = labelsData.data?.issueLabels?.nodes ?? [];
      const missingLabels = [];
      for (const name of labelNames) {
        const match = availableLabels.find(
          (label) => label.name === name && label.team?.id === teamId
        );
        if (match?.id) {
          labelIds.push(match.id);
        } else {
          missingLabels.push(name);
        }
      }
      for (const name of missingLabels) {
        const createLabelMutation = `
					mutation CreateLabel($teamId: String!, $name: String!) {
						issueLabelCreate(input: { teamId: $teamId, name: $name, color: "#6366f1" }) {
							success
							issueLabel { id }
						}
					}
				`;
        const createData2 = await linearGraphql(apiKey, createLabelMutation, {
          teamId,
          name
        });
        const createdId = createData2.data?.issueLabelCreate?.issueLabel?.id;
        if (createdId) {
          labelIds.push(createdId);
        }
      }
    }
    const createMutation = `
			mutation CreateIssue($input: IssueCreateInput!) {
				issueCreate(input: $input) {
					success
					issue {
						id
						identifier
						title
						url
					}
					userErrors {
						message
						field
					}
				}
			}
		`;
    const input = {
      teamId,
      title,
      description: description || "",
      priority: priority || 3
    };
    if (labelIds.length > 0) {
      input.labelIds = labelIds;
    }
    const createData = await linearGraphql(apiKey, createMutation, { input });
    if (createData.errors) {
      console.error("Linear create error:", createData.errors);
      return json({ error: createData.errors[0]?.message || "Failed to create issue" }, { status: 500 });
    }
    const result = createData.data?.issueCreate;
    const userErrorMessage = result?.userErrors?.[0]?.message;
    if (userErrorMessage) {
      console.error("Linear create user error:", result?.userErrors);
      return json({ error: userErrorMessage }, { status: 500 });
    }
    if (result?.success) {
      return json({
        success: true,
        issue: result.issue
      });
    } else {
      return json({ error: "Failed to create issue" }, { status: 500 });
    }
  } catch (e) {
    console.error("Linear API error:", e);
    return json({ error: "Failed to connect to Linear" }, { status: 500 });
  }
};
export {
  GET,
  POST
};
