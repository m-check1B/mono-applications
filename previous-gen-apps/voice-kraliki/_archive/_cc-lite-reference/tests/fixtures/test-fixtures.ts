import { PrismaClient, UserRole, CallStatus, CallDirection, TelephonyProvider, CampaignType, ContactStatus } from '@prisma/client';
import bcrypt from 'bcrypt';

/**
 * Comprehensive test fixtures for Voice by Kraliki application
 * Provides reusable test data for consistent testing across all test suites
 */

export interface TestFixtures {
  organizations: any[];
  users: any[];
  campaigns: any[];
  calls: any[];
  contacts: any[];
  transcripts: any[];
  recordings: any[];
}

export class TestFixtureManager {
  private prisma: PrismaClient;
  private fixtures: TestFixtures;

  constructor(prisma: PrismaClient) {
    this.prisma = prisma;
    this.fixtures = {
      organizations: [],
      users: [],
      campaigns: [],
      calls: [],
      contacts: [],
      transcripts: [],
      recordings: [],
    };
  }

  /**
   * Load all test fixtures into the database
   */
  async loadFixtures(): Promise<TestFixtures> {
    await this.createOrganizations();
    await this.createUsers();
    await this.createCampaigns();
    await this.createCalls();
    await this.createContacts();
    await this.createTranscripts();
    await this.createRecordings();

    return this.fixtures;
  }

  /**
   * Clean up all test fixtures from the database
   */
  async cleanupFixtures(): Promise<void> {
    // Delete in reverse dependency order
    await this.prisma.callTranscript.deleteMany({
      where: {
        callId: { in: this.fixtures.calls.map(c => c.id) },
      },
    });

    await this.prisma.call.deleteMany({
      where: {
        organizationId: { in: this.fixtures.organizations.map(o => o.id) },
      },
    });

    await this.prisma.contact.deleteMany({
      where: {
        campaignId: { in: this.fixtures.campaigns.map(c => c.id) },
      },
    });

    await this.prisma.campaign.deleteMany({
      where: {
        organizationId: { in: this.fixtures.organizations.map(o => o.id) },
      },
    });

    await this.prisma.userSession.deleteMany({
      where: {
        userId: { in: this.fixtures.users.map(u => u.id) },
      },
    });

    await this.prisma.user.deleteMany({
      where: {
        organizationId: { in: this.fixtures.organizations.map(o => o.id) },
      },
    });

    await this.prisma.organization.deleteMany({
      where: {
        id: { in: this.fixtures.organizations.map(o => o.id) },
      },
    });

    // Reset fixtures
    this.fixtures = {
      organizations: [],
      users: [],
      campaigns: [],
      calls: [],
      contacts: [],
      transcripts: [],
      recordings: [],
    };
  }

  private async createOrganizations(): Promise<void> {
    const organizations = [
      {
        id: 'org-small-business',
        name: 'Small Business Corp',
        domain: 'smallbiz.local',
        settings: {
          language: 'en',
          timezone: 'America/New_York',
          features: {
            ai_transcription: true,
            sentiment_analysis: false,
            call_recording: true,
          },
        },
      },
      {
        id: 'org-enterprise',
        name: 'Enterprise Solutions Inc',
        domain: 'enterprise.local',
        settings: {
          language: 'en',
          timezone: 'America/Los_Angeles',
          features: {
            ai_transcription: true,
            sentiment_analysis: true,
            call_recording: true,
            advanced_analytics: true,
          },
        },
      },
      {
        id: 'org-international',
        name: 'Global Communications Ltd',
        domain: 'global.local',
        settings: {
          language: 'en',
          timezone: 'Europe/London',
          features: {
            ai_transcription: true,
            sentiment_analysis: true,
            call_recording: true,
            multi_language: true,
          },
        },
      },
    ];

    for (const orgData of organizations) {
      const org = await this.prisma.organization.create({ data: orgData });
      this.fixtures.organizations.push(org);
    }
  }

