import { useEffect, useState } from "react";

import { ERROR_MESSAGES } from "@/constants/errors";
import { healthService } from "@/services/health.service";

export function useHealth() {
  const [status, setStatus] = useState<string>("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const res = await healthService.check();
        setStatus(res.data.data.status);
      } catch {
        setError(ERROR_MESSAGES.HEALTH_CHECK_FAILED);
      } finally {
        setLoading(false);
      }
    };
    checkHealth();
  }, []);

  return { status, loading, error };
}
