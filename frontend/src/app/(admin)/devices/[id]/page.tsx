'use client';

import React, { use } from 'react';
import { ArrowLeft, Monitor, Cpu, Activity, ShieldCheck, DownloadCloud, Clock, CheckCircle, AlertTriangle, ShieldOff, Key } from 'lucide-react';
import { useRouter } from 'next/navigation';

import { DeviceStatus } from '@/features/devices/types';
import { useDevice } from '@/features/devices/hooks/useDevice';
import { useActivationRequests } from '@/features/activation-requests/hooks/useActivationRequests';

import { Button } from '@/components/ui/button';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

function formatDistanceTo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((date.getTime() - now.getTime()) / 1000);
  
  if (diffInSeconds < 0) return 'expired';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours`;
  return `${Math.floor(diffInSeconds / 86400)} days`;
}

export default function DeviceDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);

  const { data: device, isLoading, isError } = useDevice(id);
  const { data: requestsData, isLoading: isLoadingRequests } = useActivationRequests({ device_id: id });

  const getStatusBadge = (status: DeviceStatus) => {
    switch (status) {
      case DeviceStatus.ACTIVE: return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20"><CheckCircle className="w-3 h-3 mr-1"/> Active</Badge>;
      case DeviceStatus.TRIAL: return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20"><Clock className="w-3 h-3 mr-1"/> Trial</Badge>;
      case DeviceStatus.EXPIRED: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20"><AlertTriangle className="w-3 h-3 mr-1"/> Expired</Badge>;
      case DeviceStatus.BLOCKED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20"><ShieldOff className="w-3 h-3 mr-1"/> Blocked</Badge>;
      case DeviceStatus.REVOKED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Revoked</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  if (isLoading) {
    return <div className="p-8 space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-32 w-full" /></div>;
  }

  if (isError || !device) {
    return (
      <div className="p-8 text-center text-destructive">
        Failed to load device. It may have been deleted.
        <Button variant="link" onClick={() => router.push('/devices')}>Go Back</Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/devices')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold tracking-tight">{device.hostname || 'Unknown Device'}</h1>
              {getStatusBadge(device.status)}
            </div>
            <p className="text-muted-foreground flex items-center mt-1">
              <Monitor className="w-4 h-4 mr-1" />
              {device.os} {device.os_version} • Build {device.current_build || 'Unknown'}
            </p>
          </div>
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="hardware">Hardware</TabsTrigger>
          <TabsTrigger value="licensing">Licensing</TabsTrigger>
          <TabsTrigger value="requests">Requests</TabsTrigger>
          <TabsTrigger value="telemetry">Telemetry</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>System Information</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-2 gap-y-4">
                  <div>
                    <div className="text-sm text-muted-foreground">Hostname</div>
                    <div className="font-medium">{device.hostname || '—'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Username</div>
                    <div className="font-medium">{device.username || '—'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Operating System</div>
                    <div className="font-medium">{device.os} {device.os_version}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Architecture</div>
                    <div className="font-medium">{device.architecture || '—'}</div>
                  </div>
                  <div className="col-span-2">
                    <div className="text-sm text-muted-foreground">Fingerprint</div>
                    <div className="font-mono text-xs bg-muted p-2 rounded mt-1 overflow-x-auto">
                      {device.fingerprint}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Telemetry Status</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground flex items-center"><Activity className="w-4 h-4 mr-2" /> Last Seen</span>
                    <span className="font-medium">
                      {device.last_seen ? formatTimeAgo(device.last_seen) : 'Never'}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground flex items-center"><DownloadCloud className="w-4 h-4 mr-2" /> Current Build</span>
                    <span className="font-medium">{device.current_build || 'Unknown'}</span>
                  </div>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-muted-foreground flex items-center"><Clock className="w-4 h-4 mr-2" /> First Registered</span>
                    <span className="font-medium">
                      {new Date(device.first_seen).toLocaleDateString()}
                    </span>
                  </div>
                  {device.last_ip && (
                    <div className="flex items-center justify-between text-sm pt-4 border-t border-border/50">
                      <span className="text-muted-foreground">Last Known IP</span>
                      <span className="font-mono">{device.last_ip}</span>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="hardware">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><Cpu className="w-5 h-5 mr-2"/> Hardware Profile</CardTitle>
              <CardDescription>Extracted hardware and bios information from the host machine.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <div className="text-sm text-muted-foreground">CPU Processor</div>
                  <div className="font-medium">{device.cpu || 'Unknown'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Total RAM</div>
                  <div className="font-medium">{device.ram || 'Unknown'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">BIOS Information</div>
                  <div className="font-medium">{device.bios || 'Unknown'}</div>
                </div>
                <div>
                  <div className="text-sm text-muted-foreground">Environment</div>
                  <div className="font-medium">
                    {device.is_virtual_machine === true ? 'Virtual Machine' : 
                     device.is_virtual_machine === false ? 'Physical Hardware' : 'Unknown'}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="licensing">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center"><ShieldCheck className="w-5 h-5 mr-2"/> License & Authorization</CardTitle>
              <CardDescription>View the current operational authorization state of this device.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              
              {device.status === DeviceStatus.TRIAL && (
                <div className="bg-blue-500/10 border border-blue-500/20 p-4 rounded-lg flex items-center justify-between">
                  <div>
                    <h3 className="font-medium text-blue-500 flex items-center">
                      <Clock className="w-4 h-4 mr-2" />
                      Active Trial Period
                    </h3>
                    <p className="text-sm text-muted-foreground mt-1">
                      Started: {device.trial_started ? new Date(device.trial_started).toLocaleDateString() : 'Unknown'} <br/>
                      Ends: {device.trial_ends ? new Date(device.trial_ends).toLocaleDateString() : 'Unknown'}
                    </p>
                  </div>
                  {device.trial_ends && (
                    <div className="text-2xl font-bold text-blue-500">
                      {formatDistanceTo(device.trial_ends)} left
                    </div>
                  )}
                </div>
              )}

              {device.active_license_id ? (
                <div className="flex items-center justify-between p-4 border border-border/50 rounded-lg">
                  <div className="flex items-center">
                    <Key className="w-8 h-8 text-green-500 mr-4" />
                    <div>
                      <div className="font-medium">Active Full License</div>
                      <div className="text-sm text-muted-foreground">ID: {device.active_license_id}</div>
                    </div>
                  </div>
                  <Button variant="outline" size="sm">View License Details</Button>
                </div>
              ) : (
                device.status !== DeviceStatus.TRIAL && (
                  <div className="p-4 border border-border/50 rounded-lg text-center bg-muted/50">
                    <AlertTriangle className="w-8 h-8 mx-auto text-yellow-500 mb-2 opacity-50" />
                    <div className="font-medium">No Active License</div>
                    <div className="text-sm text-muted-foreground">This device is currently unlicensed.</div>
                  </div>
                )
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="requests">
          <Card>
            <CardHeader>
              <CardTitle>Activation Requests</CardTitle>
              <CardDescription>License requests originating from this device.</CardDescription>
            </CardHeader>
            <CardContent>
              {isLoadingRequests ? (
                <div className="text-muted-foreground text-sm">Loading requests...</div>
              ) : requestsData?.items?.length ? (
                <div className="space-y-4">
                  {requestsData.items.map((req: any) => (
                    <div key={req.id} className="flex justify-between items-center border p-4 rounded-md">
                      <div>
                        <div className="font-medium text-sm text-primary hover:underline cursor-pointer" onClick={() => router.push(`/activation-requests/${req.id}`)}>
                          {req.request_number}
                        </div>
                        <div className="text-xs text-muted-foreground mt-1">Type: {req.request_type} • Date: {new Date(req.created_at).toLocaleDateString()}</div>
                      </div>
                      <Badge variant="outline">{req.status}</Badge>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-muted-foreground text-sm italic">No requests linked to this device yet.</div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="telemetry">
          <Card>
            <CardHeader>
              <CardTitle>Telemetry Stream</CardTitle>
              <CardDescription>Event logs and network activity collected during heartbeats.</CardDescription>
            </CardHeader>
            <CardContent>
               <p className="text-muted-foreground text-sm italic">Telemetry event log view placeholder (Phase 3.6)</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
