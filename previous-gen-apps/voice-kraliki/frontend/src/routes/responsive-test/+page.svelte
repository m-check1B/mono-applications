<script lang="ts">
	/**
	 * Responsive Design Test Page
	 *
	 * This page allows testing of responsive breakpoints and touch targets
	 * to ensure proper behavior across devices.
	 */

	let screenWidth = $state(0);
	let screenHeight = $state(0);
	let orientation = $state('unknown');

	function updateScreenInfo() {
		if (typeof window !== 'undefined') {
			screenWidth = window.innerWidth;
			screenHeight = window.innerHeight;
			orientation = window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';
		}
	}

	$effect(() => {
		if (typeof window !== 'undefined') {
			updateScreenInfo();
			window.addEventListener('resize', updateScreenInfo);
			window.addEventListener('orientationchange', updateScreenInfo);

			return () => {
				window.removeEventListener('resize', updateScreenInfo);
				window.removeEventListener('orientationchange', updateScreenInfo);
			};
		}
	});

	function getDeviceType() {
		if (screenWidth < 768) return 'Mobile';
		if (screenWidth < 1024) return 'Tablet';
		return 'Desktop';
	}

	function getBreakpoint() {
		if (screenWidth < 768) return '< 768px (Mobile)';
		if (screenWidth >= 768 && screenWidth <= 1024) return '768px - 1024px (Tablet)';
		if (screenWidth > 1024 && screenWidth <= 1200) return '1024px - 1200px (Small Desktop)';
		return '> 1200px (Desktop)';
	}
</script>

<div class="responsive-test">
	<div class="header">
		<h1>Responsive Design Test</h1>
		<p class="subtitle">Test responsive breakpoints and touch target sizes</p>
	</div>

	<div class="screen-info-section">
		<h2>Screen Information</h2>
		<div class="info-grid">
			<div class="info-card">
				<span class="info-label">Screen Size</span>
				<span class="info-value">{screenWidth} x {screenHeight}px</span>
			</div>
			<div class="info-card">
				<span class="info-label">Device Type</span>
				<span class="info-value">{getDeviceType()}</span>
			</div>
			<div class="info-card">
				<span class="info-label">Breakpoint</span>
				<span class="info-value">{getBreakpoint()}</span>
			</div>
			<div class="info-card">
				<span class="info-label">Orientation</span>
				<span class="info-value">{orientation}</span>
			</div>
		</div>
	</div>

	<div class="touch-target-section">
		<h2>Touch Target Test</h2>
		<p class="description">
			WCAG 2.1 AA requires minimum 44x44px touch targets. Test buttons below:
		</p>
		<div class="touch-targets">
			<div class="target-example">
				<button class="touch-target" style="min-width: 44px; min-height: 44px;">
					44px (Pass)
				</button>
				<span class="target-label">44x44px - WCAG Compliant</span>
			</div>
			<div class="target-example">
				<button class="touch-target" style="min-width: 48px; min-height: 48px;">
					48px (Better)
				</button>
				<span class="target-label">48x48px - Enhanced</span>
			</div>
			<div class="target-example">
				<button class="touch-target fail" style="min-width: 36px; min-height: 36px; min-width: 36px !important; min-height: 36px !important;">
					36px (Fail)
				</button>
				<span class="target-label fail-label">36x36px - Too Small</span>
			</div>
		</div>
	</div>

	<div class="layout-section">
		<h2>Responsive Layout Test</h2>
		<p class="description">These boxes stack on tablet portrait mode (768px-1024px):</p>
		<div class="layout-test tablet-stack">
			<div class="box box-1">Box 1</div>
			<div class="box box-2">Box 2</div>
			<div class="box box-3">Box 3</div>
		</div>
	</div>

	<div class="utility-section">
		<h2>Utility Classes Test</h2>
		<div class="utility-demos">
			<div class="demo-item">
				<span class="demo-label">.tablet-stack</span>
				<span class="demo-desc">Stacks items vertically on tablet</span>
			</div>
			<div class="demo-item">
				<span class="demo-label">.tablet-full</span>
				<span class="demo-desc">Full width on tablet</span>
			</div>
			<div class="demo-item">
				<span class="demo-label">.tablet-hidden</span>
				<span class="demo-desc">Hidden on tablet devices</span>
			</div>
			<div class="demo-item">
				<span class="demo-label">.touch-target</span>
				<span class="demo-desc">Ensures 44px minimum size</span>
			</div>
		</div>
	</div>

	<div class="breakpoint-section">
		<h2>Active Breakpoints</h2>
		<div class="breakpoint-indicators">
			<div class="breakpoint-indicator" class:active={screenWidth < 768}>
				Mobile (&lt; 768px)
			</div>
			<div class="breakpoint-indicator" class:active={screenWidth >= 768 && screenWidth <= 1024}>
				Tablet (768px - 1024px)
			</div>
			<div class="breakpoint-indicator" class:active={screenWidth >= 768 && screenWidth <= 1024 && orientation === 'landscape'}>
				Tablet Landscape
			</div>
			<div class="breakpoint-indicator" class:active={screenWidth > 1024 && screenWidth <= 1200}>
				Small Desktop (1024px - 1200px)
			</div>
			<div class="breakpoint-indicator" class:active={screenWidth > 1200}>
				Desktop (&gt; 1200px)
			</div>
		</div>
	</div>
