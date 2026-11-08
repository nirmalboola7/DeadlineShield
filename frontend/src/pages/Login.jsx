
import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  GraduationCap,
  ArrowRight,
  Sparkles,
  BookOpen
} from 'lucide-react';

export default function Login({ onLogin }) {
  const [form, setForm] = useState({
    email: '',
    password: ''
  });

  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);

  const change = (e) => {
    setForm({
      ...form,
      [e.target.name]: e.target.value
    });
  };

  async function submit(e) {
    e.preventDefault();
    setError('');
    setBusy(true);

    try {
      await onLogin(form);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="auth-page">
      <div className="login-decoration decoration-one"></div>
      <div className="login-decoration decoration-two"></div>

      <section className="login-layout">

        <div className="login-intro">
          <div className="login-logo">
            <div className="login-logo-icon">
              <GraduationCap size={25} />
            </div>
            <div>
              <h2>LEARNOVA</h2>
              <span>YOUR STUDENT WORKSPACE</span>
            </div>
          </div>

          <div className="login-welcome">
            <span className="login-tag">
              <Sparkles size={14} />
              LEARN • PLAN • ACHIEVE
            </span>

            <h1>
              Your goals deserve
              <span> a better plan.</span>
            </h1>

            <p>
              Bring your assignments, exams and projects
              together in one organised workspace.
              Stay focused and make every day count.
            </p>

            <div className="login-feature">
              <div className="feature-icon">
                <BookOpen size={19} />
              </div>
              <div>
                <strong>One workspace. Every goal.</strong>
                <small>Plan your academic journey with confidence.</small>
              </div>
            </div>
          </div>

          <div className="login-footer-note">
            Designed for students who want to achieve more.
          </div>
        </div>

        <div className="auth-card login-card">
          <div className="login-card-heading">
            <span className="section-kicker">WELCOME BACK</span>
            <h2>Sign in to LEARNOVA</h2>
            <p className="muted">
              Pick up where you left off. Your workspace is waiting.
            </p>
          </div>

          <form onSubmit={submit} className="form-stack">
            <label>
              Email address
              <input
                type="email"
                name="email"
                value={form.email}
                onChange={change}
                required
                placeholder="Enter your email address"
                autoComplete="email"
              />
            </label>

            <label>
              Password
              <input
                type="password"
                name="password"
                value={form.password}
                onChange={change}
                required
                placeholder="Enter your password"
                autoComplete="current-password"
              />
            </label>

            {error && (
              <div className="error-message">
                {error}
              </div>
            )}

            <button
              className="primary-button full login-submit"
              type="submit"
              disabled={busy}
            >
              {busy ? 'Signing in...' : 'Sign in to your workspace'}
              {!busy && <ArrowRight size={17} />}
            </button>
          </form>

          <div className="login-divider">
            <span>NEW TO LEARNOVA?</span>
          </div>

          <p className="auth-foot">
            Don't have an account?
            <Link to="/register"> Create an account</Link>
          </p>

          <div className="login-secure-note">
            Your learning journey, organised in one place.
          </div>
        </div>

      </section>
    </main>
  );
}
