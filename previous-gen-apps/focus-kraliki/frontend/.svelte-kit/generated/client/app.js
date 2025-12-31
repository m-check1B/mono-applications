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
	() => import('./nodes/23')
];

export const server_loads = [];

export const dictionary = {
		"/": [~3],
		"/auth/google/callback": [4],
		"/dashboard": [6,[2]],
		"/dashboard/agent": [18,[2]],
		"/dashboard/analytics": [21,[2]],
		"/dashboard/calendar": [13,[2]],
		"/dashboard/chat": [19,[2]],
		"/dashboard/insights": [10,[2]],
		"/dashboard/knowledge": [15,[2]],
		"/dashboard/projects": [20,[2]],
		"/dashboard/settings": [14,[2]],
		"/dashboard/shadow": [9,[2]],
		"/dashboard/subscription": [16,[2]],
		"/dashboard/tasks": [7,[2]],
		"/dashboard/team": [11,[2]],
		"/dashboard/time": [17,[2]],
		"/dashboard/voice": [12,[2]],
		"/dashboard/work": [8,[2]],
		"/login": [23],
		"/onboarding": [22],
		"/register": [5]
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