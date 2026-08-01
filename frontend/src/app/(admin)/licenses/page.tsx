'use client';

import React, { useState } from 'react';
import { Plus, MoreHorizontal, FileText, Ban, Key } from 'lucide-react';
import { toast } from 'sonner';

import { License, LicenseStatus } from '@/features/licenses/types';
import { LicenseIssueForm } from '@/features/licenses/components/LicenseIssueForm';
import { useLicenses } from '@/features/licenses/hooks/useLicenses';
import { useIssueLicense } from '@/features/licenses/hooks/useIssueLicense';
import { useRevokeLicense } from '@/features/licenses/hooks/useRevokeLicense';

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
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import { Badge } from '@/components/ui/badge';
import Link from 'next/link';

export default function LicensesPage() {
  const [isIssueOpen, setIsIssueOpen] = useState(false);
  const [revokingLicense, setRevokingLicense] = useState<License | null>(null);

  const { data: licenses, isLoading, isError } = useLicenses();

  const issueMutation = useIssueLicense({
    onSuccess: () => {
      setIsIssueOpen(false);
      toast.success('License issued successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to issue license');
    },
  });

  const revokeMutation = useRevokeLicense({
    onSuccess: () => {
      setRevokingLicense(null);
      toast.success('License revoked successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to revoke license');
    },
  });

  const getStatusBadge = (status: LicenseStatus) => {
    switch (status) {
      case LicenseStatus.ACTIVE: return <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20 border-green-500/20">Active</Badge>;
      case LicenseStatus.EXPIRED: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/20">Expired</Badge>;
      case LicenseStatus.REVOKED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 hover:bg-red-500/20 border-red-500/20">Revoked</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Licenses</h1>
          <p className="text-muted-foreground">
            Manage and issue software licenses for deployments.
          </p>
        </div>
        
        <Dialog open={isIssueOpen} onOpenChange={setIsIssueOpen}>
          <DialogTrigger asChild><Button>
            <Plus className="w-4 h-4 mr-2" />
            Issue License
          </Button></DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Issue New License</DialogTitle>
              <DialogDescription>
                Bind a subscription to a deployment to issue an active license payload.
              </DialogDescription>
            </DialogHeader>
            <LicenseIssueForm 
              onSubmit={(deploymentId, data) => issueMutation.mutate({ deploymentId, data })} 
              isSubmitting={issueMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>License ID</TableHead>
              <TableHead>Deployment</TableHead>
              <TableHead>Customer</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Expiration</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-[150px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[120px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-destructive">
                  Failed to load licenses. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && licenses?.length === 0 && (
              <TableRow>
                <TableCell colSpan={6} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Key className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No licenses found</p>
                    <p className="text-sm">Start by issuing a license for a deployment.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && licenses?.map((license) => (
              <TableRow key={license.id}>
                <TableCell>
                  <div className="font-mono text-sm">{license.id.split('-')[0]}...</div>
                  <div className="text-xs text-muted-foreground mt-0.5">
                    Issued: {new Date(license.issued_at).toLocaleDateString()}
                  </div>
                </TableCell>
                <TableCell>
                  <div className="font-medium">{license.deployment?.name || 'Unknown'}</div>
                </TableCell>
                <TableCell>
                  <div className="font-medium">{license.organization?.name || 'Unknown'}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">{license.product?.name || 'Unknown'}</div>
                </TableCell>
                <TableCell>
                  {getStatusBadge(license.status)}
                </TableCell>
                <TableCell>
                  {license.expires_at ? new Date(license.expires_at).toLocaleDateString() : 'Never'}
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
                        <Link href={`/licenses/${license.id}`}>
                          <FileText className="w-4 h-4 mr-2" /> View Details
                        </Link>
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setRevokingLicense(license)}
                        disabled={license.status === LicenseStatus.REVOKED}
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                      >
                        <Ban className="w-4 h-4 mr-2" /> Revoke License
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Revoke Confirmation Dialog */}
      <Dialog open={!!revokingLicense} onOpenChange={(open) => !open && setRevokingLicense(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Revoke License</DialogTitle>
            <DialogDescription>
              Are you sure you want to revoke this license for 
              <span className="font-bold text-foreground"> {revokingLicense?.deployment?.name}</span>? 
              This will immediately invalidate the instance.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setRevokingLicense(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => revokingLicense && revokeMutation.mutate({ id: revokingLicense.id, data: { notes: 'Revoked from UI' } })}
              disabled={revokeMutation.isPending}
            >
              {revokeMutation.isPending ? 'Revoking...' : 'Revoke License'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
