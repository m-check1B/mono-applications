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
	() => import('./nodes/30')
];

export const server_loads = [0];

export const dictionary = {
		"/": [2],
		"/agent-board": [~3],
		"/agents": [4],
		"/apps": [5],
		"/auth/login": [~6],
		"/auth/register": [7],
		"/blackboard": [~8],
		"/brain": [9],
		"/comms": [10],
		"/costs": [11],
		"/crm": [12],
		"/data": [13],
		"/genomes": [14],
		"/health": [15],
		"/insights": [16],
		"/jobs": [17],
		"/lab": [18],
		"/leaderboard": [19],
		"/learn": [20],
		"/linear": [21],
		"/memory": [~22],
		"/notebook": [23],
		"/reach": [24],
		"/recall": [25],
		"/see": [~26],
		"/see/traces": [27],
		"/settings": [28],
		"/terminal": [29],
		"/workflows": [30]
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