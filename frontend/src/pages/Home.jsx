import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api/client.js';
import JobCard from '../components/JobCard.jsx';
import { useAuth } from '../context/AuthContext.jsx';
import { homePath } from '../utils.js';

const STEPS = [
  ['1', 'Scan', 'Upload your resume once. We score it for ATS and tell you exactly what to fix.'],
  ['2', 'Match', 'Jobs are ranked for you by match score. No endless filter hunting.'],
  ['3', 'Apply', 'One click. Your verified resume is submitted automatically.'],
  ['4', 'Get feedback', 'Every application ends with a response, so you know how to improve.'],
];

const FEATURES = [
  ['ATS resume scan', 'A score out of 100 with a clear fix list before you apply.'],
  ['Ranked job feed', 'Active jobs first, then best match, then freshest.'],
  ['Limited applications', 'Capped slots with a waitlist keep recruiters focused on quality.'],
  ['Honest tracking', 'Separate Eligible, Applied and Placed counters.'],
  ['Career guide', 'Skill gaps, courses and project ideas based on live jobs.'],
  ['Fresher friendly', 'Projects and skills carry your match, not years of experience.'],
];

export default function Home() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState([]);

  useEffect(() => {
    api.get('/jobs/').then((res) => setJobs(res.data.results.slice(0, 6))).catch(() => {});
  }, []);

  return (
    <div>
      <section className="bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-600 text-white">
        <div className="mx-auto max-w-7xl px-4 py-16 md:py-24">
          <p className="mb-3 inline-block rounded-full bg-white/15 px-3 py-1 text-xs font-semibold uppercase tracking-wide">
            Fresher-first job marketplace
          </p>
          <h1 className="max-w-3xl text-3xl font-extrabold leading-tight md:text-5xl">
            Upload your resume once. Get matched. Apply in one click. Get feedback.
          </h1>
          <p className="mt-4 max-w-2xl text-base text-indigo-100 md:text-lg">
            We scan and fix your resume before you apply, rank jobs by how well you fit, and make sure every
            application ends with a response.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            {user ? (
              <Link to={homePath(user.role)} className="btn bg-white px-6 py-3 text-indigo-700 hover:bg-indigo-50">Go to dashboard</Link>
            ) : (
              <>
                <Link to="/register" className="btn bg-white px-6 py-3 text-indigo-700 hover:bg-indigo-50">Upload your resume</Link>
                <Link to="/register?role=recruiter" className="btn border border-white/40 px-6 py-3 text-white hover:bg-white/10">Hire freshers</Link>
              </>
            )}
            <Link to="/jobs" className="btn border border-white/40 px-6 py-3 text-white hover:bg-white/10">Browse jobs</Link>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4 py-14">
        <h2 className="text-2xl font-bold text-slate-900">How it works</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {STEPS.map(([n, title, text]) => (
            <div key={n} className="card p-5">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-indigo-100 text-sm font-bold text-indigo-700">{n}</span>
              <h3 className="mt-3 font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="mx-auto max-w-7xl px-4">
        <div className="flex items-end justify-between">
          <h2 className="text-2xl font-bold text-slate-900">Latest jobs</h2>
          <Link to="/jobs" className="text-sm font-semibold text-indigo-600 hover:underline">See all jobs</Link>
        </div>
        <div className="mt-6 grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {jobs.map((job) => <JobCard key={job.id} job={job} />)}
        </div>
        {jobs.length === 0 && <p className="mt-4 text-sm text-slate-500">No jobs yet. Run the seed command to load demo jobs.</p>}
      </section>

      <section className="mx-auto max-w-7xl px-4 py-14">
        <h2 className="text-2xl font-bold text-slate-900">Why FresherHire</h2>
        <div className="mt-6 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {FEATURES.map(([title, text]) => (
            <div key={title} className="card p-5">
              <h3 className="font-semibold text-slate-900">{title}</h3>
              <p className="mt-1 text-sm text-slate-600">{text}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
