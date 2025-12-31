import { g as get, w as writable, d as derived } from "./index.js";
import { a as api } from "./client.js";
import { l as logger } from "./logger.js";
let timeoutAction;
let timeoutEnable;
function withoutTransition(action) {
  if (typeof document === "undefined")
    return;
  clearTimeout(timeoutAction);
  clearTimeout(timeoutEnable);
  const style = document.createElement("style");
  const css = document.createTextNode(`* {
     -webkit-transition: none !important;
     -moz-transition: none !important;
     -o-transition: none !important;
     -ms-transition: none !important;
     transition: none !important;
  }`);
  style.appendChild(css);
  const disable = () => document.head.appendChild(style);
  const enable = () => document.head.removeChild(style);
  if (typeof window.getComputedStyle !== "undefined") {
    disable();
    action();
    window.getComputedStyle(style).opacity;
    enable();
    return;
  }
  if (typeof window.requestAnimationFrame !== "undefined") {
    disable();
    action();
    window.requestAnimationFrame(enable);
    return;
  }
  disable();
  timeoutAction = window.setTimeout(() => {
    action();
    timeoutEnable = window.setTimeout(enable, 120);
  }, 120);
}
function sanitizeClassNames(classNames) {
  return classNames.filter((className) => className.length > 0);
}
const noopStorage = {
  getItem: (_key) => null,
  setItem: (_key, _value) => {
  }
};
const isBrowser = typeof document !== "undefined";
const modes = ["dark", "light", "system"];
const modeStorageKey = writable("mode-watcher-mode");
const themeStorageKey = writable("mode-watcher-theme");
const userPrefersMode = createUserPrefersMode();
const systemPrefersMode = createSystemMode();
const themeColors = writable(void 0);
const theme = createCustomTheme();
const disableTransitions = writable(true);
const darkClassNames = writable([]);
const lightClassNames = writable([]);
const derivedMode = createDerivedMode();
createDerivedTheme();
function createUserPrefersMode() {
  const defaultValue = "system";
  const storage = isBrowser ? localStorage : noopStorage;
  const initialValue = storage.getItem(getModeStorageKey());
  let value = isValidMode(initialValue) ? initialValue : defaultValue;
  function getModeStorageKey() {
    return get(modeStorageKey);
  }
  const { subscribe, set: _set } = writable(value, () => {
    if (!isBrowser)
      return;
    const handler = (e) => {
      if (e.key !== getModeStorageKey())
        return;
      const newValue = e.newValue;
      if (isValidMode(newValue)) {
        _set(value = newValue);
      } else {
        _set(value = defaultValue);
      }
    };
    addEventListener("storage", handler);
    return () => removeEventListener("storage", handler);
  });
  function set(v) {
    _set(value = v);
    storage.setItem(getModeStorageKey(), value);
  }
  return {
    subscribe,
    set
  };
}
function createCustomTheme() {
  const storage = isBrowser ? localStorage : noopStorage;
  const initialValue = storage.getItem(getThemeStorageKey());
  let value = initialValue === null || initialValue === void 0 ? "" : initialValue;
  function getThemeStorageKey() {
    return get(themeStorageKey);
  }
  const { subscribe, set: _set } = writable(value, () => {
    if (!isBrowser)
      return;
    const handler = (e) => {
      if (e.key !== getThemeStorageKey())
        return;
      const newValue = e.newValue;
      if (newValue === null) {
        _set(value = "");
      } else {
        _set(value = newValue);
      }
    };
    addEventListener("storage", handler);
    return () => removeEventListener("storage", handler);
  });
  function set(v) {
    _set(value = v);
    storage.setItem(getThemeStorageKey(), value);
  }
  return {
    subscribe,
    set
  };
}
function createSystemMode() {
  const defaultValue = void 0;
  let track = true;
  const { subscribe, set } = writable(defaultValue, () => {
    if (!isBrowser)
      return;
    const handler = (e) => {
      if (!track)
        return;
      set(e.matches ? "light" : "dark");
    };
    const mediaQueryState = window.matchMedia("(prefers-color-scheme: light)");
    mediaQueryState.addEventListener("change", handler);
    return () => mediaQueryState.removeEventListener("change", handler);
  });
  function query() {
    if (!isBrowser)
      return;
    const mediaQueryState = window.matchMedia("(prefers-color-scheme: light)");
    set(mediaQueryState.matches ? "light" : "dark");
  }
  function tracking(active) {
    track = active;
  }
  return {
    subscribe,
    query,
    tracking
  };
}
function createDerivedMode() {
  const { subscribe } = derived([
    userPrefersMode,
    systemPrefersMode,
    themeColors,
    disableTransitions,
    darkClassNames,
    lightClassNames
  ], ([$userPrefersMode, $systemPrefersMode, $themeColors, $disableTransitions, $darkClassNames, $lightClassNames]) => {
    if (!isBrowser)
      return void 0;
    const derivedMode2 = $userPrefersMode === "system" ? $systemPrefersMode : $userPrefersMode;
    const sanitizedDarkClassNames = sanitizeClassNames($darkClassNames);
    const sanitizedLightClassNames = sanitizeClassNames($lightClassNames);
    function update() {
      const htmlEl = document.documentElement;
      const themeColorEl = document.querySelector('meta[name="theme-color"]');
      if (derivedMode2 === "light") {
        if (sanitizedDarkClassNames.length)
          htmlEl.classList.remove(...sanitizedDarkClassNames);
        if (sanitizedLightClassNames.length)
          htmlEl.classList.add(...sanitizedLightClassNames);
        htmlEl.style.colorScheme = "light";
        if (themeColorEl && $themeColors) {
          themeColorEl.setAttribute("content", $themeColors.light);
        }
      } else {
        if (sanitizedLightClassNames.length)
          htmlEl.classList.remove(...sanitizedLightClassNames);
        if (sanitizedDarkClassNames.length)
          htmlEl.classList.add(...sanitizedDarkClassNames);
        htmlEl.style.colorScheme = "dark";
        if (themeColorEl && $themeColors) {
          themeColorEl.setAttribute("content", $themeColors.dark);
        }
      }
    }
    if ($disableTransitions) {
      withoutTransition(update);
    } else {
      update();
    }
    return derivedMode2;
  });
  return {
    subscribe
  };
}
function createDerivedTheme() {
  const { subscribe } = derived([theme, disableTransitions], ([$theme, $disableTransitions]) => {
    if (!isBrowser)
      return void 0;
    function update() {
      const htmlEl = document.documentElement;
      htmlEl.setAttribute("data-theme", $theme);
    }
    if ($disableTransitions) {
      withoutTransition(update);
    } else {
      update();
    }
    return $theme;
  });
  return {
    subscribe
  };
}
function isValidMode(value) {
  if (typeof value !== "string")
    return false;
  return modes.includes(value);
}
const defaultPreferences = {
  taskReminders: true,
  dailyDigest: true,
  pomodoroAlerts: true,
  projectUpdates: false
};
const initialState = {
  isSupported: false,
  permission: "default",
  isSubscribed: false,
  isLoading: false,
  error: null,
  preferences: defaultPreferences
};
function createNotificationsStore() {
  const store = writable(initialState);
  const { subscribe, set, update } = store;
  function checkSupport() {
    if (typeof window === "undefined") return false;
    return "serviceWorker" in navigator && "PushManager" in window && "Notification" in window;
  }
  function urlBase64ToUint8Array(base64String) {
    const padding = "=".repeat((4 - base64String.length % 4) % 4);
    const base64 = (base64String + padding).replace(/-/g, "+").replace(/_/g, "/");
    const rawData = window.atob(base64);
    const outputArray = new Uint8Array(rawData.length);
    for (let i = 0; i < rawData.length; ++i) {
      outputArray[i] = rawData.charCodeAt(i);
    }
    return outputArray;
  }
  async function loadPreferences() {
    try {
      const prefs = await api.notifications.getPreferences();
      update((s) => ({
        ...s,
        preferences: { ...defaultPreferences, ...prefs }
      }));
      return { success: true };
    } catch (error) {
      logger.error("Failed to load notification preferences", error);
      return { success: false, error: error.message };
    }
  }
  async function requestPermission() {
    update((state) => ({ ...state, isLoading: true, error: null }));
    try {
      const permission = await Notification.requestPermission();
      update((state) => ({
        ...state,
        permission,
        isLoading: false
      }));
      return permission === "granted";
    } catch (error) {
      update((state) => ({
        ...state,
        isLoading: false,
        error: "Failed to request permission"
      }));
      return false;
    }
  }
  return {
    subscribe,
    async initialize() {
      const isSupported = checkSupport();
      const permission = isSupported ? Notification.permission : "denied";
      update((state) => ({
        ...state,
        isSupported,
        permission
      }));
      if (!isSupported) {
        return { success: false, error: "Push notifications not supported" };
      }
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        update((state) => ({
          ...state,
          isSubscribed: !!subscription
        }));
        if (subscription) {
          await loadPreferences();
        }
        return { success: true };
      } catch (error) {
        logger.error("Failed to check subscription", error);
        return { success: false, error: error.message };
      }
    },
    requestPermission,
    async enablePush() {
      const state = get(store);
      if (!state.isSupported) {
        return { success: false, error: "Push notifications not supported" };
      }
      if (state.permission !== "granted") {
        const granted = await requestPermission();
        if (!granted) {
          return { success: false, error: "Permission denied" };
        }
      }
      update((s) => ({ ...s, isLoading: true, error: null }));
      try {
        const vapidResponse = await api.notifications.getVapidKey();
        const vapidPublicKey = vapidResponse.publicKey;
        if (!vapidPublicKey) {
          throw new Error("VAPID key not configured on server");
        }
        const registration = await navigator.serviceWorker.ready;
        const applicationServerKey = urlBase64ToUint8Array(vapidPublicKey);
        const pushSubscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey.buffer
        });
        const p256dhKey = pushSubscription.getKey("p256dh");
        const authKey = pushSubscription.getKey("auth");
        if (!p256dhKey || !authKey) {
          throw new Error("Failed to get subscription keys");
        }
        await api.notifications.subscribe({
          endpoint: pushSubscription.endpoint,
          keys: {
            p256dh: btoa(String.fromCharCode(...new Uint8Array(p256dhKey))),
            auth: btoa(String.fromCharCode(...new Uint8Array(authKey)))
          }
        });
        update((s) => ({
          ...s,
          isSubscribed: true,
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        logger.error("Subscription failed", error);
        update((s) => ({
          ...s,
          isLoading: false,
          error: error.message || "Subscription failed"
        }));
        return { success: false, error: error.message };
      }
    },
    async disablePush() {
      update((s) => ({ ...s, isLoading: true, error: null }));
      try {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        if (subscription) {
          await subscription.unsubscribe();
          await api.notifications.unsubscribe();
        }
        update((s) => ({
          ...s,
          isSubscribed: false,
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        update((s) => ({
          ...s,
          isLoading: false,
          error: error.message || "Unsubscribe failed"
        }));
        return { success: false, error: error.message };
      }
    },
    loadPreferences,
    async updatePreferences(prefs) {
      update((s) => ({ ...s, isLoading: true, error: null }));
      try {
        await api.notifications.updatePreferences(prefs);
        update((s) => ({
          ...s,
          preferences: { ...s.preferences, ...prefs },
          isLoading: false
        }));
        return { success: true };
      } catch (error) {
        update((s) => ({
          ...s,
          isLoading: false,
          error: error.message || "Failed to update preferences"
        }));
        return { success: false, error: error.message };
      }
    },
    async testNotification() {
      try {
        await api.notifications.test();
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
  };
}
const notificationsStore = createNotificationsStore();
export {
  darkClassNames as a,
  themeStorageKey as b,
  derivedMode as c,
  disableTransitions as d,
  lightClassNames as l,
  modeStorageKey as m,
  notificationsStore as n,
  themeColors as t
};
