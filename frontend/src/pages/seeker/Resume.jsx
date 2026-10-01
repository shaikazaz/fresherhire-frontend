import { useEffect, useRef, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client.js';
import { Alert, Bar, ScoreRing, Spinner } from '../../components/ui.jsx';
import { errMsg, formatDate } from '../../utils.js';

function Report({ resume }) {
  const report = resume.report || {};
  return (
    <div className="space-y-6">
      <div className="card flex flex-wrap items-center gap-6 p-6">
        <ScoreRing value={resume.ats_score} size={110} label="ATS score" />
        <div className="min-w-0 flex-1">
          {resume.passed ? (
            <Alert kind="success">Great! This resume passed the ATS scan (needs {resume.threshold}+) and is now your active resume.</Alert>
          ) : (
            <Alert kind="warn">
              This resume scored {resume.ats_score}, but you need {resume.threshold}+ to use it for applying. Fix the items
              below and upload it again.
            </Alert>
          )}
          <p className="mt-2 truncate text-xs text-slate-500">{resume.original_name} &middot; {formatDate(resume.uploaded_at)}</p>
        </div>
      </div>

      <div className="card space-y-5 p-6">
        <h2 className="font-semibold text-slate-900">Score breakdown</h2>
        {(report.groups || []).map((g) => <Bar key={g.key} label={g.label} value={g.points} max={g.max} />)}
      </div>

      {report.fixes && report.fixes.length > 0 ? (
        <div className="card p-6">
          <h2 className="font-semibold text-slate-900">What to fix</h2>
          <ul className="mt-3 space-y-2">
            {report.fixes.map((fix) => (
              <li key={fix} className="flex gap-2 text-sm text-slate-700">
                <span className="mt-0.5 text-amber-500">&#9888;</span>{fix}
              </li>
            ))}
          </ul>
        </div>
      ) : (
        <Alert kind="success">No fixes needed. Your resume is ATS friendly.</Alert>
      )}

      <div className="card p-6">
        <h2 className="font-semibold text-slate-900">Skills found ({(report.skills_found || []).length})</h2>
        <div className="mt-3 flex flex-wrap gap-2">
          {(report.skills_found || []).map((s) => (
            <span key={s} className="rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700">{s}</span>
          ))}
          {(report.skills_found || []).length === 0 && <p className="text-sm text-slate-500">No known skills detected.</p>}
        </div>
        {resume.passed && (
          <p className="mt-4 text-sm text-slate-500">
            These skills were added to your profile. <Link to="/seeker/profile" className="font-semibold text-indigo-600 hover:underline">Review your profile</Link>
          </p>
        )}
      </div>
    </div>
  );
}

export default function ResumePage() {
  const [history, setHistory] = useState(null);
  const [current, setCurrent] = useState(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  const loadHistory = () =>
    api.get('/resumes/')
      .then((res) => {
        setHistory(res.data);
        setCurrent((prev) => prev || res.data.find((r) => r.is_active) || res.data[0] || null);
      })
      .catch((err) => setError(errMsg(err)));

  useEffect(() => { loadHistory(); }, []);

  const upload = async (file) => {
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const form = new FormData();
      form.append('file', file);
      const { data } = await api.post('/resumes/', form);
      setCurrent(data);
      await loadHistory();
      setCurrent(data);
    } catch (err) {
      setError(errMsg(err));
    } finally {
      setBusy(false);
      if (inputRef.current) inputRef.current.value = '';
    }
  };

  const onDrop = (e) => {
    e.preventDefault();
    setDragging(false);
    upload(e.dataTransfer.files && e.dataTransfer.files[0]);
  };

  if (!history && !error) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Resume & ATS scan</h1>
        <p className="text-sm text-slate-500">Upload once. We scan it, fill your profile and use it for one-click applications.</p>
      </div>

      {error && <Alert>{error}</Alert>}

      <div
        onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={`card border-2 border-dashed p-8 text-center transition ${dragging ? 'border-indigo-500 bg-indigo-50' : 'border-slate-300'}`}
      >
        <p className="font-semibold text-slate-900">{busy ? 'Scanning your resume...' : 'Drag and drop your resume here'}</p>
        <p className="mt-1 text-sm text-slate-500">PDF or DOCX, up to 5 MB. Use a single-column, text-based resume.</p>
        <input ref={inputRef} type="file" accept=".pdf,.docx" className="hidden" id="resume-file"
          onChange={(e) => upload(e.target.files && e.target.files[0])} />
        <label htmlFor="resume-file" className={`btn btn-primary mt-4 cursor-pointer ${busy ? 'pointer-events-none opacity-50' : ''}`}>
          Choose file
        </label>
      </div>

      {current && <Report resume={current} />}

      {history && history.length > 1 && (
        <div className="card p-6">
          <h2 className="font-semibold text-slate-900">Upload history</h2>
          <div className="mt-3 divide-y divide-slate-100">
            {history.map((r) => (
              <button key={r.id} onClick={() => setCurrent(r)}
                className="flex w-full items-center justify-between gap-3 py-3 text-left hover:bg-slate-50">
                <span className="min-w-0">
                  <span className="block truncate text-sm font-medium text-slate-800">{r.original_name}</span>
                  <span className="text-xs text-slate-500">{formatDate(r.uploaded_at)}</span>
                </span>
                <span className="flex items-center gap-2 text-sm">
                  {r.is_active && <span className="rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">Active</span>}
                  <span className="font-semibold text-slate-700">{r.ats_score}</span>
                </span>
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
