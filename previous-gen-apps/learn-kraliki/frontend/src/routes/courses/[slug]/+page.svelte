<script lang="ts">
  import { page } from '$app/stores';
  import { onMount } from 'svelte';
  import { marked } from 'marked';

  interface Lesson {
    id: string;
    title: string;
    order: number;
  }

  interface Course {
    slug: string;
    title: string;
    description: string;
    lessons: Lesson[];
    level: string;
    duration_minutes: number;
  }

  let course: Course | null = $state(null);
  let currentLesson: Lesson | null = $state(null);
  let lessonContent = $state('');
  let loading = $state(true);
  let error = $state('');

  // Track which lesson is selected (default to first)
  let selectedLessonId = $state('');

  $effect(() => {
    const slug = $page.params.slug;
    if (slug) {
      loadCourse(slug);
    }
  });

  async function loadCourse(slug: string) {
    loading = true;
    error = '';

    try {
      const res = await fetch(`/api/courses/${slug}`);
      if (!res.ok) throw new Error('Course not found');
      course = await res.json();

      // Auto-select first lesson if available
      if (course && course.lessons.length > 0) {
        selectedLessonId = course.lessons[0].id;
        await loadLesson(course.lessons[0].id);
      }
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load course';
    } finally {
      loading = false;
    }
  }

  async function loadLesson(lessonId: string) {
    if (!course) return;

    selectedLessonId = lessonId;
    currentLesson = course.lessons.find(l => l.id === lessonId) || null;

    try {
      const res = await fetch(`/api/courses/${course.slug}/lessons/${lessonId}`);
      if (!res.ok) throw new Error('Lesson not found');
      const data = await res.json();
      lessonContent = await marked(data.content);
    } catch (e) {
      lessonContent = '<p class="text-red-600">Failed to load lesson content.</p>';
    }
  }

  function getCurrentLessonIndex(): number {
    if (!course || !selectedLessonId) return -1;
    return course.lessons.findIndex(l => l.id === selectedLessonId);
  }

  function hasPrevious(): boolean {
    return getCurrentLessonIndex() > 0;
  }

  function hasNext(): boolean {
    if (!course) return false;
    return getCurrentLessonIndex() < course.lessons.length - 1;
  }

  function goToPrevious() {
    if (!course || !hasPrevious()) return;
    const idx = getCurrentLessonIndex();
    loadLesson(course.lessons[idx - 1].id);
  }

  function goToNext() {
    if (!course || !hasNext()) return;
    const idx = getCurrentLessonIndex();
    loadLesson(course.lessons[idx + 1].id);
  }
</script>

<svelte:head>
  <title>{course?.title || 'Loading...'} - Learn by Kraliki</title>
</svelte:head>

{#if loading}
  <div class="max-w-4xl mx-auto px-4 py-12 text-center">
    <div class="text-2xl font-bold">Loading course...</div>
  </div>
{:else if error}
  <div class="max-w-4xl mx-auto px-4 py-12">
    <div class="card bg-red-50 text-red-700">
      <p class="font-bold">Error: {error}</p>
      <a href="/" class="btn-secondary inline-block mt-4">Back to Courses</a>
    </div>
  </div>
{:else if course}
  <div class="flex min-h-[calc(100vh-200px)]">
    <!-- Sidebar: Lesson List -->
    <aside class="w-80 bg-white border-r-4 border-black p-6 overflow-y-auto">
      <a href="/" class="text-sm font-bold text-gray-500 hover:text-black mb-4 block">
        &larr; ALL COURSES
      </a>

      <h2 class="text-xl font-black mb-2">{course.title}</h2>
      <p class="text-sm text-gray-500 mb-6">{course.lessons.length} lessons</p>

      <nav class="space-y-2">
        {#each course.lessons as lesson, index}
          <button
            onclick={() => loadLesson(lesson.id)}
            class="w-full text-left p-3 border-2 border-black transition-all
                   {selectedLessonId === lesson.id
                     ? 'bg-black text-white'
                     : 'bg-white hover:bg-gray-100'}"
          >
            <span class="text-sm font-bold">{index + 1}. {lesson.title}</span>
          </button>
        {/each}
      </nav>

      <!-- Progress indicator -->
      <div class="mt-8 pt-6 border-t-2 border-gray-200">
        <div class="text-sm font-bold text-gray-500 mb-2">PROGRESS</div>
        <div class="progress-bar">
          <div
            class="progress-bar-fill"
            style="width: {Math.round(((getCurrentLessonIndex() + 1) / course.lessons.length) * 100)}%"
          ></div>
        </div>
        <div class="text-sm text-gray-500 mt-1">
          {getCurrentLessonIndex() + 1} / {course.lessons.length} lessons
        </div>
      </div>
    </aside>

    <!-- Main Content: Lesson Viewer -->
    <main class="flex-1 p-8 overflow-y-auto">
      {#if currentLesson}
        <div class="max-w-3xl mx-auto">
          <!-- Lesson Header -->
          <div class="mb-8">
            <span class="text-sm font-bold text-gray-500">
              LESSON {getCurrentLessonIndex() + 1}
            </span>
            <h1 class="text-4xl font-black mt-2">{currentLesson.title}</h1>
          </div>

          <!-- Lesson Content -->
          <article class="lesson-content">
            {@html lessonContent}
          </article>

          <!-- Navigation Buttons -->
          <div class="flex justify-between items-center mt-12 pt-8 border-t-4 border-black">
            <button
              onclick={goToPrevious}
              disabled={!hasPrevious()}
              class="btn-secondary disabled:opacity-50 disabled:cursor-not-allowed"
            >
              &larr; PREVIOUS
            </button>

            {#if hasNext()}
              <button onclick={goToNext} class="btn-primary">
                NEXT &rarr;
              </button>
            {:else}
              <a href="/" class="btn-primary">
                COMPLETE COURSE
              </a>
            {/if}
          </div>
        </div>
      {:else}
        <div class="text-center py-12">
          <p class="text-gray-500">Select a lesson to begin</p>
        </div>
      {/if}
    </main>
  </div>
{/if}
