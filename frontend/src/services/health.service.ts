import { API_PATHS } from "@/constants/api";
import { apiClient } from "@/services/api-client";
import type { ApiSuccessResponse, HealthData } from "@/types/api";

export const healthService = {
  check: () =>
    apiClient.get<ApiSuccessResponse<HealthData>>(API_PATHS.HEALTH),
};
