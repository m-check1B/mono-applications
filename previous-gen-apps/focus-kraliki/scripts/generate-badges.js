#!/usr/bin/env node

/**
 * Generate status badges for README
 */

const fs = require('fs');
const path = require('path');

const repository = process.env.GITHUB_REPOSITORY || 'focus-kraliki';
const baseUrl = `https://github.com/${repository}`;

const badges = [
  {
    name: 'CI/CD Pipeline',
    shield: `![CI/CD Pipeline](${baseUrl}/actions/workflows/ci.yml/badge.svg)`,
    link: `${baseUrl}/actions/workflows/ci.yml`
  },
  {
    name: 'Deployment',
    shield: `![Deployment](${baseUrl}/actions/workflows/deploy.yml/badge.svg)`,
    link: `${baseUrl}/actions/workflows/deploy.yml`
  },
  {
    name: 'Performance Tests',
    shield: `![Performance](${baseUrl}/actions/workflows/performance.yml/badge.svg)`,
    link: `${baseUrl}/actions/workflows/performance.yml`
  },
  {
    name: 'Playwright Tests',
    shield: `![E2E Tests](${baseUrl}/actions/workflows/playwright-tests.yml/badge.svg)`,
    link: `${baseUrl}/actions/workflows/playwright-tests.yml`
  },
  {
    name: 'Codecov',
    shield: `![codecov](https://codecov.io/gh/${repository}/branch/main/graph/badge.svg)`,
    link: `https://codecov.io/gh/${repository}`
  },
  {
    name: 'License',
    shield: `![License](https://img.shields.io/badge/license-MIT-blue.svg)`,
    link: `${baseUrl}/blob/main/LICENSE`
  },
  {
    name: 'Node Version',
    shield: `![Node.js Version](https://img.shields.io/badge/node-%3E%3D18.0.0-brightgreen)`,
    link: 'https://nodejs.org/'
  },
  {
    name: 'Package Manager',
    shield: `![Package Manager](https://img.shields.io/badge/package%20manager-pnpm-orange)`,
    link: 'https://pnpm.io/'
  }
];

function generateBadgeSection() {
  let content = '## Status Badges\n\n';

  badges.forEach(badge => {
    content += `[![${badge.name}](${badge.shield.replace('![', '').replace('](', ' "').replace(')', '")')})](${badge.link})\n`;
  });

  content += '\n';
  return content;
}

function updateReadme() {
  const readmePath = path.join(process.cwd(), 'README.md');

  if (!fs.existsSync(readmePath)) {
    console.log('Creating new README.md with badges...');

    const newReadme = `# Focus by Kraliki

${generateBadgeSection()}

Focus by Kraliki is a revolutionary AI-first productivity system that combines cutting-edge AI technology with intuitive design.

## Features

- ✨ **Revolutionary UI/UX**: "Simply in, simply out" philosophy
- 🧠 **High Reasoning Integration**: GPT-5 + Claude collaborative intelligence
- 🎭 **Shadow Analysis System**: Jungian psychology for productivity insights
- 💾 **Flow Memory System**: Persistent context across sessions
- 🎯 **Natural Language Orchestration**: Convert thoughts to structured workflows
- 🎨 **Type Manager**: Customizable types with drag-and-drop for personal mental models
- 🎤 **Voice Processing**: Natural speech to task conversion

## Tech Stack

- **Frontend**: Vite + React + TypeScript + TailwindCSS
- **Backend**: Fastify + tRPC + Prisma + PostgreSQL
- **AI**: Claude 3.5 + GPT-4 + Deepgram
- **DevOps**: Docker + GitHub Actions + PM2

## Development

\`\`\`bash
# Install dependencies
pnpm install

# Start development servers
pnpm dev:backend  # Backend on port 3017
pnpm dev:frontend # Frontend on port 5175
\`\`\`

## Testing

\`\`\`bash
# Run all tests
pnpm test

# Run specific test suites
pnpm test:unit
pnpm test:integration
pnpm test:e2e
\`\`\`

## Deployment

\`\`\`bash
# Build for production
pnpm build

# Deploy with Docker
docker-compose up -d
\`\`\`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT License - see [LICENSE](LICENSE) file for details.
`;

    fs.writeFileSync(readmePath, newReadme);
    console.log('✅ Created README.md with status badges');
  } else {
    let content = fs.readFileSync(readmePath, 'utf8');

    // Check if badges section already exists
    if (content.includes('## Status Badges')) {
      // Replace existing badges section
      content = content.replace(
        /## Status Badges[\s\S]*?(?=\n## |$)/,
        generateBadgeSection()
      );
    } else {
      // Add badges section after the title
      const lines = content.split('\n');
      const titleIndex = lines.findIndex(line => line.startsWith('# '));

      if (titleIndex !== -1) {
        lines.splice(titleIndex + 1, 0, '', generateBadgeSection().trim());
        content = lines.join('\n');
      }
    }

    fs.writeFileSync(readmePath, content);
    console.log('✅ Updated README.md with status badges');
  }
}

// Run if called directly
if (require.main === module) {
  updateReadme();
}

module.exports = { generateBadgeSection, updateReadme };