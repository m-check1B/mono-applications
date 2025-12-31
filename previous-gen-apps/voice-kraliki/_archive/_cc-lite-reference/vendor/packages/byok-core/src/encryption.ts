/**
 * @stack-2025/byok-core - Encryption Service
 * Secure encryption and decryption of API keys using AES-256-GCM
 */

import crypto from 'node:crypto';
import { EncryptionError } from './types.js';

/**
 * Encryption configuration
 */
export interface EncryptionConfig {
  algorithm: string;
  keyLength: number;
  nonceLength: number;
  tagLength: number;
  iterations: number; // For PBKDF2
  saltLength: number;
}

/**
 * Default encryption configuration
 */
export const DEFAULT_ENCRYPTION_CONFIG: EncryptionConfig = {
  algorithm: 'aes-256-gcm',
  keyLength: 32, // 256 bits
  nonceLength: 12, // 96 bits (recommended for GCM)
  tagLength: 16, // 128 bits
  iterations: 100000, // PBKDF2 iterations
  saltLength: 32 // 256 bits
};

/**
 * Encrypted data structure
 */
export interface EncryptedData {
  data: string; // Base64 encoded encrypted data + tag
  nonce: string; // Base64 encoded nonce/IV
  salt: string; // Base64 encoded salt (for key derivation)
}

/**
 * Encryption service for API keys
 */
export class EncryptionService {
  private config: EncryptionConfig;
  private masterKey: string;

  constructor(masterKey: string, config?: Partial<EncryptionConfig>) {
    if (!masterKey || masterKey.length < 32) {
      throw new EncryptionError('Master key must be at least 32 characters long', 'encrypt');
    }

    this.masterKey = masterKey;
    this.config = { ...DEFAULT_ENCRYPTION_CONFIG, ...config };
  }

  /**
   * Derive a user-specific encryption key
   */
  private deriveUserKey(userId: string, salt: Buffer): Buffer {
    try {
      const keyMaterial = `${this.masterKey}:${userId}`;
      return crypto.pbkdf2Sync(
        keyMaterial,
        salt,
        this.config.iterations,
        this.config.keyLength,
        'sha256'
      );
    } catch (error) {
      throw new EncryptionError(`Failed to derive user key: ${error}`, 'encrypt');
    }
  }

  /**
   * Generate a cryptographically secure nonce
   */
  private generateNonce(): Buffer {
    return crypto.randomBytes(this.config.nonceLength);
  }

  /**
   * Generate a cryptographically secure salt
   */
  private generateSalt(): Buffer {
    return crypto.randomBytes(this.config.saltLength);
  }

  /**
   * Encrypt API key data for a specific user
   */
  public encrypt(data: Record<string, any>, userId: string): EncryptedData {
    try {
      // Generate salt and derive user-specific key
      const salt = this.generateSalt();
      const userKey = this.deriveUserKey(userId, salt);
      
      // Generate nonce for this encryption
      const nonce = this.generateNonce();
      
      // Serialize data to JSON
      const plaintext = JSON.stringify(data);
      const plaintextBuffer = Buffer.from(plaintext, 'utf8');
      
      // Create cipher
      const cipher = crypto.createCipherGCM(this.config.algorithm, userKey, nonce);
      
      // Encrypt data
      const encrypted = Buffer.concat([
        cipher.update(plaintextBuffer),
        cipher.final()
      ]);
      
      // Get authentication tag
      const tag = cipher.getAuthTag();
      
      // Combine encrypted data with tag
      const encryptedWithTag = Buffer.concat([encrypted, tag]);
      
      return {
        data: encryptedWithTag.toString('base64'),
        nonce: nonce.toString('base64'),
        salt: salt.toString('base64')
      };
      
    } catch (error) {
      throw new EncryptionError(`Encryption failed: ${error}`, 'encrypt');
    }
  }

  /**
   * Decrypt API key data for a specific user
   */
  public decrypt(encryptedData: EncryptedData, userId: string): Record<string, any> {
    try {
      // Decode base64 data
      const dataBuffer = Buffer.from(encryptedData.data, 'base64');
      const nonce = Buffer.from(encryptedData.nonce, 'base64');
      const salt = Buffer.from(encryptedData.salt, 'base64');
      
      // Derive the same user-specific key
      const userKey = this.deriveUserKey(userId, salt);
      
      // Split encrypted data and tag
      const encrypted = dataBuffer.subarray(0, -this.config.tagLength);
      const tag = dataBuffer.subarray(-this.config.tagLength);
      
      // Create decipher
      const decipher = crypto.createDecipherGCM(this.config.algorithm, userKey, nonce);
      decipher.setAuthTag(tag);
      
      // Decrypt data
      const decrypted = Buffer.concat([
        decipher.update(encrypted),
        decipher.final()
      ]);
      
      // Parse JSON
      const plaintext = decrypted.toString('utf8');
      return JSON.parse(plaintext);
      
    } catch (error) {
      throw new EncryptionError(`Decryption failed: ${error}`, 'decrypt');
    }
  }

  /**
   * Generate a hash of the key data for duplicate detection
   */
  public generateKeyHash(data: Record<string, any>): string {
    try {
      // Create a deterministic string representation
      const normalized = this.normalizeKeyData(data);
      const dataString = JSON.stringify(normalized);
      
      // Generate SHA-256 hash
      return crypto.createHash('sha256')
        .update(dataString)
        .digest('hex');
        
    } catch (error) {
      throw new EncryptionError(`Hash generation failed: ${error}`, 'encrypt');
    }
  }

