import { useEffect, useState } from 'react';
import { EXP_LEVELS, JOB_TYPES } from '../utils.js';

const EMPTY = { q: '', location: '', job_type: '', exp_level: '', skills: '', salary_min: '', posted: '', sort: '' };

export default function JobFilters({ values, skillOptions, onApply, onReset }) {
  const [draft, setDraft] = useState({ ...EMPTY, ...values });
  useEffect(() => setDraft({ ...EMPTY, ...values }), [values]);

  const set = (key) => (e) => setDraft({ ...draft, [key]: e.target.value });
  const submit = (e) => {
    e.preventDefault();
    onApply(draft);
  };

  return (
    <form onSubmit={submit} className="card space-y-4 p-5">
      <div>
        <label className="label" htmlFor="f-q">Search</label>
        <input id="f-q" className="input" placeholder="Title, company or keyword" value={draft.q} onChange={set('q')} />
      </div>
      <div>
        <label className="label" htmlFor="f-loc">Location</label>
        <input id="f-loc" className="input" placeholder="e.g. Hyderabad or Remote" value={draft.location} onChange={set('location')} />
      </div>
      <div>
        <label className="label" htmlFor="f-skills">Skills (comma separated)</label>
        <input id="f-skills" list="skill-options" className="input" placeholder="Python, React" value={draft.skills} onChange={set('skills')} />
        <datalist id="skill-options">
          {skillOptions.map((s) => <option key={s} value={s} />)}
        </datalist>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label" htmlFor="f-type">Job type</label>
          <select id="f-type" className="input" value={draft.job_type} onChange={set('job_type')}>
            <option value="">Any</option>
            {Object.entries(JOB_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
        <div>
          <label className="label" htmlFor="f-exp">Experience</label>
          <select id="f-exp" className="input" value={draft.exp_level} onChange={set('exp_level')}>
            <option value="">Any</option>
            {Object.entries(EXP_LEVELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
          </select>
        </div>
      </div>
      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className="label" htmlFor="f-sal">Min salary</label>
          <select id="f-sal" className="input" value={draft.salary_min} onChange={set('salary_min')}>
            <option value="">Any</option>
            <option value="200000">2 LPA+</option>
            <option value="300000">3 LPA+</option>
            <option value="500000">5 LPA+</option>
            <option value="800000">8 LPA+</option>
          </select>
        </div>
        <div>
          <label className="label" htmlFor="f-posted">Posted</label>
          <select id="f-posted" className="input" value={draft.posted} onChange={set('posted')}>
            <option value="">Any time</option>
            <option value="1">Last 24 hours</option>
            <option value="3">Last 3 days</option>
            <option value="7">Last 7 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>
      </div>
      <div>
        <label className="label" htmlFor="f-sort">Sort by</label>
        <select id="f-sort" className="input" value={draft.sort} onChange={set('sort')}>
          <option value="">Best match / newest</option>
          <option value="salary">Highest salary</option>
        </select>
      </div>
      <div className="flex gap-2">
        <button type="submit" className="btn btn-primary flex-1">Apply filters</button>
        <button type="button" className="btn btn-outline" onClick={onReset}>Reset</button>
      </div>
    </form>
  );
}
