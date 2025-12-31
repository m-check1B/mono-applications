<script lang="ts">
  import { onMount } from 'svelte';

  interface Course {
    slug: string;
    title: string;
    description: string;
    lessons_count: number;
    level: string;
    duration_minutes: number;
    is_free: boolean;
  }

  let courses: Course[] = $state([]);
  let loading = $state(true);
  let error = $state('');

  onMount(async () => {
    try {
      const res = await fetch('/api/courses');
      if (!res.ok) throw new Error('Failed to load courses');
      courses = await res.json();
    } catch (e) {
      error = e instanceof Error ? e.message : 'Failed to load courses';
    } finally {
      loading = false;
    }
  });

  function getLevelColor(level: string): string {
    switch (level.toLowerCase()) {
      case 'beginner': return 'bg-green-500';
      case 'intermediate': return 'bg-yellow-500';
      case 'advanced': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  }
</script>

<svelte:head>
  <title>Learn by Kraliki - Course Catalog</title>
</svelte:head>

<div class="max-w-6xl mx-auto px-4 py-12">
  <!-- Hero Section -->
  <div class="text-center mb-16">
    <h1 class="text-6xl font-black mb-6 tracking-tight">
      LEARN<span class="text-blue-500">.</span>BUILD<span class="text-blue-500">.</span>GROW
    </h1>
    <p class="text-xl max-w-2xl mx-auto">
      Master the Kraliki ecosystem and AI fundamentals with our structured courses.
      Start free, go as deep as you want.
    </p>
  </div>

  <!-- Course Grid -->
  {#if loading}
    <div class="text-center py-12">
      <div class="text-2xl font-bold">Loading courses...</div>
    </div>
  {:else if error}
    <div class="card bg-red-50 text-red-700">
      <p class="font-bold">Error: {error}</p>
      <p class="mt-2">Make sure the backend is running on port 8030.</p>
    </div>
  {:else if courses.length === 0}
    <div class="text-center py-12">
      <div class="text-2xl font-bold">No courses available yet</div>
      <p class="mt-2 text-gray-600">Check back soon!</p>
    </div>
  {:else}
    <div class="grid md:grid-cols-2 gap-8">
      {#each courses as course}
        <a href="/courses/{course.slug}" class="card group block transition-transform">
          <div class="flex items-center gap-3 mb-4">
            <span class="{getLevelColor(course.level)} text-white text-xs font-bold px-3 py-1 uppercase">
              {course.level}
            </span>
            {#if course.is_free}
              <span class="bg-blue-500 text-white text-xs font-bold px-3 py-1 uppercase">
                FREE
              </span>
            {/if}
          </div>

          <h2 class="text-2xl font-black mb-3 group-hover:text-blue-600 transition-colors">
            {course.title}
          </h2>

          <p class="text-gray-600 mb-4">
            {course.description}
          </p>

          <div class="flex items-center gap-6 text-sm font-bold text-gray-500">
            <span>{course.lessons_count} LESSONS</span>
            <span>{course.duration_minutes} MIN</span>
          </div>

          <div class="mt-6 pt-4 border-t-2 border-gray-200">
            <span class="btn-secondary inline-block text-sm">
              START LEARNING
            </span>
          </div>
        </a>
      {/each}
    </div>
  {/if}

  <!-- CTA Section -->
  <div class="mt-16 card bg-black text-white text-center">
    <h2 class="text-3xl font-black mb-4">Ready for AI Academy?</h2>
    <p class="mb-6 text-gray-300">
      Go from AI basics to architecture mastery with our comprehensive L1-L4 program.
    </p>
    <a href="/courses/ai-fundamentals" class="btn-primary bg-white text-black hover:bg-gray-200 inline-block">
      PREVIEW AI FUNDAMENTALS
    </a>
  </div>
</div>
