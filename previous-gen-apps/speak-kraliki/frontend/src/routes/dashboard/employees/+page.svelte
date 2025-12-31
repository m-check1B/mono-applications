<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { accessToken, isAuthenticated } from '$stores/auth';
  import { employees, type Employee } from '$api/client';
  import { t } from '$lib/i18n';

  let employeeList = $state<Employee[]>([]);
  let departments = $state<Array<{ id: string; name: string }>>([]);
  let loading = $state(true);
  let showAddModal = $state(false);
  let showImportModal = $state(false);
  let departmentFilter = $state<string>('');

  // New employee form
  let newEmployee = $state({
    first_name: '',
    last_name: '',
    email: '',
    department_id: '',
    job_title: '',
  });

  // Import
  let importFile = $state<File | null>(null);
  let importStatus = $state<'idle' | 'loading' | 'success' | 'error'>('idle');
  let importMessage = $state('');

  onMount(async () => {
    if (!$isAuthenticated) {
      goto('/login');
      return;
    }

    await Promise.all([loadEmployees(), loadDepartments()]);
  });

  async function loadEmployees() {
    try {
      loading = true;
      const deptId = departmentFilter || undefined;
      employeeList = await employees.list($accessToken!, deptId);
    } catch (e) {
      console.error('Failed to load employees', e);
    } finally {
      loading = false;
    }
  }

  async function loadDepartments() {
    try {
      departments = await employees.departments($accessToken!);
    } catch (e) {
      console.error('Failed to load departments', e);
    }
  }

  async function addEmployee() {
    try {
      await employees.create(newEmployee, $accessToken!);
      showAddModal = false;
      newEmployee = {
        first_name: '',
        last_name: '',
        email: '',
        department_id: '',
        job_title: '',
      };
      await loadEmployees();
    } catch (e) {
      console.error('Failed to add employee', e);
    }
  }

  async function toggleActive(emp: Employee) {
    try {
      await employees.update(emp.id, { is_active: !emp.is_active }, $accessToken!);
      await loadEmployees();
    } catch (e) {
      console.error('Failed to toggle employee status', e);
    }
  }

  function handleFileSelect(event: Event) {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
      importFile = target.files[0];
    }
  }

  async function importCSV() {
    if (!importFile) return;

    try {
      importStatus = 'loading';
      const result = await employees.import(importFile, $accessToken!);
      importStatus = 'success';
      importMessage = `Imported ${result.imported} employees`;
      await loadEmployees();
      setTimeout(() => {
        showImportModal = false;
        importStatus = 'idle';
        importFile = null;
      }, 2000);
    } catch (e) {
      importStatus = 'error';
      importMessage = 'Import failed. Check CSV format.';
    }
  }

  $effect(() => {
    if (departmentFilter !== undefined) {
      loadEmployees();
    }
  });
</script>

<svelte:head>
  <title>{$t('employees.title')} - Speak by Kraliki</title>
</svelte:head>

