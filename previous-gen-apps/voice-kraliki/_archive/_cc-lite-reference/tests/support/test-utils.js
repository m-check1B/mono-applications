class TestUtils {
  static noop() {}
  static async waitForMicrotask() {
    await Promise.resolve();
  }
}

module.exports = { TestUtils };
