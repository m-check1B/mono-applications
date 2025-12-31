import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import { RecordingService } from '@server/services/recording-service';
import { PrismaClient, RecordingStatus, ConsentMethod, RecordingQuality, TelephonyProvider } from '@prisma/client';

// Mock AWS SDK
const awsMocks = vi.hoisted(() => ({
  mockS3Client: { send: vi.fn() },
  mockPutObjectCommand: vi.fn(),
  mockGetObjectCommand: vi.fn(),
  mockDeleteObjectCommand: vi.fn(),
  mockHeadObjectCommand: vi.fn(),
  mockGetSignedUrl: vi.fn()
}));

vi.mock('@aws-sdk/client-s3', () => ({
  S3Client: vi.fn(() => awsMocks.mockS3Client),
  PutObjectCommand: awsMocks.mockPutObjectCommand,
  GetObjectCommand: awsMocks.mockGetObjectCommand,
  DeleteObjectCommand: awsMocks.mockDeleteObjectCommand,
  HeadObjectCommand: awsMocks.mockHeadObjectCommand
}));

vi.mock('@aws-sdk/s3-request-presigner', () => ({
  getSignedUrl: awsMocks.mockGetSignedUrl
}));

// Mock crypto
vi.mock('node:crypto', () => ({
  createHash: vi.fn().mockReturnValue({
    update: vi.fn().mockReturnThis(),
    digest: vi.fn().mockReturnValue('mock-hash')
  }),
  randomBytes: vi.fn().mockReturnValue(Buffer.from('random-bytes')),
  default: {
    createHash: vi.fn().mockReturnValue({
      update: vi.fn().mockReturnThis(),
      digest: vi.fn().mockReturnValue('mock-hash')
    }),
    randomBytes: vi.fn().mockReturnValue(Buffer.from('random-bytes'))
  }
}));

// Mock telephony service
vi.mock('@server/services/telephony-service', () => ({
  getTelephonyService: vi.fn().mockReturnValue({
    startRecording: vi.fn().mockResolvedValue({ recordingId: 'twilio-recording-123' }),
    stopRecording: vi.fn().mockResolvedValue(true),
    pauseRecording: vi.fn().mockResolvedValue(true),
    resumeRecording: vi.fn().mockResolvedValue(true)
  })
}));

// Mock logger
vi.mock('@server/services/logger-service', () => ({
  systemLogger: {
    info: vi.fn(),
    warn: vi.fn(),
    error: vi.fn(),
    debug: vi.fn()
  }
}));

