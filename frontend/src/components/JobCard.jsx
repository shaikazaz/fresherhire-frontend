import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client.js';
import { useAuth } from '../context/AuthContext.jsx';
import { EXP_LEVELS, JOB_TYPES, errMsg, formatSalary, timeAgo } from '../utils.js';
import { ScoreRing, StatusBadge } from './ui.jsx';

export default function JobCard({ job, onApplied }) {
  const { user } = useAuth();
  const [status, setStatus] = useState(job.application_status);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => setStatus(job.application_status), [job.application_status]);

  const isSeeker = user && user.role === 'seeker';
  const full = job.slots_left === 0;

  const apply = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const { data } = await api.post('/applications/', { job_id: job.id });
      setStatus(data.application.status);
      setMessage({ ok: true, text: data.detail });
      if (onApplied) onApplied(job, data.application.status);
    } catch (err) {
      setMessage({ ok: false, text: errMsg(err) });
    } finally {
      setBusy(false);
    }
  };

  let action;
  if (!isSeeker) {
    action = <Link to={`/jobs/${job.slug}`} className="btn btn-outline">View job</Link>;
  } else if (status) {
    action = <StatusBadge status={status} />;
  } else if (job.match_score === null || job.match_score === undefined) {
    action = <Link to="/seeker/resume" className="btn btn-outline">Upload resume to apply</Link>;
  } else if (!job.eligible) {
    action = <span className="text-xs font-medium text-red-600">Needs {job.min_match_score}+ match</span>;
  } else {
    action = (
      <button className="btn btn-primary" onClick={apply} disabled={busy}>
        {busy ? 'Applying...' : full ? 'Join waitlist' : 'Apply now'}
      </button>
    );
  }

  return (
    <article className="card p-5 transition hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="min-w-0">
          <Link to={`/jobs/${job.slug}`} className="block truncate text-base font-semibold text-slate-900 hover:text-indigo-600">
            {job.title}
          </Link>
          <p className="mt-0.5 text-sm text-slate-600">
            {job.company.name}
            {job.company.is_verified && <span title="Verified company" className="ml-1 text-emerald-600">&#10003;</span>}
          </p>
        </div>
        {job.match_score !== null && job.match_score !== undefined && (
          <ScoreRing value={job.match_score} size={52} label="match" />
        )}
      </div>

      <div className="mt-3 flex flex-wrap gap-2 text-xs">
        <span className="chip">{job.location}</span>
        <span className="chip">{JOB_TYPES[job.job_type] || job.job_type}</span>
        <span className="chip">{EXP_LEVELS[job.exp_level] || job.exp_level}</span>
        <span className="chip">{formatSalary(job)}</span>
      </div>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {job.skills.slice(0, 5).map((s) => (
          <span key={s.name} className="rounded-md bg-indigo-50 px-2 py-0.5 text-xs font-medium text-indigo-700">{s.name}</span>
        ))}
        {job.skills.length > 5 && <span className="text-xs text-slate-500">+{job.skills.length - 5} more</span>}
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-100 pt-3">
        <div className="text-xs text-slate-500">
          <span className={full ? 'font-semibold text-amber-600' : 'font-semibold text-emerald-600'}>
            {full ? 'Full: waitlist only' : `${job.slots_left} of ${job.application_cap} slots left`}
          </span>
          <span className="mx-1.5">&middot;</span>
          {timeAgo(job.created_at)}
        </div>
        {action}
      </div>
      {message && (
        <p className={`mt-2 text-xs ${message.ok ? 'text-emerald-600' : 'text-red-600'}`}>{message.text}</p>
      )}
    </article>
  );
}
