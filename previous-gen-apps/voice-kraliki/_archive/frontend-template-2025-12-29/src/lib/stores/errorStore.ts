import { writable } from 'svelte/store';

export interface ErrorDetails {
  id: string;
  message: string;
  stack?: string;
  component?: string;
  timestamp: Date;
  severity: 'error' | 'warning' | 'info';
  recovered: boolean;
}

function createErrorStore() {
  const { subscribe, update } = writable<ErrorDetails[]>([]);

  return {
    subscribe,
    addError: (error: Omit<ErrorDetails, 'id' | 'timestamp'>) => {
      update(errors => [
        ...errors,
        {
          ...error,
          id: crypto.randomUUID(),
          timestamp: new Date()
        }
      ]);
    },
    clearError: (id: string) => {
      update(errors => errors.filter(e => e.id !== id));
    },
    clearAll: () => {
      update(() => []);
    }
  };
}

export const errorStore = createErrorStore();
