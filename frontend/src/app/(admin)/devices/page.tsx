'use client';

import React from 'react';
import { Monitor, MoreHorizontal, FileText, CheckCircle, Clock, AlertTriangle, ShieldOff } from 'lucide-react';
import { toast } from 'sonner';

import { DeviceStatus } from '@/features/devices/types';
import { useDevices } from '@/features/devices/hooks/useDevices';

import { Button } from '@/components/ui/button';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { Skeleton } from '@/components/ui/skeleton';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

function formatTimeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

export default function DevicesPage() {
  const { data: devices, isLoading, isError } = useDevices();

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

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Devices</h1>
          <p className="text-muted-foreground">
            Monitor registered forensic workstations, heartbeats, and trial status.
          </p>
        </div>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Hostname / User</TableHead>
              <TableHead>OS</TableHead>
              <TableHead>Build</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last Seen</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-[150px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-[60px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-destructive">
                  Failed to load devices. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && devices?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Monitor className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No devices found</p>
                    <p className="text-sm">Devices will appear here once they register on first launch.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && devices?.map((device) => (
              <TableRow key={device.id}>
                <TableCell>
                  <div className="font-medium">{device.hostname || 'Unknown'}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    {device.username || 'Unknown User'} • {device.fingerprint.substring(0,8)}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-medium text-sm">{device.os || 'Unknown OS'}</div>
                  <div className="text-xs text-muted-foreground">{device.os_version}</div>
                </TableCell>
                <TableCell>
                  <div className="font-mono text-sm">{device.current_build || '—'}</div>
                </TableCell>
                <TableCell>
                  {getStatusBadge(device.status)}
                </TableCell>
                <TableCell>
                  <div className="text-sm">
                    {device.last_seen ? formatTimeAgo(device.last_seen) : 'Never'}
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" className="h-8 w-8 p-0">
                        <span className="sr-only">Open menu</span>
                        <MoreHorizontal className="h-4 w-4" />
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem asChild>
                        <Link href={`/devices/${device.id}`}>
                          <FileText className="w-4 h-4 mr-2" /> View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem className="text-destructive focus:bg-destructive focus:text-destructive-foreground">
                        <ShieldOff className="w-4 h-4 mr-2" /> Block Device
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
