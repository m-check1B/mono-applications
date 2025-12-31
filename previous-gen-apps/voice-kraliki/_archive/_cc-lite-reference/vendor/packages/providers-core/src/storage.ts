/**
 * Unified Storage Provider Interface
 * Supports SQL, NoSQL, Vector, and Object storage providers
 */

// Storage provider types
export type StorageProvider = 
  | 'postgresql'
  | 'mysql'
  | 'sqlite'
  | 'mongodb'
  | 'redis'
  | 'dynamodb'
  | 'firestore'
  | 'supabase'
  | 'pinecone'
  | 'qdrant'
  | 'weaviate'
  | 's3'
  | 'gcs'
  | 'azure-blob';

// Storage types
export type StorageType = 'sql' | 'nosql' | 'vector' | 'object' | 'cache';

// Common storage object
export interface StorageObject {
  id: string;
  data: any;
  metadata?: Record<string, any>;
  createdAt?: Date;
  updatedAt?: Date;
  ttl?: number; // Time to live in seconds
}

// Query options
export interface QueryOptions {
  limit?: number;
  offset?: number;
  orderBy?: string;
  order?: 'asc' | 'desc';
  where?: Record<string, any>;
  select?: string[];
  include?: string[]; // Relations to include
}

// Vector search options
export interface VectorSearchOptions {
  vector: number[];
  topK?: number;
  threshold?: number; // Similarity threshold
  filter?: Record<string, any>;
  includeMetadata?: boolean;
  includeDistances?: boolean;
}

// Transaction support
export interface Transaction {
  commit(): Promise<void>;
  rollback(): Promise<void>;
  execute<T>(fn: () => Promise<T>): Promise<T>;
}

// Main storage client interface
export interface StorageClient {
  provider: StorageProvider;
  type: StorageType;
  
  // CRUD operations
  get(collection: string, id: string): Promise<StorageObject | null>;
  
  create(collection: string, data: any, id?: string): Promise<StorageObject>;
  
  update(collection: string, id: string, data: any): Promise<StorageObject>;
  
  delete(collection: string, id: string): Promise<boolean>;
  
  // Query operations
  query(collection: string, options?: QueryOptions): Promise<StorageObject[]>;
  
  count(collection: string, where?: Record<string, any>): Promise<number>;
  
  // Batch operations
  batchCreate?(collection: string, items: any[]): Promise<StorageObject[]>;
  
  batchDelete?(collection: string, ids: string[]): Promise<number>;
  
  // Vector operations (for vector databases)
  vectorSearch?(collection: string, options: VectorSearchOptions): Promise<Array<{
    id: string;
    data: any;
    distance?: number;
    metadata?: Record<string, any>;
  }>>;
  
  upsertVector?(collection: string, id: string, vector: number[], metadata?: any): Promise<void>;
  
  // Transaction support (for SQL databases)
  beginTransaction?(): Promise<Transaction>;
  
  // Schema operations
  createCollection?(name: string, schema?: any): Promise<void>;
  
  dropCollection?(name: string): Promise<void>;
  
  listCollections?(): Promise<string[]>;
  
  // Connection management
  connect(): Promise<void>;
  
  disconnect(): Promise<void>;
  
  ping(): Promise<boolean>;
}

// Base implementation
export abstract class BaseStorageClient implements StorageClient {
  abstract provider: StorageProvider;
  abstract type: StorageType;
  
  constructor(protected config: {
    connectionString?: string;
    host?: string;
    port?: number;
    database?: string;
    username?: string;
    password?: string;
    apiKey?: string;
    region?: string;
    ssl?: boolean;
  }) {}
  
  abstract get(collection: string, id: string): Promise<StorageObject | null>;
  abstract create(collection: string, data: any, id?: string): Promise<StorageObject>;
  abstract update(collection: string, id: string, data: any): Promise<StorageObject>;
  abstract delete(collection: string, id: string): Promise<boolean>;
  abstract query(collection: string, options?: QueryOptions): Promise<StorageObject[]>;
  abstract count(collection: string, where?: Record<string, any>): Promise<number>;
  abstract connect(): Promise<void>;
  abstract disconnect(): Promise<void>;
  abstract ping(): Promise<boolean>;
}

// Factory for creating clients
export class StorageProviderFactory {
  private static providers = new Map<StorageProvider, typeof BaseStorageClient>();
  
  static register(provider: StorageProvider, clientClass: typeof BaseStorageClient) {
    this.providers.set(provider, clientClass);
  }
  
  static create(provider: StorageProvider, config: any): StorageClient {
    const ClientClass = this.providers.get(provider);
    if (!ClientClass) {
      throw new Error(`Storage provider ${provider} not registered`);
    }
    return new (ClientClass as any)(config);
  }
}

// Helper type for Prisma-like query building
export interface QueryBuilder<T> {
  where(conditions: Partial<T>): QueryBuilder<T>;
  orderBy(field: keyof T, order?: 'asc' | 'desc'): QueryBuilder<T>;
  limit(n: number): QueryBuilder<T>;
  offset(n: number): QueryBuilder<T>;
  include(relations: string[]): QueryBuilder<T>;
  execute(): Promise<T[]>;
  first(): Promise<T | null>;
  count(): Promise<number>;
}