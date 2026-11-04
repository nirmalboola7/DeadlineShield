import { ClipboardList, GraduationCap, Clock3, CheckCircle2 } from 'lucide-react';
const icons = {Tasks:ClipboardList, Exams:GraduationCap, 'Due soon':Clock3, Completed:CheckCircle2};
export default function StatsCard({label,value,sub}) {
  const Icon = icons[label] || ClipboardList;
  return <div className="stat-card"><div className="stat-top"><span>{label}</span><div className="stat-icon"><Icon size={19}/></div></div><strong>{value}</strong><small>{sub}</small></div>;
}
