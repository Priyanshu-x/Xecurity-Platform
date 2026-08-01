'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, MoreHorizontal, Pencil, Archive, Zap } from 'lucide-react';
import { toast } from 'sonner';

import { capabilityService } from '@/features/capabilities/capabilityService';
import { Capability, CapabilityCreate, CapabilityUpdate } from '@/features/capabilities/types';
import { CapabilityForm } from '@/features/capabilities/components/CapabilityForm';

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
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';

export default function CapabilitiesPage() {
  const queryClient = useQueryClient();
  
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingCapability, setEditingCapability] = useState<Capability | null>(null);
  const [archivingCapability, setArchivingCapability] = useState<Capability | null>(null);

  const { data: capabilities, isLoading, isError } = useQuery({
    queryKey: ['capabilities'],
    queryFn: () => capabilityService.getCapabilities(),
  });

  const createMutation = useMutation({
    mutationFn: (data: CapabilityCreate) => capabilityService.createCapability(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['capabilities'] });
      setIsCreateOpen(false);
      toast.success('Capability created successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to create capability');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: CapabilityUpdate }) => capabilityService.updateCapability(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['capabilities'] });
      setEditingCapability(null);
      toast.success('Capability updated successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to update capability');
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (id: string) => capabilityService.deleteCapability(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['capabilities'] });
      setArchivingCapability(null);
      toast.success('Capability archived successfully');
    },
    onError: (error: any) => {
      toast.error(error?.response?.data?.detail?.message || 'Failed to archive capability');
    },
  });

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Capabilities</h1>
          <p className="text-muted-foreground">
            Manage granular permissions and features for your products.
          </p>
        </div>
        
        <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
          <DialogTrigger asChild><Button>
            <Plus className="w-4 h-4 mr-2" />
            Add Capability
          </Button></DialogTrigger>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Create New Capability</DialogTitle>
              <DialogDescription>
                Define a new capability that can be bundled into plans.
              </DialogDescription>
            </DialogHeader>
            <CapabilityForm 
              onSubmit={(data) => createMutation.mutate(data as CapabilityCreate)} 
              isSubmitting={createMutation.isPending}
            />
          </DialogContent>
        </Dialog>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>Capability</TableHead>
              <TableHead>Slug</TableHead>
              <TableHead>Status</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-4 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[150px]" /></TableCell>
                  <TableCell><Skeleton className="h-6 w-[80px] rounded-full" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={4} className="h-24 text-center text-destructive">
                  Failed to load capabilities. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && capabilities?.length === 0 && (
              <TableRow>
                <TableCell colSpan={4} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <Zap className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No capabilities found</p>
                    <p className="text-sm">Get started by defining your first capability.</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && capabilities?.map((capability) => (
              <TableRow key={capability.id}>
                <TableCell className="font-medium">
                  {capability.name}
                  {capability.description && (
                    <p className="text-xs text-muted-foreground mt-1 truncate max-w-xs">{capability.description}</p>
                  )}
                </TableCell>
                <TableCell>
                  <code className="text-xs bg-muted px-1.5 py-0.5 rounded text-muted-foreground">{capability.slug}</code>
                </TableCell>
                <TableCell>
                  {capability.is_active ? (
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 hover:bg-green-500/20">
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="outline" className="bg-gray-500/10 text-gray-500 hover:bg-gray-500/20">
                      Inactive
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
                      <DropdownMenuItem onClick={() => setEditingCapability(capability)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        onClick={() => setArchivingCapability(capability)}
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
      <Dialog open={!!editingCapability} onOpenChange={(open) => !open && setEditingCapability(null)}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Edit Capability</DialogTitle>
            <DialogDescription>
              Make changes to {editingCapability?.name}.
            </DialogDescription>
          </DialogHeader>
          {editingCapability && (
            <CapabilityForm 
              initialData={editingCapability}
              onSubmit={(data) => updateMutation.mutate({ id: editingCapability.id, data })}
              isSubmitting={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>

      {/* Archive Confirmation Dialog */}
      <Dialog open={!!archivingCapability} onOpenChange={(open) => !open && setArchivingCapability(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Archive Capability</DialogTitle>
            <DialogDescription>
              Are you sure you want to archive 
              <span className="font-bold text-foreground"> {archivingCapability?.name}</span>? 
              This will disable it across all assigned plans.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end space-x-2 pt-4">
            <Button variant="outline" onClick={() => setArchivingCapability(null)}>
              Cancel
            </Button>
            <Button 
              variant="destructive" 
              onClick={() => archivingCapability && deleteMutation.mutate(archivingCapability.id)}
              disabled={deleteMutation.isPending}
            >
              {deleteMutation.isPending ? 'Archiving...' : 'Archive Capability'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
