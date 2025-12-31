/**
 * Learn by Kraliki - API Client
 * Handles all API requests to the backend
 */

const API_BASE = '/api';

export interface Course {
  slug: string;
  title: string;
  description: string;
  lessons_count: number;
  level: string;
  duration_minutes: number;
  is_free: boolean;
}

export interface CourseDetail extends Course {
  lessons: Lesson[];
}

export interface Lesson {
  id: string;
  title: string;
  order: number;
}

export interface LessonContent {
  id: string;
  title: string;
  content: string;
}

export interface Progress {
  course_slug: string;
  completed_lessons: string[];
  current_lesson: string;
  percent_complete: number;
}

class ApiClient {
  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${API_BASE}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    });

    if (!res.ok) {
      const error = await res.json().catch(() => ({ detail: 'Request failed' }));
      throw new Error(error.detail || 'Request failed');
    }

    return res.json();
  }

  // Courses
  async getCourses(): Promise<Course[]> {
    return this.fetch('/courses');
  }

  async getCourse(slug: string): Promise<CourseDetail> {
    return this.fetch(`/courses/${slug}`);
  }

  async getLesson(courseSlug: string, lessonId: string): Promise<LessonContent> {
    return this.fetch(`/courses/${courseSlug}/lessons/${lessonId}`);
  }

  // Progress
  async getProgress(): Promise<Progress[]> {
    return this.fetch('/progress');
  }

  async getCourseProgress(courseSlug: string): Promise<Progress> {
    return this.fetch(`/progress/${courseSlug}`);
  }

  async markLessonComplete(courseSlug: string, lessonId: string): Promise<Progress> {
    return this.fetch(`/progress/${courseSlug}/${lessonId}`, {
      method: 'POST',
    });
  }
}

export const api = new ApiClient();
