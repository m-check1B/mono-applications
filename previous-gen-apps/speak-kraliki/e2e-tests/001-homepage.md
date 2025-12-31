# Test 001: Homepage and Landing Page

**Priority:** HIGH
**URL:** https://speak.verduona.dev

## Preconditions

- Browser is open
- No authentication required

## Test Steps

### Step 1: Load Landing Page

1. Navigate to https://speak.verduona.dev
2. Wait for page to fully load

**Expected:**
- Page loads without errors
- Title contains "Speak by Kraliki"
- Main heading "SPEAK BY KRALIKI" is visible
- Page has Modern Brutalism design (sharp corners, 2px borders, terminal green accents)

### Step 2: Verify Feature Cards

1. Scroll down if needed to see feature cards

**Expected:**
- Three feature cards are visible (labeled 01, 02, 03)
- Each card has a title and description
- Cards have consistent styling

### Step 3: Verify Navigation Buttons

1. Locate the Login and Register buttons

**Expected:**
- Login button is visible and clickable
- Register button is visible and clickable
- Buttons are styled with brutalist design (uppercase text, borders)

### Step 4: Test Login Navigation

1. Click the Login button

**Expected:**
- Browser navigates to /login
- Login form is displayed

### Step 5: Test Register Navigation

1. Navigate back to homepage
2. Click the Register button

**Expected:**
- Browser navigates to /register
- Registration form is displayed

### Step 6: Mobile Responsiveness

1. Resize browser to mobile width (375px)
2. Check homepage layout

**Expected:**
- No horizontal scrollbar appears
- Feature cards stack vertically
- Buttons remain visible and accessible
- Text is readable

## Success Criteria

All steps pass without JavaScript errors in console.

## Notes

- Default language is Czech (cs)
- Button text: "PRIHLASIT SE" (Login), "ZALOZIT UCET" (Register)
