'use client';

import { useAuth } from '@/features/auth/authContext';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import { LogOut, LayoutDashboard, Key, Users, Building, Package, ShieldCheck, Zap, Layers, CreditCard, Monitor } from 'lucide-react';

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading, user, logoutState } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  if (isLoading || !isAuthenticated) {
    return <div className="min-h-screen flex items-center justify-center bg-background">Loading...</div>;
  }

  const handleLogout = () => {
    logoutState();
    router.push('/login');
  };

  const role = user?.role || 'VIEWER';

  const allNavItems = [
    { name: 'Dashboard', icon: LayoutDashboard, href: '/', roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { name: 'Requests', icon: Key, href: '/activation-requests', roles: ['OWNER', 'ADMIN', 'SUPPORT'] },
    { name: 'Devices', icon: Monitor, href: '/devices', roles: ['OWNER'] },
    { name: 'Organizations', icon: Building, href: '/organizations', roles: ['OWNER', 'ADMIN'] },
    { name: 'Products', icon: Package, href: '/products', roles: ['OWNER', 'ADMIN'] },
    { name: 'Plans', icon: Layers, href: '/plans', roles: ['OWNER', 'ADMIN', 'VIEWER'] },
    { name: 'Releases', icon: Package, href: '/releases', roles: ['OWNER', 'ADMIN', 'SUPPORT', 'VIEWER'] },
    { name: 'Users', icon: Users, href: '/users', roles: ['OWNER'] },
  ];

  const navItems = allNavItems.filter((item) => item.roles.includes(role));

  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar */}
      <aside className="w-64 border-r border-border/50 bg-card flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-border/50">
          <ShieldCheck className="w-6 h-6 text-primary mr-2" />
          <span className="font-bold text-lg tracking-tight">Xecurity</span>
        </div>
        <div className="flex-1 overflow-y-auto py-4">
          <nav className="space-y-1 px-3">
            {navItems.map((item) => (
              <a
                key={item.name}
                href={item.href}
                className="flex items-center px-3 py-2 text-sm font-medium rounded-md text-muted-foreground hover:bg-secondary hover:text-foreground transition-colors"
              >
                <item.icon className="mr-3 h-5 w-5 opacity-75" />
                {item.name}
              </a>
            ))}
          </nav>
        </div>
        <div className="p-4 border-t border-border/50">
          <div className="flex items-center mb-4">
            <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold mr-3">
              {user?.email?.[0].toUpperCase() || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium truncate">{user?.email}</p>
              <p className="text-xs text-muted-foreground truncate">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center w-full px-3 py-2 text-sm font-medium text-destructive hover:bg-destructive/10 rounded-md transition-colors"
          >
            <LogOut className="mr-3 h-4 w-4" />
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-16 border-b border-border/50 bg-card/50 backdrop-blur-sm flex items-center px-8 justify-between">
          <h1 className="text-lg font-medium">Platform Admin</h1>
          {/* Add user menu or actions here */}
        </header>
        <div className="flex-1 overflow-y-auto p-8">
          <div className="max-w-6xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}