  private async createUsers(): Promise<void> {
    const passwordHash = await bcrypt.hash('TestPassword123!', 10);

    const users = [
      // Small Business Corp users
      {
        email: 'admin@smallbiz.local',
        username: 'admin_smallbiz',
        firstName: 'Alice',
        lastName: 'Administrator',
        passwordHash,
        role: UserRole.ADMIN,
        status: 'ACTIVE',
        organizationId: 'org-small-business',
        skills: ['customer_service', 'billing'],
        preferences: {
          language: 'en',
          timezone: 'America/New_York',
          notifications: true,
        },
      },
      {
        email: 'supervisor@smallbiz.local',
        username: 'supervisor_smallbiz',
        firstName: 'Bob',
        lastName: 'Supervisor',
        passwordHash,
        role: UserRole.SUPERVISOR,
        status: 'ACTIVE',
        organizationId: 'org-small-business',
        skills: ['team_management', 'quality_assurance'],
        preferences: {
          language: 'en',
          timezone: 'America/New_York',
          notifications: true,
        },
      },
      {
        email: 'agent1@smallbiz.local',
        username: 'agent1_smallbiz',
        firstName: 'Charlie',
        lastName: 'Agent',
        passwordHash,
        role: UserRole.AGENT,
        status: 'ACTIVE',
        organizationId: 'org-small-business',
        skills: ['sales', 'customer_service'],
        preferences: {
          language: 'en',
          timezone: 'America/New_York',
          notifications: true,
        },
      },
      {
        email: 'agent2@smallbiz.local',
        username: 'agent2_smallbiz',
        firstName: 'Diana',
        lastName: 'Agent',
        passwordHash,
        role: UserRole.AGENT,
        status: 'ACTIVE',
        organizationId: 'org-small-business',
        skills: ['technical_support', 'troubleshooting'],
        preferences: {
          language: 'en',
          timezone: 'America/New_York',
          notifications: false,
        },
      },

      // Enterprise users
      {
        email: 'admin@enterprise.local',
        username: 'admin_enterprise',
        firstName: 'Edward',
        lastName: 'Administrator',
        passwordHash,
        role: UserRole.ADMIN,
        status: 'ACTIVE',
        organizationId: 'org-enterprise',
        skills: ['system_administration', 'analytics'],
        preferences: {
          language: 'en',
          timezone: 'America/Los_Angeles',
          notifications: true,
        },
      },
      {
        email: 'supervisor1@enterprise.local',
        username: 'supervisor1_enterprise',
        firstName: 'Fiona',
        lastName: 'Supervisor',
        passwordHash,
        role: UserRole.SUPERVISOR,
        status: 'ACTIVE',
        organizationId: 'org-enterprise',
        skills: ['team_management', 'training'],
        preferences: {
          language: 'en',
          timezone: 'America/Los_Angeles',
          notifications: true,
        },
      },
      {
        email: 'supervisor2@enterprise.local',
        username: 'supervisor2_enterprise',
        firstName: 'George',
        lastName: 'Supervisor',
        passwordHash,
        role: UserRole.SUPERVISOR,
        status: 'ACTIVE',
        organizationId: 'org-enterprise',
        skills: ['quality_assurance', 'performance_management'],
        preferences: {
          language: 'en',
          timezone: 'America/Los_Angeles',
          notifications: true,
        },
      },

      // International users
      {
        email: 'admin@global.local',
        username: 'admin_global',
        firstName: 'Henry',
        lastName: 'Administrator',
        passwordHash,
        role: UserRole.ADMIN,
        status: 'ACTIVE',
        organizationId: 'org-international',
        skills: ['global_operations', 'compliance'],
        preferences: {
          language: 'en',
          timezone: 'Europe/London',
          notifications: true,
        },
      },
    ];

    for (const userData of users) {
      const user = await this.prisma.user.create({ data: userData });
      this.fixtures.users.push(user);
    }
  }

