import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client.js';
import { Alert, EmptyState, Spinner, StatCard } from '../../components/ui.jsx';
import { errMsg, formatSalary, timeAgo } from '../../utils.js';

export default function RecruiterDashboard() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);

  useEffect(() => {
    api.get('/recruiter/dashboard/').then((res) => setData(res.data)).catch((err) => setError(errMsg(err)));
  }, []);

  if (error) return <Alert>{error}</Alert>;
  if (!data) return <Spinner />;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{data.company ? data.company.name : 'Recruiter dashboard'}</h1>
          <p className="text-sm text-slate-500">
            {data.company && data.company.is_verified ? 'Verified company' : 'Verification pending: an admin will verify your company.'}
          </p>
        </div>
        <Link to="/recruiter/post-job" className="btn btn-primary">Post a job</Link>
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard label="Active jobs" value={data.active_jobs} accent="text-indigo-600" />
        <StatCard label="Closed jobs" value={data.closed_jobs} accent="text-slate-600" />
        <StatCard label="Total applicants" value={data.total_applicants} accent="text-emerald-600" />
      </div>

      <section>
        <h2 className="mb-3 text-lg font-semibold text-slate-900">Your jobs</h2>
        {data.jobs.length === 0 ? (
          <EmptyState title="No jobs posted yet" text="Post your first job. It is free, and matching candidates are ranked for you."
            action={<Link to="/recruiter/post-job" className="btn btn-primary">Post a job</Link>} />
        ) : (
          <div className="card divide-y divide-slate-100">
            {data.jobs.map((job) => (
              <div key={job.id} className="flex flex-wrap items-center justify-between gap-3 p-4">
                <div className="min-w-0">
                  <Link to={`/jobs/${job.slug}`} className="font-medium text-slate-900 hover:text-indigo-600">{job.title}</Link>
                  <p className="text-xs text-slate-500">{job.location} &middot; {formatSalary(job)} &middot; posted {timeAgo(job.created_at)}</p>
                </div>
                <div className="text-right text-sm">
                  <p className="font-semibold text-slate-800">{job.applicants} applicant{job.applicants === 1 ? '' : 's'}</p>
                  <p className="text-xs text-slate-500">{job.slots_left} of {job.application_cap} slots left &middot; {job.status}</p>
                  <div className="mt-2 flex gap-2 justify-end">
                    <button className="btn btn-outline text-xs" disabled={busy===job.id} onClick={async()=>{
                      const amount=Number(window.prompt('How many review slots should be added?', '5'));
                      if(!amount || amount<1) return;
                      setBusy(job.id);
                      try { await api.post(`/recruiter/jobs/${job.id}/extend-cap/`, {additional_slots:amount}); const r=await api.get('/recruiter/dashboard/'); setData(r.data); }
                      catch(e){ setError(errMsg(e)); } finally { setBusy(null); }
                    }}>Extend cap</button>
                    {job.cap_mode==='best_match_window' && <button className="btn btn-outline text-xs" disabled={busy===job.id} onClick={async()=>{
                      setBusy(job.id);
                      try { await api.post(`/recruiter/jobs/${job.id}/finalize-window/`); const r=await api.get('/recruiter/dashboard/'); setData(r.data); }
                      catch(e){ setError(errMsg(e)); } finally { setBusy(null); }
                    }}>Promote best matches</button>}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
