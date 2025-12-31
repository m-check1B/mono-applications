export class TestUtils {
  static noop(): void {
    // Placeholder utility
  }

  static async waitForMicrotask(): Promise<void> {
    await Promise.resolve();
  }
}

export default TestUtils;