  private async createCampaigns(): Promise<void> {
    const campaigns = [
      {
        name: 'Customer Satisfaction Survey',
        description: 'Post-purchase satisfaction survey campaign',
        type: CampaignType.OUTBOUND,
        organizationId: 'org-small-business',
        active: true,
        language: 'en',
        instructions: {
          script: 'Hello, we recently served you and would like to get your feedback on your experience.',
          settings: {
            maxConcurrentCalls: 3,
            maxAttemptsPerContact: 2,
            timeBetweenAttempts: 60,
            dialingHours: {
              start: '09:00',
              end: '17:00',
              timezone: 'America/New_York',
            },
          },
        },
        tools: {
          survey: {
            questions: [
              'How satisfied were you with our service?',
              'Would you recommend us to others?',
            ],
          },
        },
        voice: null,
        analytics: {
          targetCompletionRate: 0.7,
          expectedDuration: 180,
        },
      },
      {
        name: 'Sales Outreach - Q4',
        description: 'Q4 sales outreach to prospects',
        type: CampaignType.OUTBOUND,
        organizationId: 'org-enterprise',
        active: true,
        language: 'en',
        instructions: {
          script: 'Hi, I am calling from Enterprise Solutions to discuss how we can help your business grow.',
          settings: {
            maxConcurrentCalls: 10,
            maxAttemptsPerContact: 3,
            timeBetweenAttempts: 120,
            dialingHours: {
              start: '08:00',
              end: '18:00',
              timezone: 'America/Los_Angeles',
            },
          },
        },
        tools: {
          crm: {
            enabled: true,
            updateOnContact: true,
          },
          scheduler: {
            enabled: true,
            availableSlots: ['morning', 'afternoon'],
          },
        },
        voice: null,
        analytics: {
          targetCompletionRate: 0.15,
          expectedDuration: 300,
        },
      },
      {
        name: 'Technical Support Inbound',
        description: 'Inbound technical support campaign',
        type: CampaignType.INBOUND,
        organizationId: 'org-international',
        active: true,
        language: 'en',
        instructions: {
          script: 'Thank you for calling Global Communications technical support. How can I help you today?',
          settings: {
            maxConcurrentCalls: 20,
            queueTimeout: 300,
            priorityRouting: true,
          },
        },
        tools: {
          ticketing: {
            enabled: true,
            autoCreate: true,
          },
          knowledgeBase: {
            enabled: true,
            searchEnabled: true,
          },
        },
        voice: null,
        analytics: {
          targetResolutionRate: 0.8,
          expectedDuration: 420,
        },
      },
    ];

    for (const campaignData of campaigns) {
      const campaign = await this.prisma.campaign.create({ data: campaignData });
      this.fixtures.campaigns.push(campaign);
    }
  }

  private async createCalls(): Promise<void> {
    const now = new Date();
    const oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
    const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);

    // Get users for assignment
    const smallBizAgents = this.fixtures.users.filter(
      u => u.organizationId === 'org-small-business' && u.role === UserRole.AGENT
    );
    const enterpriseUsers = this.fixtures.users.filter(
      u => u.organizationId === 'org-enterprise'
    );

