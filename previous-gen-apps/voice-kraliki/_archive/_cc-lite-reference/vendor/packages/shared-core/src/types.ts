// Common types shared across the application

// API Response types
export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: {
    message: string;
    code?: string;
    details?: unknown;
  };
  meta?: {
    timestamp: string;
    requestId: string;
  };
}

// Pagination types
export interface PaginationParams {
  page: number;
  limit: number;
  sortBy?: string;
  sortOrder?: 'asc' | 'desc';
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination: {
    page: number;
    limit: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrev: boolean;
  };
}

// User types
export interface User {
  id: string;
  email: string;
  name?: string;
  emailVerified: boolean;
  createdAt: Date;
  updatedAt: Date;
}

export interface Session {
  id: string;
  token: string;
  userId: string;
  expiresAt: Date;
  createdAt: Date;
  updatedAt: Date;
}

// Task types
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'DONE' | 'CANCELLED';
export type Priority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: Priority;
  dueDate?: Date;
  completedAt?: Date;
  userId: string;
  createdAt: Date;
  updatedAt: Date;
}

// Call types
export type CallDirection = 'INBOUND' | 'OUTBOUND';
export type CallStatus = 
  | 'INITIATED'
  | 'RINGING'
  | 'IN_PROGRESS'
  | 'COMPLETED'
  | 'FAILED'
  | 'NO_ANSWER'
  | 'BUSY'
  | 'CANCELLED';

export interface Call {
  id: string;
  phoneNumber: string;
  direction: CallDirection;
  status: CallStatus;
  duration?: number;
  recordingUrl?: string;
  transcription?: string;
  userId?: string;
  startedAt: Date;
  endedAt?: Date;
  createdAt: Date;
  updatedAt: Date;
}

// WebSocket event types
export interface WebSocketMessage<T = unknown> {
  type: string;
  payload: T;
  timestamp: string;
}

export interface WebSocketError {
  code: string;
  message: string;
  details?: unknown;
}

// Environment types
export type Environment = 'development' | 'test' | 'staging' | 'production';

// Feature flags
export interface FeatureFlags {
  enableCalls: boolean;
  enableTasks: boolean;
  enableAI: boolean;
  enableWebSockets: boolean;
  maxConcurrentCalls: number;
  maxTasksPerUser: number;
}