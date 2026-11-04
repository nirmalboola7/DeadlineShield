import { useEffect, useState } from 'react';
import { Bell, AlertTriangle, Clock } from 'lucide-react';
import { api } from '../services/api';

export default function NotificationPanel() {
  const [data, setData] = useState({ count: 0, notifications: [] });
  const [error, setError] = useState('');

  async function loadNotifications() {
    try {
      const result = await api('/notifications');
      setData(result);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    loadNotifications();
    const timer = setInterval(loadNotifications, 60000);
    return () => clearInterval(timer);
  }, []);

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">STAY UPDATED</span>
          <h3><Bell size={17} /> Notifications</h3>
        </div>
        <span className="count-pill">{data.count} alerts</span>
      </div>

      {error && <p className="error-message">{error}</p>}

      {!error && data.notifications.length === 0 && (
        <p className="muted">No upcoming or overdue deadlines right now.</p>
      )}

      <div className="notification-list">
        {data.notifications.map((item, index) => (
          <div className="notification-item" key={`${item.activity_id}-${index}`}>
            {item.type === 'overdue'
              ? <AlertTriangle size={19} />
              : <Clock size={19} />}
            <div>
              <strong>{item.title}</strong>
              <p>{item.message}</p>
            </div>
          </div>
        ))}
      </div>
    </section>
  );
}
