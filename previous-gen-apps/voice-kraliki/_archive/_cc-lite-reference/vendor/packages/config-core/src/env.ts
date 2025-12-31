import { z } from 'zod';

export const stackEnvSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']).default('development'),
  DATABASE_URL: z.string().min(1, 'DATABASE_URL is required'),
  FRONTEND_URL: z.string().url().optional(),
});

export type StackEnv = z.infer<typeof stackEnvSchema>;

export function loadEnv<T extends z.ZodTypeAny>(schema: T): z.infer<T> {
  // Map process.env (string | undefined) into object and parse
  const input: Record<string, unknown> = { ...process.env };
  const parsed = schema.safeParse(input);
  if (!parsed.success) {
    const issues = parsed.error.issues.map(i => `${i.path.join('.')}: ${i.message}`).join('; ');
    throw new Error(`[config-core] Invalid environment configuration: ${issues}`);
  }
  return parsed.data;
}

export function requireInProduction(env: StackEnv, keys: (keyof StackEnv)[]) {
  if (env.NODE_ENV !== 'production') return;
  const missing = keys.filter((k) => !env[k]);
  if (missing.length) {
    throw new Error(`[config-core] Missing required env in production: ${missing.join(', ')}`);
  }
}

