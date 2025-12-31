export { matchers } from './matchers.js';

export const nodes = [
	() => import('./nodes/0'),
	() => import('./nodes/1'),
	() => import('./nodes/2'),
	() => import('./nodes/3'),
	() => import('./nodes/4'),
	() => import('./nodes/5'),
	() => import('./nodes/6'),
	() => import('./nodes/7'),
	() => import('./nodes/8'),
	() => import('./nodes/9'),
	() => import('./nodes/10'),
	() => import('./nodes/11'),
	() => import('./nodes/12'),
	() => import('./nodes/13'),
	() => import('./nodes/14'),
	() => import('./nodes/15'),
	() => import('./nodes/16'),
	() => import('./nodes/17'),
	() => import('./nodes/18'),
	() => import('./nodes/19'),
	() => import('./nodes/20'),
	() => import('./nodes/21'),
	() => import('./nodes/22'),
	() => import('./nodes/23'),
	() => import('./nodes/24'),
	() => import('./nodes/25'),
	() => import('./nodes/26'),
	() => import('./nodes/27'),
	() => import('./nodes/28'),
	() => import('./nodes/29'),
	() => import('./nodes/30'),
	() => import('./nodes/31'),
	() => import('./nodes/32'),
	() => import('./nodes/33'),
	() => import('./nodes/34'),
	() => import('./nodes/35'),
	() => import('./nodes/36'),
	() => import('./nodes/37'),
	() => import('./nodes/38')
];

export const server_loads = [];

export const dictionary = {
		"/": [3],
		"/about": [17],
		"/agents": [18],
		"/agents/[id]": [19],
		"/(protected)/analytics": [4,[2]],
		"/(protected)/arena": [5,[2]],
		"/auth/login": [20],
		"/auth/register": [21],
		"/(protected)/calls/agent": [6,[2]],
		"/(protected)/calls/incoming": [7,[2]],
		"/(protected)/calls/outbound": [8,[2]],
		"/(protected)/campaigns": [9,[2]],
		"/(protected)/chat": [10,[2]],
		"/(protected)/companies": [11,[2]],
		"/contact-lists/[id]": [22],
		"/cross-tab-demo": [23],
		"/(protected)/dashboard": [12,[2]],
		"/operations/ivr": [24],
		"/operations/ivr/builder": [25],
		"/operations/recordings": [26],
		"/operations/routing": [27],
		"/operations/routing/builder": [28],
		"/operations/voicemail": [29],
		"/privacy": [30],
		"/responsive-test": [31],
		"/(protected)/scenarios": [13,[2]],
		"/(protected)/scenarios/builder": [14,[2]],
		"/(protected)/scenarios/practice": [15,[2]],
		"/(protected)/settings": [16,[2]],
		"/shifts": [32],
		"/supervisor/active-calls": [33],
		"/supervisor/dashboard": [34],
		"/supervisor/queue": [35],
		"/teams": [36],
		"/teams/new": [38],
		"/teams/[id]": [37]
	};

export const hooks = {
	handleError: (({ error }) => { console.error(error) }),
	
	reroute: (() => {}),
	transport: {}
};

export const decoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.decode]));
export const encoders = Object.fromEntries(Object.entries(hooks.transport).map(([k, v]) => [k, v.encode]));

export const hash = false;

export const decode = (type, value) => decoders[type](value);

export { default as root } from '../root.js';