// Minimal ESM specifier loader to resolve extensionless relative imports
// Tries appending ".js" and "/index.js" when default resolution fails.

export async function resolve(specifier, context, defaultResolve) {
  try {
    return await defaultResolve(specifier, context, defaultResolve);
  } catch (e) {
    // Only attempt for relative or absolute file specifiers
    const isRelative = specifier.startsWith('./') || specifier.startsWith('../');
    const isAbsolute = specifier.startsWith('/') || specifier.startsWith('file:');
    if (!isRelative && !isAbsolute) {
      throw e;
    }

    // Try with .js
    try {
      return await defaultResolve(specifier + '.js', context, defaultResolve);
    } catch {}

    // Try index.js in directory
    try {
      const indexSpecifier = specifier.endsWith('/') ? specifier + 'index.js' : specifier + '/index.js';
      return await defaultResolve(indexSpecifier, context, defaultResolve);
    } catch {}

    throw e;
  }
}