  /**
   * Normalize key data for consistent hashing
   */
  private normalizeKeyData(data: Record<string, any>): Record<string, any> {
    // Sort keys and remove undefined values
    const normalized: Record<string, any> = {};
    
    const sortedKeys = Object.keys(data).sort();
    for (const key of sortedKeys) {
      if (data[key] !== undefined && data[key] !== null) {
        if (typeof data[key] === 'object') {
          normalized[key] = this.normalizeKeyData(data[key]);
        } else {
          normalized[key] = data[key];
        }
      }
    }
    
    return normalized;
  }

  /**
   * Verify the integrity of encrypted data
   */
  public verifyIntegrity(encryptedData: EncryptedData): boolean {
    try {
      // Check that all required fields are present
      if (!encryptedData.data || !encryptedData.nonce || !encryptedData.salt) {
        return false;
      }

      // Verify base64 encoding
      const dataBuffer = Buffer.from(encryptedData.data, 'base64');
      const nonceBuffer = Buffer.from(encryptedData.nonce, 'base64');
      const saltBuffer = Buffer.from(encryptedData.salt, 'base64');

      // Check expected lengths
      if (nonceBuffer.length !== this.config.nonceLength) {
        return false;
      }

      if (saltBuffer.length !== this.config.saltLength) {
        return false;
      }

      // Check minimum data length (should include at least the tag)
      if (dataBuffer.length < this.config.tagLength) {
        return false;
      }

      return true;
    } catch {
      return false;
    }
  }

  /**
   * Generate a secure encryption key for initialization
   */
  public static generateMasterKey(): string {
    return crypto.randomBytes(32).toString('hex');
  }

  /**
   * Test encryption/decryption with sample data
   */
  public test(): boolean {
    try {
      const testData = {
        apiKey: 'test-key-12345',
        organization: 'test-org',
        timestamp: Date.now()
      };
      
      const userId = 'test-user';
      const encrypted = this.encrypt(testData, userId);
      const decrypted = this.decrypt(encrypted, userId);
      
      // Verify data integrity
      return JSON.stringify(testData) === JSON.stringify(decrypted);
    } catch {
      return false;
    }
  }
}

/**
 * Factory function for creating encryption service
 */
export function createEncryptionService(
  masterKey: string, 
  config?: Partial<EncryptionConfig>
): EncryptionService {
  return new EncryptionService(masterKey, config);
}

/**
 * Utility functions for key derivation and validation
 */
export class EncryptionUtils {
  /**
   * Generate a strong master key with entropy validation
   */
  static generateSecureMasterKey(): string {
    const key = crypto.randomBytes(32);
    
    // Validate entropy (basic check)
    const entropy = this.calculateEntropy(key);
    if (entropy < 7.5) { // Should be close to 8 for truly random data
      // Regenerate if entropy is too low (very unlikely)
      return this.generateSecureMasterKey();
    }
    
    return key.toString('hex');
  }

  /**
   * Calculate Shannon entropy of data
   */
  static calculateEntropy(data: Buffer): number {
    const frequency = new Array(256).fill(0);
    
    // Count byte frequencies
    for (let i = 0; i < data.length; i++) {
      frequency[data[i]]++;
    }
    
    // Calculate entropy
    let entropy = 0;
    for (let i = 0; i < 256; i++) {
      if (frequency[i] > 0) {
        const p = frequency[i] / data.length;
        entropy -= p * Math.log2(p);
      }
    }
    
    return entropy;
  }

  /**
   * Validate master key strength
   */
  static validateMasterKey(key: string): boolean {
    if (!key || key.length < 32) {
      return false;
    }

    // Check for basic patterns that indicate weak keys
    const patterns = [
      /^(.)\1+$/, // All same character
      /^(01|10)+$/, // Alternating 0,1
      /^(0123456789abcdef)+$/i, // Sequential hex
      /^(.{1,4})\1+$/ // Repeated short patterns
    ];

    for (const pattern of patterns) {
      if (pattern.test(key)) {
        return false;
      }
    }

    return true;
  }

  /**
   * Derive a test key for validation purposes
   */
  static deriveTestKey(baseKey: string): string {
    return crypto.createHash('sha256')
      .update(`test:${baseKey}`)
      .digest('hex');
  }
}

/**
 * Key rotation utilities
 */
export class KeyRotation {
  private oldService: EncryptionService;
  private newService: EncryptionService;

  constructor(oldMasterKey: string, newMasterKey: string) {
    this.oldService = new EncryptionService(oldMasterKey);
    this.newService = new EncryptionService(newMasterKey);
  }

  /**
   * Rotate encrypted data from old key to new key
   */
  public rotateEncryptedData(
    oldEncryptedData: EncryptedData, 
    userId: string
  ): EncryptedData {
    try {
      // Decrypt with old key
      const plainData = this.oldService.decrypt(oldEncryptedData, userId);
      
      // Re-encrypt with new key
      return this.newService.encrypt(plainData, userId);
    } catch (error) {
      throw new EncryptionError(`Key rotation failed: ${error}`, 'encrypt');
    }
  }

  /**
   * Verify both old and new services work correctly
   */
  public verifyRotation(): boolean {
    try {
      return this.oldService.test() && this.newService.test();
    } catch {
      return false;
    }
  }
}