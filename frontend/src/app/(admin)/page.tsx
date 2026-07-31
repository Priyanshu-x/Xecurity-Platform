import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { ShieldCheck, Users, Package, Key, Building } from "lucide-react";

export default function DashboardPage() {
  const stats = [
    { title: "Active Organizations", value: "12", icon: Building },
    { title: "Total Users", value: "48", icon: Users },
    { title: "Products", value: "3", icon: Package },
    { title: "Active Licenses", value: "1,204", icon: Key },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold tracking-tight">Dashboard</h2>
        <p className="text-muted-foreground">
          Welcome to the Xecurity Platform Admin Portal. Here's what's happening today.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        {stats.map((stat) => (
          <Card key={stat.title}>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">
                {stat.title}
              </CardTitle>
              <stat.icon className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{stat.value}</div>
              <p className="text-xs text-muted-foreground mt-1">
                +12% from last month
              </p>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-7 mt-4">
        <Card className="col-span-4">
          <CardHeader>
            <CardTitle>Overview</CardTitle>
          </CardHeader>
          <CardContent className="pl-2 flex justify-center items-center h-[300px] text-muted-foreground border-2 border-dashed border-border/50 rounded-lg m-4 mt-0">
            Chart Placeholder
          </CardContent>
        </Card>
        <Card className="col-span-3">
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest domain events in the system.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex justify-center items-center h-[300px] text-muted-foreground border-2 border-dashed border-border/50 rounded-lg m-4 mt-0">
            Activity Feed Placeholder
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
