import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../api/client.js';
import { Alert, Spinner } from '../../components/ui.jsx';
import { errMsg } from '../../utils.js';

export default function CareerGuide() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [role, setRole] = useState('');
  const [loading, setLoading] = useState(true);

  const load = (r) => {
    setLoading(true);
    setError(null);
    api.get('/career/guide/', { params: r ? { role: r } : {} })
      .then((res) => setData(res.data))
      .catch((err) => setError(errMsg(err)))
      .finally(() => setLoading(false));
  };

  useEffect(() => { load(''); }, []);

  if (!data && loading) return <Spinner />;

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Career guide</h1>
        <p className="text-sm text-slate-500">Skill gaps based on what open jobs ask for right now.</p>
      </div>
      {error && <Alert>{error}</Alert>}

      <form className="card flex flex-wrap items-end gap-3 p-4" onSubmit={(e) => { e.preventDefault(); load(role.trim()); }}>
        <div className="min-w-[220px] flex-1">
          <label className="label" htmlFor="role">Target role (optional)</label>
          <input id="role" className="input" placeholder="e.g. Python, Data Analyst, React" value={role} onChange={(e) => setRole(e.target.value)} />
        </div>
        <button className="btn btn-primary">Update guide</button>
      </form>

      {data && (
        <>
          <p className="text-sm text-slate-600">
            Based on <strong>{data.total_jobs}</strong> open job{data.total_jobs === 1 ? '' : 's'}{data.role ? ` matching "${data.role}"` : ''}.
          </p>

          {!data.has_resume && (
            <Alert kind="warn">
              Upload a resume so we can compare your skills. <Link to="/seeker/resume" className="font-semibold underline">Upload resume</Link>
            </Alert>
          )}

          <section className="card p-6">
            <h2 className="font-semibold text-slate-900">Skills employers want that you are missing</h2>
            {data.gaps.length === 0 ? (
              <p className="mt-3 text-sm text-slate-500">No gaps found. You already have the skills these jobs ask for.</p>
            ) : (
              <div className="mt-4 space-y-5">
                {data.gaps.map((g) => (
                  <div key={g.skill} className="border-b border-slate-100 pb-5 last:border-0 last:pb-0">
                    <div className="flex items-center justify-between text-sm">
                      <span className="font-semibold text-slate-800">{g.skill}</span>
                      <span className="text-slate-500">{g.demand_jobs} jobs ({g.demand_pct}%)</span>
                    </div>
                    <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
                      <div className="h-full rounded-full bg-indigo-500" style={{ width: `${g.demand_pct}%` }} />
                    </div>
                    {g.resources.length > 0 && (
                      <ul className="mt-2 space-y-1 text-sm">
                        {g.resources.map((r) => (
                          <li key={r.title + r.kind}>
                            <span className="mr-2 rounded bg-slate-100 px-1.5 py-0.5 text-xs font-medium text-slate-600">{r.kind === 'course' ? 'Course' : 'Project'}</span>
                            {r.url ? <a href={r.url} target="_blank" rel="noreferrer" className="text-indigo-600 hover:underline">{r.title}</a> : r.title}
                            {r.provider && <span className="ml-1 text-xs text-slate-400">({r.provider})</span>}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                ))}
              </div>
            )}
          </section>

          {data.project_ideas.length > 0 && (
            <section className="card p-6">
              <h2 className="font-semibold text-slate-900">Project ideas to close the gap</h2>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
                {data.project_ideas.map((p) => <li key={p.title}>{p.title}</li>)}
              </ul>
            </section>
          )}

          <section className="card p-6">
            <h2 className="font-semibold text-slate-900">Most in-demand skills right now</h2>
            <div className="mt-3 flex flex-wrap gap-2">
              {data.market_top.map((m) => (
                <span key={m.skill} className={`rounded-md px-2.5 py-1 text-xs font-medium ${m.you_have ? 'bg-emerald-50 text-emerald-700' : 'bg-slate-100 text-slate-700'}`}>
                  {m.you_have && '\u2713 '}{m.skill} &middot; {m.demand_pct}%
                </span>
              ))}
            </div>
          </section>

          {data.resume_fixes.length > 0 && (
            <section className="card p-6">
              <h2 className="font-semibold text-slate-900">Resume fixes (ATS score {data.ats_score})</h2>
              <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-slate-700">
                {data.resume_fixes.map((f) => <li key={f}>{f}</li>)}
              </ul>
            </section>
          )}
        </>
      )}
    </div>
  );
}