<div class="container mx-auto p-6">
  <div class="flex items-center justify-between mb-8">
    <div>
      <a href="/dashboard" class="text-sm text-muted-foreground hover:text-foreground mb-2 inline-block">
        &lt; {$t('nav.dashboard')}
      </a>
      <h1 class="text-3xl">{$t('employees.title').toUpperCase()}</h1>
    </div>
    <div class="flex gap-2">
      <button onclick={() => (showImportModal = true)} class="brutal-btn">
        {$t('employees.import').toUpperCase()}
      </button>
      <button onclick={() => (showAddModal = true)} class="brutal-btn brutal-btn-primary">
        {$t('employees.add').toUpperCase()}
      </button>
    </div>
  </div>

  <!-- Department Filter -->
  {#if departments.length > 0}
    <div class="mb-6">
      <select bind:value={departmentFilter} class="brutal-input">
        <option value="">{$t('common.all')} {$t('employees.department')}</option>
        {#each departments as dept}
          <option value={dept.id}>{dept.name}</option>
        {/each}
      </select>
    </div>
  {/if}

  {#if loading}
    <div class="text-center py-12">
      <span class="animate-pulse">{$t('common.loading').toUpperCase()}</span>
    </div>
  {:else if employeeList.length === 0}
    <div class="brutal-card p-12 text-center">
      <p class="text-muted-foreground mb-4">{$t('employees.noEmployees')}</p>
      <div class="flex gap-2 justify-center">
        <button onclick={() => (showImportModal = true)} class="brutal-btn">
          {$t('employees.import').toUpperCase()}
        </button>
        <button onclick={() => (showAddModal = true)} class="brutal-btn brutal-btn-primary">
          {$t('employees.add').toUpperCase()}
        </button>
      </div>
    </div>
  {:else}
    <div class="brutal-card overflow-hidden">
      <table class="w-full">
        <thead class="bg-card border-b-2 border-foreground">
          <tr>
            <th class="text-left p-4 text-sm">{$t('employees.firstName').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('employees.lastName').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('employees.email').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('employees.department').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('employees.jobTitle').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('status.active').toUpperCase()}</th>
            <th class="text-left p-4 text-sm">{$t('employees.optedOut').toUpperCase()}</th>
          </tr>
        </thead>
        <tbody>
          {#each employeeList as emp}
            <tr class="border-b border-foreground/20 hover:bg-card/50">
              <td class="p-4">{emp.first_name}</td>
              <td class="p-4">{emp.last_name}</td>
              <td class="p-4 text-sm text-muted-foreground">{emp.email}</td>
              <td class="p-4 text-sm">{departments.find(d => d.id === emp.department_id)?.name || '-'}</td>
              <td class="p-4 text-sm">{emp.job_title || '-'}</td>
              <td class="p-4">
                <button
                  onclick={() => toggleActive(emp)}
                  class="text-sm {emp.is_active ? 'text-terminal-green' : 'text-system-red'}"
                >
                  {emp.is_active ? $t('common.yes') : $t('common.no')}
                </button>
              </td>
              <td class="p-4">
                <span class="text-sm {emp.vop_opted_out ? 'text-system-red' : 'text-muted-foreground'}">
                  {emp.vop_opted_out ? $t('common.yes') : $t('common.no')}
                </span>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>

<!-- Add Employee Modal -->
{#if showAddModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="brutal-card max-w-lg w-full p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl">{$t('employees.add').toUpperCase()}</h2>
        <button onclick={() => (showAddModal = false)} class="text-2xl hover:text-terminal-green">
          X
        </button>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); addEmployee(); }}>
        <div class="space-y-4">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="emp-first-name" class="block text-sm mb-1">{$t('employees.firstName').toUpperCase()}</label>
              <input id="emp-first-name" type="text" bind:value={newEmployee.first_name} class="brutal-input w-full" required />
            </div>
            <div>
              <label for="emp-last-name" class="block text-sm mb-1">{$t('employees.lastName').toUpperCase()}</label>
              <input id="emp-last-name" type="text" bind:value={newEmployee.last_name} class="brutal-input w-full" required />
            </div>
          </div>

          <div>
            <label for="emp-email" class="block text-sm mb-1">{$t('employees.email').toUpperCase()}</label>
            <input id="emp-email" type="email" bind:value={newEmployee.email} class="brutal-input w-full" required />
          </div>

          <div>
            <label for="emp-department" class="block text-sm mb-1">{$t('employees.department').toUpperCase()}</label>
            <select id="emp-department" bind:value={newEmployee.department_id} class="brutal-input w-full">
              <option value="">-- Select --</option>
              {#each departments as dept}
                <option value={dept.id}>{dept.name}</option>
              {/each}
            </select>
          </div>

          <div>
            <label for="emp-job-title" class="block text-sm mb-1">{$t('employees.jobTitle').toUpperCase()}</label>
            <input id="emp-job-title" type="text" bind:value={newEmployee.job_title} class="brutal-input w-full" />
          </div>
        </div>

        <div class="flex gap-3 mt-6 pt-6 border-t-2 border-foreground/20">
          <button type="button" onclick={() => (showAddModal = false)} class="brutal-btn flex-1">
            {$t('common.cancel').toUpperCase()}
          </button>
          <button type="submit" class="brutal-btn brutal-btn-primary flex-1">
            {$t('common.create').toUpperCase()}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

<!-- Import Modal -->
{#if showImportModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
    <div class="brutal-card max-w-lg w-full p-6">
      <div class="flex items-center justify-between mb-6">
        <h2 class="text-xl">{$t('employees.import').toUpperCase()}</h2>
        <button onclick={() => (showImportModal = false)} class="text-2xl hover:text-terminal-green">
          X
        </button>
      </div>

      <div class="space-y-4">
        <p class="text-sm text-muted-foreground">
          Upload a CSV file with columns: first_name, last_name, email, department, job_title
        </p>

        <div class="border-2 border-dashed border-foreground/30 p-6 text-center">
          <input
            type="file"
            accept=".csv"
            onchange={handleFileSelect}
            class="hidden"
            id="csv-upload"
          />
          <label for="csv-upload" class="cursor-pointer">
            {#if importFile}
              <span class="text-terminal-green">{importFile.name}</span>
            {:else}
              <span class="text-muted-foreground">Click to select CSV file</span>
            {/if}
          </label>
        </div>

        {#if importStatus === 'success'}
          <div class="text-terminal-green text-sm">{importMessage}</div>
        {:else if importStatus === 'error'}
          <div class="text-system-red text-sm">{importMessage}</div>
        {/if}
      </div>

      <div class="flex gap-3 mt-6 pt-6 border-t-2 border-foreground/20">
        <button type="button" onclick={() => (showImportModal = false)} class="brutal-btn flex-1">
          {$t('common.cancel').toUpperCase()}
        </button>
        <button
          onclick={importCSV}
          class="brutal-btn brutal-btn-primary flex-1"
          disabled={!importFile || importStatus === 'loading'}
        >
          {importStatus === 'loading' ? $t('common.loading').toUpperCase() : $t('employees.import').toUpperCase()}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
</style>
