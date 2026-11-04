import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function SubjectManager() {
  const [subjects, setSubjects] = useState([]);
  const [name, setName] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  async function loadSubjects() {
    try {
      const data = await api('/subjects');
      setSubjects(data);
      setError('');
    } catch (e) {
      setError(e.message);
    }
  }

  useEffect(() => {
    loadSubjects();
  }, []);

  async function addSubject(e) {
    e.preventDefault();
    if (!name.trim()) return;

    try {
      await api('/subjects', {
        method: 'POST',
        body: JSON.stringify({ name: name.trim() })
      });

      setName('');
      setMessage('Subject added successfully.');
      setError('');
      await loadSubjects();
    } catch (e) {
      setError(e.message);
      setMessage('');
    }
  }

  async function deleteSubject(id) {
    if (!confirm('Delete this subject?')) return;

    try {
      await api(`/subjects/${id}`, { method: 'DELETE' });
      await loadSubjects();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section className="panel">
      <div className="panel-heading">
        <div>
          <span className="section-kicker">ACADEMIC ORGANIZATION</span>
          <h3>My Subjects</h3>
        </div>
        <span className="count-pill">{subjects.length} subjects</span>
      </div>

      <form onSubmit={addSubject} className="subject-add-form">
        <input
          value={name}
          onChange={e => setName(e.target.value)}
          placeholder="Enter subject name, e.g. DBMS"
          required
        />
        <button className="primary-button" type="submit">Add Subject</button>
      </form>

      {message && <p className="inline-message">{message}</p>}
      {error && <p className="error-message">{error}</p>}

      {subjects.length === 0 ? (
        <p className="muted">No subjects added yet.</p>
      ) : (
        <div className="subject-list">
          {subjects.map(subject => (
            <div className="subject-item" key={subject.subject_id}>
              <span>{subject.name}</span>
              <button
                type="button"
                className="text-button"
                onClick={() => deleteSubject(subject.subject_id)}
              >
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </section>
  );
}
