import { redirect } from "@sveltejs/kit";
const load = async () => {
  throw redirect(302, "/agents");
};
export {
  load
};
