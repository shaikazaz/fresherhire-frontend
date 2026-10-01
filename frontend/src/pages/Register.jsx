import { useState } from 'react';
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { Alert } from '../components/ui.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { errMsg, homePath } from '../utils.js';

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const { code } = useParams();
  const [searchParams] = useSearchParams();
  const [role, setRole] = useState(searchParams.get('role') === 'recruiter' ? 'recruiter' : 'seeker');
  const [form, setForm] = useState({ full_name: '', email: '', password: '', company_name: '', campus_code: code || '' });
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  const set = (key) => (e) => setForm({ ...form, [key]: e.target.value });

  const submit = async (e) => {
    e.preventDefault();
    setBusy(true);
    setError(null);
    try {
      const payload = { role, full_name: form.full_name.trim(), email: form.email.trim(), password: form.password };
      if (role === 'recruiter') payload.company_name = form.company_name.trim();
      else if (form.campus_code.trim()) payload.campus_code = form.campus_code.trim();
      const user = await register(payload);
      navigate(role === 'seeker' ? '/seeker/resume' : homePath(user.role), { replace: true });
    } catch (err) {
      setError(errMsg(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-12">
      <div className="card p-6 md:p-8">
        <h1 className="text-2xl font-bold text-slate-900">Create your account</h1>
        <div className="mt-5 grid grid-cols-2 gap-2 rounded-xl bg-slate-100 p-1">
          {[['seeker', 'I am a job seeker'], ['recruiter', 'I am hiring']].map(([value, label]) => (
            <button key={value} type="button" onClick={() => setRole(value)}
              className={`rounded-lg px-3 py-2 text-sm font-semibold ${role === value ? 'bg-white text-indigo-700 shadow-sm' : 'text-slate-600'}`}>
              {label}
            </button>
          ))}
        </div>

        <form onSubmit={submit} className="mt-6 space-y-4">
          {error && <Alert>{error}</Alert>}
          <div>
            <label className="label" htmlFor="full_name">Full name</label>
            <input id="full_name" required className="input" value={form.full_name} onChange={set('full_name')} />
          </div>
          {role === 'recruiter' && (
            <div>
              <label className="label" htmlFor="company">Company name</label>
              <input id="company" required className="input" value={form.company_name} onChange={set('company_name')} />
            </div>
          )}
          <div>
            <label className="label" htmlFor="email">Email</label>
            <input id="email" type="email" required autoComplete="email" className="input" value={form.email} onChange={set('email')} />
          </div>
          <div>
            <label className="label" htmlFor="password">Password (8+ characters)</label>
            <input id="password" type="password" required minLength={8} autoComplete="new-password" className="input"
              value={form.password} onChange={set('password')} />
          </div>
          {role === 'seeker' && (
            <div>
              <label className="label" htmlFor="campus">Campus code (optional)</label>
              <input id="campus" className="input" placeholder="e.g. jntu-hyd" value={form.campus_code} onChange={set('campus_code')} />
            </div>
          )}
          <button className="btn btn-primary w-full" disabled={busy}>{busy ? 'Creating account...' : 'Sign up'}</button>
        </form>
        <p className="mt-6 text-center text-sm text-slate-500">
          Already registered? <Link to="/login" className="font-semibold text-indigo-600 hover:underline">Log in</Link>
        </p>
      </div>
    </div>
  );
}
