import { Organization } from '../organizations/types';
import { Product } from '../products/types';

export enum DeploymentEnvironment {
  DEVELOPMENT = 'DEVELOPMENT',
  STAGING = 'STAGING',
  PRODUCTION = 'PRODUCTION',
}

export enum DeploymentStatus {
  PROVISIONING = 'PROVISIONING',
  RUNNING = 'RUNNING',
  STOPPED = 'STOPPED',
  DEGRADED = 'DEGRADED',
  OFFLINE = 'OFFLINE',
  DECOMMISSIONED = 'DECOMMISSIONED',
}

export interface Deployment {
  id: string;
  name: string;
  organization_id: string;
  product_id: string;
  environment: DeploymentEnvironment;
  status: DeploymentStatus;
  current_release_version?: string;
  last_ping_at?: string;
  created_at: string;
  updated_at: string;
  
  // Eagerly loaded
  organization?: Organization;
  product?: Product;
}

export interface DeploymentCreate {
  name: string;
  organization_id: string;
  product_id: string;
  environment?: DeploymentEnvironment;
}

export interface DeploymentUpdate {
  name?: string;
  environment?: DeploymentEnvironment;
  status?: DeploymentStatus;
  current_release_version?: string;
}
