/**
 * @stack-2025/byok-core - Telephony Core Integration
 * Integration with @stack-2025/telephony-core for BYOK key management
 */

import { BYOKManager } from '../manager.js';
import { ProviderType, Environment, DecryptedKey } from '../types.js';

/**
 * BYOK-enabled telephony configuration
 */
export class BYOKTelephonyConfig {
  private byokManager: BYOKManager;

  constructor(byokManager: BYOKManager) {
    this.byokManager = byokManager;
  }

  /**
   * Get Twilio configuration with BYOK key
   */
  async getTwilioConfig(
    userId: string,
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
      validateKey?: boolean;
    } = {}
  ) {
    const {
      environment = Environment.PRODUCTION,
      fallbackToSystem = true,
      validateKey = true
    } = options;

    try {
      const key = await this.byokManager.getActiveKey(userId, ProviderType.TWILIO, {
        environment,
        fallbackToSystem,
        validateKey
      });

      return this.createTwilioConfig(key);
    } catch (error) {
      if (fallbackToSystem) {
        const systemConfig = this.createTwilioSystemConfig();
        if (systemConfig.accountSid) {
          return systemConfig;
        }
      }
      
      throw new Error(`Failed to get Twilio configuration: ${error}`);
    }
  }

  /**
   * Get Telnyx configuration with BYOK key
   */
  async getTelnyxConfig(
    userId: string,
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
      validateKey?: boolean;
    } = {}
  ) {
    const {
      environment = Environment.PRODUCTION,
      fallbackToSystem = true,
      validateKey = true
    } = options;

    try {
      const key = await this.byokManager.getActiveKey(userId, ProviderType.TELNYX, {
        environment,
        fallbackToSystem,
        validateKey
      });

      return this.createTelnyxConfig(key);
    } catch (error) {
      if (fallbackToSystem) {
        const systemConfig = this.createTelnyxSystemConfig();
        if (systemConfig.apiKey) {
          return systemConfig;
        }
      }
      
      throw new Error(`Failed to get Telnyx configuration: ${error}`);
    }
  }

  /**
   * Create unified telephony client with BYOK
   */
  async createTelephonyClient(
    userId: string,
    provider: 'twilio' | 'telnyx',
    options: {
      environment?: Environment;
      fallbackToSystem?: boolean;
      capabilities?: string[];
    } = {}
  ) {
    const {
      environment = Environment.PRODUCTION,
      fallbackToSystem = true,
      capabilities = ['voice', 'sms']
    } = options;

    if (provider === 'twilio') {
      const config = await this.getTwilioConfig(userId, {
        environment,
        fallbackToSystem,
        validateKey: false // Skip validation for performance
      });

      return {
        provider: 'twilio',
        config,
        capabilities,
        
        // Client methods
        async makeCall(from: string, to: string, url: string) {
          return makeTwilioCall(config, from, to, url);
        },
        
        async sendSMS(from: string, to: string, body: string) {
          return sendTwilioSMS(config, from, to, body);
        },
        
        async getCallStatus(callSid: string) {
          return getTwilioCallStatus(config, callSid);
        },
        
        // BYOK metadata
        byok: {
          enabled: true,
          userId,
          keyId: config.keyId,
          environment
        }
      };
    } else if (provider === 'telnyx') {
      const config = await this.getTelnyxConfig(userId, {
        environment,
        fallbackToSystem,
        validateKey: false
      });

      return {
        provider: 'telnyx',
        config,
        capabilities,
        
        // Client methods
        async makeCall(from: string, to: string, webhookUrl: string) {
          return makeTelnyxCall(config, from, to, webhookUrl);
        },
        
        async sendSMS(from: string, to: string, text: string) {
          return sendTelnyxSMS(config, from, to, text);
        },
        
        async getCallStatus(callControlId: string) {
          return getTelnyxCallStatus(config, callControlId);
        },
        
        // BYOK metadata
        byok: {
          enabled: true,
          userId,
          keyId: config.keyId,
          environment
        }
      };
    } else {
      throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  /**
   * Get phone numbers available for user's telephony provider
   */
  async getAvailableNumbers(
    userId: string,
    provider: 'twilio' | 'telnyx',
    options: {
      environment?: Environment;
      countryCode?: string;
      capabilities?: string[];
    } = {}
  ) {
    const {
      environment = Environment.PRODUCTION,
      countryCode = 'US',
      capabilities = ['voice', 'SMS']
    } = options;

    if (provider === 'twilio') {
      const config = await this.getTwilioConfig(userId, { environment });
      return getTwilioAvailableNumbers(config, countryCode, capabilities);
    } else if (provider === 'telnyx') {
      const config = await this.getTelnyxConfig(userId, { environment });
      return getTelnyxAvailableNumbers(config, countryCode, capabilities);
    } else {
      throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  /**
   * Purchase phone number
   */
  async purchaseNumber(
    userId: string,
    provider: 'twilio' | 'telnyx',
    phoneNumber: string,
    options: {
      environment?: Environment;
      friendlyName?: string;
    } = {}
  ) {
    const { environment = Environment.PRODUCTION, friendlyName } = options;

    if (provider === 'twilio') {
      const config = await this.getTwilioConfig(userId, { environment });
      return purchaseTwilioNumber(config, phoneNumber, friendlyName);
    } else if (provider === 'telnyx') {
      const config = await this.getTelnyxConfig(userId, { environment });
      return purchaseTelnyxNumber(config, phoneNumber, friendlyName);
    } else {
      throw new Error(`Unsupported provider: ${provider}`);
    }
  }

  /**
   * Record telephony usage for billing
   */
  async recordUsage(
    userId: string,
    provider: 'twilio' | 'telnyx',
    usage: {
      operation: 'call' | 'sms' | 'mms';
      duration?: number; // for calls in seconds
      messageCount?: number; // for SMS/MMS
      from: string;
      to: string;
      cost?: number;
      success: boolean;
      error?: string;
    }
  ) {
    try {
      // This would integrate with BYOK usage tracking
      console.log(`Recording ${provider} usage for ${userId}:`, usage);
    } catch (error) {
      console.warn(`Failed to record ${provider} usage:`, error);
    }
  }

  // Private helper methods

  private createTwilioConfig(key: DecryptedKey) {
    const keyData = key.keyData as any;
    
    return {
      accountSid: keyData.accountSid,
      authToken: keyData.authToken,
      apiKeySid: keyData.apiKeySid,
      apiKeySecret: keyData.apiKeySecret,
      keyId: key.id,
      environment: key.environment,
      capabilities: key.capabilities,
      healthScore: key.healthScore,
      metadata: key.metadata
    };
  }

  private createTwilioSystemConfig() {
    return {
      accountSid: process.env.TWILIO_ACCOUNT_SID,
      authToken: process.env.TWILIO_AUTH_TOKEN,
      apiKeySid: process.env.TWILIO_API_KEY_SID,
      apiKeySecret: process.env.TWILIO_API_KEY_SECRET,
      keyId: 'system-fallback',
      environment: Environment.PRODUCTION,
      capabilities: ['voice', 'sms', 'whatsapp'],
      healthScore: 100,
      metadata: { isSystemFallback: true }
    };
  }

  private createTelnyxConfig(key: DecryptedKey) {
    const keyData = key.keyData as any;
    
    return {
      apiKey: keyData.apiKey,
      publicKey: keyData.publicKey,
      applicationId: keyData.applicationId,
      keyId: key.id,
      environment: key.environment,
      capabilities: key.capabilities,
      healthScore: key.healthScore,
      metadata: key.metadata
    };
  }

  private createTelnyxSystemConfig() {
    return {
      apiKey: process.env.TELNYX_API_KEY,
      publicKey: process.env.TELNYX_PUBLIC_KEY,
      applicationId: process.env.TELNYX_APPLICATION_ID,
      keyId: 'system-fallback',
      environment: Environment.PRODUCTION,
      capabilities: ['voice', 'sms'],
      healthScore: 100,
      metadata: { isSystemFallback: true }
    };
  }
}

// Twilio API wrapper functions
async function makeTwilioCall(config: any, from: string, to: string, url: string) {
  try {
    // Simulate Twilio API call
    const response = await fetch('https://api.twilio.com/2010-04-01/Accounts/' + config.accountSid + '/Calls.json', {
      method: 'POST',
      headers: {
        'Authorization': 'Basic ' + Buffer.from(`${config.accountSid}:${config.authToken}`).toString('base64'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        From: from,
        To: to,
        Url: url
      })
    });

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to make Twilio call: ${error}`);
  }
}

async function sendTwilioSMS(config: any, from: string, to: string, body: string) {
  try {
    const response = await fetch('https://api.twilio.com/2010-04-01/Accounts/' + config.accountSid + '/Messages.json', {
      method: 'POST',
      headers: {
        'Authorization': 'Basic ' + Buffer.from(`${config.accountSid}:${config.authToken}`).toString('base64'),
        'Content-Type': 'application/x-www-form-urlencoded'
      },
      body: new URLSearchParams({
        From: from,
        To: to,
        Body: body
      })
    });

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to send Twilio SMS: ${error}`);
  }
}

async function getTwilioCallStatus(config: any, callSid: string) {
  try {
    const response = await fetch(`https://api.twilio.com/2010-04-01/Accounts/${config.accountSid}/Calls/${callSid}.json`, {
      headers: {
        'Authorization': 'Basic ' + Buffer.from(`${config.accountSid}:${config.authToken}`).toString('base64')
      }
    });

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to get Twilio call status: ${error}`);
  }
}

async function getTwilioAvailableNumbers(config: any, countryCode: string, capabilities: string[]) {
  try {
    const response = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${config.accountSid}/AvailablePhoneNumbers/${countryCode}/Local.json`,
      {
        headers: {
          'Authorization': 'Basic ' + Buffer.from(`${config.accountSid}:${config.authToken}`).toString('base64')
        }
      }
    );

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to get Twilio available numbers: ${error}`);
  }
}

async function purchaseTwilioNumber(config: any, phoneNumber: string, friendlyName?: string) {
  try {
    const body = new URLSearchParams({ PhoneNumber: phoneNumber });
    if (friendlyName) {
      body.set('FriendlyName', friendlyName);
    }

    const response = await fetch(
      `https://api.twilio.com/2010-04-01/Accounts/${config.accountSid}/IncomingPhoneNumbers.json`,
      {
        method: 'POST',
        headers: {
          'Authorization': 'Basic ' + Buffer.from(`${config.accountSid}:${config.authToken}`).toString('base64'),
          'Content-Type': 'application/x-www-form-urlencoded'
        },
        body
      }
    );

    if (!response.ok) {
      throw new Error(`Twilio API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to purchase Twilio number: ${error}`);
  }
}

// Telnyx API wrapper functions (simplified implementations)
async function makeTelnyxCall(config: any, from: string, to: string, webhookUrl: string) {
  try {
    const response = await fetch('https://api.telnyx.com/v2/calls', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from,
        to,
        webhook_url: webhookUrl,
        connection_id: config.applicationId
      })
    });

    if (!response.ok) {
      throw new Error(`Telnyx API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to make Telnyx call: ${error}`);
  }
}

