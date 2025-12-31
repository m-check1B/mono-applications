<script lang="ts">
  import { onMount } from 'svelte';
  import { fly } from 'svelte/transition';
  import { quintOut } from 'svelte/easing';
  import Button from '$lib/components/shared/Button.svelte';
  import Card from '$lib/components/shared/Card.svelte';
  import Badge from '$lib/components/shared/Badge.svelte';
  import { trpc } from '$lib/trpc/client';

  let users = $state<any[]>([]);
  let loading = $state(true);
  let error = $state<string | null>(null);
  let showCreateModal = $state(false);
  let selectedUser = $state<any>(null);
  let showEditModal = $state(false);
  let showDeleteModal = $state(false);

  let formData = $state({
    email: '',
    firstName: '',
    lastName: '',
    role: 'AGENT' as 'AGENT' | 'SUPERVISOR' | 'ADMIN',
    password: ''
  });

  const loadUsers = async () => {
    try {
      loading = true;
      error = null;

      // Try to load from backend
      const result = await trpc.agent.list.query({ limit: 100, offset: 0 });
      users = result.agents || [];
    } catch (err: any) {
      console.error('Failed to load users:', err);
      error = err.message;

      // Fallback to mock data
      users = [
        {
          id: '1',
          email: 'admin@cc-lite.local',
          firstName: 'Admin',
          lastName: 'User',
          role: 'ADMIN',
          status: 'AVAILABLE',
          createdAt: new Date().toISOString()
        },
        {
          id: '2',
          email: 'supervisor@cc-lite.local',
          firstName: 'Super',
          lastName: 'Visor',
          role: 'SUPERVISOR',
          status: 'AVAILABLE',
          createdAt: new Date().toISOString()
        },
        {
          id: '3',
          email: 'agent1@cc-lite.local',
          firstName: 'Agent',
          lastName: 'One',
          role: 'AGENT',
          status: 'BUSY',
          createdAt: new Date().toISOString()
        }
      ];
    } finally {
      loading = false;
    }
  };

  onMount(() => {
    loadUsers();
  });

  const resetForm = () => {
    formData = {
      email: '',
      firstName: '',
      lastName: '',
      role: 'AGENT',
      password: ''
    };
  };

  const handleCreate = async () => {
    try {
      console.log('Creating user:', formData);
      // TODO: Call backend API when available
      // const newUser = await trpc.user.create.mutate(formData);

      // Mock creation for now
      const newUser = {
        id: Date.now().toString(),
        ...formData,
        status: 'OFFLINE',
        createdAt: new Date().toISOString()
      };

      users = [...users, newUser];
      showCreateModal = false;
      resetForm();
    } catch (err: any) {
      alert(`Failed to create user: ${err.message}`);
    }
  };

  const handleEdit = (user: any) => {
    selectedUser = user;
    formData = {
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      password: ''
    };
    showEditModal = true;
  };

  const handleUpdate = async () => {
    if (!selectedUser) return;

    try {
      console.log('Updating user:', formData);
      // TODO: Call backend API

      users = users.map(u =>
        u.id === selectedUser.id
          ? { ...u, ...formData }
          : u
      );

      showEditModal = false;
      resetForm();
      selectedUser = null;
    } catch (err: any) {
      alert(`Failed to update user: ${err.message}`);
    }
  };

  const handleDelete = async () => {
    if (!selectedUser) return;

    try {
      console.log('Deleting user:', selectedUser.id);
      // TODO: Call backend API

      users = users.filter(u => u.id !== selectedUser.id);
      showDeleteModal = false;
      selectedUser = null;
    } catch (err: any) {
      alert(`Failed to delete user: ${err.message}`);
    }
  };

  const getRoleBadgeColor = (role: string) => {
    switch (role) {
      case 'ADMIN': return 'danger';
      case 'SUPERVISOR': return 'warning';
      case 'AGENT': return 'primary';
      default: return 'gray';
    }
  };

  const getStatusBadgeColor = (status: string) => {
    switch (status) {
      case 'AVAILABLE': return 'success';
      case 'BUSY': return 'warning';
      case 'BREAK': return 'secondary';
      case 'OFFLINE': return 'gray';
      default: return 'gray';
    }
  };
</script>

