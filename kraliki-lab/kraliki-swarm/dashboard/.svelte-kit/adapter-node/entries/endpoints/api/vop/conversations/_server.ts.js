import { json } from "@sveltejs/kit";
const legacyResponse = () => json(
  { error: "Legacy Speak endpoint removed. Use /api/speak instead." },
  { status: 410 }
);
const GET = async () => legacyResponse();
export {
  GET
};
