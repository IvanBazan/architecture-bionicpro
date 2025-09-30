export interface TelemetryData {
  valueA: number;
  valueB: number;
  valueC: number;
  valueD: string;
  timestamp: string;
}

export interface UserInfo {
  username: string;
  first_name: string;
  last_name: string;
  email: string;
}

export interface ApiResponse {
  report: string;
  user: UserInfo;
  telemetry_data: TelemetryData[];
  count: number;
}

export interface ReportState {
  data: ApiResponse | null;
  loading: boolean;
  error: string | null;
}