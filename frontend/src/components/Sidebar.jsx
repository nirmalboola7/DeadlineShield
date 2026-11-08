import { NavLink, useNavigate } from 'react-router-dom';
import { LayoutDashboard, CalendarDays, ChartNoAxesColumn, UserRound, ShieldCheck, LogOut, BookOpen } from 'lucide-react';

const links = [
  { to: '/', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/calendar', label: 'Calendar', icon: CalendarDays },
  { to: '/analytics', label: 'Analytics', icon: ChartNoAxesColumn },
  { to: '/profile', label: 'Profile', icon: UserRound },
];

export default function Sidebar({ user, onLogout }) {
  return <aside className="sidebar">
    <div className="brand"><div className="brand-icon"><ShieldCheck size={22}/></div><div><b>LEARNOVA</b><small>STUDENT WORKSPACE</small></div></div>
    <div className="side-label">WORKSPACE</div>
    <nav>{links.map(({to,label,icon:Icon}) => <NavLink key={to} to={to} end={to === '/'} className={({isActive}) => isActive ? 'nav-link active' : 'nav-link'}><Icon size={18}/>{label}</NavLink>)}</nav>
    <div className="sidebar-bottom">
      <div className="mini-user"><div className="avatar">{(user?.name || 'S')[0].toUpperCase()}</div><div><b>{user?.name || 'Student'}</b><small>{user?.email || ''}</small></div></div>
      <button className="logout-link" onClick={onLogout}><LogOut size={17}/> Sign out</button>
    </div>
  </aside>;
}

