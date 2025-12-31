/**
 * Comprehensive Event Security Tests
 * Tests the event security manager and WebSocket event filtering
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import crypto from 'crypto';
import {
  EventSecurityManager,
  EventPermission,
  EventSecurityContext,
  getEventPermissionLevel,
  SENSITIVE_EVENT_TYPES
} from '../../server/utils/event-security';

describe('Event Security Manager', () => {
  let securityManager: EventSecurityManager;
  let mockContext: EventSecurityContext;

  beforeEach(() => {
    securityManager = new EventSecurityManager();
    mockContext = {
      userId: 'user-123',
      orgId: 'org-456',
      role: 'SUPERVISOR',
      permissions: ['read:events', 'send:messages'],
      securityLevel: 'high'
    };
  });

  describe('Event Encryption/Decryption', () => {
    it('should encrypt and decrypt sensitive data correctly', () => {
      const sensitiveData = {
        customerName: 'John Doe',
        phoneNumber: '+1234567890',
        transcription: 'This is confidential information'
      };

      const encrypted = securityManager.encryptEventData(sensitiveData);
      expect(encrypted).toHaveProperty('encryptedData');
      expect(encrypted).toHaveProperty('iv');
      expect(encrypted).toHaveProperty('tag');

      const decrypted = securityManager.decryptEventData(
        encrypted.encryptedData,
        encrypted.iv,
        encrypted.tag
      );

      expect(decrypted).toEqual(sensitiveData);
    });

    it('should fail gracefully on invalid decryption', () => {
      expect(() => {
        securityManager.decryptEventData('invalid', 'data', 'here');
      }).toThrow('Failed to decrypt event data');
    });

    it('should handle encryption failures', () => {
      // Mock crypto to fail
      const originalCreateCipher = crypto.createCipher;
      crypto.createCipher = vi.fn().mockImplementation(() => {
        throw new Error('Crypto failure');
      });

      expect(() => {
        securityManager.encryptEventData({ test: 'data' });
      }).toThrow('Failed to encrypt event data');

      crypto.createCipher = originalCreateCipher;
    });
  });

  describe('Event Signature Verification', () => {
    it('should create and verify valid signatures', () => {
      const event = {
        event: 'test.event',
        data: { message: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.PUBLIC
      };

      const signature = securityManager.signEvent(event);
      expect(signature).toHaveLength(64); // SHA256 hex length

      const isValid = securityManager.verifyEventSignature(event, signature);
      expect(isValid).toBe(true);
    });

    it('should detect tampered events', () => {
      const event = {
        event: 'test.event',
        data: { message: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.PUBLIC
      };

      const signature = securityManager.signEvent(event);

      // Tamper with the event
      event.data.message = 'tampered';

      const isValid = securityManager.verifyEventSignature(event, signature);
      expect(isValid).toBe(false);
    });

    it('should reject invalid signature formats', () => {
      const event = {
        event: 'test.event',
        data: { message: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.PUBLIC
      };

      const isValid = securityManager.verifyEventSignature(event, 'invalid-signature');
      expect(isValid).toBe(false);
    });
  });

  describe('Permission Checking', () => {
    it('should allow public events to all authenticated users', () => {
      const publicEvent = {
        event: 'system.status',
        data: { status: 'online' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.PUBLIC
      };

      const hasPermission = securityManager.checkEventPermission(publicEvent, mockContext);
      expect(hasPermission).toBe(true);
    });

    it('should restrict supervisor-only events', () => {
      const supervisorEvent = {
        event: 'team.metrics',
        data: { metrics: 'sensitive' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.SUPERVISOR_ONLY
      };

      // Supervisor should have access
      const supervisorHasAccess = securityManager.checkEventPermission(supervisorEvent, mockContext);
      expect(supervisorHasAccess).toBe(true);

      // Agent should not have access
      const agentContext = { ...mockContext, role: 'AGENT' };
      const agentHasAccess = securityManager.checkEventPermission(supervisorEvent, agentContext);
      expect(agentHasAccess).toBe(false);
    });

    it('should enforce strict organization isolation', () => {
      const orgEvent = {
        event: 'test.event',
        data: { message: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'different-org',
        permission: EventPermission.PUBLIC
      };

      const hasPermission = securityManager.checkEventPermission(orgEvent, mockContext);
      expect(hasPermission).toBe(false);
    });

    it('should require high security level for sensitive events', () => {
      const sensitiveEvent = {
        event: 'customer.pii',
        data: { pii: 'sensitive' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.SENSITIVE
      };

      // High security supervisor should have access
      const highSecurityAccess = securityManager.checkEventPermission(sensitiveEvent, mockContext);
      expect(highSecurityAccess).toBe(true);

      // Low security context should not have access
      const lowSecurityContext = { ...mockContext, securityLevel: 'low' as const };
      const lowSecurityAccess = securityManager.checkEventPermission(sensitiveEvent, lowSecurityContext);
      expect(lowSecurityAccess).toBe(false);
    });

    it('should handle unknown permission levels securely', () => {
      const unknownEvent = {
        event: 'test.event',
        data: { message: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: 'unknown' as EventPermission
      };

      const hasPermission = securityManager.checkEventPermission(unknownEvent, mockContext);
      expect(hasPermission).toBe(false);
    });
  });

  describe('Event Processing for Transmission', () => {
    it('should process public events without encryption', () => {
      const processedEvent = securityManager.processEventForTransmission(
        'system.status',
        { status: 'online' },
        'org-456',
        EventPermission.PUBLIC
      );

      expect(processedEvent.encrypted).toBeUndefined();
      expect(processedEvent.signature).toBeDefined();
      expect(processedEvent.auditId).toBeDefined();
    });

    it('should encrypt sensitive events automatically', () => {
      const processedEvent = securityManager.processEventForTransmission(
        'call.transcript',
        { transcript: 'Customer said: I need help' },
        'org-456'
      );

      expect(processedEvent.encrypted).toBe(true);
      expect(processedEvent.data.encrypted).toBe(true);
      expect(processedEvent.data.payload).toBeDefined();
      expect(processedEvent.data.iv).toBeDefined();
      expect(processedEvent.data.tag).toBeDefined();
    });

    it('should encrypt events marked as sensitive permission', () => {
      const processedEvent = securityManager.processEventForTransmission(
        'custom.event',
        { sensitiveData: 'secret information' },
        'org-456',
        EventPermission.SENSITIVE
      );

      expect(processedEvent.encrypted).toBe(true);
      expect(processedEvent.data.encrypted).toBe(true);
    });
  });

  describe('Event Filtering for Users', () => {
    it('should filter events based on user permissions', () => {
      const events = [
        securityManager.processEventForTransmission('system.status', { status: 'online' }, 'org-456', EventPermission.PUBLIC),
        securityManager.processEventForTransmission('team.metrics', { metrics: 'data' }, 'org-456', EventPermission.SUPERVISOR_ONLY),
        securityManager.processEventForTransmission('admin.config', { config: 'data' }, 'org-456', EventPermission.ADMIN_ONLY)
      ];

      // Supervisor should see first two events
      const supervisorEvents = securityManager.filterEventsForUser(events, mockContext);
      expect(supervisorEvents).toHaveLength(2);

      // Agent should only see first event
      const agentContext = { ...mockContext, role: 'AGENT' };
      const agentEvents = securityManager.filterEventsForUser(events, agentContext);
      expect(agentEvents).toHaveLength(1);
    });

    it('should decrypt events for authorized users', () => {
      const sensitiveEvent = securityManager.processEventForTransmission(
        'call.transcript',
        { transcript: 'Customer conversation' },
        'org-456',
        EventPermission.SENSITIVE
      );

      const filteredEvents = securityManager.filterEventsForUser([sensitiveEvent], mockContext);

      expect(filteredEvents).toHaveLength(1);
      expect(filteredEvents[0].encrypted).toBe(false);
      expect(filteredEvents[0].data.transcript).toBe('Customer conversation');
    });

    it('should handle decryption failures gracefully', () => {
      // Create an event with corrupted encryption data
      const corruptedEvent = securityManager.processEventForTransmission(
        'call.transcript',
        { transcript: 'test' },
        'org-456',
        EventPermission.SENSITIVE
      );

      // Corrupt the encrypted data
      corruptedEvent.data.payload = 'corrupted-data';

      const filteredEvents = securityManager.filterEventsForUser([corruptedEvent], mockContext);

      expect(filteredEvents).toHaveLength(1);
      expect(filteredEvents[0].event).toBe('event.decryption_error');
      expect(filteredEvents[0].data.error).toBe('Event data unavailable');
    });
  });

  describe('Audit Trail and Security Metrics', () => {
    it('should track event access in audit trail', () => {
      const event = securityManager.processEventForTransmission(
        'test.event',
        { data: 'test' },
        'org-456',
        EventPermission.PUBLIC
      );

      securityManager.filterEventsForUser([event], mockContext);

      const auditTrail = securityManager.getAuditTrail('org-456');
      expect(auditTrail.length).toBeGreaterThan(0);

      const receivedEntry = auditTrail.find(entry => entry.action === 'received');
      expect(receivedEntry).toBeDefined();
      expect(receivedEntry?.userId).toBe(mockContext.userId);
      expect(receivedEntry?.event).toBe('test.event');
    });

    it('should track blocked events', () => {
      const adminEvent = securityManager.processEventForTransmission(
        'admin.config',
        { config: 'sensitive' },
        'org-456',
        EventPermission.ADMIN_ONLY
      );

      const agentContext = { ...mockContext, role: 'AGENT' };
      securityManager.filterEventsForUser([adminEvent], agentContext);

      const auditTrail = securityManager.getAuditTrail('org-456');
      const blockedEntry = auditTrail.find(entry => entry.action === 'blocked');

      expect(blockedEntry).toBeDefined();
      expect(blockedEntry?.reason).toBe('insufficient_permissions');
    });

    it('should provide security metrics', () => {
      // Generate some test events
      const publicEvent = securityManager.processEventForTransmission('test.public', { data: 'test' }, 'org-456', EventPermission.PUBLIC);
      const sensitiveEvent = securityManager.processEventForTransmission('call.transcript', { data: 'test' }, 'org-456', EventPermission.SENSITIVE);
      const adminEvent = securityManager.processEventForTransmission('admin.config', { data: 'test' }, 'org-456', EventPermission.ADMIN_ONLY);

      // Process events
      securityManager.filterEventsForUser([publicEvent, sensitiveEvent], mockContext);

      const agentContext = { ...mockContext, role: 'AGENT' };
      securityManager.filterEventsForUser([adminEvent], agentContext); // This should be blocked

      const metrics = securityManager.getSecurityMetrics('org-456');

      expect(metrics.totalEvents).toBeGreaterThan(0);
      expect(metrics.blockedEvents).toBeGreaterThan(0);
      expect(metrics.encryptedEvents).toBeGreaterThan(0);
    });

    it('should clear old audit entries', () => {
      // Add some test entries
      const event = securityManager.processEventForTransmission('test.event', { data: 'test' }, 'org-456', EventPermission.PUBLIC);
      securityManager.filterEventsForUser([event], mockContext);

      const initialCount = securityManager.getAuditTrail('org-456').length;
      expect(initialCount).toBeGreaterThan(0);

      // Clear entries older than 0 days (all entries)
      const cleared = securityManager.clearOldAuditEntries(0);
      expect(cleared).toBeGreaterThan(0);

      const finalCount = securityManager.getAuditTrail('org-456').length;
      expect(finalCount).toBe(0);
    });
  });

  describe('Event Permission Level Detection', () => {
    it('should correctly identify sensitive event types', () => {
      for (const sensitiveType of SENSITIVE_EVENT_TYPES) {
        const permission = getEventPermissionLevel(sensitiveType);
        expect(permission).toBe(EventPermission.SENSITIVE);
      }
    });

    it('should assign appropriate permission levels', () => {
      expect(getEventPermissionLevel('system.status')).toBe(EventPermission.PUBLIC);
      expect(getEventPermissionLevel('agent.task_assigned')).toBe(EventPermission.AGENT_ONLY);
      expect(getEventPermissionLevel('team.metrics_updated')).toBe(EventPermission.SUPERVISOR_ONLY);
      expect(getEventPermissionLevel('system.configuration_changed')).toBe(EventPermission.ADMIN_ONLY);
      expect(getEventPermissionLevel('call.transcript')).toBe(EventPermission.SENSITIVE);
    });

    it('should default to public for unknown event types', () => {
      const permission = getEventPermissionLevel('unknown.event.type');
      expect(permission).toBe(EventPermission.PUBLIC);
    });
  });

  describe('Role Hierarchy Validation', () => {
    it('should respect role hierarchy for permissions', () => {
      const event = {
        event: 'agent.task',
        data: { task: 'test' },
        timestamp: new Date().toISOString(),
        orgId: 'org-456',
        permission: EventPermission.AGENT_ONLY
      };

      // Admin should have access to agent-level events
      const adminContext = { ...mockContext, role: 'ADMIN' };
      expect(securityManager.checkEventPermission(event, adminContext)).toBe(true);

      // Supervisor should have access to agent-level events
      const supervisorContext = { ...mockContext, role: 'SUPERVISOR' };
      expect(securityManager.checkEventPermission(event, supervisorContext)).toBe(true);

      // Agent should have access to agent-level events
      const agentContext = { ...mockContext, role: 'AGENT' };
      expect(securityManager.checkEventPermission(event, agentContext)).toBe(true);

      // Viewer should not have access to agent-level events
      const viewerContext = { ...mockContext, role: 'VIEWER' };
      expect(securityManager.checkEventPermission(event, viewerContext)).toBe(false);
    });
  });
});