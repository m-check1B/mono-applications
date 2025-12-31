const LOG_PREFIX = '[VoiceKraliki]';
const ENABLE_LOGGING = import.meta.env.DEV;
const LOG_LEVEL = import.meta.env.VITE_LOG_LEVEL || 'INFO';

type LogLevel = 'DEBUG' | 'INFO' | 'WARN' | 'ERROR';
type LogContext = Record<string, unknown>;

const LOG_LEVEL_PRIORITY: Record<LogLevel, number> = {
	DEBUG: 0,
	INFO: 1,
	WARN: 2,
	ERROR: 3
};

function shouldLog(level: LogLevel): boolean {
	if (!ENABLE_LOGGING) return false;
	return LOG_LEVEL_PRIORITY[level] >= LOG_LEVEL_PRIORITY[LOG_LEVEL as LogLevel];
}

function formatMessage(level: LogLevel, message: string, context?: LogContext): string {
	const contextStr = context ? ` ${JSON.stringify(context)}` : '';
	return `${LOG_PREFIX} [${level}] ${message}${contextStr}`;
}

function debug(message: string, context?: LogContext): void {
	if (shouldLog('DEBUG')) {
		console.debug(formatMessage('DEBUG', message, context));
	}
}

function info(message: string, context?: LogContext): void {
	if (shouldLog('INFO')) {
		console.info(formatMessage('INFO', message, context));
	}
}

function warn(message: string, context?: LogContext): void {
	if (shouldLog('WARN')) {
		console.warn(formatMessage('WARN', message, context));
	}
}

function error(message: string, error?: Error | unknown, context?: LogContext): void {
	if (shouldLog('ERROR')) {
		console.error(formatMessage('ERROR', message, context), error || '');
	}
}

export const logger = {
	debug,
	info,
	warn,
	error
};
