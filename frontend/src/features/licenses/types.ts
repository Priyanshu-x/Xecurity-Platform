import { Organization } from '../organizations/types';
import { Product } from '../products/types';
import { Subscription } from '../subscriptions/types';
import { Deployment } from '../deployments/types';

export enum LicenseStatus {
  ACTIVE = 'ACTIVE',
  REVOKED = 'REVOKED',
  EXPIRED = 'EXPIRED',
}

export interface License {
  id: string;
  subscription_id: string;
  deployment_id: string;
  organization_id: string;
  product_id: string;
  product_plan_id: string;
  
  status: LicenseStatus;
  
  issued_at: string;
  expires_at?: string;
  
  payload_json: Record<string, any>;
  notes?: string;

  // Eagerly loaded
  organization?: Organization;
  product?: Product;
  subscription?: Subscription;
  deployment?: Deployment;
}

export interface LicenseIssue {
  subscription_id: string;
  notes?: string;
}

export interface LicenseRevoke {
  notes?: string;
}