async function sendTelnyxSMS(config: any, from: string, to: string, text: string) {
  try {
    const response = await fetch('https://api.telnyx.com/v2/messages', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from,
        to,
        text
      })
    });

    if (!response.ok) {
      throw new Error(`Telnyx API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to send Telnyx SMS: ${error}`);
  }
}

async function getTelnyxCallStatus(config: any, callControlId: string) {
  try {
    const response = await fetch(`https://api.telnyx.com/v2/calls/${callControlId}`, {
      headers: {
        'Authorization': `Bearer ${config.apiKey}`
      }
    });

    if (!response.ok) {
      throw new Error(`Telnyx API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to get Telnyx call status: ${error}`);
  }
}

async function getTelnyxAvailableNumbers(config: any, countryCode: string, capabilities: string[]) {
  try {
    const params = new URLSearchParams({
      'filter[country_code]': countryCode,
      'filter[features]': capabilities.join(',')
    });

    const response = await fetch(`https://api.telnyx.com/v2/available_phone_numbers?${params}`, {
      headers: {
        'Authorization': `Bearer ${config.apiKey}`
      }
    });

    if (!response.ok) {
      throw new Error(`Telnyx API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to get Telnyx available numbers: ${error}`);
  }
}

async function purchaseTelnyxNumber(config: any, phoneNumber: string, friendlyName?: string) {
  try {
    const response = await fetch('https://api.telnyx.com/v2/phone_numbers', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${config.apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        phone_number: phoneNumber,
        ...(friendlyName && { name: friendlyName })
      })
    });

    if (!response.ok) {
      throw new Error(`Telnyx API error: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    throw new Error(`Failed to purchase Telnyx number: ${error}`);
  }
}

/**
 * Factory function for BYOK telephony integration
 */
export function createBYOKTelephonyIntegration(byokManager: BYOKManager) {
  return {
    config: new BYOKTelephonyConfig(byokManager)
  };
}