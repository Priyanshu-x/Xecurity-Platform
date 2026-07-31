export enum ReleaseChannel {
  STABLE = 'STABLE',
  BETA = 'BETA',
  ALPHA = 'ALPHA',
  NIGHTLY = 'NIGHTLY',
  INTERNAL = 'INTERNAL',
}

export enum ReleaseStatus {
  DRAFT = 'DRAFT',
  TESTING = 'TESTING',
  RELEASE_CANDIDATE = 'RELEASE_CANDIDATE',
  PUBLISHED = 'PUBLISHED',
  DEPRECATED = 'DEPRECATED',
  ARCHIVED = 'ARCHIVED',
}

export enum ReleasePlatform {
  WINDOWS = 'WINDOWS',
  LINUX = 'LINUX',
  MACOS = 'MACOS',
}

export enum ReleaseArchitecture {
  X64 = 'x64',
  ARM64 = 'ARM64',
  X86 = 'x86',
}

export enum ArtifactType {
  EXE = 'EXE',
  ZIP = 'ZIP',
  MSI = 'MSI',
  PKG = 'PKG',
  DEB = 'DEB',
  RPM = 'RPM',
  DOCS = 'DOCS',
  SYMBOLS = 'SYMBOLS',
}

export interface ReleaseArtifact {
  id: string;
  release_id: string;
  platform: ReleasePlatform;
  architecture: ReleaseArchitecture;
  artifact_type: ArtifactType;
  filename: string;
  download_path: string;
  sha256: string;
  filesize: number;
  signature?: string;
  signature_algorithm?: string;
  signed_at?: string;
  created_at: string;
  updated_at: string;
}

export type ReleaseArtifactCreate = Omit<
  ReleaseArtifact,
  'id' | 'release_id' | 'created_at' | 'updated_at'
>;

export interface Release {
  id: string;
  product_id: string;
  version: string;
  build_number: number;
  channel: ReleaseChannel;
  status: ReleaseStatus;
  release_notes?: string;
  mandatory: boolean;
  minimum_license_build?: number;
  minimum_lms_build?: number;
  is_latest: boolean;
  published_at?: string;
  published_by?: string;
  created_at: string;
  updated_at: string;
  is_deleted: boolean;
  artifacts: ReleaseArtifact[];
}

export type ReleaseCreate = Omit<
  Release,
  | 'id'
  | 'published_at'
  | 'published_by'
  | 'created_at'
  | 'updated_at'
  | 'is_deleted'
  | 'artifacts'
> & {
  artifacts: ReleaseArtifactCreate[];
};

export type ReleaseUpdate = Partial<
  Omit<
    Release,
    | 'id'
    | 'product_id'
    | 'published_at'
    | 'published_by'
    | 'created_at'
    | 'updated_at'
    | 'is_deleted'
    | 'artifacts'
  >
>;
