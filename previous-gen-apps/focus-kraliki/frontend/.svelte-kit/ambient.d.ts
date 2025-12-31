
// this file is generated — do not edit it


/// <reference types="@sveltejs/kit" />

/**
 * Environment variables [loaded by Vite](https://vitejs.dev/guide/env-and-mode.html#env-files) from `.env` files and `process.env`. Like [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), this module cannot be imported into client-side code. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * _Unlike_ [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), the values exported from this module are statically injected into your bundle at build time, enabling optimisations like dead code elimination.
 * 
 * ```ts
 * import { API_KEY } from '$env/static/private';
 * ```
 * 
 * Note that all environment variables referenced in your code should be declared (for example in an `.env` file), even if they don't have a value until the app is deployed:
 * 
 * ```
 * MY_FEATURE_FLAG=""
 * ```
 * 
 * You can override `.env` values from the command line like so:
 * 
 * ```sh
 * MY_FEATURE_FLAG="enabled" npm run dev
 * ```
 */
declare module '$env/static/private' {
	export const SHELL: string;
	export const COLORTERM: string;
	export const PYTHONUNBUFFERED: string;
	export const NVM_INC: string;
	export const unstable_restarts: string;
	export const TERM_PROGRAM_VERSION: string;
	export const treekill: string;
	export const prev_restart_delay: string;
	export const env: string;
	export const filter_env: string;
	export const namespace: string;
	export const SSH_AUTH_SOCK: string;
	export const AGENT: string;
	export const restart_time: string;
	export const max_restarts: string;
	export const axm_options: string;
	export const vizion_running: string;
	export const PWD: string;
	export const LOGNAME: string;
	export const XDG_SESSION_TYPE: string;
	export const LINEAR_API_KEY: string;
	export const CODEX_MANAGED_BY_NPM: string;
	export const restart_delay: string;
	export const PM2_USAGE: string;
	export const args: string;
	export const _: string;
	export const log_date_format: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const ENABLE_IDE_INTEGRATION: string;
	export const exec_interpreter: string;
	export const PM2_HOME: string;
	export const HOME: string;
	export const NODE_APP_INSTANCE: string;
	export const OPENCODE: string;
	export const LANG: string;
	export const GITHUB_TOKEN: string;
	export const LS_COLORS: string;
	export const pm_id: string;
	export const PYTHONSTARTUP: string;
	export const SSL_CERT_DIR: string;
	export const version: string;
	export const pm_uptime: string;
	export const km_link: string;
	export const GIT_ASKPASS: string;
	export const pm_cwd: string;
	export const time: string;
	export const ANTHROPIC_BASE_URL: string;
	export const autostart: string;
	export const SSH_CONNECTION: string;
	export const axm_monitor: string;
	export const instance_var: string;
	export const pmx: string;
	export const exit_code: string;
	export const NVM_DIR: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
	export const CLAUDE_CODE_SSE_PORT: string;
	export const unique_id: string;
	export const LESSCLOSE: string;
	export const XDG_SESSION_CLASS: string;
	export const TERM: string;
	export const PYTHON_BASIC_REPL: string;
	export const vizion: string;
	export const username: string;
	export const LESSOPEN: string;
	export const CLAUDE_FLOW_HOME: string;
	export const USER: string;
	export const GIT_PAGER: string;
	export const watch: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const windowsHide: string;
	export const instances: string;
	export const automation: string;
	export const axm_actions: string;
	export const SHLVL: string;
	export const NVM_CD_FLAGS: string;
	export const PAGER: string;
	export const ANTHROPIC_MODEL: string;
	export const XDG_SESSION_ID: string;
	export const NO_COLOR: string;
	export const cwd: string;
	export const LC_CTYPE: string;
	export const XDG_RUNTIME_DIR: string;
	export const SSL_CERT_FILE: string;
	export const SSH_CLIENT: string;
	export const PM2_JSON_PROCESSING: string;
	export const DEBUGINFOD_URLS: string;
	export const BUN_INSTALL: string;
	export const created_at: string;
	export const LC_ALL: string;
	export const merge_logs: string;
	export const pm_pid_path: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const XDG_DATA_DIRS: string;
	export const BROWSER: string;
	export const PATH: string;
	export const ANTHROPIC_SMALL_FAST_MODEL: string;
	export const pm_err_log_path: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const NVM_BIN: string;
	export const kill_retry_time: string;
	export const autorestart: string;
	export const axm_dynamic: string;
	export const node_args: string;
	export const exec_mode: string;
	export const pm_exec_path: string;
	export const status: string;
	export const name: string;
	export const pm_out_log_path: string;
	export const TERM_PROGRAM: string;
	export const VSCODE_IPC_HOOK_CLI: string;
	export const BUN_BE_BUN: string;
	export const NODE_ENV: string;
}

/**
 * Similar to [`$env/static/private`](https://svelte.dev/docs/kit/$env-static-private), except that it only includes environment variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Values are replaced statically at build time.
 * 
 * ```ts
 * import { PUBLIC_BASE_URL } from '$env/static/public';
 * ```
 */
declare module '$env/static/public' {
	export const PUBLIC_API_URL: string;
	export const PUBLIC_VOICE_PROVIDER: string;
	export const PUBLIC_ENABLE_VOICE: string;
}