describe('RecordingService', () => {
  let recordingService: RecordingService;
  let mockPrisma: any;
  let mockCall: any;
  let mockRecording: any;
  let originalEnv: any;

  beforeEach(() => {
    // Save original environment
    originalEnv = {
      S3_RECORDING_BUCKET: process.env.S3_RECORDING_BUCKET,
      S3_RECORDING_REGION: process.env.S3_RECORDING_REGION,
      AWS_ACCESS_KEY_ID: process.env.AWS_ACCESS_KEY_ID,
      AWS_SECRET_ACCESS_KEY: process.env.AWS_SECRET_ACCESS_KEY
    };

    mockCall = {
      id: 'call-123',
      fromNumber: '+1234567890',
      toNumber: '+0987654321',
      status: 'ACTIVE',
      organizationId: 'org-123',
      providerCallId: 'twilio-call-123',
      recordings: []
    };

    mockRecording = {
      id: 'recording-123',
      callId: 'call-123',
      status: RecordingStatus.RECORDING,
      s3Key: 'recordings/call-123/recording-123.wav',
      s3Bucket: 'cc-lite-recordings',
      consent: {
        given: true,
        method: ConsentMethod.VERBAL,
        timestamp: new Date()
      },
      quality: RecordingQuality.STANDARD,
      createdAt: new Date(),
      startedAt: new Date()
    };

    mockPrisma = {
      call: {
        findUnique: vi.fn(),
        update: vi.fn()
      },
      recording: {
        create: vi.fn(),
        findUnique: vi.fn(),
        findMany: vi.fn(),
        update: vi.fn(),
        delete: vi.fn(),
        deleteMany: vi.fn()
      },
      organization: {
        findUnique: vi.fn()
      }
    };

    vi.clearAllMocks();

    // Set up default successful mocks
    mockPrisma.call.findUnique.mockResolvedValue(mockCall);
    mockPrisma.recording.create.mockResolvedValue(mockRecording);
    mockPrisma.recording.findUnique.mockResolvedValue(mockRecording);
    awsMocks.mockS3Client.send.mockResolvedValue({ ETag: 'mock-etag' });
    mockGetSignedUrl.mockResolvedValue('https://signed-url.example.com');

    recordingService = new RecordingService(mockPrisma);
  });

  afterEach(() => {
    // Restore original environment
    Object.keys(originalEnv).forEach(key => {
      if (originalEnv[key] !== undefined) {
        process.env[key] = originalEnv[key];
      } else {
        delete process.env[key];
      }
    });
    vi.clearAllMocks();
  });

  describe('Constructor', () => {
    it('should initialize with default configuration', () => {
      expect(recordingService).toBeDefined();
    });

    it('should use environment variables for S3 configuration', () => {
      process.env.S3_RECORDING_BUCKET = 'custom-bucket';
      process.env.S3_RECORDING_REGION = 'eu-west-1';
      process.env.AWS_ACCESS_KEY_ID = 'test-key';
      process.env.AWS_SECRET_ACCESS_KEY = 'test-secret';

      const customService = new RecordingService(mockPrisma);
      expect(customService).toBeDefined();
    });

    it('should accept custom configuration', () => {
      const customConfig = {
        bucket: 'custom-recordings',
        region: 'us-west-2',
        encryptionEnabled: false,
        retentionDays: 30
      };

      const customService = new RecordingService(mockPrisma, customConfig);
      expect(customService).toBeDefined();
    });
  });

  describe('startRecording', () => {
    const validConsent = {
      given: true,
      method: ConsentMethod.VERBAL as const,
      timestamp: new Date()
    };

    it('should start recording with valid consent', async () => {
      const result = await recordingService.startRecording('call-123', validConsent);

      expect(result).toEqual({
        recordingId: 'recording-123',
        controls: expect.objectContaining({
          start: expect.any(Function),
          pause: expect.any(Function),
          resume: expect.any(Function),
          stop: expect.any(Function)
        })
      });

      expect(mockPrisma.call.findUnique).toHaveBeenCalledWith({
        where: { id: 'call-123' },
        include: { recordings: true }
      });

      expect(mockPrisma.recording.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          callId: 'call-123',
          status: RecordingStatus.RECORDING,
          consent: validConsent,
          quality: RecordingQuality.STANDARD
        })
      });
    });

    it('should throw error when consent is not given', async () => {
      const invalidConsent = {
        given: false,
        method: ConsentMethod.VERBAL as const,
        timestamp: new Date()
      };

      await expect(recordingService.startRecording('call-123', invalidConsent))
        .rejects.toThrow('Recording consent is required but not provided');
    });

    it('should throw error for non-existent call', async () => {
      mockPrisma.call.findUnique.mockResolvedValue(null);

      await expect(recordingService.startRecording('nonexistent-call', validConsent))
        .rejects.toThrow('Call not found');
    });

    it('should throw error if recording already exists', async () => {
      const callWithRecording = {
        ...mockCall,
        recordings: [{
          id: 'existing-recording',
          status: RecordingStatus.RECORDING
        }]
      };
      mockPrisma.call.findUnique.mockResolvedValue(callWithRecording);

      await expect(recordingService.startRecording('call-123', validConsent))
        .rejects.toThrow('Recording already in progress for this call');
    });

    it('should include optional parameters in recording creation', async () => {
      const options = {
        quality: RecordingQuality.HIGH as const,
        provider: TelephonyProvider.TELNYX as const,
        userId: 'user-123',
        organizationId: 'org-456'
      };

      await recordingService.startRecording('call-123', validConsent, options);

      expect(mockPrisma.recording.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          quality: RecordingQuality.HIGH,
          userId: 'user-123',
          organizationId: 'org-456'
        })
      });
    });

    it('should start provider recording', async () => {
      const { getTelephonyService } = await import('@server/services/telephony-service');
      const telephonyService = getTelephonyService();

      await recordingService.startRecording('call-123', validConsent);

      expect(telephonyService.startRecording).toHaveBeenCalledWith('twilio-call-123');
    });
  });

  describe('Recording Controls', () => {
    let controls: any;

    beforeEach(async () => {
      const validConsent = {
        given: true,
        method: ConsentMethod.VERBAL as const,
        timestamp: new Date()
      };

      const result = await recordingService.startRecording('call-123', validConsent);
      controls = result.controls;
    });

    describe('pause', () => {
      it('should pause active recording', async () => {
        mockPrisma.recording.update.mockResolvedValue({
          ...mockRecording,
          status: RecordingStatus.PAUSED
        });

        await controls.pause();

        expect(mockPrisma.recording.update).toHaveBeenCalledWith({
          where: { id: 'recording-123' },
          data: { status: RecordingStatus.PAUSED }
        });
      });

      it('should call telephony service to pause recording', async () => {
        const { getTelephonyService } = await import('@server/services/telephony-service');
        const telephonyService = getTelephonyService();

        await controls.pause();

        expect(telephonyService.pauseRecording).toHaveBeenCalledWith('twilio-call-123');
      });
    });

    describe('resume', () => {
      it('should resume paused recording', async () => {
        mockPrisma.recording.findUnique.mockResolvedValue({
          ...mockRecording,
          status: RecordingStatus.PAUSED
        });
        mockPrisma.recording.update.mockResolvedValue({
          ...mockRecording,
          status: RecordingStatus.RECORDING
        });

        await controls.resume();

        expect(mockPrisma.recording.update).toHaveBeenCalledWith({
          where: { id: 'recording-123' },
          data: { status: RecordingStatus.RECORDING }
        });
      });

      it('should call telephony service to resume recording', async () => {
        const { getTelephonyService } = await import('@server/services/telephony-service');
        const telephonyService = getTelephonyService();

        await controls.resume();

        expect(telephonyService.resumeRecording).toHaveBeenCalledWith('twilio-call-123');
      });
    });

    describe('stop', () => {
      it('should stop recording and finalize', async () => {
        mockPrisma.recording.update.mockResolvedValue({
          ...mockRecording,
          status: RecordingStatus.COMPLETED,
          endedAt: new Date(),
          duration: 300
        });

        await controls.stop();

        expect(mockPrisma.recording.update).toHaveBeenCalledWith({
          where: { id: 'recording-123' },
          data: expect.objectContaining({
            status: RecordingStatus.COMPLETED,
            endedAt: expect.any(Date),
            duration: expect.any(Number)
          })
        });
      });

      it('should call telephony service to stop recording', async () => {
        const { getTelephonyService } = await import('@server/services/telephony-service');
        const telephonyService = getTelephonyService();

        await controls.stop();

        expect(telephonyService.stopRecording).toHaveBeenCalledWith('twilio-call-123');
      });
    });
  });

  describe('getRecording', () => {
    it('should retrieve recording by ID', async () => {
      const result = await recordingService.getRecording('recording-123');

      expect(result).toEqual(mockRecording);
      expect(mockPrisma.recording.findUnique).toHaveBeenCalledWith({
        where: { id: 'recording-123' },
        include: { call: true }
      });
    });

    it('should return null for non-existent recording', async () => {
      mockPrisma.recording.findUnique.mockResolvedValue(null);

      const result = await recordingService.getRecording('nonexistent');

      expect(result).toBeNull();
    });
  });

  describe('getCallRecordings', () => {
    it('should retrieve all recordings for a call', async () => {
      const recordings = [mockRecording, { ...mockRecording, id: 'recording-456' }];
      mockPrisma.recording.findMany.mockResolvedValue(recordings);

      const result = await recordingService.getCallRecordings('call-123');

      expect(result).toEqual(recordings);
      expect(mockPrisma.recording.findMany).toHaveBeenCalledWith({
        where: { callId: 'call-123' },
        orderBy: { createdAt: 'desc' }
      });
    });

    it('should return empty array for call with no recordings', async () => {
      mockPrisma.recording.findMany.mockResolvedValue([]);

      const result = await recordingService.getCallRecordings('call-no-recordings');

      expect(result).toEqual([]);
    });
  });

  describe('uploadRecording', () => {
    const mockAudioBuffer = Buffer.from('mock audio data');

    it('should upload recording to S3', async () => {
      await recordingService.uploadRecording('recording-123', mockAudioBuffer);

      expect(awsMocks.mockS3Client.send).toHaveBeenCalledWith(
        expect.objectContaining({
          input: expect.objectContaining({
            Bucket: 'cc-lite-recordings',
            Key: expect.stringContaining('recording-123'),
            Body: mockAudioBuffer,
            ContentType: 'audio/wav'
          })
        })
      );

      expect(mockPrisma.recording.update).toHaveBeenCalledWith({
        where: { id: 'recording-123' },
        data: expect.objectContaining({
          s3Uploaded: true,
          s3UploadedAt: expect.any(Date)
        })
      });
    });

    it('should handle S3 upload failures', async () => {
    awsMocks.mockS3Client.send.mockRejectedValue(new Error('S3 upload failed'));

      await expect(recordingService.uploadRecording('recording-123', mockAudioBuffer))
        .rejects.toThrow('S3 upload failed');
    });

    it('should use encryption when enabled', async () => {
      const encryptedService = new RecordingService(mockPrisma, {
        encryptionEnabled: true
      });

      await encryptedService.uploadRecording('recording-123', mockAudioBuffer);

      expect(awsMocks.mockS3Client.send).toHaveBeenCalledWith(
        expect.objectContaining({
          input: expect.objectContaining({
            ServerSideEncryption: 'AES256'
          })
        })
      );
    });
  });

  describe('getPlaybackUrl', () => {
    it('should generate signed URL for playback', async () => {
      const url = await recordingService.getPlaybackUrl('recording-123');

      expect(url).toBe('https://signed-url.example.com');
      expect(mockGetSignedUrl).toHaveBeenCalledWith(
        awsMocks.mockS3Client,
        expect.any(Object),
        { expiresIn: 3600 }
      );
    });

    it('should throw error for non-existent recording', async () => {
      mockPrisma.recording.findUnique.mockResolvedValue(null);

      await expect(recordingService.getPlaybackUrl('nonexistent'))
        .rejects.toThrow('Recording not found');
    });

    it('should throw error for recording not uploaded to S3', async () => {
      mockPrisma.recording.findUnique.mockResolvedValue({
        ...mockRecording,
        s3Uploaded: false
      });

      await expect(recordingService.getPlaybackUrl('recording-123'))
        .rejects.toThrow('Recording not available for playback');
    });

    it('should use custom expiration time', async () => {
      await recordingService.getPlaybackUrl('recording-123', 7200);

      expect(mockGetSignedUrl).toHaveBeenCalledWith(
        awsMocks.mockS3Client,
        expect.any(Object),
        { expiresIn: 7200 }
      );
    });
  });

  describe('deleteRecording', () => {
    it('should delete recording from database and S3', async () => {
      await recordingService.deleteRecording('recording-123');

      expect(awsMocks.mockS3Client.send).toHaveBeenCalledWith(
        expect.objectContaining({
          input: expect.objectContaining({
            Bucket: 'cc-lite-recordings',
            Key: 'recordings/call-123/recording-123.wav'
          })
        })
      );

      expect(mockPrisma.recording.delete).toHaveBeenCalledWith({
        where: { id: 'recording-123' }
      });
    });

    it('should handle S3 deletion failures gracefully', async () => {
      awsMocks.mockS3Client.send.mockRejectedValue(new Error('S3 delete failed'));

      // Should still delete from database
      await recordingService.deleteRecording('recording-123');

      expect(mockPrisma.recording.delete).toHaveBeenCalled();
    });

    it('should throw error for non-existent recording', async () => {
      mockPrisma.recording.findUnique.mockResolvedValue(null);

      await expect(recordingService.deleteRecording('nonexistent'))
        .rejects.toThrow('Recording not found');
    });
  });

  describe('Consent Management', () => {
    it('should validate consent methods', async () => {
      const digitalConsent = {
        given: true,
        method: ConsentMethod.DIGITAL as const,
        timestamp: new Date(),
        details: { ip: '127.0.0.1', userAgent: 'Test Browser' }
      };

      await recordingService.startRecording('call-123', digitalConsent);

      expect(mockPrisma.recording.create).toHaveBeenCalledWith({
        data: expect.objectContaining({
          consent: digitalConsent
        })
      });
    });

    it('should update consent information', async () => {
      const newConsent = {
        given: true,
        method: ConsentMethod.WRITTEN as const,
        timestamp: new Date(),
        details: { documentId: 'consent-doc-123' }
      };

      await recordingService.updateConsent('recording-123', newConsent);

      expect(mockPrisma.recording.update).toHaveBeenCalledWith({
        where: { id: 'recording-123' },
        data: { consent: newConsent }
      });
    });

    it('should handle consent withdrawal', async () => {
      const withdrawnConsent = {
        given: false,
        method: ConsentMethod.VERBAL as const,
        timestamp: new Date(),
        details: { reason: 'Customer requested removal' }
      };

      await recordingService.updateConsent('recording-123', withdrawnConsent);

      // Should also stop and delete recording when consent is withdrawn
      expect(mockPrisma.recording.update).toHaveBeenCalledWith({
        where: { id: 'recording-123' },
        data: expect.objectContaining({
          consent: withdrawnConsent,
          status: RecordingStatus.DELETED
        })
      });
    });
  });

  describe('Compliance and Retention', () => {
    it('should clean up expired recordings', async () => {
      const expiredDate = new Date();
      expiredDate.setDate(expiredDate.getDate() - 91); // 91 days ago

      const expiredRecordings = [
        { ...mockRecording, id: 'expired-1', createdAt: expiredDate },
        { ...mockRecording, id: 'expired-2', createdAt: expiredDate }
      ];

      mockPrisma.recording.findMany.mockResolvedValue(expiredRecordings);

      await recordingService.cleanupExpiredRecordings();

      expect(mockPrisma.recording.deleteMany).toHaveBeenCalledWith({
        where: {
          createdAt: {
            lt: expect.any(Date)
          }
        }
      });
    });

    it('should generate compliance report', async () => {
      const recordings = [
        mockRecording,
        { ...mockRecording, id: 'recording-456', status: RecordingStatus.COMPLETED }
      ];
      mockPrisma.recording.findMany.mockResolvedValue(recordings);

      const report = await recordingService.generateComplianceReport('org-123', {
        startDate: new Date('2024-01-01'),
        endDate: new Date('2024-12-31')
      });

      expect(report).toEqual({
        totalRecordings: 2,
        recordingsByStatus: {
          [RecordingStatus.RECORDING]: 1,
          [RecordingStatus.COMPLETED]: 1
        },
        consentBreakdown: {
          [ConsentMethod.VERBAL]: 2
        },
        complianceIssues: []
      });
    });

    it('should identify compliance issues', async () => {
      const recordingsWithIssues = [
        {
          ...mockRecording,
          consent: { given: false, method: ConsentMethod.VERBAL, timestamp: new Date() }
        }
      ];
      mockPrisma.recording.findMany.mockResolvedValue(recordingsWithIssues);

      const report = await recordingService.generateComplianceReport('org-123');

      expect(report.complianceIssues).toContain('Recording without valid consent found');
    });
  });

  describe('Error Handling', () => {
    it('should handle database connection errors', async () => {
      mockPrisma.recording.findUnique.mockRejectedValue(new Error('Database connection failed'));

      await expect(recordingService.getRecording('recording-123'))
        .rejects.toThrow('Database connection failed');
    });

    it('should handle S3 connectivity issues', async () => {
      awsMocks.mockS3Client.send.mockRejectedValue(new Error('Network error'));

      const buffer = Buffer.from('test audio');
      await expect(recordingService.uploadRecording('recording-123', buffer))
        .rejects.toThrow('Network error');
    });

    it('should handle telephony service failures gracefully', async () => {
      const { getTelephonyService } = await import('@server/services/telephony-service');
      const telephonyService = getTelephonyService();
      telephonyService.startRecording.mockRejectedValue(new Error('Telephony error'));

      const validConsent = {
        given: true,
        method: ConsentMethod.VERBAL as const,
        timestamp: new Date()
      };

      // Should still create database record even if telephony fails
      await recordingService.startRecording('call-123', validConsent);

      expect(mockPrisma.recording.create).toHaveBeenCalled();
    });
  });

  describe('Performance and Scalability', () => {
    it('should handle concurrent recording operations', async () => {
      const validConsent = {
        given: true,
        method: ConsentMethod.VERBAL as const,
        timestamp: new Date()
      };

      // Set up different calls
      const calls = Array.from({ length: 10 }, (_, i) => ({
        ...mockCall,
        id: `call-${i}`,
        recordings: []
      }));

      mockPrisma.call.findUnique.mockImplementation(({ where }) => {
        return Promise.resolve(calls.find(call => call.id === where.id));
      });

      mockPrisma.recording.create.mockImplementation(({ data }) => {
        return Promise.resolve({
          ...mockRecording,
          id: `recording-${data.callId}`,
          callId: data.callId
        });
      });

      const promises = calls.map(call =>
        recordingService.startRecording(call.id, validConsent)
      );

      const results = await Promise.all(promises);

      expect(results).toHaveLength(10);
      expect(mockPrisma.recording.create).toHaveBeenCalledTimes(10);
    });

    it('should handle large file uploads efficiently', async () => {
      const largeBuffer = Buffer.alloc(100 * 1024 * 1024); // 100MB

      await recordingService.uploadRecording('recording-123', largeBuffer);

      expect(awsMocks.mockS3Client.send).toHaveBeenCalledWith(
        expect.objectContaining({
          input: expect.objectContaining({
            Body: largeBuffer
          })
        })
      );
    });
  });
});
