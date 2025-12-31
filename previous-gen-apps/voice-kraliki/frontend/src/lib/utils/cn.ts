type ClassValue = string | Record<string, boolean | undefined | null> | false | null | undefined
export function cn(...inputs: ClassValue[]): string {
	const classes: string[] = [];

	for (const input of inputs) {
		if (!input) continue;

		if (typeof input === 'string') {
			classes.push(input);
			continue;
		}

		for (const [key, value] of Object.entries(input)) {
			if (value) {
				classes.push(key);
			}
		}
	}

	return classes.join(' ');
}
