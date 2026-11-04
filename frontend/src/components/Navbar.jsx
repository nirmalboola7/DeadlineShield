import { Bell, Search } from 'lucide-react';
export default function Navbar({ title, user }) {
  return <header className="topbar"><div><div className="eyebrow">STUDENT WORKSPACE / {title.toUpperCase()}</div><h2>{title}</h2></div><div className="top-actions"><div className="search-pill"><Search size={16}/><span>Stay on top of your goals</span></div><button className="icon-button" title="Notifications"><Bell size={18}/></button><div className="avatar">{(user?.name || 'S')[0].toUpperCase()}</div></div></header>;
}
