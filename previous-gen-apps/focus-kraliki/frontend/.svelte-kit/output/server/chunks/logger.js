const LOG_PREFIX = "[FocusKraliki]";
function shouldLog(level) {
  return false;
}
function formatMessage(level, message, context) {
  const contextStr = context ? ` ${JSON.stringify(context)}` : "";
  return `${LOG_PREFIX} [${level}] ${message}${contextStr}`;
}
function debug(message, context) {
  if (shouldLog()) {
    console.debug(formatMessage("DEBUG", message, context));
  }
}
function info(message, context) {
  if (shouldLog()) {
    console.info(formatMessage("INFO", message, context));
  }
}
function warn(message, context) {
  if (shouldLog()) {
    console.warn(formatMessage("WARN", message, context));
  }
}
function error(message, error2, context) {
  if (shouldLog()) {
    console.error(formatMessage("ERROR", message, context), error2 || "");
  }
}
const logger = {
  debug,
  info,
  warn,
  error
};
export {
  logger as l
};
