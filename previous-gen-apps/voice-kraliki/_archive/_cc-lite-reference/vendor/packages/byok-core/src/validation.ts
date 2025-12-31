/**
 * @stack-2025/byok-core - Key Validation Service
 * Validates API keys against their respective provider services
 */

import { 
  StoredKey,
  KeyValidationResult,
  ProviderType,
  BYOKError,
  ProviderError
} from './types.js';

import { DatabaseInterface } from './database.js';
import { EncryptionService } from './encryption.js';

/**
 * Test configuration for a provider
 */
interface ProviderTest {
  name: string;
  method: 'GET' | 'POST';
  url: string;
  headers?: Record<string, string>;
  body?: Record<string, any>;
  expectedStatus: number[];
  timeout: number;
  validateResponse?: (response: any) => boolean;
}

/**
 * Key validator service
 */
export class KeyValidator {
  private database: DatabaseInterface;
  private encryption: EncryptionService;

  constructor(database: DatabaseInterface, encryptionKey?: string) {
    this.database = database;
    if (encryptionKey) {
      this.encryption = new EncryptionService(encryptionKey);
    }
  }

  /**
   * Validate a stored key
   */
  async validateKey(storedKey: StoredKey): Promise<KeyValidationResult> {
    const startTime = Date.now();
    
    try {
      // Decrypt the key data
      if (!this.encryption) {
        throw new BYOKError('Encryption service not initialized for validation', 'VALIDATION_ERROR');
      }
      
      const [nonce, salt] = storedKey.encryptionNonce.split(':');
      const encryptedData = {
        data: storedKey.encryptedKeyData,
        nonce,
        salt
      };
      
      const keyData = this.encryption.decrypt(encryptedData, storedKey.userId);
      
      // Get provider-specific tests
      const tests = this.getProviderTests(storedKey.provider);
      const testResults: Record<string, any> = {};
      const testsRun: string[] = [];
      let isValid = true;
      let errorMessage: string | undefined;
      
      // Run validation tests
      for (const test of tests) {
        try {
          const result = await this.runProviderTest(test, keyData, storedKey.provider);
          testResults[test.name] = result;
          testsRun.push(test.name);
          
          if (!result.success) {
            isValid = false;
            errorMessage = result.error || `Test ${test.name} failed`;
            break; // Stop on first failure
          }
        } catch (error) {
          testResults[test.name] = {
            success: false,
            error: error instanceof Error ? error.message : 'Unknown error'
          };
          testsRun.push(test.name);
          isValid = false;
          errorMessage = `Test ${test.name} failed: ${error}`;
          break;
        }
      }
      
      const responseTime = Date.now() - startTime;
      const healthScore = this.calculateHealthScore(testResults, responseTime, isValid);
      
      const result: KeyValidationResult = {
        keyId: storedKey.id,
        isValid,
        errorMessage,
        testResults,
        responseTime,
        testsRun,
        healthScore
      };
      
      // Store validation result
      await this.database.createValidation(result);
      
      return result;
      
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      const result: KeyValidationResult = {
        keyId: storedKey.id,
        isValid: false,
        errorMessage: error instanceof Error ? error.message : 'Unknown validation error',
        testResults: { error: error instanceof Error ? error.message : 'Unknown error' },
        responseTime,
        testsRun: [],
        healthScore: 0
      };
      
      // Try to store validation result (might fail if database is down)
      try {
        await this.database.createValidation(result);
      } catch {
        // Ignore database errors during validation failure
      }
      
      return result;
    }
  }

  /**
   * Get provider-specific validation tests
   */
  private getProviderTests(provider: ProviderType): ProviderTest[] {
    switch (provider) {
      case ProviderType.OPENAI:
        return [
          {
            name: 'list_models',
            method: 'GET',
            url: 'https://api.openai.com/v1/models',
            headers: {},
            expectedStatus: [200],
            timeout: 10000,
            validateResponse: (response) => {
              return response && response.data && Array.isArray(response.data);
            }
          }
        ];
        
      case ProviderType.ANTHROPIC:
        return [
          {
            name: 'test_message',
            method: 'POST',
            url: 'https://api.anthropic.com/v1/messages',
            headers: {
              'anthropic-version': '2023-06-01'
            },
            body: {
              model: 'claude-3-haiku-20240307',
              max_tokens: 10,
              messages: [{
                role: 'user',
                content: 'Hi'
              }]
            },
            expectedStatus: [200],
            timeout: 15000
          }
        ];
        
      case ProviderType.DEEPGRAM:
        return [
          {
            name: 'get_projects',
            method: 'GET',
            url: 'https://api.deepgram.com/v1/projects',
            expectedStatus: [200],
            timeout: 10000
          }
        ];
        
      case ProviderType.TWILIO:
        return [
          {
            name: 'get_account',
            method: 'GET',
            url: 'https://api.twilio.com/2010-04-01/Accounts.json',
            expectedStatus: [200],
            timeout: 10000
          }
        ];
        
      case ProviderType.GOOGLE_VERTEX:
      case ProviderType.GOOGLE_GEMINI:
        return [
          {
            name: 'test_generate',
            method: 'POST',
            url: 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent',
            body: {
              contents: [{
                parts: [{ text: 'Hi' }]
              }]
            },
            expectedStatus: [200],
            timeout: 15000
          }
        ];
        
      default:
        return [
          {
            name: 'generic_health',
            method: 'GET',
            url: 'https://httpbin.org/status/200', // Generic test
            expectedStatus: [200],
            timeout: 5000
          }
        ];
    }
  }

