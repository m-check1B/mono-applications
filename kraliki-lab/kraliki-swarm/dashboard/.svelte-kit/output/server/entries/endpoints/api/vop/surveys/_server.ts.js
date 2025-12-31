import { json } from "@sveltejs/kit";
const legacyResponse = () => json(
  { error: "Legacy Speak endpoint removed. Use /api/speak/surveys instead." },
  { status: 410 }
);
const GET = async () => legacyResponse();
const POST = async () => legacyResponse();
const PATCH = async () => legacyResponse();
export {
  GET,
  PATCH,
  POST
};
