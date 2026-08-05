'use client';

import { useDashboardStats } from '@/features/dashboard/hooks/useDashboardStats';
import { useAuth } from '@/features/auth/authContext';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Users, Package, Key, Building, Monitor, Clock, CheckCircle2, Activity, HardDrive, Database, Server } from "lucide-react";

export default function DashboardPage() {
  const { user } = useAuth();
  const { data: stats, isLoading, isError } = useDashboardStats();

  const role = user?.role || 'VIEWER';

  if (isLoading) {
    return <div className="p-8 text-muted-foreground flex items-center justify-center">Loading dashboard...</div>;
  }

  if (isError || !stats) {
    return <div className="p-8 text-destructive flex items-center justify-center">Failed to load dashboard statistics.</div>;
  }

  // Stat cards definitions
  const statCards = [
    { title: "Organizations", value: stats.overview.organizations, icon: Building, roles: ['OWNER', 'ADMIN'] },
    { title: "Products", value: stats.overview.products, icon: Package, roles: ['OWNER', 'ADMIN'] },
    { title: "Registered Devices", value: stats.overview.devices, icon: Monitor, roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { title: "Online Devices", value: stats.overview.online_devices, icon: Activity, roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { title: "Pending Requests", value: stats.overview.pending_requests, icon: Clock, roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { title: "Active Licenses", value: stats.overview.active_licenses, icon: ShieldCheck, roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { title: "Expired Licenses", value: stats.overview.expired_licenses, icon: Key, roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
  ];

  const visibleCards = statCards.filter(card => card.roles.includes(role));

  const healthItems = [
    { name: "Backend", status: stats.system_health.backend, icon: Server },
    { name: "Database", status: stats.system_health.database, icon: Database },
    { name: "Storage", status: stats.system_health.storage, icon: HardDrive },
    { name: "Licensing Service", status: stats.system_health.licensing_service, icon: Key },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Operational Overview</h2>
        <p className="text-muted-foreground">
          Real-time metrics and platform health.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {visibleCards.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 mt-4">
        <div className="col-span-4 space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>System Health</CardTitle>
              <CardDescription>Status of core platform services</CardDescription>
            </CardHeader>
            <CardContent className="grid grid-cols-2 gap-4">
              {healthItems.map((item) => (
                <div key={item.name} className="flex items-center space-x-3 p-3 rounded-lg bg-secondary/50 border border-border/50">
                  <CheckCircle2 className="w-5 h-5 text-green-500" />
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{item.name}</span>
                    <span className="text-xs text-muted-foreground capitalize">{item.status}</span>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
          
          <Card>
            <CardHeader>
              <CardTitle>Overview</CardTitle>
            </CardHeader>
            <CardContent className="pl-2 flex justify-center items-center h-[200px] text-muted-foreground border-2 border-dashed border-border/50 rounded-lg m-4 mt-0">
              Chart Placeholder
            </CardContent>
          </Card>
        </div>
        
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest domain events in the system.
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4 overflow-y-auto max-h-[500px] pr-2">
              {stats.recent_activity.length === 0 ? (
                <div className="text-center text-sm text-muted-foreground pt-4">No recent activity found.</div>
              ) : (
                stats.recent_activity.map((event) => (
                  <div key={event.id} className="flex flex-col space-y-1 border-b border-border/50 pb-3 last:border-0">
                    <p className="text-sm font-medium">{event.message}</p>
                    <time className="text-xs text-muted-foreground">
                      {new Date(event.timestamp).toLocaleString()}
                    </time>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
