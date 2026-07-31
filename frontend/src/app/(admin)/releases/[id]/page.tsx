'use client';

import React, { use } from 'react';
import { ArrowLeft, Package, CheckCircle, Clock, Save, FileText, Download, Shield } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

import { ReleaseStatus } from '@/features/releases/types';
import { useRelease } from '@/features/releases/hooks/useRelease';
import { useProducts } from '@/features/products/hooks/useProducts';

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
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export default function ReleaseDetailsPage({ params }: { params: Promise<{ id: string }> }) {
  const router = useRouter();
  const { id } = use(params);

  const { data: release, isLoading, isError } = useRelease(id);
  const { data: products } = useProducts();

  const getStatusBadge = (status: ReleaseStatus) => {
    switch (status) {
      case ReleaseStatus.PUBLISHED: return <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">Published</Badge>;
      case ReleaseStatus.RELEASE_CANDIDATE: return <Badge variant="outline" className="bg-blue-500/10 text-blue-500 border-blue-500/20">RC</Badge>;
      case ReleaseStatus.TESTING: return <Badge variant="outline" className="bg-yellow-500/10 text-yellow-500 border-yellow-500/20">Testing</Badge>;
      case ReleaseStatus.DRAFT: return <Badge variant="outline" className="bg-slate-500/10 text-slate-500 border-slate-500/20">Draft</Badge>;
      case ReleaseStatus.DEPRECATED: return <Badge variant="outline" className="bg-orange-500/10 text-orange-500 border-orange-500/20">Deprecated</Badge>;
      case ReleaseStatus.ARCHIVED: return <Badge variant="outline" className="bg-red-500/10 text-red-500 border-red-500/20">Archived</Badge>;
      default: return <Badge variant="outline">{status}</Badge>;
    }
  };

  const getProductName = (productId?: string) => {
    if (!productId) return 'Unknown Product';
    return products?.find(p => p.id === productId)?.name || 'Unknown Product';
  };

  if (isLoading) {
    return <div className="p-8 space-y-4"><Skeleton className="h-8 w-64" /><Skeleton className="h-32 w-full" /></div>;
  }

  if (isError || !release) {
    return (
      <div className="p-8 text-center text-destructive">
        Failed to load release. It may have been deleted.
        <Button variant="link" onClick={() => router.push('/releases')}>Go Back</Button>
      </div>
    );
  }

  const isPublished = release.status === ReleaseStatus.PUBLISHED || release.status === ReleaseStatus.ARCHIVED;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Button variant="ghost" size="icon" onClick={() => router.push('/releases')}>
            <ArrowLeft className="w-5 h-5" />
          </Button>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold tracking-tight">v{release.version}</h1>
              {getStatusBadge(release.status)}
              {release.is_latest && (
                <Badge variant="outline" className="bg-green-500/10 text-green-500 border-green-500/20">
                  <CheckCircle className="w-3 h-3 mr-1" /> Latest
                </Badge>
              )}
            </div>
            <p className="text-muted-foreground">
              {getProductName(release.product_id)} • Build {release.build_number} • {release.channel}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2">
          {!isPublished && (
            <Button onClick={() => toast.info('Publishing coming soon')}>
              Publish Release
            </Button>
          )}
        </div>
      </div>

      <Tabs defaultValue="overview" className="space-y-6">
        <TabsList>
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="artifacts">Artifacts ({release.artifacts?.length || 0})</TabsTrigger>
          <TabsTrigger value="settings">Settings</TabsTrigger>
        </TabsList>

        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="md:col-span-2 space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Release Notes</CardTitle>
                </CardHeader>
                <CardContent>
                  {release.release_notes ? (
                    <div className="prose prose-sm dark:prose-invert">
                      {release.release_notes}
                    </div>
                  ) : (
                    <p className="text-sm text-muted-foreground italic">No release notes provided.</p>
                  )}
                </CardContent>
              </Card>
            </div>

            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle>Details</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Mandatory Update</span>
                    <span className="font-medium">{release.mandatory ? 'Yes' : 'No'}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Min License Build</span>
                    <span className="font-medium">{release.minimum_license_build || 'None'}</span>
                  </div>
                  <div className="flex justify-between items-center text-sm">
                    <span className="text-muted-foreground">Min LMS Build</span>
                    <span className="font-medium">{release.minimum_lms_build || 'None'}</span>
                  </div>
                  <div className="pt-4 border-t border-border/50">
                    <div className="flex items-center text-xs text-muted-foreground">
                      <Clock className="w-3 h-3 mr-2" />
                      Created {new Date(release.created_at).toLocaleDateString()}
                    </div>
                    {release.published_at && (
                      <div className="flex items-center text-xs text-muted-foreground mt-2">
                        <CheckCircle className="w-3 h-3 mr-2 text-green-500" />
                        Published {new Date(release.published_at).toLocaleDateString()}
                      </div>
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        <TabsContent value="artifacts">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle>Release Artifacts</CardTitle>
                <CardDescription>Files associated with this release build.</CardDescription>
              </div>
              {!isPublished && (
                <Button variant="outline" size="sm" onClick={() => toast.info('Artifact upload coming soon')}>
                  <Package className="w-4 h-4 mr-2" /> Upload Artifact
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {release.artifacts && release.artifacts.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Filename</TableHead>
                      <TableHead>Platform/Arch</TableHead>
                      <TableHead>Type</TableHead>
                      <TableHead>Size</TableHead>
                      <TableHead>SHA256</TableHead>
                      <TableHead className="text-right">Actions</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {release.artifacts.map((artifact) => (
                      <TableRow key={artifact.id}>
                        <TableCell className="font-medium">{artifact.filename}</TableCell>
                        <TableCell>
                          <Badge variant="secondary" className="text-xs">
                            {artifact.platform} / {artifact.architecture}
                          </Badge>
                        </TableCell>
                        <TableCell>{artifact.artifact_type}</TableCell>
                        <TableCell>{(artifact.filesize / 1024 / 1024).toFixed(2)} MB</TableCell>
                        <TableCell className="font-mono text-xs max-w-[150px] truncate" title={artifact.sha256}>
                          {artifact.sha256.substring(0, 16)}...
                        </TableCell>
                        <TableCell className="text-right">
                          <Button variant="ghost" size="sm">
                            <Download className="w-4 h-4" />
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <div className="flex flex-col items-center justify-center py-12 text-center text-muted-foreground">
                  <Package className="w-12 h-12 mb-4 opacity-20" />
                  <p className="text-lg font-medium text-foreground">No artifacts uploaded</p>
                  <p className="text-sm">Upload binaries or installers for this release.</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
        
        <TabsContent value="settings">
          <Card>
            <CardHeader>
              <CardTitle>Release Settings</CardTitle>
              <CardDescription>
                {isPublished 
                  ? "This release is published and its core attributes are immutable. You can only archive or deprecate it."
                  : "Modify properties of this draft release."}
              </CardDescription>
            </CardHeader>
            <CardContent>
               <p className="text-muted-foreground text-sm">Settings form placeholder</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
