import { x as attr_style, y as ensure_array_like, z as attr_class, F as stringify, G as attr, w as head } from "../../../chunks/index2.js";
import { e as escape_html } from "../../../chunks/context.js";
function AIReadinessAssessment($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    const questions = [
      // Current AI Usage (2 questions)
      {
        id: "ai_current_1",
        category: "Current AI Usage",
        question: "How does your team currently use AI tools?",
        options: [
          { value: 0, label: "We do not use any AI tools" },
          {
            value: 1,
            label: "Individual employees use ChatGPT/similar for personal tasks"
          },
          {
            value: 2,
            label: "We have some team-wide AI tools (e.g., Copilot, Grammarly)"
          },
          {
            value: 3,
            label: "We have integrated AI into specific business processes"
          },
          {
            value: 4,
            label: "AI is embedded across multiple departments and workflows"
          }
        ]
      },
      {
        id: "ai_current_2",
        category: "Current AI Usage",
        question: "What is your organization's attitude toward AI adoption?",
        options: [
          { value: 0, label: "Skeptical or resistant to AI" },
          { value: 1, label: "Curious but cautious" },
          { value: 2, label: "Open to experimentation" },
          { value: 3, label: "Actively pursuing AI initiatives" },
          { value: 4, label: "AI-first mindset across leadership" }
        ]
      },
      // Tech Maturity (2 questions)
      {
        id: "tech_1",
        category: "Tech Maturity",
        question: "How would you describe your current IT infrastructure?",
        options: [
          { value: 0, label: "Mostly paper-based or legacy systems" },
          { value: 1, label: "Basic digital tools (email, spreadsheets)" },
          { value: 2, label: "Modern SaaS stack with some integrations" },
          { value: 3, label: "Well-integrated tech stack with APIs" },
          { value: 4, label: "Cloud-native, API-first architecture" }
        ]
      },
      {
        id: "tech_2",
        category: "Tech Maturity",
        question: "How are your business processes documented?",
        options: [
          { value: 0, label: "Not documented - tribal knowledge only" },
          { value: 1, label: "Some documentation exists but outdated" },
          { value: 2, label: "Key processes are documented" },
          { value: 3, label: "Most processes documented with SOPs" },
          {
            value: 4,
            label: "Comprehensive documentation with version control"
          }
        ]
      },
      // Data Readiness (3 questions)
      {
        id: "data_1",
        category: "Data Readiness",
        question: "How is your business data currently stored?",
        options: [
          {
            value: 0,
            label: "Scattered across personal files and emails"
          },
          { value: 1, label: "In spreadsheets and shared drives" },
          { value: 2, label: "In departmental databases/CRMs" },
          { value: 3, label: "Centralized data warehouse or lake" },
          { value: 4, label: "Unified data platform with governance" }
        ]
      },
      {
        id: "data_2",
        category: "Data Readiness",
        question: "How would you rate your data quality?",
        options: [
          { value: 0, label: "Poor - lots of duplicates and errors" },
          { value: 1, label: "Basic - some cleanup needed regularly" },
          { value: 2, label: "Moderate - periodic data hygiene efforts" },
          { value: 3, label: "Good - established data quality processes" },
          {
            value: 4,
            label: "Excellent - automated validation and cleansing"
          }
        ]
      },
      {
        id: "data_3",
        category: "Data Readiness",
        question: "Do you have access to historical data for training AI models?",
        options: [
          { value: 0, label: "No historical data available" },
          { value: 1, label: "Less than 1 year of data" },
          { value: 2, label: "1-2 years of relevant data" },
          { value: 3, label: "2-5 years of clean, structured data" },
          { value: 4, label: "5+ years with rich metadata" }
        ]
      },
      // Team Capability (2 questions)
      {
        id: "team_1",
        category: "Team Capability",
        question: "Does your team have AI/ML expertise?",
        options: [
          { value: 0, label: "No technical AI knowledge" },
          { value: 1, label: "Basic awareness from articles/videos" },
          { value: 2, label: "Some employees have taken AI courses" },
          { value: 3, label: "Dedicated data/AI team members" },
          { value: 4, label: "Experienced AI/ML engineers on staff" }
        ]
      },
      {
        id: "team_2",
        category: "Team Capability",
        question: "How receptive is your team to new technology?",
        options: [
          { value: 0, label: "Resistant to change" },
          { value: 1, label: "Slow adopters, need lots of training" },
          { value: 2, label: "Will adopt with proper support" },
          { value: 3, label: "Eager to learn new tools" },
          { value: 4, label: "Tech-savvy early adopters" }
        ]
      },
      // Budget & Priorities (3 questions)
      {
        id: "budget_1",
        category: "Budget & Priorities",
        question: "What is your budget for AI/automation initiatives?",
        options: [
          { value: 0, label: "No dedicated budget" },
          { value: 1, label: "Under 10,000 EUR/year" },
          { value: 2, label: "10,000 - 50,000 EUR/year" },
          { value: 3, label: "50,000 - 200,000 EUR/year" },
          { value: 4, label: "200,000+ EUR/year" }
        ]
      },
      {
        id: "budget_2",
        category: "Budget & Priorities",
        question: "Is AI transformation a strategic priority for leadership?",
        options: [
          { value: 0, label: "Not on the radar" },
          { value: 1, label: "Discussed occasionally" },
          { value: 2, label: "On the roadmap for next year" },
          { value: 3, label: "Active initiative with sponsorship" },
          { value: 4, label: "Top strategic priority with board buy-in" }
        ]
      },
      {
        id: "budget_3",
        category: "Budget & Priorities",
        question: "What is your timeline for AI implementation?",
        options: [
          { value: 0, label: "No specific timeline" },
          { value: 1, label: "Exploring options, 12+ months out" },
          { value: 2, label: "Planning to start in 6-12 months" },
          { value: 3, label: "Ready to start in 3-6 months" },
          { value: 4, label: "Ready to start immediately" }
        ]
      }
    ];
    let currentQuestion = 0;
    let answers = {};
    const progress = Math.round(currentQuestion / questions.length * 100);
    const currentQ = questions[currentQuestion];
    Object.keys(answers).length === questions.length;
    $$renderer2.push(`<div class="assessment-container svelte-11v7t90">`);
    {
      $$renderer2.push("<!--[-->");
      $$renderer2.push(`<div class="text-center mb-8"><h2 class="text-3xl font-black mb-2">AI Readiness Assessment</h2> <p class="text-gray-600">Discover how prepared your organization is for AI transformation</p></div> <div class="mb-8"><div class="flex justify-between text-sm font-bold mb-2"><span>Question ${escape_html(currentQuestion + 1)} of ${escape_html(questions.length)}</span> <span>${escape_html(progress)}%</span></div> <div class="progress-bar"><div class="progress-bar-fill"${attr_style(`width: ${stringify(progress)}%`)}></div></div></div> `);
      {
        $$renderer2.push("<!--[-->");
        $$renderer2.push(`<div class="card mb-6"><div class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">${escape_html(currentQ.category)}</div> <h3 class="text-xl font-bold mb-6">${escape_html(currentQ.question)}</h3> <div class="space-y-3"><!--[-->`);
        const each_array = ensure_array_like(currentQ.options);
        for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
          let option = each_array[$$index];
          $$renderer2.push(`<button${attr_class(`option-button ${stringify(answers[currentQ.id] === option.value ? "selected" : "")}`, "svelte-11v7t90")}><span class="option-indicator svelte-11v7t90">`);
          if (answers[currentQ.id] === option.value) {
            $$renderer2.push("<!--[-->");
            $$renderer2.push(`<svg class="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>`);
          } else {
            $$renderer2.push("<!--[!-->");
          }
          $$renderer2.push(`<!--]--></span> <span>${escape_html(option.label)}</span></button>`);
        }
        $$renderer2.push(`<!--]--></div></div> <div class="flex justify-between"><button class="btn-secondary svelte-11v7t90"${attr("disabled", currentQuestion === 0, true)}>Previous</button> <div class="text-sm text-gray-500 self-center">${escape_html(currentQuestion + 1)} / ${escape_html(questions.length)}</div></div>`);
      }
      $$renderer2.push(`<!--]-->`);
    }
    $$renderer2.push(`<!--]--></div>`);
  });
}
function _page($$renderer) {
  head("1brhcb4", $$renderer, ($$renderer2) => {
    $$renderer2.title(($$renderer3) => {
      $$renderer3.push(`<title>AI Readiness Assessment | Learn by Kraliki</title>`);
    });
    $$renderer2.push(`<meta name="description" content="Take our free AI Readiness Assessment to discover how prepared your organization is for AI transformation. Get personalized recommendations and a roadmap."/> <meta property="og:title" content="AI Readiness Assessment | Verduona"/> <meta property="og:description" content="Free assessment to evaluate your organization's AI readiness. Get your score and personalized recommendations in 5 minutes."/> <meta property="og:type" content="website"/>`);
  });
  $$renderer.push(`<div class="min-h-screen bg-gray-50"><div class="bg-black text-white py-12 px-4"><div class="max-w-4xl mx-auto text-center"><div class="text-sm font-bold uppercase tracking-wider text-gray-400 mb-4">FREE ASSESSMENT</div> <h1 class="text-4xl md:text-5xl font-black mb-6">Is Your Organization <span class="text-blue-400">AI-Ready</span>?</h1> <p class="text-xl text-gray-300 max-w-2xl mx-auto">Answer 12 quick questions to get your AI Readiness Score and
        personalized recommendations for your digital transformation journey.</p> <div class="mt-6 flex items-center justify-center gap-6 text-sm"><span class="flex items-center gap-2"><svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg> 5 minutes</span> <span class="flex items-center gap-2"><svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg> 100% Free</span> <span class="flex items-center gap-2"><svg class="w-5 h-5 text-green-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg> Instant Results</span></div></div></div> <div class="py-12 px-4"><div class="max-w-4xl mx-auto">`);
  AIReadinessAssessment($$renderer);
  $$renderer.push(`<!----></div></div> <div class="bg-white border-t-4 border-black py-12 px-4"><div class="max-w-4xl mx-auto"><div class="text-center mb-8"><h2 class="text-2xl font-black">Why Take This Assessment?</h2></div> <div class="grid md:grid-cols-3 gap-8"><div class="text-center"><div class="text-4xl font-black text-blue-500 mb-2">5</div> <div class="font-bold mb-2">Key Dimensions</div> <p class="text-sm text-gray-600">Evaluate AI usage, tech maturity, data readiness, team capability, and strategic priorities.</p></div> <div class="text-center"><div class="text-4xl font-black text-blue-500 mb-2">100+</div> <div class="font-bold mb-2">Companies Assessed</div> <p class="text-sm text-gray-600">Based on real consulting experience with businesses of all sizes across Central Europe.</p></div> <div class="text-center"><div class="text-4xl font-black text-blue-500 mb-2">12</div> <div class="font-bold mb-2">Targeted Questions</div> <p class="text-sm text-gray-600">Quick but comprehensive evaluation covering the factors that matter most.</p></div></div></div></div> <div class="py-12 px-4"><div class="max-w-4xl mx-auto"><h2 class="text-2xl font-black text-center mb-8">What You Will Learn</h2> <div class="grid md:grid-cols-2 gap-6"><div class="card"><h3 class="font-bold text-lg mb-2">Your AI Readiness Score</h3> <p class="text-gray-600">Get a clear percentage score showing where you stand compared to industry benchmarks.</p></div> <div class="card"><h3 class="font-bold text-lg mb-2">Category Breakdown</h3> <p class="text-gray-600">See exactly which areas are your strengths and where you need to improve.</p></div> <div class="card"><h3 class="font-bold text-lg mb-2">Personalized Recommendations</h3> <p class="text-gray-600">Receive specific, actionable steps tailored to your current situation.</p></div> <div class="card"><h3 class="font-bold text-lg mb-2">Next Steps Roadmap</h3> <p class="text-gray-600">Know exactly what to do next to accelerate your AI transformation.</p></div></div></div></div> <div class="bg-black text-white py-12 px-4"><div class="max-w-4xl mx-auto text-center"><h2 class="text-2xl font-black mb-4">Need Expert Guidance?</h2> <p class="text-gray-300 mb-6 max-w-xl mx-auto">After your assessment, book a free Reality Check call with our AI consultants.
        We will review your results and identify your biggest automation opportunities.</p> <a href="https://cal.com/verduona/reality-check" target="_blank" rel="noopener" class="btn-primary bg-white text-black hover:bg-gray-200 inline-block">BOOK FREE CONSULTATION</a></div></div></div>`);
}
export {
  _page as default
};
