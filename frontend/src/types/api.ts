export type ApiSuccessResponse<T> = {
  is_success: true;
  data: T;
  message?: string;
};

export type ApiErrorResponse = {
  is_success: false;
  message: string;
  code: string;
};

export type ApiResponse<T> = ApiSuccessResponse<T> | ApiErrorResponse;

export type HealthData = {
  status: string;
};