/**
 * This module provides access to runtime environment variables, as defined by the platform you're running on. For example if you're using [`adapter-node`](https://github.com/sveltejs/kit/tree/main/packages/adapter-node) (or running [`vite preview`](https://svelte.dev/docs/kit/cli)), this is equivalent to `process.env`. This module only includes variables that _do not_ begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) _and do_ start with [`config.kit.env.privatePrefix`](https://svelte.dev/docs/kit/configuration#env) (if configured).
 * 
 * This module cannot be imported into client-side code.
 * 
 * ```ts
 * import { env } from '$env/dynamic/private';
 * console.log(env.DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 * 
 * > [!NOTE] In `dev`, `$env/dynamic` always includes environment variables from `.env`. In `prod`, this behavior will depend on your adapter.
 */
declare module '$env/dynamic/private' {
	export const env: {
		SHELL: string;
		COLORTERM: string;
		PYTHONUNBUFFERED: string;
		NVM_INC: string;
		unstable_restarts: string;
		TERM_PROGRAM_VERSION: string;
		treekill: string;
		prev_restart_delay: string;
		env: string;
		filter_env: string;
		namespace: string;
		SSH_AUTH_SOCK: string;
		AGENT: string;
		restart_time: string;
		max_restarts: string;
		axm_options: string;
		vizion_running: string;
		PWD: string;
		LOGNAME: string;
		XDG_SESSION_TYPE: string;
		LINEAR_API_KEY: string;
		CODEX_MANAGED_BY_NPM: string;
		restart_delay: string;
		PM2_USAGE: string;
		args: string;
		_: string;
		log_date_format: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		ENABLE_IDE_INTEGRATION: string;
		exec_interpreter: string;
		PM2_HOME: string;
		HOME: string;
		NODE_APP_INSTANCE: string;
		OPENCODE: string;
		LANG: string;
		GITHUB_TOKEN: string;
		LS_COLORS: string;
		pm_id: string;
		PYTHONSTARTUP: string;
		SSL_CERT_DIR: string;
		version: string;
		pm_uptime: string;
		km_link: string;
		GIT_ASKPASS: string;
		pm_cwd: string;
		time: string;
		ANTHROPIC_BASE_URL: string;
		autostart: string;
		SSH_CONNECTION: string;
		axm_monitor: string;
		instance_var: string;
		pmx: string;
		exit_code: string;
		NVM_DIR: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
		CLAUDE_CODE_SSE_PORT: string;
		unique_id: string;
		LESSCLOSE: string;
		XDG_SESSION_CLASS: string;
		TERM: string;
		PYTHON_BASIC_REPL: string;
		vizion: string;
		username: string;
		LESSOPEN: string;
		CLAUDE_FLOW_HOME: string;
		USER: string;
		GIT_PAGER: string;
		watch: string;
		VSCODE_GIT_IPC_HANDLE: string;
		windowsHide: string;
		instances: string;
		automation: string;
		axm_actions: string;
		SHLVL: string;
		NVM_CD_FLAGS: string;
		PAGER: string;
		ANTHROPIC_MODEL: string;
		XDG_SESSION_ID: string;
		NO_COLOR: string;
		cwd: string;
		LC_CTYPE: string;
		XDG_RUNTIME_DIR: string;
		SSL_CERT_FILE: string;
		SSH_CLIENT: string;
		PM2_JSON_PROCESSING: string;
		DEBUGINFOD_URLS: string;
		BUN_INSTALL: string;
		created_at: string;
		LC_ALL: string;
		merge_logs: string;
		pm_pid_path: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		XDG_DATA_DIRS: string;
		BROWSER: string;
		PATH: string;
		ANTHROPIC_SMALL_FAST_MODEL: string;
		pm_err_log_path: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		NVM_BIN: string;
		kill_retry_time: string;
		autorestart: string;
		axm_dynamic: string;
		node_args: string;
		exec_mode: string;
		pm_exec_path: string;
		status: string;
		name: string;
		pm_out_log_path: string;
		TERM_PROGRAM: string;
		VSCODE_IPC_HOOK_CLI: string;
		BUN_BE_BUN: string;
		NODE_ENV: string;
		[key: `PUBLIC_${string}`]: undefined;
		[key: `${string}`]: string | undefined;
	}
}

/**
 * Similar to [`$env/dynamic/private`](https://svelte.dev/docs/kit/$env-dynamic-private), but only includes variables that begin with [`config.kit.env.publicPrefix`](https://svelte.dev/docs/kit/configuration#env) (which defaults to `PUBLIC_`), and can therefore safely be exposed to client-side code.
 * 
 * Note that public dynamic environment variables must all be sent from the server to the client, causing larger network requests — when possible, use `$env/static/public` instead.
 * 
 * ```ts
 * import { env } from '$env/dynamic/public';
 * console.log(env.PUBLIC_DEPLOYMENT_SPECIFIC_VARIABLE);
 * ```
 */
declare module '$env/dynamic/public' {
	export const env: {
		PUBLIC_API_URL: string;
		PUBLIC_VOICE_PROVIDER: string;
		PUBLIC_ENABLE_VOICE: string;
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
