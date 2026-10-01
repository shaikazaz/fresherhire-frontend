import { useEffect, useMemo, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../api/client.js';
import JobCard from '../components/JobCard.jsx';
import JobFilters from '../components/JobFilters.jsx';
import { Alert, EmptyState, Spinner } from '../components/ui.jsx';
import { errMsg } from '../utils.js';

export default function Jobs() {
  const [searchParams, setSearchParams] = useSearchParams();
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const [skillOptions, setSkillOptions] = useState([]);
  const [showFilters, setShowFilters] = useState(false);

  const query = searchParams.toString();
  const values = useMemo(() => Object.fromEntries(new URLSearchParams(query)), [query]);

  useEffect(() => {
    api.get('/jobs/skills/').then((res) => setSkillOptions(res.data)).catch(() => {});
  }, []);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    api.get(`/jobs/?${query}`)
      .then((res) => { if (!cancelled) setData(res.data); })
      .catch((err) => { if (!cancelled) setError(errMsg(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [query]);

  const applyFilters = (draft) => {
    const next = {};
    Object.entries(draft).forEach(([k, v]) => { if (v !== '' && v !== undefined && k !== 'page') next[k] = v; });
    setSearchParams(next);
    setShowFilters(false);
  };

  const goPage = (page) => {
    setSearchParams({ ...values, page: String(page) });
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="mx-auto max-w-7xl px-4 py-8">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Jobs</h1>
          {data && <p className="text-sm text-slate-500">{data.count} job{data.count === 1 ? '' : 's'} found</p>}
        </div>
        <button className="btn btn-outline lg:hidden" onClick={() => setShowFilters(!showFilters)}>
          {showFilters ? 'Hide filters' : 'Show filters'}
        </button>
      </div>

      {data && data.is_seeker && !data.has_resume && (
        <div className="mt-4">
          <Alert kind="info">
            Jobs are ranked by how well you match once you have a resume that passes the ATS scan.{' '}
            <Link to="/seeker/resume" className="font-semibold underline">Upload your resume</Link>
          </Alert>
        </div>
      )}
      {data && data.is_seeker && data.has_resume && (
        <div className="mt-4"><Alert kind="success">Ranked for you: open jobs first, then best match, then newest.</Alert></div>
      )}

      <div className="mt-6 grid gap-6 lg:grid-cols-[300px_1fr]">
        <div className={`${showFilters ? 'block' : 'hidden'} lg:block`}>
          <JobFilters values={values} skillOptions={skillOptions} onApply={applyFilters} onReset={() => setSearchParams({})} />
        </div>

        <div>
          {loading && <Spinner label="Finding jobs..." />}
          {error && <Alert>{error}</Alert>}
          {!loading && !error && data && data.results.length === 0 && (
            <EmptyState title="No jobs match these filters" text="Try removing a filter or searching a broader location."
              action={<button className="btn btn-primary" onClick={() => setSearchParams({})}>Clear filters</button>} />
          )}
          {!loading && !error && data && data.results.length > 0 && (
            <>
              <div className="grid gap-4 md:grid-cols-2">
                {data.results.map((job) => <JobCard key={job.id} job={job} />)}
              </div>
              {data.total_pages > 1 && (
                <div className="mt-6 flex items-center justify-center gap-3">
                  <button className="btn btn-outline" disabled={data.page <= 1} onClick={() => goPage(data.page - 1)}>Previous</button>
                  <span className="text-sm text-slate-600">Page {data.page} of {data.total_pages}</span>
                  <button className="btn btn-outline" disabled={data.page >= data.total_pages} onClick={() => goPage(data.page + 1)}>Next</button>
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
}
