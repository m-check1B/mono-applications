class AudioProcessor extends AudioWorkletProcessor {
  constructor() {
    super();
    this.frameSize = 960; // 20ms at 48kHz mono
  }

  process(inputs) {
    const input = inputs[0];
    if (!input || input.length === 0) {
      return true;
    }

    const channelData = input[0];
    if (!channelData) {
      return true;
    }

    const int16 = new Int16Array(channelData.length);
    for (let i = 0; i < channelData.length; i += 1) {
      const sample = Math.max(-1, Math.min(1, channelData[i]));
      int16[i] = sample < 0 ? sample * 0x8000 : sample * 0x7fff;
    }

    this.port.postMessage({ type: 'audioData', buffer: int16 });
    return true;
  }
}

registerProcessor('audio-processor', AudioProcessor);