</div>

<style>
	.responsive-test {
		padding: 2rem;
		max-width: 1400px;
		margin: 0 auto;
		background: var(--bg-primary);
		color: var(--text-primary);
	}

	.header {
		text-align: center;
		margin-bottom: 3rem;
	}

	.header h1 {
		font-size: 2.5rem;
		font-weight: 700;
		margin-bottom: 0.5rem;
		color: var(--text-primary);
	}

	.subtitle {
		font-size: 1.1rem;
		color: var(--text-secondary);
	}

	.screen-info-section,
	.touch-target-section,
	.layout-section,
	.utility-section,
	.breakpoint-section {
		background: var(--bg-card);
		border: 1px solid var(--border-subtle);
		border-radius: 12px;
		padding: 2rem;
		margin-bottom: 2rem;
	}

	h2 {
		font-size: 1.5rem;
		font-weight: 600;
		margin-bottom: 1.5rem;
		color: var(--text-primary);
	}

	.description {
		color: var(--text-secondary);
		margin-bottom: 1.5rem;
	}

	.info-grid {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
		gap: 1rem;
	}

	.info-card {
		background: var(--bg-secondary);
		border: 1px solid var(--border-default);
		border-radius: 8px;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.info-label {
		font-size: 0.85rem;
		color: var(--text-muted);
		font-weight: 500;
		text-transform: uppercase;
	}

	.info-value {
		font-size: 1.5rem;
		font-weight: 700;
		color: var(--color-primary);
	}

	.touch-targets {
		display: flex;
		gap: 2rem;
		flex-wrap: wrap;
		align-items: flex-start;
	}

	.target-example {
		display: flex;
		flex-direction: column;
		align-items: center;
		gap: 1rem;
	}

	.touch-target {
		background: var(--color-primary);
		color: white;
		border: none;
		border-radius: 8px;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s ease;
		display: inline-flex;
		align-items: center;
		justify-content: center;
		padding: 0.75rem;
	}

	.touch-target:hover {
		background: var(--color-primary-hover);
		transform: scale(1.05);
	}

	.touch-target.fail {
		background: var(--color-error);
	}

	.target-label {
		font-size: 0.9rem;
		color: var(--text-secondary);
		text-align: center;
	}

	.fail-label {
		color: var(--color-error);
		font-weight: 600;
	}

	.layout-test {
		display: flex;
		gap: 1rem;
	}

	.box {
		flex: 1;
		padding: 2rem;
		border-radius: 8px;
		color: white;
		font-weight: 600;
		font-size: 1.1rem;
		text-align: center;
		min-height: 100px;
		display: flex;
		align-items: center;
		justify-content: center;
	}

	.box-1 {
		background: hsl(var(--card));
	}

	.box-2 {
		background: hsl(var(--card));
	}

	.box-3 {
		background: hsl(var(--card));
	}

	.utility-demos {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
		gap: 1rem;
	}

	.demo-item {
		background: var(--bg-secondary);
		border: 1px solid var(--border-default);
		border-radius: 8px;
		padding: 1.5rem;
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.demo-label {
		font-family: 'Courier New', monospace;
		font-size: 0.9rem;
		color: var(--color-primary);
		font-weight: 600;
	}

	.demo-desc {
		font-size: 0.85rem;
		color: var(--text-secondary);
	}

	.breakpoint-indicators {
		display: flex;
		flex-wrap: wrap;
		gap: 1rem;
	}

	.breakpoint-indicator {
		padding: 1rem 1.5rem;
		border: 2px solid var(--border-default);
		border-radius: 8px;
		background: var(--bg-secondary);
		color: var(--text-muted);
		font-weight: 600;
		transition: all 0.3s ease;
	}

	.breakpoint-indicator.active {
		background: var(--color-primary);
		border-color: var(--color-primary);
		color: white;
		box-shadow: 0 4px 12px rgba(74, 158, 255, 0.35);
	}

	/* Tablet Portrait */
	@media (min-width: 768px) and (max-width: 1024px) {
		.responsive-test {
			padding: 1.5rem;
		}

		.header h1 {
			font-size: 2rem;
		}

		.info-grid {
			grid-template-columns: repeat(2, 1fr);
		}
	}

	/* Mobile */
	@media (max-width: 767px) {
		.responsive-test {
			padding: 1rem;
		}

		.header h1 {
			font-size: 1.75rem;
		}

		.screen-info-section,
		.touch-target-section,
		.layout-section,
		.utility-section,
		.breakpoint-section {
			padding: 1.5rem;
		}

		.info-grid {
			grid-template-columns: 1fr;
		}

		.touch-targets {
			flex-direction: column;
			align-items: stretch;
		}

		.target-example {
			width: 100%;
		}

		.layout-test {
			flex-direction: column;
		}
	}
</style>
