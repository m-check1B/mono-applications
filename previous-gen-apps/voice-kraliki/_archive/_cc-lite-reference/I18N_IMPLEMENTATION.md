# Voice by Kraliki Internationalization

## Implemented Features
- Czech (cs) + English (en) support
- 20+ translation keys
- Locale persistence in localStorage
- Route-based locale switching

## Usage
```svelte
<script>
  import { t } from '$lib/i18n';
</script>

<h1>{$t('nav.dashboard')}</h1>
```

## Files Created
1. /frontend/src/lib/i18n/index.ts (translations + locale store)
2. /frontend/src/routes/+layout.ts (locale initialization)
