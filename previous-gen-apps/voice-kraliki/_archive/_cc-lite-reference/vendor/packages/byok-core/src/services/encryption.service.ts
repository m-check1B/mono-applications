/**
 * @stack-2025/byok-core Encryption Service
 * AES-256-GCM encryption for API keys with user-specific key derivation
 */

import * as crypto from 'crypto';
import { BYOKError, BYOKErrorCode } from '../types';

export class EncryptionService {
  private readonly algorithm = 'aes-256-gcm';
  private readonly saltLength = 32;
  private readonly ivLength = 16;
  private readonly tagLength = 16;
  private readonly iterations = 100000;
  private readonly keyLength = 32;

  constructor(private readonly masterKey: string) {
    if (!masterKey || masterKey.length < 32) {
      throw new BYOKError(
        'Master key must be at least 32 characters',
        BYOKErrorCode.CONFIGURATION_ERROR,
        500
      );
    }
  }

  /**
   * Encrypt an API key with user-specific key derivation
   */
  async encrypt(plaintext: string, userId: string): Promise<string> {
    try {
      // Generate random salt and IV
      const salt = crypto.randomBytes(this.saltLength);
      const iv = crypto.randomBytes(this.ivLength);

      // Derive user-specific key using PBKDF2
      const key = await this.deriveKey(userId, salt);

      // Create cipher
      const cipher = crypto.createCipheriv(this.algorithm, key, iv);

      // Encrypt the plaintext
      const encrypted = Buffer.concat([
        cipher.update(plaintext, 'utf8'),
        cipher.final()
      ]);

      // Get the authentication tag
      const tag = cipher.getAuthTag();

      // Combine salt, iv, tag, and encrypted data
      const combined = Buffer.concat([salt, iv, tag, encrypted]);

      // Return base64 encoded
      return combined.toString('base64');
    } catch (error) {
      throw new BYOKError(
        'Encryption failed',
        BYOKErrorCode.ENCRYPTION_ERROR,
        500,
        error
      );
    }
  }

  /**
   * Decrypt an API key with user-specific key derivation
   */
  async decrypt(encryptedData: string, userId: string): Promise<string> {
    try {
      // Decode from base64
      const combined = Buffer.from(encryptedData, 'base64');

      // Extract components
      const salt = combined.slice(0, this.saltLength);
      const iv = combined.slice(this.saltLength, this.saltLength + this.ivLength);
      const tag = combined.slice(
        this.saltLength + this.ivLength,
        this.saltLength + this.ivLength + this.tagLength
      );
      const encrypted = combined.slice(this.saltLength + this.ivLength + this.tagLength);

      // Derive user-specific key
      const key = await this.deriveKey(userId, salt);

      // Create decipher
      const decipher = crypto.createDecipheriv(this.algorithm, key, iv);
      decipher.setAuthTag(tag);

      // Decrypt the data
      const decrypted = Buffer.concat([
        decipher.update(encrypted),
        decipher.final()
      ]);

      return decrypted.toString('utf8');
    } catch (error) {
      throw new BYOKError(
        'Decryption failed',
        BYOKErrorCode.ENCRYPTION_ERROR,
        500,
        error
      );
    }
  }

  /**
   * Generate a hash of the API key for comparison
   */
  async hash(plaintext: string): Promise<string> {
    const hash = crypto.createHash('sha256');
    hash.update(plaintext);
    return hash.digest('hex');
  }

  /**
   * Compare a plaintext key with a hash (constant time)
   */
  async compareHash(plaintext: string, hash: string): Promise<boolean> {
    const newHash = await this.hash(plaintext);
    return crypto.timingSafeEqual(
      Buffer.from(newHash),
      Buffer.from(hash)
    );
  }

  /**
   * Derive a user-specific encryption key using PBKDF2
   */
  private async deriveKey(userId: string, salt: Buffer): Promise<Buffer> {
    return new Promise((resolve, reject) => {
      crypto.pbkdf2(
        this.masterKey + userId,
        salt,
        this.iterations,
        this.keyLength,
        'sha256',
        (err, derivedKey) => {
          if (err) {
            reject(new BYOKError(
              'Key derivation failed',
              BYOKErrorCode.ENCRYPTION_ERROR,
              500,
              err
            ));
          } else {
            resolve(derivedKey);
          }
        }
      );
    });
  }

  /**
   * Generate a secure random token
   */
  generateToken(length: number = 32): string {
    return crypto.randomBytes(length).toString('hex');
  }

  /**
   * Rotate encryption keys (for key rotation)
   */
  async rotateKey(
    encryptedData: string,
    userId: string,
    newMasterKey: string
  ): Promise<string> {
    // Decrypt with old key
    const plaintext = await this.decrypt(encryptedData, userId);

    // Create new encryption service with new key
    const newService = new EncryptionService(newMasterKey);

    // Encrypt with new key
    return newService.encrypt(plaintext, userId);
  }

  /**
   * Validate master key strength
   */
  validateMasterKey(): boolean {
    if (!this.masterKey || this.masterKey.length < 32) {
      return false;
    }

    // Check for minimum complexity
    const hasUpperCase = /[A-Z]/.test(this.masterKey);
    const hasLowerCase = /[a-z]/.test(this.masterKey);
    const hasNumbers = /\d/.test(this.masterKey);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(this.masterKey);

    return hasUpperCase && hasLowerCase && hasNumbers && hasSpecialChar;
  }

  /**
   * Secure erase of sensitive data from memory
   */
  secureClear(data: string | Buffer): void {
    if (typeof data === 'string') {
      // Convert to buffer and fill with zeros
      const buffer = Buffer.from(data);
      buffer.fill(0);
    } else if (Buffer.isBuffer(data)) {
      data.fill(0);
    }
  }
}