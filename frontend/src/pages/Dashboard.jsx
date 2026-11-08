
import { useEffect, useState } from 'react';
import { Plus, AlertTriangle, ArrowUpRight } from 'lucide-react';

import StatsCard from '../components/StatsCard';
import ActivityCard from '../components/ActivityCard';
import RevisionPanel from '../components/RevisionPanel';
import SubjectManager from '../components/SubjectManager';
import ExamScheduler from '../components/ExamScheduler';
import NotificationPanel from '../components/NotificationPanel';
import AchievementBadges from '../components/AchievementBadges';
import Leaderboard from '../components/Leaderboard';

import { api } from '../services/api';

const emptyForm = {
  title: '',
  description: '',
  activity_type: 'Assignment',
  subject: '',
  due_date: '',
  priority: 'Medium',
  status: 'Pending'
};

export default function Dashboard() {
  const [data, setData] = useState({
    stats: {},
    activities: [],
    overload: []
  });

  const [gamification, setGamification] = useState({
    leaderboard: [],
    my_performance: null
  });

  const [error, setError] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [form, setForm] = useState(emptyForm);

  async function load() {
    try {
      const dashboardResult = await api('/dashboard');
      setData(dashboardResult);
      setError('');

      try {
        const leaderboardResult = await api('/leaderboard');
        setGamification(leaderboardResult);
      } catch (leaderboardError) {
        setError(`Leaderboard: ${leaderboardError.message}`);
      }
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    load();
  }, []);

  function startEdit(activity) {
    setEditing(activity.activity_id);

    setForm({
      ...activity,
      due_date: activity.due_date?.slice(0, 16)
    });

    setShowForm(true);
  }

  async function save(e) {
    e.preventDefault();

    try {
      const payload = {
        ...form,
        due_date: new Date(form.due_date).toISOString()
      };

      if (editing) {
        await api(`/activities/${editing}`, {
          method: 'PUT',
          body: JSON.stringify(payload)
        });
      } else {
        await api('/activities', {
          method: 'POST',
          body: JSON.stringify(payload)
        });
      }

      setShowForm(false);
      setEditing(null);
      setForm(emptyForm);

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function complete(activity) {
    try {
      const result = await api(
        `/activities/${activity.activity_id}`,
        {
          method: 'PATCH',
          body: JSON.stringify({ status: 'Completed' })
        }
      );

      if (result.points_awarded > 0) {
        alert(`Activity completed! You earned ${result.points_awarded} XP.`);
      }

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(activity) {
    if (!window.confirm(`Delete "${activity.title}"?`)) {
      return;
    }

    try {
      await api(`/activities/${activity.activity_id}`, {
        method: 'DELETE'
      });

      await load();
    } catch (e) {
      setError(e.message);
    }
  }

  const stats = data.stats || {};
  const myPerformance = gamification.my_performance || {};

  return (
    <div className="page-content">

      <div className="welcome-row">
        <div>
          <span className="section-kicker">WELCOME TO LEARNOVA</span>
          <h1>Welcome to your learning space.</h1>
          <p className="muted">
            Organize your studies, manage deadlines and achieve your goals.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => {
            setEditing(null);
            setForm(emptyForm);
            setShowForm(true);
          }}
        >
          <Plus size={17} />
          Add activity
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="tools-grid">
        <SubjectManager />
        <NotificationPanel />
      </div>

      <ExamScheduler onScheduled={load} />

      <div className="stats-grid">
        <StatsCard
          label="Tasks"
          value={stats.total ?? 0}
          sub="All academic activities"
        />

        <StatsCard
          label="Exams"
          value={stats.exams ?? 0}
          sub="Upcoming examinations"
        />

        <StatsCard
          label="Due soon"
          value={stats.due_soon ?? 0}
          sub="Due in the next 48 hours"
        />

        <StatsCard
          label="Completed"
          value={stats.completed ?? 0}
          sub="Activities finished"
        />
      </div>

      {data.overload?.length > 0 && (
        <div className="alert-banner">
          <AlertTriangle size={20} />

          <div>
            <b>Academic overload detected</b>
            <p>
              {data.overload
                .map(item => `${item.date}: ${item.count} deadlines`)
                .join(' · ')}
              . Consider planning your workload early.
            </p>
          </div>
        </div>
      )}

      {/* ACHIEVEMENTS */}
      <AchievementBadges
        badges={myPerformance.badges || []}
        completed={myPerformance.completed || 0}
        xp={myPerformance.xp || 0}
      />

      {/* GLOBAL STUDENT LEADERBOARD */}
      <Leaderboard
        students={gamification.leaderboard || []}
        myPerformance={gamification.my_performance}
      />

      {showForm && (
        <section className="panel form-panel">

          <div className="panel-heading">
            <h3>{editing ? 'Edit activity' : 'Add academic activity'}</h3>

            <button
              className="text-button"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>

          <form onSubmit={save} className="activity-form">

            <label>
              Title
              <input
                required
                value={form.title}
                onChange={e =>
                  setForm({ ...form, title: e.target.value })
                }
                placeholder="e.g. DBMS examination"
              />
            </label>

            <label>
              Type
              <select
                value={form.activity_type}
                onChange={e =>
                  setForm({ ...form, activity_type: e.target.value })
                }
              >
                {['Assignment', 'Project', 'Exam', 'Lab Record', 'Other'].map(type => (
                  <option key={type}>{type}</option>
                ))}
              </select>
            </label>

            <label>
              Subject
              <input
                value={form.subject || ''}
                onChange={e =>
                  setForm({ ...form, subject: e.target.value })
                }
                placeholder="e.g. DBMS"
              />
            </label>

            <label>
              Due date and time
              <input
                type="datetime-local"
                required
                value={form.due_date || ''}
                onChange={e =>
                  setForm({ ...form, due_date: e.target.value })
                }
              />
            </label>

            <label>
              Priority
              <select
                value={form.priority}
                onChange={e =>
                  setForm({ ...form, priority: e.target.value })
                }
              >
                {['Low', 'Medium', 'High'].map(priority => (
                  <option key={priority}>{priority}</option>
                ))}
              </select>
            </label>

            {editing && (
              <label>
                Status
                <select
                  value={form.status}
                  onChange={e =>
                    setForm({ ...form, status: e.target.value })
                  }
                >
                  {['Pending', 'In Progress', 'Completed'].map(status => (
                    <option key={status}>{status}</option>
                  ))}
                </select>
              </label>
            )}

            <label className="wide">
              Description
              <textarea
                rows="2"
                value={form.description || ''}
                onChange={e =>
                  setForm({ ...form, description: e.target.value })
                }
                placeholder="Add details..."
              />
            </label>

            <div className="wide">
              <button className="primary-button">
                {editing ? 'Save changes' : 'Create activity'}
              </button>
            </div>

          </form>
        </section>
      )}

      <div className="content-grid">

        <section className="panel">

          <div className="panel-heading">
            <div>
              <span className="section-kicker">STAY ORGANIZED</span>
              <h3>All academic activities</h3>
            </div>

            <span className="count-pill">
              {data.activities?.length || 0} total
            </span>
          </div>

          {data.activities?.length ? (
            data.activities.map(activity => (
              <ActivityCard
                key={activity.activity_id}
                activity={activity}
                onComplete={complete}
                onEdit={startEdit}
                onDelete={remove}
              />
            ))
          ) : (
            <div className="empty-state">
              <div className="empty-icon">
                <Plus />
              </div>

              <h4>No activities yet</h4>
              <p>Add your first assignment, project or exam.</p>
            </div>
          )}

        </section>

        <div className="right-column">

          <RevisionPanel onUploaded={load} />

          <section className="panel tip-panel">
            <span className="section-kicker">A SMALL REMINDER</span>

            <h3>Progress beats pressure.</h3>

            <p>
              Break large academic tasks into smaller steps and give
              yourself time to revise before an exam.
            </p>

            <div className="tip-foot">
              <ArrowUpRight size={16} />
              Plan your next action
            </div>
          </section>

        </div>
      </div>

    </div>
  );
}
