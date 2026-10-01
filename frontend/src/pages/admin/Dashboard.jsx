import { useEffect, useState } from 'react';
import { api } from '../../api/client.js';
import { Alert, Spinner, StatCard } from '../../components/ui.jsx';
import { errMsg } from '../../utils.js';

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    Promise.all([
      api.get('/platform/stats/'),
      api.get('/platform/analytics/'),
    ]).then(([summary, analytics]) => {
      setStats({ ...summary.data, analytics: analytics.data });
    }).catch((err) => setError(errMsg(err)));
  }, []);

  if (error) return <Alert>{error}</Alert>;
  if (!stats) return <Spinner />;

  const a = stats.analytics;
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Platform analytics</h1>
        <p className="text-sm text-slate-500">
          Marketplace health, application flow and recruiter activity.
          {' '}
          <a className="font-semibold text-indigo-600 hover:underline" href="http://127.0.0.1:8000/admin/" target="_blank" rel="noreferrer">
            Open Django admin
          </a>
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard label="Job seekers" value={stats.seekers} />
        <StatCard label="Recruiters" value={stats.recruiters} accent="text-sky-600" />
        <StatCard label="Active jobs" value={stats.active_jobs} accent="text-emerald-600" />
        <StatCard label="Applications" value={stats.applications} accent="text-violet-600" />
        <StatCard label="Placements" value={stats.placements} accent="text-emerald-600" />
        <StatCard label="Companies" value={stats.companies} accent="text-slate-700" />
        <StatCard label="Subscriptions" value={a.active_subscriptions} accent="text-indigo-600" />
        <StatCard label="Notifications" value={a.notifications} accent="text-amber-600" />
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <section className="card p-5">
          <h2 className="font-bold text-slate-900">Application pipeline</h2>
          <div className="mt-4 space-y-2">
            {a.applications_by_status.map((row) => (
              <div key={row.status} className="flex justify-between border-b border-slate-100 py-2 text-sm">
                <span className="capitalize">{row.status.replaceAll('_', ' ')}</span>
                <b>{row.count}</b>
              </div>
            ))}
          </div>
        </section>

        <section className="card p-5">
          <h2 className="font-bold text-slate-900">Top jobs by applications</h2>
          <div className="mt-4 space-y-2">
            {a.top_jobs.map((job) => (
              <div key={job.id} className="flex justify-between border-b border-slate-100 py-2 text-sm">
                <span>{job.title}</span>
                <b>{job.applications_count}</b>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="card p-5">
        <h2 className="font-bold text-slate-900">Response SLA</h2>
        <p className="mt-2 text-sm text-slate-600">
          Average response time:{' '}
          <b>{a.average_response_hours == null ? 'No responses yet' : `${a.average_response_hours} hours`}</b>
        </p>
      </section>
    </div>
  );
}
