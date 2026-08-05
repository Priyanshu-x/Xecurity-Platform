export type ActivationRequestStatus = 
  | 'PENDING'
  | 'UNDER_REVIEW'
  | 'APPROVED'
  | 'LICENSE_GENERATED'
  | 'DOWNLOADED'
  | 'REJECTED'
  | 'EXPIRED'
  | 'CANCELLED'
  | 'COMPLETED';

export type ActivationRequestType = 
  | 'ACTIVATION'
  | 'RENEWAL'
  | 'TRANSFER'
  | 'UPGRADE'
  | 'RECOVERY'
  | 'EMERGENCY';

export interface ActivationRequestEvent {
  id: string;
  request_id: string;
  status_from?: string;
  status_to: string;
  actor_id?: string;
  timestamp: string;
  notes?: string;
}

export interface ActivationRequest {
  id: string;
  request_number: string;
  device_id?: string;
  request_type: ActivationRequestType;
  status: ActivationRequestStatus;
  
  fingerprint: string;
  hostname?: string;
  username?: string;
  os?: string;
  os_version?: string;
  architecture?: string;
  cpu?: string;
  ram?: string;
  bios?: string;
  mac_address?: string;
  windows_sid?: string;
  current_build?: number;
  timezone?: string;
  locale?: string;
  hardware_tokens?: any[];

  original_filename?: string;
  sha256: string;
  size?: number;

  reject_reason?: string;
  admin_notes?: string;
  approved_by?: string;
  approved_at?: string;
  rejected_by?: string;
  rejected_at?: string;
  generated_license_id?: string;

  events: ActivationRequestEvent[];
  created_at: string;
  updated_at: string;
}

export interface LicenseGenerationConfig {
  organization_id: string;
  product_id: string;
  plan_id?: string;
  license_type: string;
  validity_months?: number;
  capabilities_override?: Record<string, any>;
  notes?: string;
}
