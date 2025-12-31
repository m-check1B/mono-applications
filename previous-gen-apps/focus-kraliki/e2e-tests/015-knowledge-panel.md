# Test 015: Knowledge Panel

**Priority:** P1 (High)
**URL:** https://focus.verduona.dev/dashboard
**Estimated Time:** 5 minutes

## Objective

Verify the Knowledge context panel displays and functions correctly.

## Preconditions

- User is logged in
- On the dashboard page

## Test Steps

### Scenario A: Open Knowledge Panel

1. Navigate to: `https://focus.verduona.dev/dashboard`
2. Click Knowledge FAB button (Book icon)

**Expected Results:**
- [ ] Knowledge panel slides in from the side
- [ ] Panel header shows "Knowledge"
- [ ] Close button is available
- [ ] Knowledge items list or empty state displayed

### Scenario B: Empty State

1. Open Knowledge panel with no items

**Expected Results:**
- [ ] Empty state message displayed
- [ ] Helpful text about adding knowledge
- [ ] Option to create first item

### Scenario C: Create Knowledge Item via Panel

1. Open Knowledge panel
2. Find "Add" or "Create" functionality
3. Create a new knowledge item:
   - Title: "Test Note"
   - Content: "This is test content"
4. Save the item

**Expected Results:**
- [ ] Creation form/modal is available
- [ ] Can enter title and content
- [ ] Item is saved
- [ ] New item appears in list

### Scenario D: Create via AI Fast Path

1. Close Knowledge panel
2. In AI input, type: `# Important meeting notes`
3. Submit

**Expected Results:**
- [ ] Fast path recognized (# prefix)
- [ ] Note/Knowledge item created
- [ ] Success toast appears
- [ ] Opening Knowledge panel shows new item

### Scenario E: View Knowledge Item

1. Open Knowledge panel
2. Click on an existing item

**Expected Results:**
- [ ] Item details displayed
- [ ] Title visible
- [ ] Full content visible
- [ ] Metadata (created date, type) may be shown

### Scenario F: Search Knowledge

1. Open Knowledge panel
2. Find search input
3. Search for a term

**Expected Results:**
- [ ] Search input is available
- [ ] Results filter based on search
- [ ] Matching items displayed

### Scenario G: Knowledge Types

1. Look for item type categories

**Expected Results:**
- [ ] Different item types may exist:
  - Notes
  - Tasks
  - Ideas
  - Files
- [ ] Can filter by type

### Scenario H: Delete Knowledge Item

1. Open Knowledge panel
2. Select an item
3. Delete the item

**Expected Results:**
- [ ] Delete option available
- [ ] Confirmation may be required
- [ ] Item removed from list
- [ ] Success feedback

## Knowledge Item Properties

| Property | Type | Description |
|----------|------|-------------|
| Title | string | Item title |
| Content | string | Item content/body |
| Type | enum | Notes, Tasks, Ideas, etc. |
| Created | date | Creation timestamp |
| Metadata | object | Additional data |

## Fast Path Commands for Knowledge

| Command | Creates |
|---------|---------|
| `# Note text` | Note item |
| `/note Text` | Note item |
| `/idea Concept` | Idea item |

## Deep Link

### Scenario I: Direct URL

1. Navigate to: `https://focus.verduona.dev/dashboard/knowledge`

**Expected Results:**
- [ ] Redirects to dashboard
- [ ] Knowledge panel opens automatically

## Gemini File Search

1. If Gemini enabled, test semantic search

**Expected Results:**
- [ ] Can search by meaning, not just keywords
- [ ] AI-powered results

## Pass Criteria

- Knowledge panel opens correctly
- Can create, view, and delete items
- Search functionality works
- AI fast path creates items
- Deep link works

## Screenshots Required

1. Knowledge panel empty state
2. Knowledge panel with items
3. Item creation form
4. Item detail view
