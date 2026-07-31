'use client';

import { useActivationRequests } from '@/features/activation-requests/hooks/useActivationRequests';
import { useUploadRequest } from '@/features/activation-requests/hooks/useUploadRequest';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import Link from 'next/link';
import { formatDistanceToNow } from 'date-fns';
import { Laptop, Cpu, Hash, UploadCloud } from 'lucide-react';
import { useRef } from 'react';

export default function ActivationRequestsPage() {
  const { data: response, isLoading, isError } = useActivationRequests();
  const uploadMutation = useUploadRequest();
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const requests = response?.items || [];

  if (isLoading) return <div className="p-8">Loading requests...</div>;
  if (isError) return <div className="p-8 text-red-500">Failed to load requests</div>;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold tracking-tight">License Requests</h1>
        <div>
          <input 
            type="file" 
            accept=".wfareq,.json" 
            className="hidden" 
            ref={fileInputRef}
            onChange={(e) => {
              if (e.target.files && e.target.files[0]) {
                uploadMutation.mutate(e.target.files[0]);
              }
            }}
          />
          <Button 
            onClick={() => fileInputRef.current?.click()} 
            disabled={uploadMutation.isPending}
            className="flex items-center"
          >
            <UploadCloud className="mr-2 h-4 w-4" />
            {uploadMutation.isPending ? "Uploading..." : "Upload Request"}
          </Button>
        </div>
      </div>

      <div className="grid gap-6">
        {requests.map((request) => (
          <Card key={request.id} className="hover:bg-accent/5 transition-colors">
            <CardHeader className="pb-2">
              <div className="flex justify-between items-start">
                <div className="flex items-center space-x-3">
                  <Laptop className="h-6 w-6 text-primary" />
                  <div>
                    <CardTitle className="text-xl">
                      <Link href={`/activation-requests/${request.id}`} className="hover:underline">
                        {request.hostname || 'Unknown Host'}
                      </Link>
                    </CardTitle>
                    <div className="text-sm text-muted-foreground flex items-center space-x-2 mt-1">
                      <Hash className="h-4 w-4" />
                      <span>{request.request_number}</span>
                    </div>
                  </div>
                </div>
                <Badge variant={
                  request.status === 'APPROVED' ? 'default' :
                  request.status === 'REJECTED' ? 'destructive' :
                  request.status === 'PENDING' ? 'secondary' :
                  'outline'
                }>
                  {request.status}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm mt-4">
                <div>
                  <div className="text-muted-foreground mb-1">Type</div>
                  <div className="font-medium">{request.request_type}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">OS</div>
                  <div className="font-medium">{request.os} {request.os_version}</div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Fingerprint</div>
                  <div className="font-medium truncate" title={request.fingerprint}>
                    {request.fingerprint}
                  </div>
                </div>
                <div>
                  <div className="text-muted-foreground mb-1">Generated</div>
                  <div className="font-medium">
                    {formatDistanceToNow(new Date(request.created_at), { addSuffix: true })}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
        {requests.length === 0 && (
          <div className="text-center py-12 text-muted-foreground">
            No license requests found.
          </div>
        )}
      </div>
    </div>
  );
}
