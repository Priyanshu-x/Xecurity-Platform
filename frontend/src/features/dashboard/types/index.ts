export interface DashboardOverview {
  organizations: number;
  products: number;
  devices: number;
  online_devices: number;
  pending_requests: number;
  active_licenses: number;
  expired_licenses: number;
}

export interface RecentActivityEvent {
  id: string;
  timestamp: string;
  message: string;
}

export interface SystemHealth {
  backend: string;
  database: string;
  storage: string;
  licensing_service: string;
}

export interface DashboardStatsResponse {
  overview: DashboardOverview;
  recent_activity: RecentActivityEvent[];
  system_health: SystemHealth;
}
