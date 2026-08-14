'use client';

import React, { useState } from 'react';
import { useTrialTokens, useGenerateTrialToken, useRevokeTrialToken, useManifest } from '@/features/trial-tokens/hooks/useTrialTokens';
import { format } from 'date-fns';
import { CheckCircle, AlertTriangle, Download, Plus, Trash2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { toast } from 'sonner';
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
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export default function CommunityTrialsPage() {
  const { data: tokens, isLoading } = useTrialTokens();
  const generateMutation = useGenerateTrialToken();
  const revokeMutation = useRevokeTrialToken();
  const { data: manifest } = useManifest();

  const [isGenerateOpen, setIsGenerateOpen] = useState(false);
  
  const currentMonth = new Date().getMonth() + 1;
  const currentYear = new Date().getFullYear();
  
  const [selectedMonth, setSelectedMonth] = useState<string>(currentMonth.toString());
  const [selectedYear, setSelectedYear] = useState<string>(currentYear.toString());

  const handleGenerate = () => {
    generateMutation.mutate(
      { month: parseInt(selectedMonth), year: parseInt(selectedYear) },
      {
        onSuccess: () => {
          toast.success('Trial token generated and pushed to GitHub successfully');
          setIsGenerateOpen(false);
        },
        onError: (error: any) => {
          toast.error(error?.response?.data?.detail || 'Failed to generate token');
        }
      }
    );
  };

  const handleRevoke = (id: string) => {
    if (confirm('Are you sure you want to revoke this token? This will immediately invalidate trials using it.')) {
      revokeMutation.mutate(id, {
        onSuccess: () => toast.success('Token revoked successfully and GitHub manifest updated'),
        onError: (error: any) => toast.error(error?.response?.data?.detail || 'Failed to revoke token')
      });
    }
  };

  const downloadManifest = () => {
    if (!manifest) return;
    const blob = new Blob([JSON.stringify(manifest, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'community-trial.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold tracking-tight">Community Trials</h2>
          <p className="text-muted-foreground mt-1">
            Manage WFA Community Trial tokens and GitHub manifest sync.
          </p>
        </div>
        <div className="flex space-x-3">
          <Button variant="outline" onClick={downloadManifest} disabled={!manifest}>
            <Download className="w-4 h-4 mr-2" />
            Download Manifest
          </Button>

          <Dialog open={isGenerateOpen} onOpenChange={setIsGenerateOpen}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="w-4 h-4 mr-2" />
                Generate Token
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Generate New Trial Token</DialogTitle>
                <DialogDescription>
                  This will generate a new token and automatically push the updated manifest to GitHub. 
                  Any currently active tokens will be revoked.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 pt-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Month</label>
                    <Select value={selectedMonth} onValueChange={(val) => { if(val) setSelectedMonth(val); }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select month" />
                      </SelectTrigger>
                      <SelectContent>
                        {Array.from({ length: 12 }, (_, i) => i + 1).map(m => (
                          <SelectItem key={m} value={m.toString()}>
                            {new Date(0, m - 1).toLocaleString('default', { month: 'long' })}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Year</label>
                    <Select value={selectedYear} onValueChange={(val) => { if(val) setSelectedYear(val); }}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select year" />
                      </SelectTrigger>
                      <SelectContent>
                        {[0, 1, 2].map(offset => (
                          <SelectItem key={offset} value={(currentYear + offset).toString()}>
                            {currentYear + offset}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <Button 
                  className="w-full" 
                  onClick={handleGenerate}
                  disabled={generateMutation.isPending}
                >
                  {generateMutation.isPending ? 'Generating & Syncing...' : 'Generate & Sync GitHub'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      <div className="bg-card rounded-lg border border-border/50 overflow-hidden">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Token String</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Expires At</TableHead>
              <TableHead>Created At</TableHead>
              <TableHead className="text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {isLoading ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  Loading trial tokens...
                </TableCell>
              </TableRow>
            ) : tokens?.length === 0 ? (
              <TableRow>
                <TableCell colSpan={5} className="text-center py-8 text-muted-foreground">
                  No trial tokens found.
                </TableCell>
              </TableRow>
            ) : (
              tokens?.map((token) => (
                <TableRow key={token.id}>
                  <TableCell className="font-mono">{token.token_string}</TableCell>
                  <TableCell>
                    {token.is_active ? (
                      <Badge variant="default" className="bg-green-500/10 text-green-500 hover:bg-green-500/20">
                        Active
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-muted-foreground">
                        Revoked / Expired
                      </Badge>
                    )}
                  </TableCell>
                  <TableCell>{format(new Date(token.expires_at), 'MMM d, yyyy HH:mm')}</TableCell>
                  <TableCell>{format(new Date(token.created_at), 'MMM d, yyyy HH:mm')}</TableCell>
                  <TableCell className="text-right">
                    {token.is_active && (
                      <Button 
                        variant="destructive" 
                        size="sm" 
                        onClick={() => handleRevoke(token.id)}
                        disabled={revokeMutation.isPending}
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Revoke
                      </Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
