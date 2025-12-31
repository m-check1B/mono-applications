export interface TestCredentials {
  email: string;
  password: string;
}

const resolvePassword = (): string => {
  const password = process.env.TEST_ADMIN_PASSWORD
    || process.env.DEFAULT_ADMIN_PASSWORD
    || process.env.SEED_ADMIN_PASSWORD;

  if (!password || password.trim().length === 0) {
    throw new Error('Missing admin password for tests. Set TEST_ADMIN_PASSWORD or DEFAULT_ADMIN_PASSWORD.');
  }

  return password;
};

export const getAdminCredentials = (): TestCredentials => ({
  email: process.env.TEST_ADMIN_EMAIL || process.env.DEFAULT_ADMIN_EMAIL || 'admin@cc-light.local',
  password: resolvePassword(),
});

export const getSupervisorCredentials = (): TestCredentials => ({
  email: process.env.TEST_SUPERVISOR_EMAIL || 'supervisor@cc-light.local',
  password: process.env.TEST_SUPERVISOR_PASSWORD
    || process.env.DEFAULT_SUPERVISOR_PASSWORD
    || process.env.SEED_SUPERVISOR_PASSWORD
    || resolvePassword(),
});

export const getAgentCredentials = (): TestCredentials => ({
  email: process.env.TEST_AGENT_EMAIL || 'agent1@cc-light.local',
  password: process.env.TEST_AGENT_PASSWORD
    || process.env.DEFAULT_AGENT_PASSWORD
    || process.env.SEED_AGENT_PASSWORD
    || resolvePassword(),
});