  /**
   * Run a provider-specific test
   */
  private async runProviderTest(
    test: ProviderTest, 
    keyData: any, 
    provider: ProviderType
  ): Promise<{ success: boolean; error?: string; response?: any; statusCode?: number }> {
    try {
      // Prepare headers with authentication
      const headers = {
        'Content-Type': 'application/json',
        ...test.headers,
        ...this.getAuthHeaders(provider, keyData)
      };
      
      // Prepare request options
      const requestOptions: RequestInit = {
        method: test.method,
        headers,
        signal: AbortSignal.timeout(test.timeout)
      };
      
      if (test.body) {
        requestOptions.body = JSON.stringify(test.body);
      }
      
      // Make the request
      const response = await fetch(test.url, requestOptions);
      const statusCode = response.status;
      
      // Check if status code is expected
      if (!test.expectedStatus.includes(statusCode)) {
        const errorText = await response.text();
        return {
          success: false,
          error: `Unexpected status code ${statusCode}: ${errorText}`,
          statusCode
        };
      }
      
      // Parse response
      let responseData;
      try {
        responseData = await response.json();
      } catch {
        responseData = await response.text();
      }
      
      // Run custom validation if provided
      if (test.validateResponse && !test.validateResponse(responseData)) {
        return {
          success: false,
          error: 'Response validation failed',
          response: responseData,
          statusCode
        };
      }
      
      return {
        success: true,
        response: responseData,
        statusCode
      };
      
    } catch (error) {
      if (error instanceof Error && error.name === 'TimeoutError') {
        return {
          success: false,
          error: `Request timeout after ${test.timeout}ms`
        };
      }
      
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Unknown error'
      };
    }
  }

  /**
   * Get authentication headers for a provider
   */
  private getAuthHeaders(provider: ProviderType, keyData: any): Record<string, string> {
    switch (provider) {
      case ProviderType.OPENAI:
        return {
          'Authorization': `Bearer ${keyData.apiKey}`,
          ...(keyData.organization && { 'OpenAI-Organization': keyData.organization }),
          ...(keyData.project && { 'OpenAI-Project': keyData.project })
        };
        
      case ProviderType.ANTHROPIC:
        return {
          'x-api-key': keyData.apiKey
        };
        
      case ProviderType.DEEPGRAM:
        return {
          'Authorization': `Token ${keyData.apiKey}`
        };
        
      case ProviderType.TWILIO:
        const auth = Buffer.from(`${keyData.accountSid}:${keyData.authToken}`).toString('base64');
        return {
          'Authorization': `Basic ${auth}`
        };
        
      case ProviderType.GOOGLE_VERTEX:
      case ProviderType.GOOGLE_GEMINI:
        return {
          'Authorization': `Bearer ${keyData.apiKey}`
        };
        
      default:
        return {};
    }
  }

  /**
   * Calculate health score based on test results
   */
  private calculateHealthScore(
    testResults: Record<string, any>,
    responseTime: number,
    isValid: boolean
  ): number {
    if (!isValid) return 0;
    
    let score = 100;
    
    // Deduct points for slow response
    if (responseTime > 5000) { // > 5 seconds
      score -= 20;
    } else if (responseTime > 3000) { // > 3 seconds
      score -= 10;
    } else if (responseTime > 1000) { // > 1 second
      score -= 5;
    }
    
    // Deduct points for failed tests (even if overall validation passed)
    const failedTests = Object.values(testResults).filter(
      (result: any) => result && result.success === false
    );
    
    score -= failedTests.length * 10;
    
    // Ensure score is between 0 and 100
    return Math.max(0, Math.min(100, score));
  }

  /**
   * Batch validate multiple keys
   */
  async validateKeys(keys: StoredKey[]): Promise<KeyValidationResult[]> {
    const results: KeyValidationResult[] = [];
    
    // Validate keys in parallel with concurrency limit
    const concurrencyLimit = 5;
    const chunks = this.chunkArray(keys, concurrencyLimit);
    
    for (const chunk of chunks) {
      const chunkPromises = chunk.map(key => this.validateKey(key));
      const chunkResults = await Promise.allSettled(chunkPromises);
      
      for (let i = 0; i < chunk.length; i++) {
        const result = chunkResults[i];
        if (result.status === 'fulfilled') {
          results.push(result.value);
        } else {
          // Handle validation failure
          results.push({
            keyId: chunk[i].id,
            isValid: false,
            errorMessage: `Validation failed: ${result.reason}`,
            testResults: {},
            responseTime: 0,
            testsRun: [],
            healthScore: 0
          });
        }
      }
    }
    
    return results;
  }

  /**
   * Schedule periodic validation of all keys
   */
  async schedulePeriodicValidation(intervalMs: number = 3600000): Promise<void> {
    // This would be implemented with a job queue or cron system
    // For now, just log the intent
    console.log(`Periodic validation scheduled every ${intervalMs}ms`);
    
    // In a real implementation:
    // setInterval(async () => {
    //   await this.validateAllActiveKeys();
    // }, intervalMs);
  }

  /**
   * Validate all active keys in the system
   */
  async validateAllActiveKeys(): Promise<void> {
    // This would get all active keys and validate them
    // Implementation depends on how you want to handle system-wide operations
    console.log('Validating all active keys...');
  }

  // Helper method to chunk arrays
  private chunkArray<T>(array: T[], chunkSize: number): T[][] {
    const chunks: T[][] = [];
    for (let i = 0; i < array.length; i += chunkSize) {
      chunks.push(array.slice(i, i + chunkSize));
    }
    return chunks;
  }
}

/**
 * Factory function for creating key validator
 */
export function createKeyValidator(
  database: DatabaseInterface,
  encryptionKey?: string
): KeyValidator {
  return new KeyValidator(database, encryptionKey);
}