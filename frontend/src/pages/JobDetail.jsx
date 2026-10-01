import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { api } from '../api/client.js';
import { Alert, Bar, ScoreRing, Spinner, StatusBadge } from '../components/ui.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { EXP_LEVELS, JOB_TYPES, errMsg, formatSalary, timeAgo } from '../utils.js';

export default function JobDetail() {
  const { slug } = useParams();
  const { user } = useAuth();
  const [job, setJob] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState(null);

  const load = () =>
    api.get(`/jobs/${slug}/`)
      .then((res) => setJob(res.data))
      .catch((err) => setError(err.response && err.response.status === 404 ? 'This job could not be found.' : errMsg(err)));

  useEffect(() => {
    setJob(null);
    setError(null);
    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [slug]);

  const apply = async () => {
    setBusy(true);
    setMessage(null);
    try {
      const { data } = await api.post('/applications/', { job_id: job.id });
      setMessage({ ok: true, text: data.detail });
      await load();
    } catch (err) {
      setMessage({ ok: false, text: errMsg(err) });
    } finally {
      setBusy(false);
    }
  };

  if (error) return <div className="mx-auto max-w-3xl px-4 py-12"><Alert>{error}</Alert></div>;
  if (!job) return <Spinner />;

  const match = job.match;
  const isSeeker = user && user.role === 'seeker';
  const matchedSet = new Set(match ? match.matched_skills : []);
  const full = job.slots_left === 0;
  const closed = job.status !== 'active';

  let action;
  if (!user) {
    action = <Link to="/login" state={{ from: `/jobs/${job.slug}` }} className="btn btn-primary w-full">Log in to apply</Link>;
  } else if (!isSeeker) {
    action = <p className="text-sm text-slate-500">Only job seekers can apply.</p>;
  } else if (job.application_status) {
    action = <div className="flex items-center justify-between"><span className="text-sm text-slate-600">Your application</span><StatusBadge status={job.application_status} /></div>;
  } else if (closed) {
    action = <p className="text-sm font-medium text-red-600">This job is closed.</p>;
  } else if (!job.viewer.has_resume) {
    action = <Link to="/seeker/resume" className="btn btn-primary w-full">Upload a resume to apply</Link>;
  } else if (!job.eligible) {
    action = <button className="btn btn-primary w-full" disabled>Need a {job.min_match_score}+ match (you have {job.match_score})</button>;
  } else {
    action = <button className="btn btn-primary w-full" onClick={apply} disabled={busy}>{busy ? 'Applying...' : full ? 'Join waitlist' : 'Apply in one click'}</button>;
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-8">
      <Link to="/jobs" className="text-sm text-indigo-600 hover:underline">&larr; All jobs</Link>
      <div className="mt-4 grid gap-6 lg:grid-cols-[1fr_340px]">
        <div className="space-y-6">
          <div className="card p-6">
            <h1 className="text-2xl font-bold text-slate-900">{job.title}</h1>
            <p className="mt-1 text-slate-600">
              {job.company.name}
              {job.company.is_verified && <span className="ml-2 rounded-full bg-emerald-50 px-2 py-0.5 text-xs font-semibold text-emerald-700">Verified</span>}
            </p>
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <span className="chip">{job.location}</span>
              <span className="chip">{JOB_TYPES[job.job_type]}</span>
              <span className="chip">{EXP_LEVELS[job.exp_level]}</span>
              <span className="chip">{formatSalary(job)}</span>
              <span className="chip">Posted {timeAgo(job.created_at)}</span>
            </div>
            <h2 className="mt-6 font-semibold text-slate-900">About the role</h2>
            <p className="mt-2 whitespace-pre-line text-sm leading-relaxed text-slate-700">{job.description}</p>
            <h2 className="mt-6 font-semibold text-slate-900">Skills</h2>
            <div className="mt-2 flex flex-wrap gap-2">
              {job.skills.map((s) => {
                const have = matchedSet.has(s.name);
                const cls = match ? (have ? 'bg-emerald-50 text-emerald-700' : 'bg-red-50 text-red-700') : 'bg-indigo-50 text-indigo-700';
                return (
                  <span key={s.name} className={`rounded-md px-2.5 py-1 text-xs font-medium ${cls}`}>
                    {match && (have ? '\u2713 ' : '\u2717 ')}{s.name}{s.is_required ? '' : ' (nice to have)'}
                  </span>
                );
              })}
            </div>
            {match && <p className="mt-2 text-xs text-slate-500">Green skills are on your resume. Red skills are missing.</p>}
          </div>

          {match && (
            <div className="card p-6">
              <h2 className="font-semibold text-slate-900">How your match score is calculated</h2>
              <div className="mt-4 space-y-4">
                {match.breakdown.map((b) => <Bar key={b.key} label={b.label} value={b.points} max={b.max} detail={b.detail} />)}
              </div>
            </div>
          )}
        </div>

        <aside className="space-y-4 lg:sticky lg:top-24 lg:self-start">
          <div className="card space-y-4 p-6">
            {job.match_score !== null && (
              <div className="flex items-center gap-4">
                <ScoreRing value={job.match_score} size={72} />
                <div>
                  <p className="font-semibold text-slate-900">Your match</p>
                  <p className="text-xs text-slate-500">Minimum to apply: {job.min_match_score}</p>
                </div>
              </div>
            )}
            <div className="rounded-lg bg-slate-50 p-3 text-sm">
              <p className={full ? 'font-semibold text-amber-600' : 'font-semibold text-emerald-600'}>
                {full ? 'All slots taken: waitlist open' : `${job.slots_left} of ${job.application_cap} slots left`}
              </p>
              <p className="mt-0.5 text-xs text-slate-500">Applications are limited so recruiters can review each one.</p>
            </div>
            {action}
            {message && <Alert kind={message.ok ? 'success' : 'error'}>{message.text}</Alert>}
          </div>
        </aside>
      </div>
    </div>
  );
}
