import { g as getContext } from "./context.js";
import "clsx";
import { A as APP_CONFIG_KEY } from "./app.js";
function useAppConfig() {
  const config = getContext(APP_CONFIG_KEY);
  if (!config) {
    throw new Error("AppConfig context is missing. Make sure you are inside the root layout.");
  }
  return config;
}
export {
  useAppConfig as u
};
