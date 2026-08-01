'use client';

import { useParams, useRouter } from 'next/navigation';
import { useState } from 'react';
import { useActivationRequest } from '@/features/activation-requests/hooks/useActivationRequest';
import { useReviewRequest } from '@/features/activation-requests/hooks/useReviewRequest';
import { LicenseGenerationWizard } from '@/features/activation-requests/components/LicenseGenerationWizard';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { formatDistanceToNow, format } from 'date-fns';
import { Laptop, Activity, Key, FileText, CheckCircle, XCircle } from 'lucide-react';
import { api } from '@/lib/api';

export default function RequestDetailsPage() {
  const params = useParams();
  const router = useRouter();
  const id = params.id as string;
  const [showWizard, setShowWizard] = useState(false);

  const { data: request, isLoading, isError } = useActivationRequest(id);
  const reviewMutation = useReviewRequest(id);

  if (isLoading) return <div className="p-8">Loading request details...</div>;
  if (isError || !request) return <div className="p-8 text-red-500">Failed to load request details</div>;

  const handleReview = () => {
    reviewMutation.mutate();
  };

  const handleDownload = async () => {
    try {
      const response = await api.get(`/activation-requests/${id}/download`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(response.data);
      const a = document.createElement('a');
      a.href = url;
      
      let filename = `${request.request_number.replace('REQ', 'LIC')}.wfalic`;
      if (request.original_filename) {
        filename = request.original_filename.replace('.wfareq', '.wfalic').replace('-Request-', '-License-');
      }
      a.download = filename;
      
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    } catch (err: any) {
      console.error(err);
      alert(err.message || 'Failed to download license');
    }
  };

  return (
    <div className="space-y-6">
      {showWizard && <LicenseGenerationWizard requestId={id} onClose={() => setShowWizard(false)} />}
      <div className="flex justify-between items-start">
        <div>
          <div className="flex items-center space-x-3 mb-2">
            <h1 className="text-3xl font-bold tracking-tight">Request {request.request_number}</h1>
            <Badge variant={
                  request.status === 'APPROVED' ? 'default' :
                  request.status === 'REJECTED' ? 'destructive' :
                  request.status === 'PENDING' ? 'secondary' :
                  request.status === 'UNDER_REVIEW' ? 'outline' :
                  'outline'
            }>
              {request.status}
            </Badge>
          </div>
          <p className="text-muted-foreground">Type: {request.request_type}</p>
        </div>
        
        <div className="space-x-3">
          {request.status === 'PENDING' && (
            <Button onClick={handleReview} disabled={reviewMutation.isPending}>
              Start Review
            </Button>
          )}
          {request.status === 'UNDER_REVIEW' && (
            <>
              <Button variant="destructive">Reject</Button>
              <Button onClick={() => setShowWizard(true)}>Generate License</Button>
            </>
          )}
          {request.status === 'LICENSE_GENERATED' && (
             <Button onClick={handleDownload}>Download License</Button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Laptop className="w-5 h-5 mr-2 text-primary" />
              Machine Snapshot
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <div className="text-sm font-medium text-muted-foreground">Hostname</div>
                <div>{request.hostname || '-'}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Username</div>
                <div>{request.username || '-'}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">OS</div>
                <div>{request.os} {request.os_version}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">Architecture</div>
                <div>{request.architecture || '-'}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">CPU</div>
                <div>{request.cpu || '-'}</div>
              </div>
              <div>
                <div className="text-sm font-medium text-muted-foreground">RAM</div>
                <div>{request.ram || '-'}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm font-medium text-muted-foreground">Fingerprint</div>
                <div className="font-mono text-sm break-all">{request.fingerprint}</div>
              </div>
              <div className="col-span-2">
                <div className="text-sm font-medium text-muted-foreground mb-2">Hardware Tokens</div>
                {request.hardware_tokens && request.hardware_tokens.length > 0 ? (
                  <div className="bg-muted p-2 rounded text-xs font-mono break-all max-h-32 overflow-y-auto whitespace-pre-wrap">
                    {JSON.stringify(request.hardware_tokens, null, 2)}
                  </div>
                ) : (
                  <div className="text-sm">-</div>
                )}
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-lg flex items-center">
              <Activity className="w-5 h-5 mr-2 text-primary" />
              Timeline
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {request.events.map((event, i) => (
                <div key={event.id} className="relative pl-6 pb-6 last:pb-0">
                  {i !== request.events.length - 1 && (
                    <div className="absolute left-[11px] top-6 bottom-0 w-px bg-border" />
                  )}
                  <div className="absolute left-0 top-1 w-6 h-6 rounded-full border-2 border-background bg-primary/20 flex items-center justify-center">
                    <div className="w-2 h-2 rounded-full bg-primary" />
                  </div>
                  <div>
                    <div className="flex justify-between items-baseline mb-1">
                      <span className="font-medium">{event.status_to.replace('_', ' ')}</span>
                      <span className="text-xs text-muted-foreground">
                        {format(new Date(event.timestamp), 'PP p')}
                      </span>
                    </div>
                    {event.notes && (
                      <p className="text-sm text-muted-foreground">{event.notes}</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
