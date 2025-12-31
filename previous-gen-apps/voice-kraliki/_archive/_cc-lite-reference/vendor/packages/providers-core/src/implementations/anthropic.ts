/**
 * Anthropic Claude implementation
 */

import { BaseLLMClient, LLMProvider, Message, CompletionOptions, CompletionResponse, ModelId } from '../llm';

export class AnthropicClient extends BaseLLMClient {
  provider: LLMProvider = 'anthropic';
  
  private apiUrl = 'https://api.anthropic.com/v1';
  
  async complete(messages: Message[], options?: CompletionOptions): Promise<CompletionResponse> {
    const response = await fetch(`${this.apiUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.config.apiKey!,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: options?.model || this.config.defaultModel || 'claude-3-sonnet-20240229',
        messages: messages.map(m => ({
          role: m.role === 'system' ? 'user' : m.role,
          content: m.role === 'system' ? `System: ${m.content}` : m.content,
        })),
        max_tokens: options?.maxTokens || 1024,
        temperature: options?.temperature,
        stop_sequences: options?.stopSequences,
        stream: false,
      }),
    });

    if (!response.ok) {
      throw new Error(`Anthropic API error: ${response.statusText}`);
    }

    const data = await response.json() as any;
    
    return {
      content: data.content[0].text,
      usage: {
        promptTokens: data.usage.input_tokens,
        completionTokens: data.usage.output_tokens,
        totalTokens: data.usage.input_tokens + data.usage.output_tokens,
      },
      model: data.model,
      finishReason: data.stop_reason as any,
    };
  }

  async *completeStream(messages: Message[], options?: CompletionOptions): AsyncIterable<string> {
    const response = await fetch(`${this.apiUrl}/messages`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': this.config.apiKey!,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify({
        model: options?.model || this.config.defaultModel || 'claude-3-sonnet-20240229',
        messages: messages.map(m => ({
          role: m.role === 'system' ? 'user' : m.role,
          content: m.role === 'system' ? `System: ${m.content}` : m.content,
        })),
        max_tokens: options?.maxTokens || 1024,
        temperature: options?.temperature,
        stop_sequences: options?.stopSequences,
        stream: true,
      }),
    });

    if (!response.ok || !response.body) {
      throw new Error(`Anthropic API error: ${response.statusText}`);
    }

    const reader = response.body.getReader();
    const decoder = new TextDecoder();

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      const chunk = decoder.decode(value);
      const lines = chunk.split('\n');
      
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6);
          if (data === '[DONE]') continue;
          
          try {
            const parsed = JSON.parse(data);
            if (parsed.delta?.text) {
              yield parsed.delta.text;
            }
          } catch (e) {
            // Skip invalid JSON
          }
        }
      }
    }
  }

  async embed(texts: string[], model?: string): Promise<number[][]> {
    // Anthropic doesn't have embeddings API yet
    throw new Error('Anthropic does not support embeddings. Use OpenAI or another provider.');
  }

  async listModels(): Promise<ModelId[]> {
    return [
      'anthropic/claude-3-opus-20240229',
      'anthropic/claude-3-sonnet-20240229',
      'anthropic/claude-3-haiku-20240307',
    ];
  }
}