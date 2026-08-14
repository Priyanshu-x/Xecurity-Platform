export interface TrialToken {
  id: string;
  token_string: string;
  expires_at: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface GenerateTokenRequest {
  month: number;
  year: number;
}

export interface ManifestResponse {
  version: number;
  active: boolean;
  token: string;
  expires_at: string | null;
}
