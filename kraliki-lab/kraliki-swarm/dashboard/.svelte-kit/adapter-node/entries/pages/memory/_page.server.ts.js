import { redirect } from "@sveltejs/kit";
const load = () => {
  throw redirect(302, "/recall");
};
export {
  load
};
