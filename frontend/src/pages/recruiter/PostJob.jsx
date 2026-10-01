import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../../api/client.js';
import { Alert } from '../../components/ui.jsx';
import { EXP_LEVELS, JOB_TYPES, errMsg } from '../../utils.js';

const INITIAL = {
  title: '', description: '', location: '', job_type: 'full_time', exp_level: 'fresher', salary_min: '', salary_max: '',
  application_cap: 50, cap_mode: 'first_come', min_match_score: 40, skills: '',
};

export default function PostJob() {
  const navigate = useNavigate();
  const [form, setForm] = useState(INITIAL);
  const [skillOptions, setSkillOptions] = useState([]);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api.get('/jobs/skills/').then((res) => setSkillOptions(res.data)).catch(() => {});
  }, []);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const payload = {
        title: form.title.trim(), description: form.description.trim(), location: form.location.trim(),
        job_type: form.job_type, exp_level: form.exp_level, cap_mode: form.cap_mode,
        application_cap: Number(form.application_cap), min_match_score: Number(form.min_match_score),
        skills: form.skills.split(',').map((s) => s.trim()).filter(Boolean),
      };
      if (form.salary_min !== '') payload.salary_min = Number(form.salary_min);
      if (form.salary_max !== '') payload.salary_max = Number(form.salary_max);
      const { data } = await api.post('/jobs/', payload);
      navigate(`/jobs/${data.slug}`);
    } catch (err) {
      setError(errMsg(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">Post a job</h1>
        <p className="text-sm text-slate-500">Set a review capacity so your team only reviews the best matches.</p>
      </div>
      <form onSubmit={submit} className="card space-y-5 p-6">
        {error && <Alert>{error}</Alert>}
        <div><label className="label" htmlFor="j-title">Job title</label><input id="j-title" required className="input" value={form.title} onChange={set('title')} /></div>
        <div><label className="label" htmlFor="j-desc">Description</label><textarea id="j-desc" required rows={6} className="input" value={form.description} onChange={set('description')} /></div>
        <div className="grid gap-4 md:grid-cols-3">
          <div><label className="label" htmlFor="j-loc">Location</label><input id="j-loc" required className="input" placeholder="Hyderabad or Remote" value={form.location} onChange={set('location')} /></div>
          <div>
            <label className="label" htmlFor="j-type">Job type</label>
            <select id="j-type" className="input" value={form.job_type} onChange={set('job_type')}>
              {Object.entries(JOB_TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <div>
            <label className="label" htmlFor="j-exp">Experience</label>
            <select id="j-exp" className="input" value={form.exp_level} onChange={set('exp_level')}>
              {Object.entries(EXP_LEVELS).map(([k, v]) => <option key={k} value={k}>{v}</option>)}
            </select>
          </div>
          <div><label className="label" htmlFor="j-smin">Min salary (per year)</label><input id="j-smin" type="number" min="0" className="input" value={form.salary_min} onChange={set('salary_min')} /></div>
          <div><label className="label" htmlFor="j-smax">Max salary (per year)</label><input id="j-smax" type="number" min="0" className="input" value={form.salary_max} onChange={set('salary_max')} /></div>
        </div>
        <div>
          <label className="label" htmlFor="j-skills">Required skills (comma separated)</label>
          <input id="j-skills" list="job-skills" className="input" placeholder="Python, Django, SQL" value={form.skills} onChange={set('skills')} />
          <datalist id="job-skills">{skillOptions.map((s) => <option key={s} value={s} />)}</datalist>
          <p className="mt-1 text-xs text-slate-500">Keep it to the skills that really matter. Lists of 15+ skills discourage freshers.</p>
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          <div>
            <label className="label" htmlFor="j-cap">Review capacity</label>
            <input id="j-cap" type="number" min="1" max="1000" required className="input" value={form.application_cap} onChange={set('application_cap')} />
            <p className="mt-1 text-xs text-slate-500">How many applications can your team review?</p>
          </div>
          <div>
            <label className="label" htmlFor="j-mode">Capacity mode</label>
            <select id="j-mode" className="input" value={form.cap_mode} onChange={set('cap_mode')}>
              <option value="first_come">First come, then waitlist</option>
              <option value="best_match_window">Best match window</option>
            </select>
          </div>
          <div>
            <label className="label" htmlFor="j-min">Minimum match score</label>
            <input id="j-min" type="number" min="0" max="100" required className="input" value={form.min_match_score} onChange={set('min_match_score')} />
          </div>
        </div>
        <div className="flex justify-end"><button className="btn btn-primary" disabled={busy}>{busy ? 'Posting...' : 'Post job'}</button></div>
      </form>
    </div>
  );
}