    const calls = [
      // Recent completed calls
      {
        fromNumber: '+15551234567',
        toNumber: '+15559876543',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'org-small-business',
        agentId: smallBizAgents[0]?.id,
        campaignId: this.fixtures.campaigns[0]?.id,
        status: CallStatus.COMPLETED,
        startTime: oneHourAgo,
        endTime: new Date(oneHourAgo.getTime() + 5 * 60 * 1000), // 5 minutes later
        duration: 300,
        disposition: 'resolved',
        notes: 'Customer inquiry about billing resolved successfully',
        recordingUrl: 'https://recordings.example.com/call1.mp3',
        providerCallId: 'twilio-call-123',
        metadata: {
          customerSatisfaction: 5,
          category: 'billing',
          priority: 'normal',
        },
      },
      {
        fromNumber: '+15551234568',
        toNumber: '+15559876543',
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'org-small-business',
        agentId: smallBizAgents[1]?.id,
        campaignId: this.fixtures.campaigns[0]?.id,
        status: CallStatus.COMPLETED,
        startTime: new Date(oneHourAgo.getTime() - 30 * 60 * 1000),
        endTime: new Date(oneHourAgo.getTime() - 27 * 60 * 1000),
        duration: 180,
        disposition: 'completed_survey',
        notes: 'Customer completed satisfaction survey',
        recordingUrl: 'https://recordings.example.com/call2.mp3',
        providerCallId: 'twilio-call-124',
        metadata: {
          surveyResponse: {
            satisfaction: 4,
            recommendation: true,
          },
          category: 'survey',
        },
      },

      // Active calls
      {
        fromNumber: '+15551234569',
        toNumber: '+15559876543',
        direction: CallDirection.INBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'org-enterprise',
        agentId: enterpriseUsers.find(u => u.role === UserRole.AGENT)?.id,
        status: CallStatus.IN_PROGRESS,
        startTime: new Date(now.getTime() - 10 * 60 * 1000), // 10 minutes ago
        endTime: null,
        duration: null,
        disposition: null,
        notes: null,
        recordingUrl: null,
        providerCallId: 'twilio-call-125',
        metadata: {
          category: 'technical_support',
          priority: 'high',
        },
      },

      // Historical calls for analytics
      {
        fromNumber: '+15551234570',
        toNumber: '+15559876543',
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'org-enterprise',
        agentId: enterpriseUsers.find(u => u.role === UserRole.AGENT)?.id,
        campaignId: this.fixtures.campaigns[1]?.id,
        status: CallStatus.NO_ANSWER,
        startTime: oneDayAgo,
        endTime: new Date(oneDayAgo.getTime() + 30 * 1000),
        duration: 0,
        disposition: 'no_answer',
        notes: 'No answer, will retry later',
        recordingUrl: null,
        providerCallId: 'twilio-call-126',
        metadata: {
          category: 'sales',
          attemptNumber: 1,
        },
      },

      // Failed call
      {
        fromNumber: '+15551234571',
        toNumber: '+15559876543',
        direction: CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: 'org-international',
        status: CallStatus.FAILED,
        startTime: oneDayAgo,
        endTime: new Date(oneDayAgo.getTime() + 10 * 1000),
        duration: 0,
        disposition: 'number_invalid',
        notes: 'Invalid phone number',
        recordingUrl: null,
        providerCallId: 'twilio-call-127',
        metadata: {
          errorCode: 'INVALID_NUMBER',
          category: 'support',
        },
      },
    ];

