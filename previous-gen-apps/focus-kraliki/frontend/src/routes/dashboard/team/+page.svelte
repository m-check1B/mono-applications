<script lang="ts">
	import { onMount } from 'svelte';
	import { get } from 'svelte/store';
	import { workspacesStore } from '$lib/stores/workspaces';
	import type { WorkspaceMember } from '$lib/stores/workspaces';
	import { api } from '$lib/api/client';
	import { enqueueAssistantCommand } from '$lib/utils/assistantQueue';
	import { Users, UserPlus, Shield, Trash2, Sparkles } from 'lucide-svelte';

	let inviteEmail = $state('');
	let inviteRole = $state('MEMBER');
	let newWorkspaceName = $state('');
	let newWorkspaceDescription = $state('');
	let selectedWorkspaceId = $state<string | null>(null);
	let feedback = $state<string | null>(null);
	let assistantStatusMessage = $state<string | null>(null);
	let assistantStatusTimeout = $state<ReturnType<typeof setTimeout> | null>(null);

	let workspaceState = $derived($workspacesStore);
	let workspaceOptions = $derived(workspaceState.workspaces);
	let workspaceMembers = $derived(workspaceState.members);

	onMount(async () => {
		await workspacesStore.loadWorkspaces();
		const state = get(workspacesStore);
		selectedWorkspaceId = state.activeWorkspaceId;
		if (selectedWorkspaceId) {
			await workspacesStore.loadMembers(selectedWorkspaceId);
		}
	});

	$effect(() => {
		if (workspaceState.activeWorkspaceId && workspaceState.activeWorkspaceId !== selectedWorkspaceId) {
			selectedWorkspaceId = workspaceState.activeWorkspaceId;
			workspacesStore.loadMembers(selectedWorkspaceId);
		}
	});

	async function handleWorkspaceSelect(workspaceId: string) {
		selectedWorkspaceId = workspaceId;
		await workspacesStore.switchWorkspace(workspaceId);
	}

	async function handleInviteMember() {
		if (!selectedWorkspaceId || !inviteEmail.trim()) return;
		const result = await workspacesStore.inviteMember(selectedWorkspaceId, inviteEmail.trim(), inviteRole);
		if (result.success) {
			inviteEmail = '';
			feedback = 'Invitation sent!';
		} else {
			feedback = result.error || 'Could not invite member';
		}
	}

async function handleRoleChange(member: WorkspaceMember, role: string) {
	if (!selectedWorkspaceId) return;
	await workspacesStore.updateMemberRole(selectedWorkspaceId, member.id, role);
}

function handleRoleSelectChange(member: WorkspaceMember, event: Event) {
	const target = event.currentTarget as HTMLSelectElement | null;
	if (target) {
		handleRoleChange(member, target.value);
	}
}

async function handleRemoveMember(member: WorkspaceMember) {
	if (!selectedWorkspaceId) return;
	if (!confirm(`Remove ${member.email || member.name || 'member'} from workspace?`)) return;
	await workspacesStore.removeMember(selectedWorkspaceId, member.id);
}

async function handleCreateWorkspace() {
		if (!newWorkspaceName.trim()) return;
		await api.workspaces.create({
			name: newWorkspaceName.trim(),
			description: newWorkspaceDescription
		});
		newWorkspaceName = '';
		newWorkspaceDescription = '';
		await workspacesStore.loadWorkspaces();
		const state = get(workspacesStore);
		selectedWorkspaceId = state.activeWorkspaceId;
		if (selectedWorkspaceId) {
			await workspacesStore.loadMembers(selectedWorkspaceId);
	}
}

function notifyAssistant(message: string) {
	assistantStatusMessage = message;
	if (assistantStatusTimeout) clearTimeout(assistantStatusTimeout);
	assistantStatusTimeout = setTimeout(() => {
		assistantStatusMessage = null;
	}, 2500);
}

function sendTeamPrompt(prompt: string, context?: Record<string, unknown>) {
	enqueueAssistantCommand({ prompt, context });
	notifyAssistant('Sent to assistant. Continue in the Assistant tab.');
}

function requestStaffingReview() {
	const context = {
		workspaceId: selectedWorkspaceId,
		memberCount: workspaceMembers.length
	};
	const prompt = `Review the staffing plan for my workspace${selectedWorkspaceId ? ` (${selectedWorkspaceId})` : ''}. Highlight role gaps and onboarding priorities.`;
	sendTeamPrompt(prompt, context);
}

function requestInviteHelp() {
	const prompt = 'Draft an invite note to attract collaborators to my Focus by Kraliki workspace.';
	sendTeamPrompt(prompt);
}

