<script lang="ts">
  /**
   * AI Readiness Assessment Tool
   * Lead generation questionnaire for Verduona consulting services
   *
   * Categories covered:
   * - Current AI Usage
   * - Tech Maturity
   * - Data Readiness
   * - Team Capability
   * - Budget & Priorities
   */

  interface Question {
    id: string;
    category: string;
    question: string;
    options: { value: number; label: string }[];
  }

  interface Props {
    onComplete?: (result: AssessmentResult) => void;
    apiEndpoint?: string;
  }

  interface AssessmentResult {
    score: number;
    maxScore: number;
    percentage: number;
    level: 'Beginner' | 'Developing' | 'Intermediate' | 'Advanced' | 'Leader';
    categoryScores: Record<string, { score: number; max: number }>;
    recommendations: string[];
    email: string;
  }

  let { onComplete, apiEndpoint = '/api/assessment/submit' }: Props = $props();

  const questions: Question[] = [
    // Current AI Usage (2 questions)
    {
      id: 'ai_current_1',
      category: 'Current AI Usage',
      question: 'How does your team currently use AI tools?',
      options: [
        { value: 0, label: 'We do not use any AI tools' },
        { value: 1, label: 'Individual employees use ChatGPT/similar for personal tasks' },
        { value: 2, label: 'We have some team-wide AI tools (e.g., Copilot, Grammarly)' },
        { value: 3, label: 'We have integrated AI into specific business processes' },
        { value: 4, label: 'AI is embedded across multiple departments and workflows' }
      ]
    },
    {
      id: 'ai_current_2',
      category: 'Current AI Usage',
      question: 'What is your organization\'s attitude toward AI adoption?',
      options: [
        { value: 0, label: 'Skeptical or resistant to AI' },
        { value: 1, label: 'Curious but cautious' },
        { value: 2, label: 'Open to experimentation' },
        { value: 3, label: 'Actively pursuing AI initiatives' },
        { value: 4, label: 'AI-first mindset across leadership' }
      ]
    },
    // Tech Maturity (2 questions)
    {
      id: 'tech_1',
      category: 'Tech Maturity',
      question: 'How would you describe your current IT infrastructure?',
      options: [
        { value: 0, label: 'Mostly paper-based or legacy systems' },
        { value: 1, label: 'Basic digital tools (email, spreadsheets)' },
        { value: 2, label: 'Modern SaaS stack with some integrations' },
        { value: 3, label: 'Well-integrated tech stack with APIs' },
        { value: 4, label: 'Cloud-native, API-first architecture' }
      ]
    },
    {
      id: 'tech_2',
      category: 'Tech Maturity',
      question: 'How are your business processes documented?',
      options: [
        { value: 0, label: 'Not documented - tribal knowledge only' },
        { value: 1, label: 'Some documentation exists but outdated' },
        { value: 2, label: 'Key processes are documented' },
        { value: 3, label: 'Most processes documented with SOPs' },
        { value: 4, label: 'Comprehensive documentation with version control' }
      ]
    },
    // Data Readiness (3 questions)
    {
      id: 'data_1',
      category: 'Data Readiness',
      question: 'How is your business data currently stored?',
      options: [
        { value: 0, label: 'Scattered across personal files and emails' },
        { value: 1, label: 'In spreadsheets and shared drives' },
        { value: 2, label: 'In departmental databases/CRMs' },
        { value: 3, label: 'Centralized data warehouse or lake' },
        { value: 4, label: 'Unified data platform with governance' }
      ]
    },
    {
      id: 'data_2',
      category: 'Data Readiness',
      question: 'How would you rate your data quality?',
      options: [
        { value: 0, label: 'Poor - lots of duplicates and errors' },
        { value: 1, label: 'Basic - some cleanup needed regularly' },
        { value: 2, label: 'Moderate - periodic data hygiene efforts' },
        { value: 3, label: 'Good - established data quality processes' },
        { value: 4, label: 'Excellent - automated validation and cleansing' }
      ]
    },
    {
      id: 'data_3',
      category: 'Data Readiness',
      question: 'Do you have access to historical data for training AI models?',
      options: [
        { value: 0, label: 'No historical data available' },
        { value: 1, label: 'Less than 1 year of data' },
        { value: 2, label: '1-2 years of relevant data' },
        { value: 3, label: '2-5 years of clean, structured data' },
        { value: 4, label: '5+ years with rich metadata' }
      ]
    },
    // Team Capability (2 questions)
    {
      id: 'team_1',
      category: 'Team Capability',
      question: 'Does your team have AI/ML expertise?',
      options: [
        { value: 0, label: 'No technical AI knowledge' },
        { value: 1, label: 'Basic awareness from articles/videos' },
        { value: 2, label: 'Some employees have taken AI courses' },
        { value: 3, label: 'Dedicated data/AI team members' },
        { value: 4, label: 'Experienced AI/ML engineers on staff' }
      ]
    },
    {
      id: 'team_2',
      category: 'Team Capability',
      question: 'How receptive is your team to new technology?',
      options: [
        { value: 0, label: 'Resistant to change' },
        { value: 1, label: 'Slow adopters, need lots of training' },
        { value: 2, label: 'Will adopt with proper support' },
        { value: 3, label: 'Eager to learn new tools' },
        { value: 4, label: 'Tech-savvy early adopters' }
      ]
    },
    // Budget & Priorities (3 questions)
    {
      id: 'budget_1',
      category: 'Budget & Priorities',
      question: 'What is your budget for AI/automation initiatives?',
      options: [
        { value: 0, label: 'No dedicated budget' },
        { value: 1, label: 'Under 10,000 EUR/year' },
        { value: 2, label: '10,000 - 50,000 EUR/year' },
        { value: 3, label: '50,000 - 200,000 EUR/year' },
        { value: 4, label: '200,000+ EUR/year' }
      ]
    },
    {
      id: 'budget_2',
      category: 'Budget & Priorities',
      question: 'Is AI transformation a strategic priority for leadership?',
      options: [
        { value: 0, label: 'Not on the radar' },
        { value: 1, label: 'Discussed occasionally' },
        { value: 2, label: 'On the roadmap for next year' },
        { value: 3, label: 'Active initiative with sponsorship' },
        { value: 4, label: 'Top strategic priority with board buy-in' }
      ]
    },
    {
      id: 'budget_3',
      category: 'Budget & Priorities',
      question: 'What is your timeline for AI implementation?',
      options: [
        { value: 0, label: 'No specific timeline' },
        { value: 1, label: 'Exploring options, 12+ months out' },
        { value: 2, label: 'Planning to start in 6-12 months' },
        { value: 3, label: 'Ready to start in 3-6 months' },
        { value: 4, label: 'Ready to start immediately' }
      ]
    }
  ];

  let currentQuestion = $state(0);
  let answers: Record<string, number> = $state({});
  let email = $state('');
  let companyName = $state('');
  let showEmailForm = $state(false);
  let showResults = $state(false);
  let result: AssessmentResult | null = $state(null);
  let submitting = $state(false);
  let error = $state('');

  const progress = $derived(Math.round((currentQuestion / questions.length) * 100));
  const currentQ = $derived(questions[currentQuestion]);
  const allAnswered = $derived(Object.keys(answers).length === questions.length);

  function selectAnswer(value: number) {
    answers[currentQ.id] = value;

    // Auto-advance after brief delay
    setTimeout(() => {
      if (currentQuestion < questions.length - 1) {
        currentQuestion++;
      } else {
        showEmailForm = true;
      }
    }, 300);
  }

  function previousQuestion() {
    if (currentQuestion > 0) {
      currentQuestion--;
      showEmailForm = false;
    }
  }

  function calculateResults(): AssessmentResult {
    const categoryScores: Record<string, { score: number; max: number }> = {};
    let totalScore = 0;
    let maxScore = 0;

    // Calculate category scores
    for (const q of questions) {
      if (!categoryScores[q.category]) {
        categoryScores[q.category] = { score: 0, max: 0 };
      }
      categoryScores[q.category].score += answers[q.id] || 0;
      categoryScores[q.category].max += 4;
      totalScore += answers[q.id] || 0;
      maxScore += 4;
    }

    const percentage = Math.round((totalScore / maxScore) * 100);

    // Determine level
    let level: AssessmentResult['level'];
    if (percentage < 20) level = 'Beginner';
    else if (percentage < 40) level = 'Developing';
    else if (percentage < 60) level = 'Intermediate';
    else if (percentage < 80) level = 'Advanced';
    else level = 'Leader';

    // Generate recommendations based on weak areas
    const recommendations: string[] = [];
    const sortedCategories = Object.entries(categoryScores)
      .map(([cat, data]) => ({ category: cat, percentage: (data.score / data.max) * 100 }))
      .sort((a, b) => a.percentage - b.percentage);

    for (const { category, percentage: catPct } of sortedCategories.slice(0, 2)) {
      if (catPct < 50) {
        switch (category) {
          case 'Current AI Usage':
            recommendations.push('Start with a pilot project using AI assistants for routine tasks (email drafting, meeting summaries)');
            break;
          case 'Tech Maturity':
            recommendations.push('Audit and modernize your tech stack - focus on API-first tools that enable AI integration');
            break;
          case 'Data Readiness':
            recommendations.push('Implement a data consolidation strategy - clean, centralized data is the foundation of AI success');
            break;
          case 'Team Capability':
            recommendations.push('Invest in AI literacy training for your team - consider our AI Academy L1 course');
            break;
          case 'Budget & Priorities':
            recommendations.push('Build a business case for AI investment - we can help identify quick wins with high ROI');
            break;
        }
      }
    }

    // Add general recommendations based on overall level
    if (level === 'Beginner' || level === 'Developing') {
      recommendations.push('Book a free 30-minute Reality Check call to identify your biggest automation opportunities');
    } else if (level === 'Intermediate') {
      recommendations.push('You are ready for a structured AI transformation - our Internal AI Audit can map your path forward');
    } else {
      recommendations.push('With your strong foundation, focus on advanced AI orchestration and multi-agent workflows');
    }

    return {
      score: totalScore,
      maxScore,
      percentage,
      level,
      categoryScores,
      recommendations,
      email
    };
  }

  async function submitAssessment() {
    if (!email || !email.includes('@')) {
      error = 'Please enter a valid email address';
      return;
    }

    submitting = true;
    error = '';

    try {
      result = calculateResults();

      // Submit to API (if endpoint exists)
      try {
        await fetch(apiEndpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            email,
            companyName,
            answers,
            result: {
              score: result.score,
              maxScore: result.maxScore,
              percentage: result.percentage,
              level: result.level
            },
            timestamp: new Date().toISOString()
          })
        });
      } catch {
        // Silently continue - lead capture is optional
        console.log('Lead submission to API skipped');
      }

      showResults = true;
      onComplete?.(result);
    } catch (e) {
      error = 'Something went wrong. Please try again.';
    } finally {
      submitting = false;
    }
  }

  function restart() {
    currentQuestion = 0;
    answers = {};
    email = '';
    companyName = '';
    showEmailForm = false;
    showResults = false;
    result = null;
    error = '';
  }

  function getLevelColor(level: string): string {
    switch (level) {
      case 'Beginner': return 'bg-red-500';
      case 'Developing': return 'bg-orange-500';
      case 'Intermediate': return 'bg-yellow-500';
      case 'Advanced': return 'bg-green-500';
      case 'Leader': return 'bg-blue-500';
      default: return 'bg-gray-500';
    }
  }

  function getCategoryIcon(category: string): string {
    switch (category) {
      case 'Current AI Usage': return 'robot';
      case 'Tech Maturity': return 'server';
      case 'Data Readiness': return 'database';
      case 'Team Capability': return 'users';
      case 'Budget & Priorities': return 'chart';
      default: return 'check';
    }
  }
