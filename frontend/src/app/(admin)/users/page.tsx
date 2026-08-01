'use client';

import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/features/auth/authContext';
import { Plus, MoreHorizontal, ShieldOff, Pencil, Shield, User as UserIcon } from 'lucide-react';
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
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
import { toast } from 'sonner';

import { userService } from '@/features/users/userService';
import { User, UserCreate, UserUpdate, UserRole } from '@/features/users/types';
import { UserForm } from '@/features/users/components/UserForm';
function formatTimeAgo(dateString: string) {
  const date = new Date(dateString);
  const now = new Date();
  const diffInSeconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  
  if (diffInSeconds < 60) return 'just now';
  if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)}m ago`;
  if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)}h ago`;
  return `${Math.floor(diffInSeconds / 86400)}d ago`;
}

export default function UsersPage() {
  const { user } = useAuth();
  const router = useRouter();
  const queryClient = useQueryClient();

  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  // RBAC: Only OWNER can access this page
  useEffect(() => {
    if (user && user.role !== 'OWNER') {
      router.push('/');
    }
  }, [user, router]);

  const { data: users, isLoading, isError } = useQuery({
    queryKey: ['users'],
    queryFn: () => userService.getUsers(),
    enabled: user?.role === 'OWNER',
  });

  const createMutation = useMutation({
    mutationFn: (data: UserCreate) => userService.createUser(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setIsCreateOpen(false);
      toast.success('User created successfully.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to create user');
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UserUpdate }) => userService.updateUser(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      setEditingUser(null);
      toast.success('User updated successfully.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to update user');
    },
  });

  const disableMutation = useMutation({
    mutationFn: (id: string) => userService.disableUser(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
      toast.success('User disabled.');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.detail || 'Failed to disable user');
    },
  });

  const getRoleBadge = (role: UserRole) => {
    switch (role) {
      case UserRole.OWNER: return <Badge variant="default" className="bg-primary/20 text-primary hover:bg-primary/30 border-primary/30">Owner</Badge>;
      case UserRole.ADMIN: return <Badge variant="secondary" className="bg-blue-500/10 text-blue-500 hover:bg-blue-500/20 border-blue-500/30">Admin</Badge>;
      case UserRole.SUPPORT: return <Badge variant="secondary" className="bg-yellow-500/10 text-yellow-500 hover:bg-yellow-500/20 border-yellow-500/30">Support</Badge>;
      case UserRole.VIEWER: return <Badge variant="outline" className="text-muted-foreground">Viewer</Badge>;
      default: return <Badge variant="outline">{role}</Badge>;
    }
  };

  // If not owner, return empty layout while redirecting
  if (user?.role !== 'OWNER') {
    return <div className="min-h-screen bg-background" />;
  }

  return (
    <div className="flex-1 space-y-8 p-8 pt-6">
      <div className="flex items-center justify-between space-y-2">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Users</h1>
          <p className="text-muted-foreground">
            Manage platform users, roles, and access controls.
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Button onClick={() => setIsCreateOpen(true)}>
            <Plus className="w-4 h-4 mr-2" /> Add User
          </Button>
        </div>
      </div>

      <div className="border border-border/50 rounded-lg bg-card/50 backdrop-blur-sm overflow-hidden">
        <Table>
          <TableHeader className="bg-muted/50">
            <TableRow>
              <TableHead>User</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Last Login</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading && (
              Array.from({ length: 3 }).map((_, i) => (
                <TableRow key={i}>
                  <TableCell><Skeleton className="h-5 w-[200px]" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-[80px]" /></TableCell>
                  <TableCell><Skeleton className="h-5 w-[80px]" /></TableCell>
                  <TableCell><Skeleton className="h-4 w-[100px]" /></TableCell>
                  <TableCell className="text-right"><Skeleton className="h-8 w-8 ml-auto rounded-md" /></TableCell>
                </TableRow>
              ))
            )}
            
            {isError && (
              <TableRow>
                <TableCell colSpan={5} className="h-24 text-center text-destructive">
                  Failed to load users. Please try again.
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && users?.length === 0 && (
              <TableRow>
                <TableCell colSpan={5} className="h-48 text-center">
                  <div className="flex flex-col items-center justify-center text-muted-foreground">
                    <UserIcon className="w-12 h-12 mb-4 opacity-20" />
                    <p className="text-lg font-medium text-foreground">No users found</p>
                  </div>
                </TableCell>
              </TableRow>
            )}

            {!isLoading && !isError && users?.map((u) => (
              <TableRow key={u.id} className={!u.is_active ? "opacity-50" : ""}>
                <TableCell>
                  <div className="font-medium flex items-center">
                    {u.email}
                    {u.id === user?.id && (
                      <Badge variant="outline" className="ml-2 text-xs py-0 h-5">You</Badge>
                    )}
                  </div>
                  <div className="text-xs text-muted-foreground mt-1">
                    Joined {formatTimeAgo(u.created_at)}
                  </div>
                </TableCell>
                <TableCell>
                  {getRoleBadge(u.role)}
                </TableCell>
                <TableCell>
                  {u.is_active ? (
                    <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Active</Badge>
                  ) : (
                    <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Disabled</Badge>
                  )}
                </TableCell>
                <TableCell>
                  <div className="text-sm">
                    {u.last_login_at ? formatTimeAgo(u.last_login_at) : 'Never'}
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
                      <DropdownMenuItem onClick={() => setEditingUser(u)}>
                        <Pencil className="w-4 h-4 mr-2" /> Edit User
                      </DropdownMenuItem>
                      <DropdownMenuSeparator />
                      <DropdownMenuItem 
                        className="text-destructive focus:bg-destructive focus:text-destructive-foreground"
                        disabled={u.id === user?.id || !u.is_active}
                        onClick={() => {
                          if (confirm(`Are you sure you want to disable ${u.email}?`)) {
                            disableMutation.mutate(u.id);
                          }
                        }}
                      >
                        <ShieldOff className="w-4 h-4 mr-2" /> Disable User
                      </DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </div>

      {/* Create Dialog */}
      <Dialog open={isCreateOpen} onOpenChange={setIsCreateOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Add New User</DialogTitle>
            <DialogDescription>
              Create a new user and assign them a role. They can change their password later.
            </DialogDescription>
          </DialogHeader>
          <UserForm 
            onSubmit={(data) => createMutation.mutate(data as UserCreate)}
            isLoading={createMutation.isPending}
          />
        </DialogContent>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={!!editingUser} onOpenChange={(open) => !open && setEditingUser(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Edit User</DialogTitle>
            <DialogDescription>
              Update user details or change their role.
            </DialogDescription>
          </DialogHeader>
          {editingUser && (
            <UserForm 
              initialData={editingUser}
              onSubmit={(data) => updateMutation.mutate({ id: editingUser.id, data: data as UserUpdate })}
              isLoading={updateMutation.isPending}
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
