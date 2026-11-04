import { CalendarClock, Trash2, Check, Pencil } from 'lucide-react';
const typeClass = t => (t || 'Other').toLowerCase().replace(' ','-');
export default function ActivityCard({activity,onComplete,onEdit,onDelete}) {
  const date = new Date(activity.due_date);
  const due = Number.isNaN(date.getTime()) ? activity.due_date : date.toLocaleString([], {month:'short',day:'numeric',hour:'2-digit',minute:'2-digit'});
  return <article className="activity-card">
    <div className={`type-dot ${typeClass(activity.activity_type)}`}></div>
    <div className="activity-main"><div className="activity-heading"><h4>{activity.title}</h4><span className={`type-tag ${typeClass(activity.activity_type)}`}>{activity.activity_type}</span></div>
      <p>{activity.subject || 'General'} · Due {due}</p>
      <div className="activity-meta"><span className={`priority ${activity.priority?.toLowerCase()}`}>{activity.priority} priority</span><span className={`status ${activity.status?.toLowerCase().replace(' ','-')}`}>{activity.status}</span></div>
    </div>
    <div className="activity-actions">
      {activity.status !== 'Completed' && <button title="Mark completed" onClick={()=>onComplete(activity)}><Check size={16}/></button>}
      <button title="Edit" onClick={()=>onEdit(activity)}><Pencil size={16}/></button>
      <button title="Delete" onClick={()=>onDelete(activity)}><Trash2 size={16}/></button>
    </div>
  </article>;
}
