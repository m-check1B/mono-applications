const API_BASE = "http://127.0.0.1:3020/api";
async function getItem(category, itemId) {
  const response = await fetch(`${API_BASE}/capture/${category}/${itemId}`);
  if (!response.ok) {
    throw new Error(`Failed to get item: ${response.statusText}`);
  }
  return await response.json();
}
async function getRecentItems(category, limit = 20) {
  const params = new URLSearchParams();
  params.append("limit", limit.toString());
  const response = await fetch(`${API_BASE}/capture/recent?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to get recent items: ${response.statusText}`);
  }
  return await response.json();
}
async function getGraph(category, tag, depth = 2, limit = 100) {
  const params = new URLSearchParams();
  params.append("depth", depth.toString());
  params.append("limit", limit.toString());
  const response = await fetch(`${API_BASE}/graph?${params}`);
  if (!response.ok) {
    throw new Error(`Failed to get graph: ${response.statusText}`);
  }
  return await response.json();
}
export {
  getItem as a,
  getRecentItems as b,
  getGraph as g
};
