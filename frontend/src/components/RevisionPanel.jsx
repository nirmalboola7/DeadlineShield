import { useState } from 'react';
import { FileUp, Sparkles, FileText } from 'lucide-react';
import { api } from '../services/api';

export default function RevisionPanel({onUploaded}) {
  const [file,setFile] = useState(null);
  const [busy,setBusy] = useState(false);
  const [message,setMessage] = useState('');
  async function upload(e) {
    e.preventDefault();
    if (!file) return setMessage('Choose a PDF, DOCX or TXT file first.');
    const body = new FormData(); body.append('file',file);
    setBusy(true); setMessage('');
    try { const result = await api('/revision/upload',{method:'POST',body}); setMessage(result.message); setFile(null); e.target.reset(); onUploaded?.(); }
    catch(err) { setMessage(err.message); }
    finally { setBusy(false); }
  }
  return <section className="panel revision-panel"><div className="panel-heading"><div><span className="section-kicker">STUDY SMARTER</span><h3><Sparkles size={18}/> Smart Exam Revision</h3></div><span className="ai-label">REVISION TOOL</span></div>
    <p>Upload your notes or previous question papers to keep your revision resources together. AI-powered question generation can be added in the next phase.</p>
    <form className="upload-row" onSubmit={upload}><label className="file-pick"><FileUp size={18}/><span>{file ? file.name : 'Choose study material'}</span><input type="file" accept=".pdf,.docx,.txt" onChange={e=>setFile(e.target.files[0])}/></label><button className="primary-button" disabled={busy}>{busy?'Uploading...':'Upload file'}</button></form>
    {message && <div className="inline-message">{message}</div>}
  </section>;
}
