# Test 006: Remedies Recommendations

**Feature:** /remedies command - holistic wellness suggestions
**Priority:** P1 (Important)
**Type:** Telegram Bot
**Estimated Time:** 3 minutes

## Objective

Verify the remedies feature provides contextual wellness recommendations based on current sensitivity level and specific user needs.

## Preconditions

- Bot is running
- For best results, user has location set (weather-aware recommendations)

## Test Steps

### Test 6.1: Basic Remedies Command

1. Send `/remedies`
2. **Expected:** Remedies based on current sensitivity level
3. Response includes:
   - Current sensitivity level
   - Category of recommendations
   - Specific remedies list

### Test 6.2: Sleep Remedies

1. Send `/remedies sleep`
2. **Expected:** Sleep-focused recommendations:
   - Herbal suggestions (chamomile, valerian)
   - Sleep hygiene tips
   - Screen time advice
   - Breathing exercises

### Test 6.3: Focus Remedies

1. Send `/remedies focus`
2. **Expected:** Mental clarity recommendations:
   - Cognitive support (rosemary, peppermint)
   - Environment optimization
   - Break schedules
   - Brain food suggestions

### Test 6.4: Emotional Remedies

1. Send `/remedies emotional`
2. **Expected:** Emotional balance recommendations:
   - Calming herbs (lavender, passionflower)
   - Grounding exercises
   - Journaling prompts
   - Social support suggestions

### Test 6.5: Anxiety-Specific

1. Send `/remedies anxiety`
2. **Expected:** Same as emotional remedies
3. Anxiety keyword triggers emotional support

### Test 6.6: Sensitivity-Based Auto-Selection

When no specific type requested:

1. Get current sensitivity level (`/sense`)
2. Send `/remedies`
3. **Expected:** Recommendations match sensitivity:
   - Low: Productivity focus
   - Moderate: Balance tips
   - Elevated: Calming remedies
   - High: Strong grounding
   - Extreme: Rest priority

### Test 6.7: High Sensitivity Remedies

1. When sensitivity is 60+
2. Send `/remedies`
3. **Expected:** Recommendations include:
   - Reduce stimulants (caffeine, screens)
   - Grounding exercises
   - Extra rest suggestions
   - Gentle movement (yoga, walking)

### Test 6.8: Extreme Sensitivity Remedies

1. When sensitivity is 80+
2. Send `/remedies`
3. **Expected:** Urgent recommendations:
   - Avoid major decisions
   - Cancel non-essential activities
   - Strong grounding (earthing)
   - Nature immersion

### Test 6.9: Remedy Plan Structure

Verify response format:

```
Recommended Remedies:
Level: [MODERATE/HIGH/etc]

- Herbs: [list]
- Activities: [list]
- Environment: [list]
- Nutrition: [list]
- Mindfulness: [list]
```

## Success Criteria

- [ ] /remedies provides contextual recommendations
- [ ] /remedies sleep shows sleep-specific tips
- [ ] /remedies focus shows mental clarity tips
- [ ] /remedies emotional shows calming tips
- [ ] Auto-selection based on sensitivity level
- [ ] High sensitivity triggers stronger recommendations
- [ ] Format is readable and actionable

## Remedy Categories

### By Sensitivity Level

| Level | Focus | Key Remedies |
|-------|-------|--------------|
| Low (0-19) | Productivity | Energizing herbs, active movement |
| Moderate (20-39) | Balance | Adaptogens, moderate exercise |
| Elevated (40-59) | Calming | Relaxing herbs, gentle movement |
| High (60-79) | Grounding | Strong calming, reduce stimuli |
| Extreme (80-100) | Rest | Complete rest, nature, support |

### Herb Suggestions

| Purpose | Herbs |
|---------|-------|
| Sleep | Chamomile, Valerian, Passionflower |
| Focus | Rosemary, Peppermint, Ginkgo |
| Calm | Lavender, Lemon Balm, Ashwagandha |
| Energy | Ginseng, Rhodiola, Green Tea |
| Ground | Vetiver, Cedarwood, Patchouli |

### Activities

| Purpose | Activities |
|---------|------------|
| Ground | Barefoot walking, gardening, clay work |
| Calm | Yoga, meditation, breathing exercises |
| Energy | Brisk walking, dancing, swimming |
| Rest | Napping, bath, gentle stretching |

## Notes

- Remedies are general wellness suggestions, not medical advice
- Premium users get personalized remedy tracking
- Weather influences recommendations (high humidity = indoor focus)
- Biorhythm low cycles trigger specific suggestions
