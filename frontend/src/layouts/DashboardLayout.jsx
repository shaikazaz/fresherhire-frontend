import { NavLink, Outlet } from 'react-router-dom';

import Footer from '../components/Footer.jsx';
import Navbar from '../components/Navbar.jsx';
import { useAuth } from '../context/AuthContext.jsx';

const NAV = {
  seeker: [
    ['/seeker/dashboard', 'Dashboard'],
    ['/jobs', 'Find jobs'],
    ['/seeker/resume', 'Resume & ATS'],
    ['/seeker/profile', 'Profile'],
    ['/seeker/applications', 'My applications'],
    ['/seeker/career-guide', 'Career guide'],
    ['/seeker/plans', 'Plans'],
    ['/notifications', 'Notifications'],
  ],

  recruiter: [
    ['/recruiter/dashboard', 'Dashboard'],
    ['/recruiter/post-job', 'Post a job'],
    ['/recruiter/applicants', 'Applicants'],
    ['/recruiter/candidates', 'Candidates'],
    ['/recruiter/interviews', 'Interviews'],
    ['/notifications', 'Notifications'],
    ['/jobs', 'All jobs'],
  ],

  admin: [
    ['/admin/dashboard', 'Dashboard'],
    ['/jobs', 'All jobs'],
    ['/notifications', 'Notifications'],
  ],
};

const item = ({ isActive }) =>
  `whitespace-nowrap rounded-lg px-3 py-2 text-sm font-medium ${
    isActive
      ? 'bg-indigo-600 text-white'
      : 'text-slate-600 hover:bg-slate-100'
  }`;

export default function DashboardLayout() {
  const { user } = useAuth();

  const links = NAV[user?.role] || [];

  return (
    <div className="flex min-h-screen flex-col">
      <Navbar />

      <div className="mx-auto flex w-full max-w-7xl flex-1 flex-col gap-6 px-4 py-6 lg:flex-row">
        <aside className="lg:w-56 lg:shrink-0">
          <nav className="flex gap-1 overflow-x-auto pb-2 lg:sticky lg:top-24 lg:flex-col lg:overflow-visible">
            {links.map(([to, label]) => (
              <NavLink
                key={to}
                to={to}
                end
                className={item}
              >
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>

      <Footer />
    </div>
  );
}