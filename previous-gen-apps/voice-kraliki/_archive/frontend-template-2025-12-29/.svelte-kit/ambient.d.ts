
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
	export const PYTHON_BASIC_REPL: string;
	export const LESSOPEN: string;
	export const CLAUDE_FLOW_HOME: string;
	export const ANTHROPIC_MODEL: string;
	export const pm_out_log_path: string;
	export const USER: string;
	export const SSH_CLIENT: string;
	export const CLAUDE_CODE_ENTRYPOINT: string;
	export const npm_config_user_agent: string;
	export const restart_time: string;
	export const GIT_EDITOR: string;
	export const XDG_SESSION_TYPE: string;
	export const GIT_ASKPASS: string;
	export const updateEnv: string;
	export const BUN_INSTALL: string;
	export const npm_config_fetch_retries: string;
	export const npm_node_execpath: string;
	export const script: string;
	export const PM2_USAGE: string;
	export const SHLVL: string;
	export const BROWSER: string;
	export const VIPSHOME: string;
	export const HOME: string;
	export const username: string;
	export const OLDPWD: string;
	export const TERM_PROGRAM_VERSION: string;
	export const PM2_HOME: string;
	export const created_at: string;
	export const NVM_BIN: string;
	export const VSCODE_IPC_HOOK_CLI: string;
	export const npm_package_json: string;
	export const PYTHONUNBUFFERED: string;
	export const NVM_INC: string;
	export const pm_cwd: string;
	export const ANTHROPIC_DEFAULT_SONNET_MODEL: string;
	export const COREPACK_ROOT: string;
	export const npm_package_engines_node: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const namespace: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const SSL_CERT_FILE: string;
	export const filter_env: string;
	export const PYDEVD_DISABLE_FILE_VALIDATION: string;
	export const max_restarts: string;
	export const BUNDLED_DEBUGPY_PATH: string;
	export const VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
	export const ANTHROPIC_SMALL_FAST_MODEL: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const pm_exec_path: string;
	export const npm_config_engine_strict: string;
	export const COLORTERM: string;
	export const unstable_restarts: string;
	export const pm_id: string;
	export const kill_retry_time: string;
	export const NVM_DIR: string;
	export const DEBUGINFOD_URLS: string;
	export const COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
	export const LOGNAME: string;
	export const node_args: string;
	export const pnpm_config_verify_deps_before_run: string;
	export const autostart: string;
	export const _: string;
	export const CLAUDE_CODE_SSE_PORT: string;
	export const XDG_SESSION_CLASS: string;
	export const npm_config_registry: string;
	export const ANTHROPIC_BASE_URL: string;
	export const TERM: string;
	export const XDG_SESSION_ID: string;
	export const OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE: string;
	export const out_file: string;
	export const exec_mode: string;
	export const npm_config_ignore_build_scripts: string;
	export const NODE_APP_INSTANCE: string;
	export const axm_monitor: string;
	export const windowsHide: string;
	export const ANTHROPIC_DEFAULT_OPUS_MODEL: string;
	export const status: string;
	export const npm_config_node_gyp: string;
	export const PATH: string;
	export const restart_delay: string;
	export const exec_interpreter: string;
	export const watch: string;
	export const npm_package_name: string;
	export const NODE: string;
	export const COREPACK_ENABLE_AUTO_PIN: string;
	export const prev_restart_delay: string;
	export const XDG_RUNTIME_DIR: string;
	export const npm_config_frozen_lockfile: string;
	export const axm_options: string;
	export const SSL_CERT_DIR: string;
	export const axm_dynamic: string;
	export const npm_config_fetch_retry_mintimeout: string;
	export const npm_config_maxsockets: string;
	export const VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
	export const NoDefaultCurrentDirectoryInExePath: string;
	export const LANG: string;
	export const PYTHONSTARTUP: string;
	export const vizion: string;
	export const ANTHROPIC_DEFAULT_HAIKU_MODEL: string;
	export const pm_pid_path: string;
	export const pm_err_log_path: string;
	export const treekill: string;
	export const LS_COLORS: string;
	export const time: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const TERM_PROGRAM: string;
	export const npm_config_fetch_retry_maxtimeout: string;
	export const npm_config_loglevel: string;
	export const npm_lifecycle_script: string;
	export const SSH_AUTH_SOCK: string;
	export const PM2_JSON_PROCESSING: string;
	export const SHELL: string;
	export const log_date_format: string;
	export const pmx: string;
	export const unique_id: string;
	export const npm_package_version: string;
	export const npm_lifecycle_event: string;
	export const npm_config_verify_deps_before_run: string;
	export const NODE_PATH: string;
	export const automation: string;
	export const exit_code: string;
	export const LESSCLOSE: string;
	export const error_file: string;
	export const npm_package_engines_pnpm: string;
	export const npm_config_npm_globalconfig: string;
	export const vizion_running: string;
	export const CLAUDECODE: string;
	export const cwd: string;
	export const args: string;
	export const instance_var: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const name: string;
	export const npm_config_globalconfig: string;
	export const PWD: string;
	export const ENABLE_IDE_INTEGRATION: string;
	export const npm_execpath: string;
	export const env: string;
	export const SSH_CONNECTION: string;
	export const NVM_CD_FLAGS: string;
	export const XDG_DATA_DIRS: string;
	export const km_link: string;
	export const instances: string;
	export const axm_actions: string;
	export const merge_logs: string;
	export const npm_config__jsr_registry: string;
	export const npm_command: string;
	export const PNPM_SCRIPT_SRC_DIR: string;
	export const autorestart: string;
	export const npm_config_auto_approve_builds: string;
	export const LINEAR_API_KEY: string;
	export const pm_uptime: string;
	export const INIT_CWD: string;
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
	export const PUBLIC_BACKEND_URL: string;
	export const PUBLIC_WS_URL: string;
	export const PUBLIC_TWILIO_FROM_NUMBER: string;
	export const PUBLIC_TWILIO_FROM_NUMBER_US: string;
	export const PUBLIC_TWILIO_FROM_NUMBER_CZ: string;
	export const PUBLIC_TWILIO_FROM_NUMBER_ES: string;
	export const PUBLIC_ENABLE_THEME_TOGGLE: string;
	export const PUBLIC_ENABLE_DEBUG: string;
	export const PUBLIC_APP_NAME: string;
	export const PUBLIC_APP_VERSION: string;
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
		PYTHON_BASIC_REPL: string;
		LESSOPEN: string;
		CLAUDE_FLOW_HOME: string;
		ANTHROPIC_MODEL: string;
		pm_out_log_path: string;
		USER: string;
		SSH_CLIENT: string;
		CLAUDE_CODE_ENTRYPOINT: string;
		npm_config_user_agent: string;
		restart_time: string;
		GIT_EDITOR: string;
		XDG_SESSION_TYPE: string;
		GIT_ASKPASS: string;
		updateEnv: string;
		BUN_INSTALL: string;
		npm_config_fetch_retries: string;
		npm_node_execpath: string;
		script: string;
		PM2_USAGE: string;
		SHLVL: string;
		BROWSER: string;
		VIPSHOME: string;
		HOME: string;
		username: string;
		OLDPWD: string;
		TERM_PROGRAM_VERSION: string;
		PM2_HOME: string;
		created_at: string;
		NVM_BIN: string;
		VSCODE_IPC_HOOK_CLI: string;
		npm_package_json: string;
		PYTHONUNBUFFERED: string;
		NVM_INC: string;
		pm_cwd: string;
		ANTHROPIC_DEFAULT_SONNET_MODEL: string;
		COREPACK_ROOT: string;
		npm_package_engines_node: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		namespace: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		SSL_CERT_FILE: string;
		filter_env: string;
		PYDEVD_DISABLE_FILE_VALIDATION: string;
		max_restarts: string;
		BUNDLED_DEBUGPY_PATH: string;
		VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
		ANTHROPIC_SMALL_FAST_MODEL: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		pm_exec_path: string;
		npm_config_engine_strict: string;
		COLORTERM: string;
		unstable_restarts: string;
		pm_id: string;
		kill_retry_time: string;
		NVM_DIR: string;
		DEBUGINFOD_URLS: string;
		COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
		LOGNAME: string;
		node_args: string;
		pnpm_config_verify_deps_before_run: string;
		autostart: string;
		_: string;
		CLAUDE_CODE_SSE_PORT: string;
		XDG_SESSION_CLASS: string;
		npm_config_registry: string;
		ANTHROPIC_BASE_URL: string;
		TERM: string;
		XDG_SESSION_ID: string;
		OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE: string;
		out_file: string;
		exec_mode: string;
		npm_config_ignore_build_scripts: string;
		NODE_APP_INSTANCE: string;
		axm_monitor: string;
		windowsHide: string;
		ANTHROPIC_DEFAULT_OPUS_MODEL: string;
		status: string;
		npm_config_node_gyp: string;
		PATH: string;
		restart_delay: string;
		exec_interpreter: string;
		watch: string;
		npm_package_name: string;
		NODE: string;
		COREPACK_ENABLE_AUTO_PIN: string;
		prev_restart_delay: string;
		XDG_RUNTIME_DIR: string;
		npm_config_frozen_lockfile: string;
		axm_options: string;
		SSL_CERT_DIR: string;
		axm_dynamic: string;
		npm_config_fetch_retry_mintimeout: string;
		npm_config_maxsockets: string;
		VSCODE_DEBUGPY_ADAPTER_ENDPOINTS: string;
		NoDefaultCurrentDirectoryInExePath: string;
		LANG: string;
		PYTHONSTARTUP: string;
		vizion: string;
		ANTHROPIC_DEFAULT_HAIKU_MODEL: string;
		pm_pid_path: string;
		pm_err_log_path: string;
		treekill: string;
		LS_COLORS: string;
		time: string;
		VSCODE_GIT_IPC_HANDLE: string;
		TERM_PROGRAM: string;
		npm_config_fetch_retry_maxtimeout: string;
		npm_config_loglevel: string;
		npm_lifecycle_script: string;
		SSH_AUTH_SOCK: string;
		PM2_JSON_PROCESSING: string;
		SHELL: string;
		log_date_format: string;
		pmx: string;
		unique_id: string;
		npm_package_version: string;
		npm_lifecycle_event: string;
		npm_config_verify_deps_before_run: string;
		NODE_PATH: string;
		automation: string;
		exit_code: string;
		LESSCLOSE: string;
		error_file: string;
		npm_package_engines_pnpm: string;
		npm_config_npm_globalconfig: string;
		vizion_running: string;
		CLAUDECODE: string;
		cwd: string;
		args: string;
		instance_var: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		name: string;
		npm_config_globalconfig: string;
		PWD: string;
		ENABLE_IDE_INTEGRATION: string;
		npm_execpath: string;
		env: string;
		SSH_CONNECTION: string;
		NVM_CD_FLAGS: string;
		XDG_DATA_DIRS: string;
		km_link: string;
		instances: string;
		axm_actions: string;
		merge_logs: string;
		npm_config__jsr_registry: string;
		npm_command: string;
		PNPM_SCRIPT_SRC_DIR: string;
		autorestart: string;
		npm_config_auto_approve_builds: string;
		LINEAR_API_KEY: string;
		pm_uptime: string;
		INIT_CWD: string;
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
		PUBLIC_BACKEND_URL: string;
		PUBLIC_WS_URL: string;
		PUBLIC_TWILIO_FROM_NUMBER: string;
		PUBLIC_TWILIO_FROM_NUMBER_US: string;
		PUBLIC_TWILIO_FROM_NUMBER_CZ: string;
		PUBLIC_TWILIO_FROM_NUMBER_ES: string;
		PUBLIC_ENABLE_THEME_TOGGLE: string;
		PUBLIC_ENABLE_DEBUG: string;
		PUBLIC_APP_NAME: string;
		PUBLIC_APP_VERSION: string;
		[key: `PUBLIC_${string}`]: string | undefined;
	}
}
