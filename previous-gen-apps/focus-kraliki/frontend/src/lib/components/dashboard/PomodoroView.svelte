<script lang="ts">
  import { PomodoroTimer } from '$lib/components';
</script>

<div class="space-y-6">
  <div>
    <h2 class="text-3xl font-black uppercase tracking-tighter">Focus Protocol</h2>
    <p class="text-muted-foreground font-mono text-sm mt-1">Deep focus sessions using the Pomodoro technique.</p>
  </div>

  <div class="max-w-2xl mx-auto">
    <PomodoroTimer />
  </div>

  <div class="brutal-card bg-terminal-green/10 p-6 border-2 border-terminal-green">
    <h3 class="text-lg font-black uppercase mb-3 text-terminal-green">Why use the Focus Protocol?</h3>
    <ul class="space-y-2 text-sm font-mono">
      <li class="flex items-start gap-2">
        <span class="text-terminal-green font-bold">[01]</span>
        <span>Reduces cognitive load by breaking work into segments.</span>
      </li>
      <li class="flex items-start gap-2">
        <span class="text-terminal-green font-bold">[02]</span>
        <span>Prevents burnout with mandatory short and long breaks.</span>
      </li>
      <li class="flex items-start gap-2">
        <span class="text-terminal-green font-bold">[03]</span>
        <span>Improves estimation of task duration over time.</span>
      </li>
    </ul>
  </div>
</div>
