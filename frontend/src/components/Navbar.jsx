
import { useState } from 'react';

import { Link, NavLink, useNavigate } from 'react-router-dom';

import { useAuth } from '../context/AuthContext.jsx';

import { homePath } from '../utils.js';

const linkClass = ({ isActive }) =>
  `rounded-lg px-3 py-2 text-sm font-medium ${
    isActive
      ? 'bg-indigo-50 text-indigo-700'
      : 'text-slate-600 hover:bg-slate-100'
  }`;

export default function Navbar() {
  const { user, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();

  const doLogout = () => {
    logout();
    setOpen(false);
    navigate('/');
  };

  const links = (
    <>
      <NavLink
        to="/jobs"
        className={linkClass}
        onClick={() => setOpen(false)}
      >
        Find Jobs
      </NavLink>

      {user && (
        <NavLink
          to={homePath(user.role)}
          className={linkClass}
          onClick={() => setOpen(false)}
        >
          Dashboard
        </NavLink>
      )}
    </>
  );

  return (
    <header className="sticky top-0 z-30 border-b border-slate-200 bg-white/90 backdrop-blur">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4">

        <Link
          to="/"
          className="flex items-center gap-2 text-lg font-bold text-slate-900"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-indigo-600 text-sm text-white">
            F
          </span>
          FresherHire
        </Link>

        <nav className="hidden items-center gap-1 md:flex">
          {links}
        </nav>

        <div className="hidden items-center gap-2 md:flex">
          {user ? (
            <>
              <span className="text-sm text-slate-500">
                {user.full_name || user.email}
              </span>

              <button
                className="btn btn-outline"
                onClick={doLogout}
              >
                Log out
              </button>
            </>
          ) : (
            <>
              <Link to="/login" className="btn btn-outline">
                Log in
              </Link>

              <Link to="/register" className="btn btn-primary">
                Sign up
              </Link>
            </>
          )}
        </div>

        <button
          className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 md:hidden"
          onClick={() => setOpen(!open)}
          aria-label="Menu"
        >
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
          >
            {open ? (
              <path d="M6 6l12 12M18 6L6 18" />
            ) : (
              <path d="M4 7h16M4 12h16M4 17h16" />
            )}
          </svg>
        </button>
      </div>

      {open && (
        <div className="space-y-1 border-t border-slate-200 bg-white px-4 py-3 md:hidden">
          <div className="flex flex-col gap-1">
            {links}
          </div>

          <div className="flex gap-2 pt-2">
            {user ? (
              <button
                className="btn btn-outline w-full"
                onClick={doLogout}
              >
                Log out
              </button>
            ) : (
              <>
                <Link
                  to="/login"
                  className="btn btn-outline flex-1"
                  onClick={() => setOpen(false)}
                >
                  Log in
                </Link>

                <Link
                  to="/register"
                  className="btn btn-primary flex-1"
                  onClick={() => setOpen(false)}
                >
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  );
}
