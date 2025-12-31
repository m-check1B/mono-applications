<script lang="ts">
  import AIReadinessAssessment from '$lib/components/AIReadinessAssessment.svelte';

  interface AssessmentResult {
    score: number;
    maxScore: number;
    percentage: number;
    level: string;
    recommendations: string[];
    email: string;
  }

  let completed = $state(false);
  let finalResult: AssessmentResult | null = $state(null);

  function handleComplete(result: AssessmentResult) {
    completed = true;
    finalResult = result;
    // Could trigger analytics, etc.
    console.log('Assessment completed:', result.level, result.percentage);
  }
</script>

<svelte:head>
  <title>AI Readiness Assessment | Learn by Kraliki</title>
  <meta name="description" content="Take our free AI Readiness Assessment to discover how prepared your organization is for AI transformation. Get personalized recommendations and a roadmap." />
  <meta property="og:title" content="AI Readiness Assessment | Verduona" />
  <meta property="og:description" content="Free assessment to evaluate your organization's AI readiness. Get your score and personalized recommendations in 5 minutes." />
  <meta property="og:type" content="website" />
</svelte:head>

<div class="min-h-screen bg-gray-50">
  <!-- Hero Section -->
  <div class="bg-black text-white py-12 px-4">
    <div class="max-w-4xl mx-auto text-center">
      <div class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">
        FREE ASSESSMENT
      </div>
      <h1 class="text-4xl md:text-5xl font-black mb-6">
        Is Your Organization
        <span class="text-blue-400">AI-Ready</span>?
      </h1>
      <p class="text-xl text-gray-300 max-w-2xl mx-auto">
        Answer 12 quick questions to get your AI Readiness Score and
        personalized recommendations for your digital transformation journey.
      </p>
      <div class="mt-6 flex items-center justify-center gap-6 text-sm">
        <span class="flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          5 minutes
        </span>
        <span class="flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          100% Free
        </span>
        <span class="flex items-center gap-2">
          <svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20">
            <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
          </svg>
          Instant Results
        </span>
      </div>
    </div>
  </div>

  <!-- Assessment Section -->
  <div class="py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <AIReadinessAssessment onComplete={handleComplete} />
    </div>
  </div>

  <!-- Trust Indicators -->
  <div class="bg-white border-t-4 border-black py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <div class="text-center mb-8">
        <h2 class="text-2xl font-black">Why Take This Assessment?</h2>
      </div>
      <div class="grid md:grid-cols-3 gap-8">
        <div class="text-center">
          <div class="text-4xl font-black text-blue-500 mb-2">5</div>
          <div class="font-bold mb-2">Key Dimensions</div>
          <p class="text-sm text-gray-600">
            Evaluate AI usage, tech maturity, data readiness, team capability, and strategic priorities.
          </p>
        </div>
        <div class="text-center">
          <div class="text-4xl font-black text-blue-500 mb-2">100+</div>
          <div class="font-bold mb-2">Companies Assessed</div>
          <p class="text-sm text-gray-600">
            Based on real consulting experience with businesses of all sizes across Central Europe.
          </p>
        </div>
        <div class="text-center">
          <div class="text-4xl font-black text-blue-500 mb-2">12</div>
          <div class="font-bold mb-2">Targeted Questions</div>
          <p class="text-sm text-gray-600">
            Quick but comprehensive evaluation covering the factors that matter most.
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- What You Get -->
  <div class="py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <h2 class="text-2xl font-black text-center mb-8">What You Will Learn</h2>
      <div class="grid md:grid-cols-2 gap-6">
        <div class="card">
          <h3 class="font-bold text-lg mb-2">Your AI Readiness Score</h3>
          <p class="text-gray-600">
            Get a clear percentage score showing where you stand compared to industry benchmarks.
          </p>
        </div>
        <div class="card">
          <h3 class="font-bold text-lg mb-2">Category Breakdown</h3>
          <p class="text-gray-600">
            See exactly which areas are your strengths and where you need to improve.
          </p>
        </div>
        <div class="card">
          <h3 class="font-bold text-lg mb-2">Personalized Recommendations</h3>
          <p class="text-gray-600">
            Receive specific, actionable steps tailored to your current situation.
          </p>
        </div>
        <div class="card">
          <h3 class="font-bold text-lg mb-2">Next Steps Roadmap</h3>
          <p class="text-gray-600">
            Know exactly what to do next to accelerate your AI transformation.
          </p>
        </div>
      </div>
    </div>
  </div>

  <!-- CTA Footer -->
  <div class="bg-black text-white py-12 px-4">
    <div class="max-w-4xl mx-auto text-center">
      <h2 class="text-2xl font-black mb-4">Need Expert Guidance?</h2>
      <p class="text-gray-300 mb-6 max-w-xl mx-auto">
        After your assessment, book a free Reality Check call with our AI consultants.
        We will review your results and identify your biggest automation opportunities.
      </p>
      <a
        href="https://cal.com/verduona/reality-check"
        target="_blank"
        rel="noopener"
        class="btn-primary bg-white text-black hover:bg-gray-200 inline-block"
      >
        BOOK FREE CONSULTATION
      </a>
    </div>
  </div>
</div>
