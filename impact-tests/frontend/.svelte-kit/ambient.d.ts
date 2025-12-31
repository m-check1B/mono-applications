
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
	export const LESSOPEN: string;
	export const CLAUDE_FLOW_HOME: string;
	export const ANTHROPIC_MODEL: string;
	export const USER: string;
	export const SSH_CLIENT: string;
	export const CLAUDE_CODE_ENTRYPOINT: string;
	export const npm_config_user_agent: string;
	export const GIT_EDITOR: string;
	export const XDG_SESSION_TYPE: string;
	export const GIT_ASKPASS: string;
	export const SHLVL: string;
	export const BROWSER: string;
	export const MOTD_SHOWN: string;
	export const HOME: string;
	export const TERM_PROGRAM_VERSION: string;
	export const NVM_BIN: string;
	export const VSCODE_IPC_HOOK_CLI: string;
	export const NVM_INC: string;
	export const COREPACK_ROOT: string;
	export const VSCODE_GIT_ASKPASS_MAIN: string;
	export const VSCODE_GIT_ASKPASS_NODE: string;
	export const SSL_CERT_FILE: string;
	export const VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
	export const ANTHROPIC_SMALL_FAST_MODEL: string;
	export const DBUS_SESSION_BUS_ADDRESS: string;
	export const COLORTERM: string;
	export const NVM_DIR: string;
	export const COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
	export const LOGNAME: string;
	export const pnpm_config_verify_deps_before_run: string;
	export const _: string;
	export const CLAUDE_CODE_SSE_PORT: string;
	export const XDG_SESSION_CLASS: string;
	export const ANTHROPIC_BASE_URL: string;
	export const TERM: string;
	export const XDG_SESSION_ID: string;
	export const OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE: string;
	export const PATH: string;
	export const COREPACK_ENABLE_AUTO_PIN: string;
	export const XDG_RUNTIME_DIR: string;
	export const SSL_CERT_DIR: string;
	export const NoDefaultCurrentDirectoryInExePath: string;
	export const LANG: string;
	export const LS_COLORS: string;
	export const VSCODE_GIT_IPC_HANDLE: string;
	export const TERM_PROGRAM: string;
	export const SSH_AUTH_SOCK: string;
	export const SHELL: string;
	export const npm_config_verify_deps_before_run: string;
	export const NODE_PATH: string;
	export const LESSCLOSE: string;
	export const CLAUDECODE: string;
	export const PNPM_PACKAGE_NAME: string;
	export const VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
	export const PWD: string;
	export const ENABLE_IDE_INTEGRATION: string;
	export const SSH_CONNECTION: string;
	export const NVM_CD_FLAGS: string;
	export const XDG_DATA_DIRS: string;
	export const npm_command: string;
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
		LESSOPEN: string;
		CLAUDE_FLOW_HOME: string;
		ANTHROPIC_MODEL: string;
		USER: string;
		SSH_CLIENT: string;
		CLAUDE_CODE_ENTRYPOINT: string;
		npm_config_user_agent: string;
		GIT_EDITOR: string;
		XDG_SESSION_TYPE: string;
		GIT_ASKPASS: string;
		SHLVL: string;
		BROWSER: string;
		MOTD_SHOWN: string;
		HOME: string;
		TERM_PROGRAM_VERSION: string;
		NVM_BIN: string;
		VSCODE_IPC_HOOK_CLI: string;
		NVM_INC: string;
		COREPACK_ROOT: string;
		VSCODE_GIT_ASKPASS_MAIN: string;
		VSCODE_GIT_ASKPASS_NODE: string;
		SSL_CERT_FILE: string;
		VSCODE_PYTHON_AUTOACTIVATE_GUARD: string;
		ANTHROPIC_SMALL_FAST_MODEL: string;
		DBUS_SESSION_BUS_ADDRESS: string;
		COLORTERM: string;
		NVM_DIR: string;
		COREPACK_ENABLE_DOWNLOAD_PROMPT: string;
		LOGNAME: string;
		pnpm_config_verify_deps_before_run: string;
		_: string;
		CLAUDE_CODE_SSE_PORT: string;
		XDG_SESSION_CLASS: string;
		ANTHROPIC_BASE_URL: string;
		TERM: string;
		XDG_SESSION_ID: string;
		OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE: string;
		PATH: string;
		COREPACK_ENABLE_AUTO_PIN: string;
		XDG_RUNTIME_DIR: string;
		SSL_CERT_DIR: string;
		NoDefaultCurrentDirectoryInExePath: string;
		LANG: string;
		LS_COLORS: string;
		VSCODE_GIT_IPC_HANDLE: string;
		TERM_PROGRAM: string;
		SSH_AUTH_SOCK: string;
		SHELL: string;
		npm_config_verify_deps_before_run: string;
		NODE_PATH: string;
		LESSCLOSE: string;
		CLAUDECODE: string;
		PNPM_PACKAGE_NAME: string;
		VSCODE_GIT_ASKPASS_EXTRA_ARGS: string;
		PWD: string;
		ENABLE_IDE_INTEGRATION: string;
		SSH_CONNECTION: string;
		NVM_CD_FLAGS: string;
		XDG_DATA_DIRS: string;
		npm_command: string;
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
