'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, MoreHorizontal, Pencil, Archive, Building } from 'lucide-react';
import { toast } from 'sonner';

import { organizationService } from '@/features/organizations/organizationService';
import { Organization, OrganizationCreate, OrganizationUpdate } from '@/features/organizations/types';
import { OrganizationForm } from '@/features/organizations/components/OrganizationForm';

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

export default function OrganizationsPage() {
  const queryClient = useQueryClient();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingOrganization, setEditingOrganization] = useState<Organization | null>(null);
  const [archivingOrganization, setArchivingOrganization] = useState<Organization | null>(null);

  const { data: organizations, isLoading, isError } = useQuery({
    queryKey: ['organizations'],
    queryFn: () => organizationService.getOrganizations(),
  });

  const createMutation = useMutation({
    mutationFn: (data: OrganizationCreate) => organizationService.createOrganization(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setIsCreateOpen(false);
      toast.success('Organization created successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to create organization');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: OrganizationUpdate }) => organizationService.updateOrganization(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setEditingOrganization(null);
      toast.success('Organization updated successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to update organization');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => organizationService.deleteOrganization(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setArchivingOrganization(null);
      toast.success('Organization archived successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to archive organization');
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Organizations</h1>
          <p className="text-muted-foreground">
            Manage your customer organizations and tenants.
          </p>
        </div>
        
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger render={<Button />}>
            <Plus className="w-4 h-4 mr-2" />
            Add Organization
          </DialogTrigger>
          <DialogContent className="max-w-md">
            <DialogHeader>
              <DialogTitle>Create New Organization</DialogTitle>
              <DialogDescription>
                Add a new tenant to the platform.
              </DialogDescription>
            </DialogHeader>
            <OrganizationForm 
              onSubmit={(data) => createMutation.mutate(data as OrganizationCreate)} 
              isSubmitting={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Organization</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={3} className="h-24 text-center text-destructive">
                  Failed to load organizations. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && organizations?.length === 0 && (
              <TableRow>
                <TableCell colSpan={3} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Building className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No organizations found</p>
                    <p className="text-sm">Get started by adding your first customer.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && organizations?.map((org) => (
              <TableRow key={org.id}>
                <TableCell className="font-medium">
                  {org.name}
                </TableCell>
                <TableCell>
                  {org.is_deleted ? (
                    <Badge variant="outline" className="bg-gray-500/10 text-gray-500 hover:bg-gray-500/20">
                      Archived
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20">
                      Active
                    </Badge>
                  )}
                </TableCell>
                <TableCell className="text-right">
                  <DropdownMenu>
                    <DropdownMenuTrigger render={<Button variant="ghost" className="h-8 w-8 p-0" />}>
                      <span className="sr-only">Open menu</span>
                      <MoreHorizontal className="h-4 w-4" />
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuLabel>Actions</DropdownMenuLabel>
                      <DropdownMenuItem onClick={() => setEditingOrganization(org)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setArchivingOrganization(org)}
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                      >
                        <Archive className="w-4 h-4 mr-2" /> Archive
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Edit Dialog */}
      <Dialog open={!!editingOrganization} onOpenChange={(open) => !open && setEditingOrganization(null)}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Edit Organization</DialogTitle>
            <DialogDescription>
              Update {editingOrganization?.name}.
            </DialogDescription>
          </DialogHeader>
          {editingOrganization && (
            <OrganizationForm 
              initialData={editingOrganization}
              onSubmit={(data) => updateMutation.mutate({ id: editingOrganization.id, data })}
              isSubmitting={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Archive Confirmation Dialog */}
      <Dialog open={!!archivingOrganization} onOpenChange={(open) => !open && setArchivingOrganization(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Organization</DialogTitle>
            <DialogDescription>
              Are you sure you want to archive 
              <span className="font-bold text-foreground"> {archivingOrganization?.name}</span>? 
              This will disable access for all users in this organization.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setArchivingOrganization(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => archivingOrganization && deleteMutation.mutate(archivingOrganization.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Archiving...' : 'Archive Organization'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
