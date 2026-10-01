
import { useEffect, useState } from 'react';

import { Link } from 'react-router-dom';

import { api } from '../../api/client.js';

import JobCard from '../../components/JobCard.jsx';

import {
  Alert,
  EmptyState,
  ScoreRing,
  Spinner,
  StatCard,
  StatusBadge,
} from '../../components/ui.jsx';

import { useAuth } from '../../context/AuthContext.jsx';

import { errMsg, formatDate } from '../../utils.js';

export default function SeekerDashboard() {
  const { user } = useAuth();

  const [data, setData] = useState(null);
  const [billing, setBilling] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api
      .get('/seeker/dashboard/')
      .then((res) => setData(res.data))
      .catch((err) => setError(errMsg(err)));

    api
      .get('/billing/current/')
      .then((res) => setBilling(res.data))
      .catch((err) => {
        console.error('Failed to load billing:', err);
      });
  }, []);

  if (error) return <Alert>{error}</Alert>;

  if (!data) return <Spinner />;

  const c = data.counters;

  const isPremium = billing?.plan && billing.plan !== 'Free';

  return (
    <div className="space-y-6">

      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Hi {user.full_name ? user.full_name.split(' ')[0] : 'there'}
        </h1>

        <p className="text-sm text-slate-500">
          Here is where you stand.
        </p>
      </div>

      {/* Resume warning */}
      {!data.has_resume && (
        <Alert kind="warn">
          You do not have an active resume yet. Upload one that passes the ATS
          scan to see match scores and apply.{' '}
          <Link
            to="/seeker/resume"
            className="font-semibold underline"
          >
            Upload resume
          </Link>
        </Alert>
      )}

      {/* Stats */}
      <div className="grid gap-4 sm:grid-cols-3">
        <StatCard
          label="Eligible"
          value={c.eligible}
          hint="Jobs you can apply to"
          accent="text-indigo-600"
        />

        <StatCard
          label="Applied"
          value={c.applied}
          hint={
            c.waitlisted
              ? `${c.waitlisted} on waitlist`
              : 'Applications sent'
          }
          accent="text-sky-600"
        />

        <StatCard
          label="Placed"
          value={c.placed}
          hint="Offers received"
          accent="text-emerald-600"
        />
      </div>

      {/* ATS + Profile */}
      <div className="grid gap-4 md:grid-cols-2">

        <div className="card flex items-center gap-5 p-5">
          <ScoreRing value={data.ats_score} size={84} />

          <div>
            <p className="font-semibold text-slate-900">
              Resume ATS score
            </p>

            <p className="text-sm text-slate-500">
              {data.has_resume
                ? 'Active resume'
                : 'No active resume'}
            </p>

            <Link
              to="/seeker/resume"
              className="text-sm font-semibold text-indigo-600 hover:underline"
            >
              {data.has_resume
                ? 'View report'
                : 'Scan a resume'}
            </Link>
          </div>
        </div>

        <div className="card p-5">
          <div className="flex items-center justify-between">
            <p className="font-semibold text-slate-900">
              Profile completion
            </p>

            <span className="text-sm font-semibold text-indigo-600">
              {data.profile_completion}%
            </span>
          </div>

          <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-100">
            <div
              className="h-full rounded-full bg-indigo-600"
              style={{
                width: `${data.profile_completion}%`,
              }}
            />
          </div>

          <Link
            to="/seeker/profile"
            className="mt-3 inline-block text-sm font-semibold text-indigo-600 hover:underline"
          >
            Edit profile
          </Link>
        </div>

      </div>

      {/* PREMIUM / UNLOCK FEATURES */}
      <section className="card p-5">

        <div className="flex flex-wrap items-center justify-between gap-3">

          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Unlock Premium Features
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Get more opportunities and improve your job search.
            </p>
          </div>

          <div className="rounded-full bg-indigo-50 px-3 py-1 text-sm font-semibold text-indigo-700">
            {isPremium ? `${billing.plan} Active` : 'Free Plan'}
          </div>

        </div>

        <div className="mt-5 grid gap-4 md:grid-cols-3">

          {/* Profile Boost */}
          <div className="rounded-xl border border-slate-200 p-4">

            <div className="flex items-start justify-between">

              <div>
                <h3 className="font-semibold text-slate-900">
                  Profile Boost
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Make your profile more visible to recruiters.
                </p>
              </div>

              {!billing?.profile_boost && (
                <span className="text-lg">🔒</span>
              )}

            </div>

            {billing?.profile_boost ? (
              <div className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                ✓ Unlocked
              </div>
            ) : (
              <Link
                to="/seeker/plans"
                className="mt-4 block rounded-lg bg-indigo-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700"
              >
                Unlock Feature
              </Link>
            )}

          </div>

          {/* Priority Applications */}
          <div className="rounded-xl border border-slate-200 p-4">

            <div className="flex items-start justify-between">

              <div>
                <h3 className="font-semibold text-slate-900">
                  Priority Applications
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Get priority consideration for selected jobs.
                </p>
              </div>

              {!billing?.priority_applications && (
                <span className="text-lg">🔒</span>
              )}

            </div>

            {billing?.priority_applications ? (
              <div className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                ✓ Unlocked
              </div>
            ) : (
              <Link
                to="/seeker/plans"
                className="mt-4 block rounded-lg bg-indigo-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700"
              >
                Unlock Feature
              </Link>
            )}

          </div>

          {/* Resume Review */}
          <div className="rounded-xl border border-slate-200 p-4">

            <div className="flex items-start justify-between">

              <div>
                <h3 className="font-semibold text-slate-900">
                  Resume Review
                </h3>

                <p className="mt-1 text-sm text-slate-500">
                  Get detailed feedback to improve your resume.
                </p>
              </div>

              {!billing?.resume_review && (
                <span className="text-lg">🔒</span>
              )}

            </div>

            {billing?.resume_review ? (
              <div className="mt-4 rounded-lg bg-emerald-50 px-3 py-2 text-sm font-semibold text-emerald-700">
                ✓ Unlocked
              </div>
            ) : (
              <Link
                to="/seeker/plans"
                className="mt-4 block rounded-lg bg-indigo-600 px-4 py-2 text-center text-sm font-semibold text-white hover:bg-indigo-700"
              >
                Unlock Feature
              </Link>
            )}

          </div>

        </div>

        {!isPremium && (
          <div className="mt-5 rounded-lg bg-slate-50 p-4 text-sm text-slate-600">
            <span className="font-semibold text-slate-900">
              Want to unlock these features?
            </span>{' '}
            Choose a paid plan and complete payment.
            <Link
              to="/seeker/plans"
              className="ml-1 font-semibold text-indigo-600 hover:underline"
            >
              View plans →
            </Link>
          </div>
        )}

      </section>

      {/* Top matches */}
      <section>

        <div className="mb-3 flex items-center justify-between">

          <h2 className="text-lg font-semibold text-slate-900">
            Top matches for you
          </h2>

          <Link
            to="/jobs"
            className="text-sm font-semibold text-indigo-600 hover:underline"
          >
            All jobs
          </Link>

        </div>

        {data.top_matches.length === 0 ? (

          <EmptyState
            title="No matches yet"
            text={
              data.has_resume
                ? 'No open jobs match your profile right now. Check the career guide to close skill gaps.'
                : 'Upload a resume to see jobs ranked for you.'
            }
          />

        ) : (

          <div className="grid gap-4 xl:grid-cols-2">

            {data.top_matches.map((job) => (
              <JobCard
                key={job.id}
                job={job}
              />
            ))}

          </div>

        )}

      </section>

      {/* Recent applications */}
      <section>

        <h2 className="mb-3 text-lg font-semibold text-slate-900">
          Recent applications
        </h2>

        {data.recent_applications.length === 0 ? (

          <EmptyState
            title="No applications yet"
            text="Apply to a matched job and track it here."
          />

        ) : (

          <div className="card divide-y divide-slate-100">

            {data.recent_applications.map((a) => (

              <div
                key={a.id}
                className="flex flex-wrap items-center justify-between gap-2 p-4"
              >

                <div>

                  <Link
                    to={`/jobs/${a.job.slug}`}
                    className="font-medium text-slate-900 hover:text-indigo-600"
                  >
                    {a.job.title}
                  </Link>

                  <p className="text-xs text-slate-500">
                    {a.job.company} &middot; applied{' '}
                    {formatDate(a.applied_at)}
                  </p>

                </div>

                <StatusBadge status={a.status} />

              </div>

            ))}

          </div>

        )}

      </section>

    </div>
  );
}
