# Test 008: Tasks Panel

**Priority:** P0 (Critical)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 8 minutes

## Objective

Verify the Tasks context panel displays correctly and task operations work.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Open Tasks Panel

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Click Tasks FAB button OR press Ctrl+T

**Expected Results:**
- [ ] Tasks panel slides in from the side
- [ ] Panel header shows "Tasks" or similar title
- [ ] Close button is available
- [ ] Panel has brutalist styling

### Scenario B: Empty State

1. Open Tasks panel with no tasks created

**Expected Results:**
- [ ] Empty state message is displayed
- [ ] Helpful text like "No tasks yet" or similar
- [ ] Option to create first task (button or prompt)

### Scenario C: Create Task via Panel

1. Open Tasks panel
2. Find "Add Task" or "Create" functionality
3. Enter task title: `Test Task from Panel`
4. Submit/Create the task

**Expected Results:**
- [ ] Task creation form/input is available
- [ ] New task appears in the list
- [ ] Task shows title correctly
- [ ] Success feedback (toast or inline)

### Scenario D: Create Task via AI

1. Close Tasks panel
2. In AI input, type: `+ Create a test task for E2E testing`
3. Submit

**Expected Results:**
- [ ] Fast path recognized
- [ ] Task created
- [ ] Success toast appears
- [ ] Opening Tasks panel shows new task

### Scenario E: View Task Details

1. Open Tasks panel
2. Click on an existing task

**Expected Results:**
- [ ] Task details are displayed
- [ ] Can see full task title
- [ ] Task metadata visible (priority, status, etc.)

### Scenario F: Mark Task Complete

1. Open Tasks panel
2. Find a task
3. Mark it as complete (checkbox or button)

**Expected Results:**
- [ ] Task can be marked complete
- [ ] Visual indication of completion (strikethrough, checkmark, etc.)
- [ ] Task may move to completed section

### Scenario G: Delete Task

1. Open Tasks panel
2. Find a task
3. Delete the task

**Expected Results:**
- [ ] Delete option is available
- [ ] Confirmation may be required
- [ ] Task is removed from list
- [ ] Success feedback provided

## Task Properties

| Property | Type | Description |
|----------|------|-------------|
| Title | string | Task name/description |
| Status | enum | PENDING, IN_PROGRESS, COMPLETED |
| Priority | enum | LOW, MEDIUM, HIGH |
| Due Date | date | Optional deadline |

## Filters and Search

### Scenario H: Filter Tasks

1. Open Tasks panel
2. Look for filter options
3. Filter by status or priority

**Expected Results:**
- [ ] Filter controls are available
- [ ] Filters update task list
- [ ] Active filters are indicated

### Scenario I: Search Tasks

1. Open Tasks panel
2. Look for search input
3. Search for a task

**Expected Results:**
- [ ] Search input is available
- [ ] Search filters task list
- [ ] Matching tasks are shown

## Deep Link

### Scenario J: Direct URL

1. Navigate directly to: `https://focus.verduona.dev/dashboard/tasks`

**Expected Results:**
- [ ] Redirects to dashboard
- [ ] Tasks panel opens automatically
- [ ] Uses PanelRedirect component

## Pass Criteria

- Tasks panel opens and closes correctly
- Can create, view, complete, and delete tasks
- AI fast path task creation works
- Deep link works

## Screenshots Required

1. Tasks panel empty state
2. Tasks panel with tasks
3. Task creation in progress
4. Task marked as complete
