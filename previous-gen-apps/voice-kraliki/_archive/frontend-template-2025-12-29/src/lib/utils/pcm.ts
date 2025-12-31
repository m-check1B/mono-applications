export function float32ToInt16(float32: Float32Array): Int16Array {
	const int16 = new Int16Array(float32.length);
	for (let i = 0; i < float32.length; i += 1) {
		const s = Math.max(-1, Math.min(1, float32[i]));
		int16[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
	}
	return int16;
}

export function uint8ToBase64(bytes: Uint8Array): string {
	let binary = '';
	const len = bytes.byteLength;
	for (let i = 0; i < len; i += 1) {
		binary += String.fromCharCode(bytes[i]);
	}
	return btoa(binary);
}

export function int16ToBase64(int16: Int16Array): string {
	return uint8ToBase64(new Uint8Array(int16.buffer));
}
