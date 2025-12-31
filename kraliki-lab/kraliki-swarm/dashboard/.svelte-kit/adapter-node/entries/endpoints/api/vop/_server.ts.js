import { json } from "@sveltejs/kit";
const legacyResponse = () => json(
  { error: "Legacy Speak endpoint removed. Use /api/speak instead." },
  { status: 410 }
);
const GET = async () => legacyResponse();
const POST = async () => legacyResponse();
const PUT = async () => legacyResponse();
const PATCH = async () => legacyResponse();
const DELETE = async () => legacyResponse();
export {
  DELETE,
  GET,
  PATCH,
  POST,
  PUT
};
