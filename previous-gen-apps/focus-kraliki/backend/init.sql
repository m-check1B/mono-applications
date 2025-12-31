-- Initialize database with extensions and basic setup
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Insert default user types for the TypeManager system
INSERT INTO "UserPreference" (id, "userId", "customTypes", "typeOrder", "theme", "taskView", "enableAI", "aiModel", "enableVoice", "breakInterval") 
VALUES (
  'default-preferences',
  'temp-user-id',
  '{"types": [
    {"id": "deep-work", "name": "Deep Work", "color": "#3B82F6", "icon": "Brain", "description": "Focused, uninterrupted work on complex tasks"},
    {"id": "creative", "name": "Creative", "color": "#8B5CF6", "icon": "Lightbulb", "description": "Brainstorming, design, and innovative thinking"},
    {"id": "administrative", "name": "Administrative", "color": "#10B981", "icon": "Clipboard", "description": "Organization, planning, and routine tasks"},
    {"id": "communication", "name": "Communication", "color": "#F59E0B", "icon": "MessageCircle", "description": "Meetings, emails, and coordination"},
    {"id": "learning", "name": "Learning", "color": "#EF4444", "icon": "BookOpen", "description": "Skill development and knowledge acquisition"},
    {"id": "wellness", "name": "Wellness", "color": "#06B6D4", "icon": "Heart", "description": "Health, exercise, and self-care"},
    {"id": "social", "name": "Social", "color": "#EC4899", "icon": "Users", "description": "Relationships and networking"},
    {"id": "strategic", "name": "Strategic", "color": "#6366F1", "icon": "Target", "description": "Planning and long-term thinking"}
  ]}',
  '["deep-work", "creative", "administrative", "communication", "learning", "wellness", "social", "strategic"]',
  'system',
  'list',
  true,
  'claude',
  true,
  25
) ON CONFLICT ("userId") DO NOTHING;

-- Insert sample shadow insights for demonstration
INSERT INTO "ShadowInsight" (id, "type", "severity", "title", "insight", "recommendations", "userId", "acknowledged") 
VALUES 
  (
    'sample-shadow-1',
    'avoidance',
    'moderate',
    'Procrastination Pattern',
    'You tend to delay complex tasks, preferring immediate gratification from simpler activities. This pattern suggests a fear of failure or perfectionism.',
    '["Break large tasks into smaller steps", "Set specific deadlines with accountability", "Practice self-compassion for imperfect work", "Use the 2-minute rule for quick tasks"]',
    'temp-user-id',
    false
  ),
  (
    'sample-shadow-2',
    'confrontation',
    'gentle',
    'Work-Life Boundary Issues',
    'Your work often bleeds into personal time, indicating difficulty setting boundaries or fear of missing out.',
    '["Establish clear work hours", "Create a dedicated workspace", "Schedule personal time with the same priority as work", "Practice saying no to non-essential tasks"]',
    'temp-user-id',
    false
  )
ON CONFLICT DO NOTHING;

-- Insert sample memories for the FlowMemory system
INSERT INTO "Memory" (id, "type", "content", "metadata", "priority", "sessionId", "userId") 
VALUES 
  (
    'memory-1',
    'task',
    '{"title": "Completed project proposal", "description": "Finished the Q4 strategic planning document", "outcome": "Approved by leadership", "learnings": ["Early stakeholder engagement is crucial", "Data-driven proposals get faster approval"]}',
    '{"project": "strategic-planning", "tags": ["planning", "leadership", "q4"], "importance": "high"}',
    'high',
    'session-001',
    'temp-user-id'
  ),
  (
    'memory-2',
    'decision',
    '{"decision": "Chose TypeScript over JavaScript for new project", "context": "Starting Focus by Kraliki app", "reasons": ["Type safety for complex AI features", "Better tooling support", "Easier refactoring"], "outcome": "Positive impact on development speed"}',
    '{"project": "focus-kraliki", "tags": ["typescript", "architecture", "decision"], "complexity": "medium"}',
    'high',
    'session-002',
    'temp-user-id'
  ),
  (
    'memory-3',
    'learning',
    '{"topic": "Jungian psychology integration", "insights": ["Shadow work reveals hidden motivations", "Cognitive patterns affect productivity", "Self-awareness improves task management"], "sources": ["Man and His Symbols", "Modern applications in productivity systems"]}',
    '{"area": "psychology", "tags": ["learning", "psychology", "ai"], "applicability": "high"}',
    'medium',
    'session-003',
    'temp-user-id'
  )
ON CONFLICT DO NOTHING;

-- Insert sample cognitive states
INSERT INTO "CognitiveState" (energyLevel, focusLevel, creativityLevel, stressLevel, mood, suggestedTaskType, optimalDuration, userId) 
VALUES 
  (85, 90, 75, 25, 'focused', 'deep-work', 90, 'temp-user-id'),
  (60, 70, 85, 40, 'creative', 'creative', 60, 'temp-user-id'),
  (45, 50, 60, 70, 'tired', 'wellness', 30, 'temp-user-id')
ON CONFLICT DO NOTHING;

-- Insert sample tasks
INSERT INTO "Task" (title, description, "status", priority, "aiInsights", "aiSuggestions", "urgencyScore", "complexityScore", "energyRequired", "tags", "userId") 
VALUES 
  (
    'Complete project architecture review',
    'Review and finalize the architecture document for Focus by Kraliki, ensuring all AI components are properly integrated',
    'IN_PROGRESS',
    1,
    '{"complexity_analysis": "High integration complexity between AI components", "estimated_effort": "4-6 hours", "dependencies": ["Database schema", "API design"]}',
    '["Break into smaller review sessions", "Focus on AI integration points first", "Document all architectural decisions"]',
    8.5,
    7.2,
    'high',
    '["architecture", "ai", "planning"]',
    'temp-user-id'
  ),
  (
    'Set up PostgreSQL database',
    'Configure Docker Compose with PostgreSQL and Redis for development environment',
    'COMPLETED',
    2,
    '{"complexity_analysis": "Standard setup with some configuration needed", "estimated_effort": "1-2 hours", "prerequisites": ["Docker installed"]}',
    '["Use official PostgreSQL image", "Add Redis for caching", "Include health checks"]',
    6.0,
    3.5,
    'medium',
    '["database", "setup", "docker"]',
    'temp-user-id'
  ),
  (
    'Implement authentication system',
    'Create JWT-based authentication with Stack 2025 compliance',
    'PENDING',
    1,
    '{"complexity_analysis": "Security-critical component requiring careful implementation", "estimated_effort": "2-3 days", "security_considerations": ["JWT best practices", "Session management", "Password hashing"]}',
    '["Use bcrypt for passwords", "Implement refresh tokens", "Add rate limiting", "Include proper error handling"]',
    9.2,
    8.0,
    'high',
    '["authentication", "security", "backend"]',
    'temp-user-id'
  ),
  (
    'Design shadow analysis UI',
    'Create intuitive interface for displaying Jungian psychology insights with progressive revelation',
    'PENDING',
    3,
    '{"complexity_analysis": "UX challenge requiring careful information design", "estimated_effort": "4-6 hours", "user_experience": ["Progressive disclosure", "Emotional sensitivity", "Clear visual hierarchy"]}',
    '["Use card-based layout", "Implement severity indicators", "Add acknowledgment mechanism", "Include follow-up suggestions"]',
    7.0,
    6.5,
    'medium',
    '["ui", "psychology", "design"]',
    'temp-user-id'
  )
ON CONFLICT DO NOTHING;