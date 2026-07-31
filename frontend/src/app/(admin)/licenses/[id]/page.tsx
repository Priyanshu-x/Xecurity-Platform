'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { Key, Activity, Code, ShieldCheck, FileText, Info, Copy } from 'lucide-react';
import { toast } from 'sonner';
import { useLicense } from '@/features/licenses/hooks/useLicense';
import { Badge } from '@/components/ui/badge';
import { LicenseStatus } from '@/features/licenses/types';
import { EntityDetailsLayout } from '@/components/layout/EntityDetailsLayout';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function LicenseDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: license, isLoading, isError } = useLicense(id);

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading license details...</div>;
  }

  if (isError || !license) {
    return <div className="p-8 text-center text-destructive">Failed to load license.</div>;
  }

  const getStatusBadge = (status: LicenseStatus) => {
    switch (status) {
      case LicenseStatus.ACTIVE: return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Active</Badge>;
      case LicenseStatus.EXPIRED: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Expired</Badge>;
      case LicenseStatus.REVOKED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Revoked</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const tabs = [
    { name: 'Overview', icon: FileText, current: true },
    { name: 'Payload', icon: Code, current: false },
    { name: 'Capabilities', icon: Key, current: false },
    { name: 'Activation', icon: ShieldCheck, current: false, isSoon: true },
    { name: 'Audit', icon: Activity, current: false, isSoon: true },
    { name: 'Metadata', icon: Info, current: false },
  ];

  const handleCopyPayload = () => {
    navigator.clipboard.writeText(JSON.stringify(license.payload_json, null, 2));
    toast.success('Payload copied to clipboard');
  };

  return (
    <EntityDetailsLayout
      title={`License ${license.id.split('-')[0]}`}
      subtitle={license.deployment?.name || 'Unknown Deployment'}
      badges={getStatusBadge(license.status)}
      tabs={tabs}
      sidebar={
        <div className="space-y-6">
          <div className="border border-border/50 rounded-lg p-6 bg-card/50">
            <h3 className="text-lg font-medium mb-4 flex items-center">
              <Info className="w-5 h-5 mr-2 text-muted-foreground" />
              Quick Info
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Issued At</span>
                <span className="font-medium">
                  {new Date(license.issued_at).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Expires At</span>
                <span className="font-medium">
                  {license.expires_at ? new Date(license.expires_at).toLocaleDateString() : 'Never'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Tier</span>
                <Badge variant="secondary">{license.payload_json?.tier || 'UNKNOWN'}</Badge>
              </div>
            </div>
          </div>
        </div>
      }
    >
      <div className="space-y-6">
        {/* Overview Section */}
        <div className="border border-border/50 rounded-lg p-6 bg-card/50">
          <h3 className="text-lg font-medium mb-4 flex items-center">
            <FileText className="w-5 h-5 mr-2 text-muted-foreground" />
            License Overview
          </h3>
          <div className="grid grid-cols-2 gap-8">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Organization</p>
              <p className="mt-2 text-base font-medium">{license.organization?.name || 'Unknown'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Product</p>
              <p className="mt-2 text-base font-medium">{license.product?.name || 'Unknown'}</p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Subscription</p>
              <p className="mt-2 text-base font-mono bg-muted inline-block px-2 py-0.5 rounded text-sm">
                {license.subscription_id.split('-')[0]}...
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Deployment Environment</p>
              <p className="mt-2 text-base">{license.deployment?.environment || 'Unknown'}</p>
            </div>
          </div>
        </div>

        {/* Payload Viewer */}
        <div className="border border-border/50 rounded-lg bg-card/50 overflow-hidden">
          <div className="flex items-center justify-between p-4 border-b border-border/50 bg-muted/20">
            <h3 className="text-lg font-medium flex items-center">
              <Code className="w-5 h-5 mr-2 text-muted-foreground" />
              Raw Payload
            </h3>
            <Button variant="outline" size="sm" onClick={handleCopyPayload}>
              <Copy className="w-4 h-4 mr-2" />
              Copy JSON
            </Button>
          </div>
          <ScrollArea className="h-[300px] w-full rounded-b-lg">
            <div className="p-4 bg-zinc-950">
              <pre className="text-sm text-zinc-50 font-mono">
                {JSON.stringify(license.payload_json, null, 2)}
              </pre>
            </div>
          </ScrollArea>
        </div>

        {/* Capabilities Section */}
        <div className="border border-border/50 rounded-lg p-6 bg-card/50">
          <h3 className="text-lg font-medium mb-4 flex items-center">
            <Key className="w-5 h-5 mr-2 text-muted-foreground" />
            Entitled Capabilities
          </h3>
          {license.payload_json?.capabilities && Array.isArray(license.payload_json.capabilities) ? (
            <div className="flex flex-wrap gap-2">
              {license.payload_json.capabilities.map((cap: string) => (
                <Badge key={cap} variant="secondary" className="px-3 py-1 text-sm font-mono">
                  [{cap}]
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-muted-foreground">No specific capabilities encoded in this license.</p>
          )}
        </div>

        {/* Metadata Section */}
        <div className="border border-border/50 rounded-lg p-6 bg-card/50">
          <h3 className="text-lg font-medium mb-4 flex items-center">
            <Info className="w-5 h-5 mr-2 text-muted-foreground" />
            Metadata
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="flex flex-col space-y-1">
              <span className="text-sm text-muted-foreground">License ID</span>
              <span className="font-mono text-sm break-all">{license.id}</span>
            </div>
            <div className="flex flex-col space-y-1">
              <span className="text-sm text-muted-foreground">Issued At</span>
              <span className="text-sm">{new Date(license.issued_at).toISOString()}</span>
            </div>
            <div className="flex flex-col space-y-1">
              <span className="text-sm text-muted-foreground">Signature/Fingerprint</span>
              <span className="font-mono text-sm text-muted-foreground italic">Pending Cryptographic Module</span>
            </div>
            <div className="flex flex-col space-y-1">
              <span className="text-sm text-muted-foreground">Revoked At</span>
              <span className="text-sm">{license.status === LicenseStatus.REVOKED ? 'Yes' : 'N/A'}</span>
            </div>
          </div>
        </div>

      </div>
    </EntityDetailsLayout>
  );
}
