/**
 * Provider implementations and registrations
 */

// Import implementations
import { TwilioClient } from './twilio';
import { OpenAITTSClient } from './openai-tts';
import { AWSPollyClient } from './aws-polly';

// Import factories
import { TelephonyProviderFactory } from '../telephony';
import { TTSProviderFactory } from '../voice';

// Register telephony providers
TelephonyProviderFactory.register('twilio', TwilioClient);

// Register TTS providers
TTSProviderFactory.register('openai-tts', OpenAITTSClient);
TTSProviderFactory.register('aws-polly', AWSPollyClient);

// Export implementations
export { 
  TwilioClient,
  OpenAITTSClient,
  AWSPollyClient 
};

// Export factories (already exported from main index)
export {
  TelephonyProviderFactory,
  TTSProviderFactory
};