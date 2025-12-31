import { d as derived, w as writable } from "./index.js";
function getInitialLocale() {
  return "en";
}
const locale = writable(getInitialLocale());
const translations = writable({});
const t = derived(
  [translations, locale],
  ([$translations, $locale]) => {
    return (key, params) => {
      const keys = key.split(".");
      let value = $translations;
      for (const k of keys) {
        if (value && typeof value === "object" && k in value) {
          value = value[k];
        } else {
          console.warn(`Translation key not found: ${key}`);
          return key;
        }
      }
      if (typeof value !== "string") {
        console.warn(`Translation key is not a string: ${key}`);
        return key;
      }
      if (params) {
        return value.replace(/\{(\w+)\}/g, (match, paramKey) => {
          return params[paramKey]?.toString() || match;
        });
      }
      return value;
    };
  }
);
export {
  t
};
