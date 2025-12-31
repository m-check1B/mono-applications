import { z } from 'zod';

// User validation schemas
export const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
});

export const registerSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
  name: z.string().min(1, 'Name is required').optional(),
});

// Task validation schemas
export const createTaskSchema = z.object({
  title: z.string().min(1, 'Title is required').max(200),
  description: z.string().optional(),
  status: z.enum(['TODO', 'IN_PROGRESS', 'DONE', 'CANCELLED']).default('TODO'),
  priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'URGENT']).default('MEDIUM'),
  dueDate: z.string().datetime().optional(),
});

export const updateTaskSchema = createTaskSchema.partial();

// Call validation schemas
export const createCallSchema = z.object({
  phoneNumber: z.string().regex(/^\+?[1-9]\d{1,14}$/, 'Invalid phone number'),
  direction: z.enum(['INBOUND', 'OUTBOUND']),
});

// API response schemas
export const apiResponseSchema = <T extends z.ZodType>(dataSchema: T) =>
  z.object({
    success: z.boolean(),
    data: dataSchema.optional(),
    error: z.object({
      message: z.string(),
      code: z.string().optional(),
      details: z.any().optional(),
    }).optional(),
    meta: z.object({
      timestamp: z.string().datetime(),
      requestId: z.string(),
    }).optional(),
  });

// Pagination schemas
export const paginationQuerySchema = z.object({
  page: z.coerce.number().int().positive().default(1),
  limit: z.coerce.number().int().positive().max(100).default(20),
  sortBy: z.string().optional(),
  sortOrder: z.enum(['asc', 'desc']).default('desc'),
});

export const paginatedResponseSchema = <T extends z.ZodType>(itemSchema: T) =>
  z.object({
    items: z.array(itemSchema),
    pagination: z.object({
      page: z.number(),
      limit: z.number(),
      total: z.number(),
      totalPages: z.number(),
      hasNext: z.boolean(),
      hasPrev: z.boolean(),
    }),
  });

// Export types
export type LoginInput = z.infer<typeof loginSchema>;
export type RegisterInput = z.infer<typeof registerSchema>;
export type CreateTaskInput = z.infer<typeof createTaskSchema>;
export type UpdateTaskInput = z.infer<typeof updateTaskSchema>;
export type CreateCallInput = z.infer<typeof createCallSchema>;
export type PaginationQuery = z.infer<typeof paginationQuerySchema>;