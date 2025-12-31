
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
	export const ZITADEL_DOMAIN: string;
	export const ZITADEL_CLIENT_ID: string;
	export const ZITADEL_CLIENT_SECRET: string;
	export const ORIGIN: string;
	export const LOCAL_AUTH_EMAIL: string;
	export const LOCAL_AUTH_PASSWORD: string;
	export const LOCAL_AUTH_NAME: string;
	export const DEMO_MODE: string;
	export const KRALIKI_ENV: string;
	export const REGISTRATION_PIN_DEV: string;
	export const REGISTRATION_PIN_BETA: string;
	export const LOCAL_AUTH_STORE_PATH_DEV: string;
	export const LOCAL_AUTH_STORE_PATH_BETA: string;
	export const GITHUB_TOKEN: string;
	export const PYTHON_BASIC_REPL: string;
	export const LESSOPEN: string;
	export const CLAUDE_FLOW_HOME: string;
	export const ANTHROPIC_MODEL: string;
	export const pm_out_log_path: string;
	export const USER: string;
	export const SSH_CLIENT: string;
	export const npm_config_user_agent: string;
	export const restart_time: string;
	export const XDG_SESSION_TYPE: string;
	export const GIT_ASKPASS: string;
	export const BUN_INSTALL: string;
	export const npm_config_fetch_retries: string;
	export const npm_node_execpath: string;
	export const SHLVL: string;
	export const BROWSER: string;
	export const PM2_USAGE: string;
	export const HOME: string;
	export const PORT: string;
	export const username: string;
	export const created_at: string;
	export const TERM_PROGRAM_VERSION: string;
	export const NVM_BIN: string;
	export const VSCODE_IPC_HOOK_CLI: string;
	export const PM2_HOME: string;
	export const npm_package_json: string;
	export const NVM_INC: string;
	export const pm_cwd: string;
	export const COREPACK_ROOT: string;
	export const node_version: string;
	export const PAGER: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const FOCUS_URL: string;
	export const KRALIKI_DIR: string;
	export const version: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const LC_CTYPE: string;
	export const SSL_CERT_FILE: string;
	export const SPEAK_URL: string;
	export const namespace: string;
	export const filter_env: string;
	export const VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
	export const NO_COLOR: string;
	export const ANTHROPIC_SMALL_FAST_MODEL: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const pm_exec_path: string;
	export const max_restarts: string;
	export const npm_config_engine_strict: string;
	export const unstable_restarts: string;
	export const pm_id: string;
	export const COLORTERM: string;
	export const kill_retry_time: string;
	export const NVM_DIR: string;
	export const DEBUGINFOD_URLS: string;
	export const LEARN_URL: string;
	export const COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
	export const LOGNAME: string;
	export const node_args: string;
	export const pnpm_config_verify_deps_before_run: string;
	export const _: string;
	export const autostart: string;
	export const CLAUDE_CODE_SSE_PORT: string;
	export const XDG_SESSION_CLASS: string;
	export const npm_config_registry: string;
	export const ANTHROPIC_BASE_URL: string;
	export const TERM: string;
	export const XDG_SESSION_ID: string;
	export const exec_mode: string;
	export const npm_config_ignore_build_scripts: string;
	export const axm_monitor: string;
	export const NODE_APP_INSTANCE: string;
	export const windowsHide: string;
	export const status: string;
	export const npm_config_node_gyp: string;
	export const PATH: string;
	export const exec_interpreter: string;
	export const restart_delay: string;
	export const watch: string;
	export const npm_package_name: string;
	export const NODE: string;
	export const prev_restart_delay: string;
	export const XDG_RUNTIME_DIR: string;
	export const npm_config_frozen_lockfile: string;
	export const axm_dynamic: string;
	export const axm_options: string;
	export const SSL_CERT_DIR: string;
	export const npm_config_fetch_retry_mintimeout: string;
	export const npm_config_maxsockets: string;
	export const LANG: string;
	export const PYTHONSTARTUP: string;
	export const pm_pid_path: string;
	export const pm_err_log_path: string;
	export const vizion: string;
	export const LS_COLORS: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const TERM_PROGRAM: string;
	export const time: string;
	export const treekill: string;
	export const npm_config_fetch_retry_maxtimeout: string;
	export const npm_config_loglevel: string;
	export const npm_lifecycle_script: string;
	export const SSH_AUTH_SOCK: string;
	export const PM2_JSON_PROCESSING: string;
	export const unique_id: string;
	export const SHELL: string;
	export const HOST: string;
	export const log_date_format: string;
	export const pmx: string;
	export const npm_package_version: string;
	export const npm_lifecycle_event: string;
	export const npm_config_verify_deps_before_run: string;
	export const automation: string;
	export const exit_code: string;
	export const LESSCLOSE: string;
	export const npm_config_npm_globalconfig: string;
	export const vizion_running: string;
	export const cwd: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const GIT_PAGER: string;
	export const name: string;
	export const instance_var: string;
	export const npm_config_globalconfig: string;
	export const PWD: string;
	export const ENABLE_IDE_INTEGRATION: string;
	export const LC_ALL: string;
	export const npm_execpath: string;
	export const SSH_CONNECTION: string;
	export const NVM_CD_FLAGS: string;
	export const XDG_DATA_DIRS: string;
	export const env: string;
	export const axm_actions: string;
	export const km_link: string;
	export const instances: string;
	export const merge_logs: string;
	export const npm_config__jsr_registry: string;
	export const npm_command: string;
	export const PNPM_SCRIPT_SRC_DIR: string;
	export const autorestart: string;
	export const npm_config_auto_approve_builds: string;
	export const CODEX_MANAGED_BY_NPM: string;
	export const pm_uptime: string;
	export const LINEAR_API_KEY: string;
	export const INIT_CWD: string;
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
		ZITADEL_DOMAIN: string;
		ZITADEL_CLIENT_ID: string;
		ZITADEL_CLIENT_SECRET: string;
		ORIGIN: string;
		LOCAL_AUTH_EMAIL: string;
		LOCAL_AUTH_PASSWORD: string;
		LOCAL_AUTH_NAME: string;
		DEMO_MODE: string;
		KRALIKI_ENV: string;
		REGISTRATION_PIN_DEV: string;
		REGISTRATION_PIN_BETA: string;
		LOCAL_AUTH_STORE_PATH_DEV: string;
		LOCAL_AUTH_STORE_PATH_BETA: string;
		GITHUB_TOKEN: string;
		PYTHON_BASIC_REPL: string;
		LESSOPEN: string;
		CLAUDE_FLOW_HOME: string;
		ANTHROPIC_MODEL: string;
		pm_out_log_path: string;
		USER: string;
		SSH_CLIENT: string;
		npm_config_user_agent: string;
		restart_time: string;
		XDG_SESSION_TYPE: string;
		GIT_ASKPASS: string;
		BUN_INSTALL: string;
		npm_config_fetch_retries: string;
		npm_node_execpath: string;
		SHLVL: string;
		BROWSER: string;
		PM2_USAGE: string;
		HOME: string;
		PORT: string;
		username: string;
		created_at: string;
		TERM_PROGRAM_VERSION: string;
		NVM_BIN: string;
		VSCODE_IPC_HOOK_CLI: string;
		PM2_HOME: string;
		npm_package_json: string;
		NVM_INC: string;
		pm_cwd: string;
		COREPACK_ROOT: string;
		node_version: string;
		PAGER: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		FOCUS_URL: string;
		KRALIKI_DIR: string;
		version: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		LC_CTYPE: string;
		SSL_CERT_FILE: string;
		SPEAK_URL: string;
		namespace: string;
		filter_env: string;
		VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
		NO_COLOR: string;
		ANTHROPIC_SMALL_FAST_MODEL: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		pm_exec_path: string;
		max_restarts: string;
		npm_config_engine_strict: string;
		unstable_restarts: string;
		pm_id: string;
		COLORTERM: string;
		kill_retry_time: string;
		NVM_DIR: string;
		DEBUGINFOD_URLS: string;
		LEARN_URL: string;
		COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
		LOGNAME: string;
		node_args: string;
		pnpm_config_verify_deps_before_run: string;
		_: string;
		autostart: string;
		CLAUDE_CODE_SSE_PORT: string;
		XDG_SESSION_CLASS: string;
		npm_config_registry: string;
		ANTHROPIC_BASE_URL: string;
		TERM: string;
		XDG_SESSION_ID: string;
		exec_mode: string;
		npm_config_ignore_build_scripts: string;
		axm_monitor: string;
		NODE_APP_INSTANCE: string;
		windowsHide: string;
		status: string;
		npm_config_node_gyp: string;
		PATH: string;
		exec_interpreter: string;
		restart_delay: string;
		watch: string;
		npm_package_name: string;
		NODE: string;
		prev_restart_delay: string;
		XDG_RUNTIME_DIR: string;
		npm_config_frozen_lockfile: string;
		axm_dynamic: string;
		axm_options: string;
		SSL_CERT_DIR: string;
		npm_config_fetch_retry_mintimeout: string;
		npm_config_maxsockets: string;
		LANG: string;
		PYTHONSTARTUP: string;
		pm_pid_path: string;
		pm_err_log_path: string;
		vizion: string;
		LS_COLORS: string;
		VSCODE_GIT_IPC_HANDLE: string;
		TERM_PROGRAM: string;
		time: string;
		treekill: string;
		npm_config_fetch_retry_maxtimeout: string;
		npm_config_loglevel: string;
		npm_lifecycle_script: string;
		SSH_AUTH_SOCK: string;
		PM2_JSON_PROCESSING: string;
		unique_id: string;
		SHELL: string;
		HOST: string;
		log_date_format: string;
		pmx: string;
		npm_package_version: string;
		npm_lifecycle_event: string;
		npm_config_verify_deps_before_run: string;
		automation: string;
		exit_code: string;
		LESSCLOSE: string;
		npm_config_npm_globalconfig: string;
		vizion_running: string;
		cwd: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		GIT_PAGER: string;
		name: string;
		instance_var: string;
		npm_config_globalconfig: string;
		PWD: string;
		ENABLE_IDE_INTEGRATION: string;
		LC_ALL: string;
		npm_execpath: string;
		SSH_CONNECTION: string;
		NVM_CD_FLAGS: string;
		XDG_DATA_DIRS: string;
		env: string;
		axm_actions: string;
		km_link: string;
		instances: string;
		merge_logs: string;
		npm_config__jsr_registry: string;
		npm_command: string;
		PNPM_SCRIPT_SRC_DIR: string;
		autorestart: string;
		npm_config_auto_approve_builds: string;
		CODEX_MANAGED_BY_NPM: string;
		pm_uptime: string;
		LINEAR_API_KEY: string;
		INIT_CWD: string;
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
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
