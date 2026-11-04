import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function ExamScheduler({ onScheduled }) {
  const [subjects, setSubjects] = useState([]);
  const [form, setForm] = useState({
    title: '',
    subject: '',
    due_date: '',
    priority: 'High',
    description: ''
  });
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    api('/subjects')
      .then(setSubjects)
      .catch(e => setError(e.message));
  }, []);

  async function scheduleExam(e) {
    e.preventDefault();

    if (!form.subject) {
      setError('Please add and select a subject first.');
      return;
    }

    try {
      await api('/activities', {
        method: 'POST',
        body: JSON.stringify({
          title: form.title,
          description: form.description,
          activity_type: 'Exam',
          subject: form.subject,
          due_date: new Date(form.due_date).toISOString(),
          priority: form.priority,
          status: 'Pending'
        })
      });

      setMessage('Exam scheduled successfully.');
      setError('');
      setForm({
        title: '',
        subject: '',
        due_date: '',
        priority: 'High',
        description: ''
      });

      if (onScheduled) onScheduled();
    } catch (e) {
      setError(e.message);
      setMessage('');
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">PLAN AHEAD</span>
          <h3>Schedule an Exam</h3>
        </div>
      </div>

      <form onSubmit={scheduleExam} className="activity-form">
        <label className="wide">
          Exam name
          <input
            required
            value={form.title}
            onChange={e => setForm({ ...form, title: e.target.value })}
            placeholder="e.g. DBMS Mid Examination"
          />
        </label>

        <label>
          Subject
          <select
            required
            value={form.subject}
            onChange={e => setForm({ ...form, subject: e.target.value })}
          >
            <option value="">Select subject</option>
            {subjects.map(s => (
              <option key={s.subject_id} value={s.name}>{s.name}</option>
            ))}
          </select>
        </label>

        <label>
          Exam date and time
          <input
            type="datetime-local"
            required
            value={form.due_date}
            onChange={e => setForm({ ...form, due_date: e.target.value })}
          />
        </label>

        <label>
          Priority
          <select
            value={form.priority}
            onChange={e => setForm({ ...form, priority: e.target.value })}
          >
            <option>Low</option>
            <option>Medium</option>
            <option>High</option>
          </select>
        </label>

        <label className="wide">
          Description
          <textarea
            rows="2"
            value={form.description}
            onChange={e => setForm({ ...form, description: e.target.value })}
            placeholder="Add exam details..."
          />
        </label>

        <div className="wide">
          <button className="primary-button" type="submit">
            Schedule Exam
          </button>
        </div>
      </form>

      {message && <p className="inline-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}
    </section>
  );
}
