import { C as COUNTRY_FROM_NUMBERS, D as DEFAULT_FROM_NUMBER, W as WS_URL, B as BACKEND_URL } from "../../chunks/env.js";
const load = () => {
  return {
    config: {
      backendUrl: BACKEND_URL,
      wsUrl: WS_URL,
      defaultFromNumber: DEFAULT_FROM_NUMBER,
      countryFromNumbers: COUNTRY_FROM_NUMBERS
    }
  };
};
export {
  load
};
