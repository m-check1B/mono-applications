import { redirect } from "@sveltejs/kit";
const load = () => {
  throw redirect(307, "/dashboard");
};
export {
  load
};
