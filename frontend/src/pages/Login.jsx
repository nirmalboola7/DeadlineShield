import { useState } from 'react';
import { Link } from 'react-router-dom';
import { ShieldCheck } from 'lucide-react';
export default function Login({onLogin}) {
  const [form,setForm] = useState({email:'',password:''}); const [error,setError] = useState(''); const [busy,setBusy] = useState(false);
  const change=e=>setForm({...form,[e.target.name]:e.target.value});
  async function submit(e){e.preventDefault();setError('');setBusy(true);try{await onLogin(form);}catch(err){setError(err.message);}finally{setBusy(false);}}
  return <main className="auth-page"><div className="auth-card"><div className="auth-brand"><ShieldCheck size={28}/><b>DeadlineShield</b></div><span className="section-kicker">WELCOME BACK</span><h1>Make every deadline count.</h1><p className="muted">Sign in to manage your academic workload.</p><form onSubmit={submit} className="form-stack"><label>Email address<input type="email" name="email" value={form.email} onChange={change} required placeholder="you@example.com"/></label><label>Password<input type="password" name="password" value={form.password} onChange={change} required placeholder="Your password"/></label>{error&&<div className="error-message">{error}</div>}<button className="primary-button full" disabled={busy}>{busy?'Signing in...':'Sign in'}</button></form><p className="auth-foot">New to DeadlineShield? <Link to="/register">Create an account</Link></p></div></main>;
}
