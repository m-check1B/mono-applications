import { useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';
import { logger } from '@/utils/logger';

export function useDeviceId() {
  const [deviceId, setDeviceId] = useState("");

  useEffect(() => {
    // Check if device ID exists in cookies
    let existingDeviceId = Cookies.get("device_id");

    // If no device ID exists, generate a new one and save it
    if (!existingDeviceId) {
      existingDeviceId = uuidv4();

      // Set cookie with a long expiration (1 year)
      Cookies.set("device_id", existingDeviceId, {
        expires: 365,
        sameSite: "strict",
        secure: window.location.protocol === "https:",
      });

      logger.info("Generated new device ID", { deviceId: existingDeviceId });
    } else {
      logger.debug("Using existing device ID", { deviceId: existingDeviceId });
    }

    // Set the device ID in state
    setDeviceId(existingDeviceId);
  }, []);

  return { deviceId };
}
