/**
 * Progress Store - Track user learning progress
 */

import { writable, derived } from 'svelte/store';
import type { Progress } from '$api/client';

interface ProgressState {
  courses: Record<string, Progress>;
  loading: boolean;
  error: string | null;
}

function createProgressStore() {
  const { subscribe, set, update } = writable<ProgressState>({
    courses: {},
    loading: false,
    error: null,
  });

  return {
    subscribe,

    setLoading(loading: boolean) {
      update(state => ({ ...state, loading }));
    },

    setError(error: string | null) {
      update(state => ({ ...state, error }));
    },

    setCourseProgress(courseSlug: string, progress: Progress) {
      update(state => ({
        ...state,
        courses: {
          ...state.courses,
          [courseSlug]: progress,
        },
      }));
    },

    markLessonComplete(courseSlug: string, lessonId: string) {
      update(state => {
        const current = state.courses[courseSlug];
        if (!current) return state;

        return {
          ...state,
          courses: {
            ...state.courses,
            [courseSlug]: {
              ...current,
              completed_lessons: [...current.completed_lessons, lessonId],
            },
          },
        };
      });
    },

    reset() {
      set({
        courses: {},
        loading: false,
        error: null,
      });
    },
  };
}

export const progressStore = createProgressStore();

// Derived store for a specific course
export function getCourseProgress(courseSlug: string) {
  return derived(progressStore, $state => $state.courses[courseSlug] || null);
}