</script>

<div class="assessment-container">
  {#if !showResults}
    <!-- Header -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-black mb-2">AI Readiness Assessment</h2>
      <p class="text-gray-600">Discover how prepared your organization is for AI transformation</p>
    </div>

    <!-- Progress Bar -->
    <div class="mb-8">
      <div class="flex justify-between text-sm font-bold mb-2">
        <span>Question {currentQuestion + 1} of {questions.length}</span>
        <span>{progress}%</span>
      </div>
      <div class="progress-bar">
        <div class="progress-bar-fill" style="width: {progress}%"></div>
      </div>
    </div>

    {#if !showEmailForm}
      <!-- Question Card -->
      <div class="card mb-6">
        <div class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">
          {currentQ.category}
        </div>
        <h3 class="text-xl font-bold mb-6">{currentQ.question}</h3>

        <div class="space-y-3">
          {#each currentQ.options as option}
            <button
              class="option-button {answers[currentQ.id] === option.value ? 'selected' : ''}"
              onclick={() => selectAnswer(option.value)}
            >
              <span class="option-indicator">
                {#if answers[currentQ.id] === option.value}
                  <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"/>
                  </svg>
                {/if}
              </span>
              <span>{option.label}</span>
            </button>
          {/each}
        </div>
      </div>

      <!-- Navigation -->
      <div class="flex justify-between">
        <button
          class="btn-secondary"
          onclick={previousQuestion}
          disabled={currentQuestion === 0}
        >
          Previous
        </button>
        <div class="text-sm text-gray-500 self-center">
          {currentQuestion + 1} / {questions.length}
        </div>
      </div>
    {:else}
      <!-- Email Capture Form -->
      <div class="card">
        <div class="text-center mb-6">
          <div class="text-4xl mb-4">Almost done!</div>
          <h3 class="text-xl font-bold mb-2">Get Your AI Readiness Score</h3>
          <p class="text-gray-600">Enter your email to receive your personalized assessment report</p>
        </div>

        <div class="space-y-4">
          <div>
            <label for="email" class="block text-sm font-bold mb-2">Work Email *</label>
            <input
              type="email"
              id="email"
              bind:value={email}
              placeholder="you@company.com"
              class="input-field"
              required
            />
          </div>

          <div>
            <label for="company" class="block text-sm font-bold mb-2">Company Name (optional)</label>
            <input
              type="text"
              id="company"
              bind:value={companyName}
              placeholder="Your Company"
              class="input-field"
            />
          </div>

          {#if error}
            <div class="text-red-600 font-bold text-sm">{error}</div>
          {/if}

          <button
            class="btn-primary w-full"
            onclick={submitAssessment}
            disabled={submitting}
          >
            {submitting ? 'Calculating...' : 'GET MY RESULTS'}
          </button>

          <p class="text-xs text-gray-500 text-center">
            By submitting, you agree to receive occasional emails about AI transformation.
            Unsubscribe anytime.
          </p>
        </div>

        <div class="mt-6 pt-4 border-t-2 border-gray-200">
          <button
            class="text-sm text-gray-500 hover:text-black"
            onclick={previousQuestion}
          >
            Back to questions
          </button>
        </div>
      </div>
    {/if}
  {:else if result}
    <!-- Results Section -->
    <div class="text-center mb-8">
      <h2 class="text-3xl font-black mb-2">Your AI Readiness Score</h2>
      <p class="text-gray-600">Here is your personalized assessment</p>
    </div>

    <!-- Score Card -->
    <div class="card mb-8 text-center">
      <div class="text-6xl font-black mb-2">{result.percentage}%</div>
      <div class="{getLevelColor(result.level)} text-white inline-block px-4 py-2 font-bold uppercase text-sm mb-4">
        {result.level}
      </div>
      <p class="text-gray-600">
        You scored {result.score} out of {result.maxScore} points
      </p>
    </div>

    <!-- Category Breakdown -->
    <div class="card mb-8">
      <h3 class="text-xl font-bold mb-4">Category Breakdown</h3>
      <div class="space-y-4">
        {#each Object.entries(result.categoryScores) as [category, data]}
          {@const catPct = Math.round((data.score / data.max) * 100)}
          <div>
            <div class="flex justify-between text-sm font-bold mb-1">
              <span>{category}</span>
              <span>{catPct}%</span>
            </div>
            <div class="progress-bar">
              <div
                class="progress-bar-fill {catPct >= 75 ? 'bg-green-500' : catPct >= 50 ? 'bg-yellow-500' : catPct >= 25 ? 'bg-orange-500' : 'bg-red-500'}"
                style="width: {catPct}%"
              ></div>
            </div>
          </div>
        {/each}
      </div>
    </div>

    <!-- Recommendations -->
    <div class="card mb-8">
      <h3 class="text-xl font-bold mb-4">Recommended Next Steps</h3>
      <ul class="space-y-3">
        {#each result.recommendations as rec}
          <li class="flex gap-3">
            <span class="text-green-500 font-bold">-</span>
            <span>{rec}</span>
          </li>
        {/each}
      </ul>
    </div>

    <!-- CTA Section -->
    <div class="card bg-black text-white text-center">
      <h3 class="text-2xl font-bold mb-4">Ready to Accelerate Your AI Journey?</h3>
      <p class="mb-6 text-gray-300">
        Book a free 30-minute Reality Check call with our AI experts.
        We will identify your biggest opportunities and create a roadmap.
      </p>
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <a
          href="https://cal.com/verduona/reality-check"
          target="_blank"
          rel="noopener"
          class="btn-primary bg-white text-black hover:bg-gray-200 inline-block"
        >
          BOOK FREE CALL
        </a>
        <button
          class="btn-secondary border-white text-white hover:bg-white hover:text-black"
          onclick={restart}
        >
          RETAKE ASSESSMENT
        </button>
      </div>
    </div>

    <!-- Share Section -->
    <div class="mt-8 text-center">
      <p class="text-sm text-gray-500 mb-2">Share your results:</p>
      <div class="flex justify-center gap-4">
        <a
          href="https://www.linkedin.com/sharing/share-offsite/?url={encodeURIComponent('https://learn.verduona.dev/ai-readiness')}"
          target="_blank"
          rel="noopener"
          class="text-blue-600 hover:text-blue-800 font-bold text-sm"
        >
          LinkedIn
        </a>
        <a
          href="https://twitter.com/intent/tweet?text={encodeURIComponent('I just took the AI Readiness Assessment and scored ' + result.percentage + '%! Check yours at')}&url={encodeURIComponent('https://learn.verduona.dev/ai-readiness')}"
          target="_blank"
          rel="noopener"
          class="text-blue-400 hover:text-blue-600 font-bold text-sm"
        >
          Twitter/X
        </a>
      </div>
    </div>
  {/if}
</div>

<style>
  .assessment-container {
    max-width: 640px;
    margin: 0 auto;
  }

  .option-button {
    width: 100%;
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    text-align: left;
    background: white;
    border: 3px solid #e5e5e5;
    font-weight: 500;
    transition: all 0.2s;
  }

  .option-button:hover {
    border-color: #000;
    background: #f9f9f9;
  }

  .option-button.selected {
    border-color: #000;
    background: #000;
    color: white;
  }

  .option-indicator {
    width: 24px;
    height: 24px;
    border: 3px solid currentColor;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
  }

  .option-button.selected .option-indicator {
    background: white;
    color: black;
  }

  .input-field {
    width: 100%;
    padding: 12px 16px;
    border: 3px solid #000;
    font-size: 16px;
    font-weight: 500;
  }

  .input-field:focus {
    outline: none;
    box-shadow: 4px 4px 0 0 #000;
  }

  /* Override default button disabled state */
  button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
