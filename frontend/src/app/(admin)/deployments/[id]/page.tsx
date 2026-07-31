'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import { Key, Activity, ShieldCheck, FileText, Server, Clock } from 'lucide-react';
import { useDeployment } from '@/features/deployments/hooks/useDeployment';
import { Badge } from '@/components/ui/badge';
import { DeploymentEnvironment, DeploymentStatus } from '@/features/deployments/types';
import { EntityDetailsLayout } from '@/components/layout/EntityDetailsLayout';

export default function DeploymentDetailsPage() {
  const params = useParams();
  const id = params.id as string;

  const { data: deployment, isLoading, isError } = useDeployment(id);

  if (isLoading) {
    return <div className="p-8 text-center text-muted-foreground animate-pulse">Loading deployment details...</div>;
  }

  if (isError || !deployment) {
    return <div className="p-8 text-center text-destructive">Failed to load deployment.</div>;
  }

  const getEnvBadge = (env: DeploymentEnvironment) => {
    switch (env) {
      case DeploymentEnvironment.PRODUCTION: return <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20"><span className="mr-1">🟢</span> Production</Badge>;
      case DeploymentEnvironment.STAGING: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20"><span className="mr-1">🟡</span> Staging</Badge>;
      case DeploymentEnvironment.DEVELOPMENT: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 hover:bg-slate-500/20"><span className="mr-1">⚪</span> Development</Badge>;
      default: return <Badge variant="outline">{env}</Badge>;
    }
  };

  const getStatusBadge = (status: DeploymentStatus) => {
    switch (status) {
      case DeploymentStatus.RUNNING: return <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20">Running</Badge>;
      case DeploymentStatus.PROVISIONING: return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/20">Provisioning</Badge>;
      case DeploymentStatus.DEGRADED: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/20">Degraded</Badge>;
      case DeploymentStatus.STOPPED: return <Badge variant="outline" className="bg-orange-500/10 text-orange-500 hover:bg-orange-500/20 border-orange-500/20">Stopped</Badge>;
      case DeploymentStatus.OFFLINE: return <Badge variant="outline" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20">Offline</Badge>;
      case DeploymentStatus.DECOMMISSIONED: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 hover:bg-slate-500/20 border-slate-500/20">Decommissioned</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const tabs = [
    { name: 'Overview', icon: FileText, current: true },
    { name: 'Licenses', icon: Key, current: false, isSoon: true },
    { name: 'Telemetry', icon: Activity, current: false, isSoon: true },
    { name: 'Activation', icon: ShieldCheck, current: false, isSoon: true },
    { name: 'Events', icon: Server, current: false, isSoon: true },
  ];

  return (
    <EntityDetailsLayout
      title={deployment.name}
      subtitle={deployment.current_release_version ? `Version ${deployment.current_release_version}` : 'No version recorded'}
      badges={
        <div className="flex space-x-2">
          {getEnvBadge(deployment.environment)}
          {getStatusBadge(deployment.status)}
        </div>
      }
      tabs={tabs}
      sidebar={
        <div className="space-y-6">
          <div className="border border-border/50 rounded-lg p-6 bg-card/50">
            <h3 className="text-lg font-medium mb-4 flex items-center">
              <Activity className="w-5 h-5 mr-2 text-muted-foreground" />
              Health
            </h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Status</span>
                <span className="font-medium">{getStatusBadge(deployment.status)}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Last Seen</span>
                <span className="font-medium">
                  {deployment.last_ping_at 
                    ? new Date(deployment.last_ping_at).toLocaleString() 
                    : 'Never'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Created</span>
                <span className="font-medium">
                  {new Date(deployment.created_at).toLocaleDateString()}
                </span>
              </div>
            </div>
          </div>
        </div>
      }
    >
      <div className="border border-border/50 rounded-lg p-6 bg-card/50">
        <h3 className="text-lg font-medium mb-4 flex items-center">
          <Server className="w-5 h-5 mr-2 text-muted-foreground" />
          Deployment Information
        </h3>
        <div className="grid grid-cols-2 gap-8">
          <div>
            <p className="text-sm font-medium text-muted-foreground">Environment</p>
            <p className="mt-2 text-base font-medium">{getEnvBadge(deployment.environment)}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Current Version</p>
            <p className="mt-2 text-base font-mono bg-muted inline-block px-2 py-0.5 rounded">
              {deployment.current_release_version || 'None'}
            </p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Organization</p>
            <p className="mt-2 text-base font-medium">{deployment.organization?.name || 'Unknown'}</p>
          </div>
          <div>
            <p className="text-sm font-medium text-muted-foreground">Product</p>
            <p className="mt-2 text-base font-medium">{deployment.product?.name || 'Unknown'}</p>
          </div>
        </div>
      </div>
    </EntityDetailsLayout>
  );
}
