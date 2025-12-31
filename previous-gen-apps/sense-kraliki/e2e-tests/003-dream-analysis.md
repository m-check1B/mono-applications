# Test 003: Dream Analysis

**Feature:** /dream command - Jungian dream interpretation
**Priority:** P1 (Important)
**Type:** Telegram Bot
**Estimated Time:** 5 minutes

## Objective

Verify the dream analysis feature correctly interprets dreams using Jungian psychology and correlates with current cosmic conditions.

## Preconditions

- Bot is running
- GEMINI_API_KEY is configured
- User has free dream analyses remaining (3/month for free tier)

## Test Steps

### Test 3.1: Dream Command with Text

1. Send `/dream I was flying over a dark forest and saw a wolf watching me`
2. **Expected:** First message: "Analyzing your dream through a Jungian lens..."
3. Wait for AI analysis (may take 5-10 seconds)
4. **Expected:** Dream analysis response including:
   - Identified symbols (flying, forest, wolf)
   - Jungian interpretation (shadow, archetypes)
   - Connection to current cosmic conditions
   - Suggested reflection questions

### Test 3.2: Dream Command Without Text

1. Send `/dream` (no text)
2. **Expected:** Bot prompts for dream description
3. Send dream text as a follow-up message
4. **Expected:** Analysis proceeds normally

### Test 3.3: Short Dream Description

1. Send `/dream I had a nightmare`
2. **Expected:** Bot requests more details
   - "Tell me about your dream. Describe it in as much detail..."

### Test 3.4: Long Dream Description

1. Send `/dream` followed by a detailed 500+ word dream
2. **Expected:** Bot handles long text
3. If response exceeds 4000 chars, it should split into multiple messages

### Test 3.5: Cosmic Correlation

1. Check current sensitivity score first (`/sense`)
2. Send a dream for analysis
3. **Expected:** Dream analysis references:
   - Current astrological conditions
   - Geomagnetic activity (if elevated)
   - Moon phase influence

### Test 3.6: Dream with Archetypes

Test recognition of common Jungian archetypes:

1. Send `/dream I was being chased by a dark figure that looked like me`
2. **Expected:** Analysis identifies:
   - Shadow archetype
   - Projection
   - Integration themes

### Test 3.7: Free Tier Limit

1. Use 3 dream analyses (free tier limit)
2. Attempt 4th analysis
3. **Expected:** Message about limit reached
4. Prompt to upgrade to premium

### Test 3.8: Premium User Unlimited

1. Set user as premium (via test setup)
2. Use multiple dream analyses
3. **Expected:** No limit message, all analyses work

### Test 3.9: API Error Handling

1. If Gemini API is unavailable
2. **Expected:** Graceful error message
3. Should not expose technical details

### Test 3.10: Dream Keywords Detection

1. Send a plain text message containing dream keywords:
   "Last night I dreamed about falling and woke up scared"
2. **Expected:** Bot recognizes this might be a dream
3. Suggests using /dream command

## Success Criteria

- [ ] /dream with text triggers analysis
- [ ] /dream without text prompts for description
- [ ] Analysis includes Jungian symbols and archetypes
- [ ] Analysis correlates with current cosmic conditions
- [ ] Long responses split correctly
- [ ] Free tier limit (3/month) enforced
- [ ] Premium users have unlimited access
- [ ] API errors handled gracefully
- [ ] Dream keyword detection works

## Dream Analysis Components

The analysis should include:

1. **Symbol Identification**
   - Objects, animals, people
   - Colors, settings, actions

2. **Jungian Framework**
   - Shadow aspects
   - Anima/Animus
   - Self archetype
   - Collective unconscious themes

3. **Emotional Resonance**
   - Dream mood analysis
   - Waking emotional connections

4. **Cosmic Correlation**
   - Current planetary influences
   - Moon phase relevance
   - Geomagnetic activity

5. **Reflection Questions**
   - Integration prompts
   - Journaling suggestions

## Notes

- Uses Gemini 2.0 Flash for analysis
- Dreams are not stored permanently (privacy)
- Analysis takes 5-10 seconds typically
- FREE_DREAMS_PER_MONTH = 3 (configurable)