function requestOpsHealth() {
	const prompt = 'Analyze workspace roles and recommend access or security adjustments.';
	sendTeamPrompt(prompt, { memberRoles: workspaceMembers.map((member) => member.role) });
}
</script>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold">Team Workspaces</h1>
		<p class="text-muted-foreground mt-1">Manage shared workspaces, roles, and invites</p>
	</div>

	<div class="flex flex-wrap gap-2 text-xs sm:text-sm">
		<button
			class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition"
			onclick={requestStaffingReview}
		>
			<Sparkles class="w-3.5 h-3.5" />
			Ask for staffing plan
		</button>
		<button
			class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition"
			onclick={requestInviteHelp}
		>
			<Sparkles class="w-3.5 h-3.5" />
			Craft invite note
		</button>
		<button
			class="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-dashed border-primary/40 text-primary hover:bg-primary/10 transition"
			onclick={requestOpsHealth}
		>
			<Sparkles class="w-3.5 h-3.5" />
			Review access & roles
		</button>
	</div>
	{#if assistantStatusMessage}
		<p class="text-xs text-muted-foreground">{assistantStatusMessage}</p>
	{/if}

	<div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
		<div class="bg-card border border-border rounded-lg p-6 space-y-4">
			<div class="flex items-center gap-2">
				<Users class="w-5 h-5 text-primary" />
				<h2 class="text-lg font-semibold">Your Workspaces</h2>
			</div>
			<div class="space-y-3">
				{#each workspaceOptions as workspace}
					<button
						class="w-full text-left px-3 py-2 rounded-md border {selectedWorkspaceId === workspace.id
							? 'border-primary bg-primary/10'
							: 'border-border hover:bg-accent/40'}"
						onclick={() => handleWorkspaceSelect(workspace.id)}
					>
						<p class="font-medium">{workspace.name}</p>
						<p class="text-xs text-muted-foreground">
							{workspace.memberCount || 0} member{workspace.memberCount === 1 ? '' : 's'}
						</p>
					</button>
				{/each}
			</div>

			<div class="border-t border-border pt-4 space-y-2">
				<h3 class="text-sm font-semibold">Create Workspace</h3>
				<input
					type="text"
					placeholder="Name"
					bind:value={newWorkspaceName}
					class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
				/>
				<input
					type="text"
					placeholder="Description"
					bind:value={newWorkspaceDescription}
					class="w-full px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
				/>
				<button
					onclick={handleCreateWorkspace}
					class="w-full px-3 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
				>
					Create
				</button>
			</div>
		</div>

		<div class="bg-card border border-border rounded-lg p-6 space-y-4 lg:col-span-2">
			<div class="flex items-center gap-2">
				<UserPlus class="w-5 h-5 text-primary" />
				<h2 class="text-lg font-semibold">Invite Team Members</h2>
			</div>
			<p class="text-sm text-muted-foreground">
				Invite teammates to collaborate in your active workspace.
			</p>
			<div class="grid grid-cols-1 md:grid-cols-3 gap-3">
				<input
					type="email"
					placeholder="team@company.com"
					bind:value={inviteEmail}
					class="md:col-span-2 px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
				/>
				<select
					bind:value={inviteRole}
					class="px-3 py-2 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
				>
					<option value="MEMBER">Member</option>
					<option value="ADMIN">Admin</option>
				</select>
			</div>
			<div class="flex items-center gap-3">
				<button
					onclick={handleInviteMember}
					class="px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors"
					disabled={!inviteEmail}
				>
					Send Invite
				</button>
				{#if feedback}
					<span class="text-sm text-muted-foreground">{feedback}</span>
				{/if}
			</div>
		</div>
	</div>

	<div class="bg-card border border-border rounded-lg p-6 space-y-4">
		<div class="flex items-center gap-2">
			<Shield class="w-5 h-5 text-primary" />
			<h2 class="text-lg font-semibold">Workspace Members</h2>
		</div>
		{#if !selectedWorkspaceId}
			<p class="text-muted-foreground">Select or create a workspace to manage members.</p>
		{:else if workspaceMembers.length === 0}
			<p class="text-muted-foreground">No members yet. Invite teammates to collaborate.</p>
		{:else}
			<div class="overflow-x-auto">
				<table class="w-full text-sm">
					<thead>
						<tr class="text-left text-muted-foreground border-b border-border">
							<th class="py-2">Member</th>
							<th class="py-2">Role</th>
							<th class="py-2 text-right">Actions</th>
						</tr>
					</thead>
					<tbody>
						{#each workspaceMembers as member}
							<tr class="border-b border-border/60">
								<td class="py-2">
									<p class="font-medium">{member.name || member.email || member.userId}</p>
									<p class="text-xs text-muted-foreground">{member.email}</p>
								</td>
								<td class="py-2">
									<select
										bind:value={member.role}
										onchange={(event) => handleRoleSelectChange(member, event)}
										class="px-2 py-1 bg-background border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring text-xs"
									>
										<option value="MEMBER">Member</option>
										<option value="ADMIN">Admin</option>
										<option value="OWNER" disabled>Owner</option>
									</select>
								</td>
								<td class="py-2 text-right">
									<button
										class="p-2 text-muted-foreground hover:text-destructive hover:bg-destructive/10 rounded-md transition-colors"
										onclick={() => handleRemoveMember(member)}
									>
										<Trash2 class="w-4 h-4" />
									</button>
								</td>
							</tr>
						{/each}
					</tbody>
				</table>
			</div>
		{/if}
	</div>
</div>