<div class="space-y-6">
  <!-- Header -->
  <Card>
    <div class="p-6">
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 dark:text-white">User Management</h1>
          <p class="text-gray-600 dark:text-gray-400 mt-1">Manage system users and their roles</p>
        </div>
        <Button variant="primary" onclick={() => showCreateModal = true}>
          <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path>
          </svg>
          New User
        </Button>
      </div>
    </div>
  </Card>

  <!-- Users List -->
  <Card>
    {#snippet header()}
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">All Users</h3>
        <Badge variant="gray" class="text-xs">
          Total: {users.length}
        </Badge>
      </div>
    {/snippet}

    {#if loading}
      <div class="text-center py-8">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
        <p class="mt-4 text-gray-600 dark:text-gray-400">Loading users...</p>
      </div>
    {:else if error}
      <div class="text-center py-8">
        <p class="text-red-600 dark:text-red-400">Error: {error}</p>
        <p class="text-sm text-gray-500 mt-2">Using fallback data</p>
      </div>
    {:else}
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">User</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Email</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Role</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Status</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Created</th>
              <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase">Actions</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            {#each users as user, i}
              <tr
                class="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors"
                in:fly={{ y: 20, duration: 300, delay: i * 50, easing: quintOut }}
              >
                <td class="px-4 py-3">
                  <div class="flex items-center">
                    <div class="h-10 w-10 flex-shrink-0">
                      <div class="h-10 w-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium">
                        {user.firstName[0]}{user.lastName[0]}
                      </div>
                    </div>
                    <div class="ml-4">
                      <p class="font-medium text-gray-900 dark:text-white">
                        {user.firstName} {user.lastName}
                      </p>
                    </div>
                  </div>
                </td>

                <td class="px-4 py-3">
                  <span class="text-gray-900 dark:text-white">{user.email}</span>
                </td>

                <td class="px-4 py-3">
                  <Badge variant={getRoleBadgeColor(user.role)} class="text-xs">
                    {user.role}
                  </Badge>
                </td>

                <td class="px-4 py-3">
                  <Badge variant={getStatusBadgeColor(user.status || 'OFFLINE')} class="text-xs">
                    {user.status || 'OFFLINE'}
                  </Badge>
                </td>

                <td class="px-4 py-3">
                  <span class="text-sm text-gray-500">
                    {new Date(user.createdAt).toLocaleDateString()}
                  </span>
                </td>

                <td class="px-4 py-3">
                  <div class="flex gap-2">
                    <Button size="sm" variant="secondary" onclick={() => handleEdit(user)}>
                      Edit
                    </Button>
                    <Button
                      size="sm"
                      variant="danger"
                      onclick={() => { selectedUser = user; showDeleteModal = true; }}
                    >
                      Delete
                    </Button>
                  </div>
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
    {/if}
  </Card>
</div>

<!-- Create User Modal -->
{#if showCreateModal}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Create New User</h3>

      <div class="space-y-4">
        <div>
          <label for="create-user-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email *</label>
          <input
            id="create-user-email"
            type="email"
            bind:value={formData.email}
            placeholder="user@example.com"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="create-user-first-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name *</label>
            <input
              id="create-user-first-name"
              type="text"
              bind:value={formData.firstName}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>

          <div>
            <label for="create-user-last-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name *</label>
            <input
              id="create-user-last-name"
              type="text"
              bind:value={formData.lastName}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>
        </div>

        <div>
          <label for="create-user-role" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role *</label>
          <select
            id="create-user-role"
            bind:value={formData.role}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          >
            <option value="AGENT">Agent</option>
            <option value="SUPERVISOR">Supervisor</option>
            <option value="ADMIN">Admin</option>
          </select>
        </div>

        <div>
          <label for="create-user-password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password *</label>
          <input
            id="create-user-password"
            type="password"
            bind:value={formData.password}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>
      </div>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showCreateModal = false; resetForm(); }}>
          Cancel
        </Button>
        <Button
          variant="primary"
          onclick={handleCreate}
          disabled={!formData.email || !formData.firstName || !formData.lastName || !formData.password}
        >
          Create User
        </Button>
      </div>
    </div>
  </div>
{/if}

<!-- Edit User Modal -->
{#if showEditModal && selectedUser}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white mb-4">Edit User</h3>

      <div class="space-y-4">
        <div>
          <label for="edit-user-email" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
          <input
            id="edit-user-email"
            type="email"
            bind:value={formData.email}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div>
            <label for="edit-user-first-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">First Name</label>
            <input
              id="edit-user-first-name"
              type="text"
              bind:value={formData.firstName}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>

          <div>
            <label for="edit-user-last-name" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Last Name</label>
            <input
              id="edit-user-last-name"
              type="text"
              bind:value={formData.lastName}
              class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
            />
          </div>
        </div>

        <div>
          <label for="edit-user-role" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Role</label>
          <select
            id="edit-user-role"
            bind:value={formData.role}
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          >
            <option value="AGENT">Agent</option>
            <option value="SUPERVISOR">Supervisor</option>
            <option value="ADMIN">Admin</option>
          </select>
        </div>

        <div>
          <label for="edit-user-password" class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">New Password (leave blank to keep current)</label>
          <input
            id="edit-user-password"
            type="password"
            bind:value={formData.password}
            placeholder="Leave blank to keep current"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700"
          />
        </div>
      </div>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showEditModal = false; resetForm(); selectedUser = null; }}>
          Cancel
        </Button>
        <Button variant="primary" onclick={handleUpdate}>
          Save Changes
        </Button>
      </div>
    </div>
  </div>
{/if}

<!-- Delete Confirmation Modal -->
{#if showDeleteModal && selectedUser}
  <div class="fixed inset-0 bg-black/50 flex items-center justify-center z-50" in:fly={{ y: 20, duration: 300 }}>
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full mx-4">
      <h3 class="text-lg font-bold text-red-600 mb-4">Delete User</h3>

      <p class="text-gray-700 dark:text-gray-300 mb-4">
        Are you sure you want to delete <strong>{selectedUser.firstName} {selectedUser.lastName}</strong>?
      </p>
      <p class="text-sm text-gray-500 dark:text-gray-400">
        This action cannot be undone. All user data will be permanently removed.
      </p>

      <div class="flex gap-2 justify-end mt-6">
        <Button variant="secondary" onclick={() => { showDeleteModal = false; selectedUser = null; }}>
          Cancel
        </Button>
        <Button variant="danger" onclick={handleDelete}>
          Delete User
        </Button>
      </div>
    </div>
  </div>
{/if}
