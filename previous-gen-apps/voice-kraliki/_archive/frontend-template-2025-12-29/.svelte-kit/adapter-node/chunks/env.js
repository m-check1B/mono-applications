import { p as public_env } from "./shared-server.js";
const BACKEND_URL = public_env.PUBLIC_BACKEND_URL && public_env.PUBLIC_BACKEND_URL.trim().length > 0 ? public_env.PUBLIC_BACKEND_URL : "https://gemini-api.verduona.com";
const WS_URL = public_env.PUBLIC_WS_URL && public_env.PUBLIC_WS_URL.trim().length > 0 ? public_env.PUBLIC_WS_URL : BACKEND_URL.replace(/^http/, "ws");
const DEFAULT_FROM_NUMBER = public_env.PUBLIC_TWILIO_FROM_NUMBER && public_env.PUBLIC_TWILIO_FROM_NUMBER.trim().length > 0 ? public_env.PUBLIC_TWILIO_FROM_NUMBER : "+420228810376";
const COUNTRY_FROM_NUMBERS = {
  US: public_env.PUBLIC_TWILIO_FROM_NUMBER_US && public_env.PUBLIC_TWILIO_FROM_NUMBER_US.trim().length > 0 ? public_env.PUBLIC_TWILIO_FROM_NUMBER_US : "+18455954168",
  CZ: public_env.PUBLIC_TWILIO_FROM_NUMBER_CZ && public_env.PUBLIC_TWILIO_FROM_NUMBER_CZ.trim().length > 0 ? public_env.PUBLIC_TWILIO_FROM_NUMBER_CZ : "+420228810376",
  ES: public_env.PUBLIC_TWILIO_FROM_NUMBER_ES && public_env.PUBLIC_TWILIO_FROM_NUMBER_ES.trim().length > 0 ? public_env.PUBLIC_TWILIO_FROM_NUMBER_ES : "+34123456789"
};
export {
  BACKEND_URL as B,
  COUNTRY_FROM_NUMBERS as C,
  DEFAULT_FROM_NUMBER as D,
  WS_URL as W
};