    for (const callData of calls) {
      const call = await this.prisma.call.create({ data: callData });
      this.fixtures.calls.push(call);
    }
  }

  private async createContacts(): Promise<void> {
    const contacts = [
      // Small business campaign contacts
      {
        phoneNumber: '+15551111111',
        name: 'John Smith',
        email: 'john.smith@customer.com',
        campaignId: this.fixtures.campaigns[0]?.id,
        status: ContactStatus.COMPLETED,
        attempts: 1,
        lastAttempt: new Date(),
        outcome: 'survey_completed',
        notes: 'Very satisfied customer',
        metadata: {
          customerType: 'existing',
          purchaseDate: '2023-11-15',
          orderValue: 299.99,
        },
      },
      {
        phoneNumber: '+15552222222',
        name: 'Jane Doe',
        email: 'jane.doe@customer.com',
        campaignId: this.fixtures.campaigns[0]?.id,
        status: ContactStatus.PENDING,
        attempts: 0,
        lastAttempt: null,
        outcome: null,
        notes: null,
        metadata: {
          customerType: 'new',
          purchaseDate: '2023-12-01',
          orderValue: 149.99,
        },
      },

      // Enterprise campaign contacts
      {
        phoneNumber: '+15553333333',
        name: 'ABC Corporation',
        email: 'contact@abccorp.com',
        campaignId: this.fixtures.campaigns[1]?.id,
        status: ContactStatus.PENDING,
        attempts: 1,
        lastAttempt: new Date(Date.now() - 24 * 60 * 60 * 1000),
        nextAttempt: new Date(Date.now() + 2 * 60 * 60 * 1000),
        outcome: 'no_answer',
        notes: 'No answer on first attempt, try again later',
        metadata: {
          company: 'ABC Corporation',
          industry: 'manufacturing',
          employees: '50-100',
          leadSource: 'website',
        },
      },
      {
        phoneNumber: '+15554444444',
        name: 'XYZ Enterprises',
        email: 'info@xyzent.com',
        campaignId: this.fixtures.campaigns[1]?.id,
        status: ContactStatus.COMPLETED,
        attempts: 2,
        lastAttempt: new Date(),
        outcome: 'meeting_scheduled',
        notes: 'Interested in our services, meeting scheduled for next week',
        metadata: {
          company: 'XYZ Enterprises',
          industry: 'technology',
          employees: '100-500',
          leadSource: 'referral',
          meetingDate: '2023-12-15',
        },
      },

      // International campaign contacts
      {
        phoneNumber: '+447700900123',
        name: 'London Office Ltd',
        email: 'support@londonoffice.co.uk',
        campaignId: this.fixtures.campaigns[2]?.id,
        status: ContactStatus.PENDING,
        attempts: 0,
        lastAttempt: null,
        outcome: null,
        notes: null,
        metadata: {
          timezone: 'Europe/London',
          language: 'en',
          preferredContactTime: 'morning',
        },
      },
    ];

    for (const contactData of contacts) {
      const contact = await this.prisma.contact.create({ data: contactData });
      this.fixtures.contacts.push(contact);
    }
  }

  private async createTranscripts(): Promise<void> {
    // Get completed calls for transcripts
    const completedCalls = this.fixtures.calls.filter(c => c.status === CallStatus.COMPLETED);
    const activeCall = this.fixtures.calls.find(c => c.status === CallStatus.IN_PROGRESS);

    const transcripts = [
      // Transcripts for first completed call
      {
        callId: completedCalls[0]?.id,
        role: 'SYSTEM',
        content: 'Call initiated',
        timestamp: completedCalls[0]?.startTime,
        confidence: 1.0,
        speakerId: 'system',
        metadata: { type: 'system_message' },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'ASSISTANT',
        content: 'Hello, thank you for calling our customer service. How can I help you today?',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 5000),
        confidence: 0.98,
        speakerId: 'agent',
        metadata: { type: 'greeting' },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'USER',
        content: 'Hi, I have a question about my recent bill. There seems to be an extra charge I don\'t understand.',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 15000),
        confidence: 0.95,
        speakerId: 'customer',
        metadata: {
          type: 'inquiry',
          category: 'billing',
          sentiment: 'neutral',
        },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'ASSISTANT',
        content: 'I\'d be happy to help you with that billing question. Let me look up your account. Can you please provide your account number?',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 25000),
        confidence: 0.97,
        speakerId: 'agent',
        metadata: { type: 'response' },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'USER',
        content: 'Sure, it\'s 123456789.',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 35000),
        confidence: 0.99,
        speakerId: 'customer',
        metadata: {
          type: 'information',
          contains_account_number: true,
        },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'ASSISTANT',
        content: 'Thank you. I can see the charge you\'re referring to. That\'s a one-time setup fee for the premium features you activated last month. Would you like me to explain the details?',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 60000),
        confidence: 0.96,
        speakerId: 'agent',
        metadata: {
          type: 'explanation',
          category: 'billing_clarification',
        },
      },
      {
        callId: completedCalls[0]?.id,
        role: 'USER',
        content: 'Oh, I see! Yes, that makes sense now. Thank you for clarifying that.',
        timestamp: new Date(completedCalls[0]?.startTime.getTime() + 80000),
        confidence: 0.94,
        speakerId: 'customer',
        metadata: {
          type: 'acknowledgment',
          sentiment: 'positive',
          resolution_achieved: true,
        },
      },

      // Transcripts for active call
      ...(activeCall ? [
        {
          callId: activeCall.id,
          role: 'SYSTEM',
          content: 'Call initiated',
          timestamp: activeCall.startTime,
          confidence: 1.0,
          speakerId: 'system',
          metadata: { type: 'system_message' },
        },
        {
          callId: activeCall.id,
          role: 'ASSISTANT',
          content: 'Hello, thank you for calling Enterprise Solutions technical support. How can I assist you today?',
          timestamp: new Date(activeCall.startTime.getTime() + 3000),
          confidence: 0.98,
          speakerId: 'agent',
          metadata: { type: 'greeting' },
        },
        {
          callId: activeCall.id,
          role: 'USER',
          content: 'Hi, I\'m having trouble with your software. It keeps crashing when I try to export reports.',
          timestamp: new Date(activeCall.startTime.getTime() + 12000),
          confidence: 0.92,
          speakerId: 'customer',
          metadata: {
            type: 'problem_description',
            category: 'technical_issue',
            sentiment: 'frustrated',
            keywords: ['software', 'crashing', 'export', 'reports'],
          },
        },
        {
          callId: activeCall.id,
          role: 'ASSISTANT',
          content: 'I understand that\'s frustrating. Let me help you troubleshoot this issue. What version of the software are you using?',
          timestamp: new Date(activeCall.startTime.getTime() + 25000),
          confidence: 0.96,
          speakerId: 'agent',
          metadata: {
            type: 'troubleshooting_start',
            empathy_shown: true,
          },
        },
      ] : []),
    ];

    for (const transcriptData of transcripts) {
      if (transcriptData.callId) {
        const transcript = await this.prisma.callTranscript.create({ data: transcriptData });
        this.fixtures.transcripts.push(transcript);
      }
    }
  }

  private async createRecordings(): Promise<void> {
    // Create recordings for completed calls that have recording URLs
    const callsWithRecordings = this.fixtures.calls.filter(c => c.recordingUrl);

    const recordings = callsWithRecordings.map((call, index) => ({
      callId: call.id,
      url: call.recordingUrl,
      duration: call.duration || 0,
      size: Math.floor(Math.random() * 10000000) + 1000000, // 1-10MB
      format: 'mp3',
      quality: 'high',
      metadata: {
        provider: 'twilio',
        channels: 2,
        sampleRate: 8000,
        bitRate: 64,
        encrypted: true,
      },
    }));

    for (const recordingData of recordings) {
      // Note: Recording table might not exist in current schema
      // This is a placeholder for when it's implemented
      try {
        const recording = await this.prisma.callRecording.create({ data: recordingData });
        this.fixtures.recordings.push(recording);
      } catch (error) {
        // Recording table doesn't exist yet, skip
        console.warn('Recording table not found, skipping recording fixtures');
        break;
      }
    }
  }

  /**
   * Get specific fixtures by type and criteria
   */
  getFixtures(type: keyof TestFixtures, criteria?: any): any[] {
    const fixtures = this.fixtures[type];

    if (!criteria) {
      return fixtures;
    }

    return fixtures.filter(fixture => {
      return Object.keys(criteria).every(key => {
        return fixture[key] === criteria[key];
      });
    });
  }

  /**
   * Get a single fixture by type and criteria
   */
  getFixture(type: keyof TestFixtures, criteria: any): any {
    return this.getFixtures(type, criteria)[0] || null;
  }

  /**
   * Create additional test data for specific test scenarios
   */
  async createTestScenario(scenario: string): Promise<void> {
    switch (scenario) {
      case 'high_volume_calls':
        await this.createHighVolumeCalls();
        break;
      case 'multi_language_support':
        await this.createMultiLanguageData();
        break;
      case 'performance_stress':
        await this.createPerformanceStressData();
        break;
      default:
        throw new Error(`Unknown test scenario: ${scenario}`);
    }
  }

  private async createHighVolumeCalls(): Promise<void> {
    const baseTime = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000); // 7 days ago
    const agents = this.fixtures.users.filter(u => u.role === UserRole.AGENT);
    const calls = [];

    for (let i = 0; i < 1000; i++) {
      const startTime = new Date(baseTime.getTime() + i * 60 * 1000); // 1 minute apart
      const duration = Math.floor(Math.random() * 600) + 60; // 1-10 minutes

      const call = {
        fromNumber: `+1555${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
        toNumber: '+15559876543',
        direction: Math.random() > 0.5 ? CallDirection.INBOUND : CallDirection.OUTBOUND,
        provider: TelephonyProvider.TWILIO,
        organizationId: this.fixtures.organizations[0].id,
        agentId: agents[i % agents.length]?.id,
        status: CallStatus.COMPLETED,
        startTime,
        endTime: new Date(startTime.getTime() + duration * 1000),
        duration,
        disposition: ['resolved', 'completed', 'transferred', 'escalated'][Math.floor(Math.random() * 4)],
        metadata: {
          batchType: 'high_volume_test',
          category: ['support', 'sales', 'billing'][Math.floor(Math.random() * 3)],
        },
      };

      calls.push(call);
    }

    // Batch insert
    await this.prisma.call.createMany({ data: calls });
  }

  private async createMultiLanguageData(): Promise<void> {
    const languages = [
      { code: 'es', name: 'Spanish' },
      { code: 'fr', name: 'French' },
      { code: 'de', name: 'German' },
      { code: 'zh', name: 'Chinese' },
    ];

    for (const lang of languages) {
      // Create campaign for each language
      const campaign = await this.prisma.campaign.create({
        data: {
          name: `${lang.name} Support Campaign`,
          description: `Customer support in ${lang.name}`,
          type: CampaignType.INBOUND,
          organizationId: this.fixtures.organizations[2].id, // International org
          active: true,
          language: lang.code,
          instructions: {
            script: `Hello, welcome to Global Communications ${lang.name} support.`,
          },
          tools: {},
          voice: null,
          analytics: {},
        },
      });

      this.fixtures.campaigns.push(campaign);
    }
  }

  private async createPerformanceStressData(): Promise<void> {
    // Create large amounts of test data for performance testing
    const users = [];
    const calls = [];
    const transcripts = [];

    // Create 100 additional users
    for (let i = 0; i < 100; i++) {
      users.push({
        email: `perfuser${i}@stress.test`,
        username: `perfuser${i}`,
        firstName: `User${i}`,
        lastName: 'Test',
        passwordHash: await bcrypt.hash('password', 10),
        role: UserRole.AGENT,
        status: 'ACTIVE',
        organizationId: this.fixtures.organizations[0].id,
        skills: [],
        preferences: {},
      });
    }

    await this.prisma.user.createMany({ data: users });

    // Create 10,000 calls with transcripts
    const batchSize = 100;
    for (let batch = 0; batch < 100; batch++) {
      const batchCalls = [];
      const batchTranscripts = [];

      for (let i = 0; i < batchSize; i++) {
        const callId = `stress-call-${batch}-${i}`;
        const startTime = new Date(Date.now() - Math.random() * 30 * 24 * 60 * 60 * 1000);

        batchCalls.push({
          id: callId,
          fromNumber: `+1555${String(Math.floor(Math.random() * 9000000) + 1000000)}`,
          toNumber: '+15559876543',
          direction: CallDirection.INBOUND,
          provider: TelephonyProvider.TWILIO,
          organizationId: this.fixtures.organizations[0].id,
          status: CallStatus.COMPLETED,
          startTime,
          endTime: new Date(startTime.getTime() + 180000), // 3 minutes
          duration: 180,
          metadata: { stressTest: true },
        });

        // Add transcripts for each call
        for (let t = 0; t < 10; t++) {
          batchTranscripts.push({
            callId,
            role: t % 2 === 0 ? 'USER' : 'ASSISTANT',
            content: `Stress test transcript ${t} for call ${callId}`,
            timestamp: new Date(startTime.getTime() + t * 18000), // 18 seconds apart
            confidence: 0.9,
          });
        }
      }

      await this.prisma.call.createMany({ data: batchCalls });
      await this.prisma.callTranscript.createMany({ data: batchTranscripts });
    }
  }
}

// Export commonly used test data patterns
export const TEST_PHONE_NUMBERS = {
  valid: [
    '+15551234567',
    '+14155551234',
    '+442071234567',
    '+33123456789',
  ],
  invalid: [
    '5551234567',
    'not-a-phone',
    '+1555',
    '+999999999999999',
  ],
};

export const TEST_EMAIL_ADDRESSES = {
  valid: [
    'test@example.com',
    'user.name+tag@domain.co.uk',
    'test123@subdomain.example.org',
  ],
  invalid: [
    'not-an-email',
    '@domain.com',
    'user@',
    'user..double@domain.com',
  ],
};

export const TEST_PASSWORDS = {
  strong: [
    'StrongPassword123!',
    'Complex$Pass2024',
    'Secure#System9',
  ],
  weak: [
    'password',
    '123456',
    'qwerty',
    'admin',
  ],
};

export const MOCK_AI_RESPONSES = {
  intents: [
    'billing_inquiry',
    'technical_support',
    'sales_inquiry',
    'general_inquiry',
    'complaint',
    'cancellation_request',
  ],
  sentiments: ['positive', 'neutral', 'negative'],
  responses: [
    'I can help you with that.',
    'Let me look into this for you.',
    'I understand your concern.',
    'Thank you for calling us today.',
  ],
};