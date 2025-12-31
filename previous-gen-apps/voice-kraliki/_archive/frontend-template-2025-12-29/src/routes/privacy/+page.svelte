<script lang="ts">
	import { t } from '$lib/i18n';

	const lastUpdated = '2026-01-01';
</script>

<section class="mx-auto w-full max-w-2xl px-4 py-12 text-text-primary">
	<header class="space-y-2">
		<p class="text-xs uppercase tracking-widest text-text-muted">{$t('legal.section_label')}</p>
		<h1 class="text-3xl font-bold">{$t('legal.privacy_title')}</h1>
		<p class="text-sm text-text-muted">{$t('legal.privacy_subtitle')}</p>
	</header>

	<article class="card space-y-4">
		<p>{$t('legal.privacy_body')}</p>
		<p class="text-sm text-text-muted">{$t('legal.last_updated', { date: lastUpdated })}</p>
	</article>
</section>
