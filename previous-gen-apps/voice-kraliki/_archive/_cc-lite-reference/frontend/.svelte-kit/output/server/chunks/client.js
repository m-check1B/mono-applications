import { createTRPCClient, httpBatchLink } from "@trpc/client";
const API_URL = "http://127.0.0.1:3010";
const trpc = createTRPCClient({
  links: [
    httpBatchLink({
      url: `${API_URL}/trpc`,
      credentials: "include",
      // Send cookies for auth
      headers() {
        return {
          "Content-Type": "application/json"
        };
      }
    })
  ]
});
export {
  trpc as t
};
