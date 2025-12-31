import { redirect } from "@sveltejs/kit";
const GET = () => {
  throw redirect(302, "/favicon.svg");
};
export {
  GET
};
