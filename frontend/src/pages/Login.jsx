
import { useState } from 'react';

import { Link, useLocation, useNavigate } from 'react-router-dom';

import { Alert } from '../components/ui.jsx';

import { useAuth } from '../context/AuthContext.jsx';

import { errMsg, homePath } from '../utils.js';

export default function Login() {
  const { login } = useAuth();

  const navigate = useNavigate();

  const location = useLocation();

  const [form, setForm] = useState({
    email: '',
    password: '',
  });

  const [error, setError] = useState(null);

  const [busy, setBusy] = useState(false);

  const submit = async (e) => {
    e.preventDefault();

    setBusy(true);
    setError(null);

    try {
      const user = await login(
        form.email.trim(),
        form.password
      );

      const from = location.state && location.state.from;

      navigate(
        from && from !== '/login'
          ? from
          : homePath(user.role),
        { replace: true }
      );
    } catch (err) {
      setError(
        err.response && err.response.status === 401
          ? 'Incorrect email or password.'
          : errMsg(err)
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="mx-auto max-w-md px-4 py-12">
      <div className="card p-6 md:p-8">

        {/* Login Header */}
        <h1 className="text-2xl font-bold text-slate-900">
          Welcome back
        </h1>

        <p className="mt-1 text-sm text-slate-500">
          Log in to continue.
        </p>

        {/* Login Form */}
        <form onSubmit={submit} className="mt-6 space-y-4">

          {error && <Alert>{error}</Alert>}

          {/* Email */}
          <div>
            <label
              className="label"
              htmlFor="email"
            >
              Email
            </label>

            <input
              id="email"
              type="email"
              required
              autoComplete="email"
              className="input"
              value={form.email}
              onChange={(e) =>
                setForm({
                  ...form,
                  email: e.target.value,
                })
              }
            />
          </div>

          {/* Password */}
          <div>
            <label
              className="label"
              htmlFor="password"
            >
              Password
            </label>

            <input
              id="password"
              type="password"
              required
              autoComplete="current-password"
              className="input"
              value={form.password}
              onChange={(e) =>
                setForm({
                  ...form,
                  password: e.target.value,
                })
              }
            />
          </div>

          {/* Login Button */}
          <button
            type="submit"
            className="btn btn-primary w-full"
            disabled={busy}
          >
            {busy ? 'Logging in...' : 'Log in'}
          </button>
        </form>

        {/* Demo Accounts */}
        <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <h2 className="font-semibold text-slate-900">
            Demo Accounts
          </h2>

          {/* Recruiter */}
          <div className="mt-3 rounded-md bg-white p-3">
            <p className="font-semibold text-slate-800">
              Recruiter
            </p>

            <p className="mt-1 text-sm text-slate-600">
              Email: recruiter@gmail.com
            </p>

            <p className="text-sm text-slate-600">
              Password: Recruiter@123
            </p>
          </div>

          {/* Seeker */}
          <div className="mt-3 rounded-md bg-white p-3">
            <p className="font-semibold text-slate-800">
              Seeker
            </p>

            <p className="mt-1 text-sm text-slate-600">
              Email: seeker@gmail.com
            </p>

            <p className="text-sm text-slate-600">
              Password: Seeker@123
            </p>
          </div>
        </div>

        {/* Admin Panel */}
        <div className="mt-4 text-center">
          <a
            href="http://127.0.0.1:8000/admin/"
            target="_blank"
            rel="noopener noreferrer"
            className="font-semibold text-indigo-600 hover:underline"
          >
            Open Admin Panel →
          </a>
        </div>

        {/* Register */}
        <p className="mt-6 text-center text-sm text-slate-500">
          New here?{' '}
          <Link
            to="/register"
            className="font-semibold text-indigo-600 hover:underline"
          >
            Create an account
          </Link>
        </p>

      </div>
    </div>
  );
}
