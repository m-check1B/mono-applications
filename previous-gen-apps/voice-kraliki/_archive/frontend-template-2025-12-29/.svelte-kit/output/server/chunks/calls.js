import { noop, notifyManager, QueryObserver } from "@tanstack/query-core";
import { r as readable, d as derived, g as get } from "./index.js";
import { g as getIsRestoringContext, a as getQueryClientContext } from "./context2.js";
import { a as apiGet } from "./auth2.js";
import { m as migrateEndpoint } from "./sessions.js";
function useIsRestoring() {
  return getIsRestoringContext();
}
function useQueryClient(queryClient) {
  return getQueryClientContext();
}
function isSvelteStore(obj) {
  return "subscribe" in obj && typeof obj.subscribe === "function";
}
function createBaseQuery(options, Observer, queryClient) {
  const client = useQueryClient();
  const isRestoring = useIsRestoring();
  const optionsStore = isSvelteStore(options) ? options : readable(options);
  const defaultedOptionsStore = derived([optionsStore, isRestoring], ([$optionsStore, $isRestoring]) => {
    const defaultedOptions = client.defaultQueryOptions($optionsStore);
    defaultedOptions._optimisticResults = $isRestoring ? "isRestoring" : "optimistic";
    return defaultedOptions;
  });
  const observer = new Observer(client, get(defaultedOptionsStore));
  defaultedOptionsStore.subscribe(($defaultedOptions) => {
    observer.setOptions($defaultedOptions);
  });
  const result = derived(isRestoring, ($isRestoring, set) => {
    const unsubscribe = $isRestoring ? noop : observer.subscribe(notifyManager.batchCalls(set));
    observer.updateResult();
    return unsubscribe;
  });
  const { subscribe } = derived([result, defaultedOptionsStore], ([$result, $defaultedOptionsStore]) => {
    $result = observer.getOptimisticResult($defaultedOptionsStore);
    return !$defaultedOptionsStore.notifyOnChangeProps ? observer.trackResult($result) : $result;
  });
  return { subscribe };
}
function createQuery(options, queryClient) {
  return createBaseQuery(options, QueryObserver);
}
function getCompanies(params) {
  const searchParams = new URLSearchParams();
  const query = searchParams.toString();
  return apiGet(`/api/companies${query ? `?${query}` : ""}`);
}
function fetchAvailableVoices() {
  return apiGet(migrateEndpoint("/available-voices"));
}
function fetchAvailableModels() {
  return apiGet(migrateEndpoint("/available-models"));
}
function fetchVoiceConfig() {
  return apiGet(migrateEndpoint("/api/voice-config"));
}
function fetchCampaigns() {
  return apiGet(migrateEndpoint("/campaigns"));
}
function fetchCompanies() {
  return getCompanies().then(
    (companies) => companies.map((company) => ({
      id: company.id,
      name: company.name,
      phone: company.phone_number || "",
      status: company.is_active ? "active" : "inactive"
    }))
  );
}
function fetchTelephonyStats() {
  return apiGet("/api/telephony/stats");
}
export {
  fetchAvailableModels as a,
  fetchVoiceConfig as b,
  createQuery as c,
  fetchCampaigns as d,
  fetchCompanies as e,
  fetchAvailableVoices as f,
  fetchTelephonyStats as g
};
