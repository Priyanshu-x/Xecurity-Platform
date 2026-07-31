export enum DeviceStatus {
  TRIAL = 'TRIAL',
  ACTIVE = 'ACTIVE',
  EXPIRED = 'EXPIRED',
  BLOCKED = 'BLOCKED',
  REVOKED = 'REVOKED',
  UNKNOWN = 'UNKNOWN',
}

export interface Device {
  id: string;
  fingerprint: string;
  machine_guid?: string;
  public_key?: string;
  
  device_name?: string;
  hostname?: string;
  username?: string;
  
  os?: string;
  os_version?: string;
  architecture?: string;
  
  cpu?: string;
  ram?: string;
  bios?: string;
  is_virtual_machine?: boolean;
  
  last_ip?: string;
  last_country?: string;
  timezone?: string;
  locale?: string;
  
  install_date?: string;
  last_boot?: string;
  uptime?: number;
  
  current_build?: number;
  current_version?: string;
  current_channel?: string;
  
  status: DeviceStatus;
  first_seen: string;
  last_seen: string;
  
  trial_started?: string;
  trial_ends?: string;
  
  active_license_id?: string;
  organization_id?: string;
  
  created_at: string;
  updated_at: string;
}

export interface DeviceCreate {
  fingerprint: string;
  machine_guid?: string;
  public_key?: string;
  
  device_name?: string;
  hostname?: string;
  username?: string;
  
  os?: string;
  os_version?: string;
  architecture?: string;
  
  cpu?: string;
  ram?: string;
  bios?: string;
  is_virtual_machine?: boolean;
  
  status?: DeviceStatus;
  organization_id?: string;
}

export interface DeviceUpdate {
  organization_id?: string;
  active_license_id?: string;
  status?: DeviceStatus;
  notes?: string;
}
