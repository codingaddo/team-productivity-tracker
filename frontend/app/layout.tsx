'use client';
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import './globals.css';
import { AuthProvider, useAuth } from '../lib/auth';
function Shell({ children }: { children: React.ReactNode }) {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  if (!loading && !user && pathname !== '/login') router.replace('/login');
  const nav = user ? [{ href: '/time', label: 'My time' }, ...(user.role !== 'member' ? [{ href: '/dashboard', label: 'Dashboard' }] : [])] : [];
  return <div style={{padding:24,fontFamily:'Arial'}}><header style={{display:'flex',justifyContent:'space-between',marginBottom:24}}><nav style={{display:'flex',gap:12}}>{nav.map(i => <Link key={i.href} href={i.href}>{i.label}</Link>)}</nav>{user ? <button onClick={() => { logout(); router.push('/login'); }}>Logout</button> : null}</header>{children}</div>;
}
export default function RootLayout({ children }: { children: React.ReactNode }) { return <html lang="en"><body><AuthProvider><Shell>{children}</Shell></AuthProvider></body></html>; }
