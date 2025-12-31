/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	darkMode: 'class',
	theme: {
		extend: {
			colors: {
				void: '#050505',
				concrete: '#F0F0F0',
				'terminal-green': '#33FF00',
				'system-red': '#FF3333',
				'cyan-data': '#00FFFF',
				background: 'hsl(var(--background))',
				foreground: 'hsl(var(--foreground))',
				card: 'hsl(var(--card))',
				'card-foreground': 'hsl(var(--card-foreground))',
				primary: 'hsl(var(--primary))',
				'primary-foreground': 'hsl(var(--primary-foreground))',
				secondary: 'hsl(var(--secondary))',
				'secondary-foreground': 'hsl(var(--secondary-foreground))',
				muted: 'hsl(var(--muted))',
				'muted-foreground': 'hsl(var(--muted-foreground))',
				accent: 'hsl(var(--accent))',
				'accent-foreground': 'hsl(var(--accent-foreground))',
				destructive: 'hsl(var(--destructive))',
				'destructive-foreground': 'hsl(var(--destructive-foreground))',
				border: 'hsl(var(--border))',
				input: 'hsl(var(--input))',
				ring: 'hsl(var(--ring))',
			},
			fontFamily: {
				mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
				display: ['"Archivo Black"', 'Impact', 'Arial Black', 'sans-serif'],
			},
			boxShadow: {
				brutal: '4px 4px 0px 0px currentColor',
				'brutal-lg': '8px 8px 0px 0px currentColor',
				'brutal-border': '4px 4px 0px 0px hsl(var(--border))',
			},
			borderRadius: {
				none: '0px',
			},
		}
	},
	plugins: []
};