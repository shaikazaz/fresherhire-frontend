
import { Route, Routes } from 'react-router-dom';

import ProtectedRoute from './components/ProtectedRoute.jsx';
import DashboardLayout from './layouts/DashboardLayout.jsx';
import PublicLayout from './layouts/PublicLayout.jsx';

import Home from './pages/Home.jsx';
import JobDetail from './pages/JobDetail.jsx';
import Jobs from './pages/Jobs.jsx';
import Login from './pages/Login.jsx';
import NotFound from './pages/NotFound.jsx';
import Register from './pages/Register.jsx';

import AdminDashboard from './pages/admin/Dashboard.jsx';

import RecruiterDashboard from './pages/recruiter/Dashboard.jsx';
import PostJob from './pages/recruiter/PostJob.jsx';
import Applicants from './pages/recruiter/Applicants.jsx';
import Candidates from './pages/recruiter/Candidates.jsx';
import Interviews from './pages/recruiter/Interviews.jsx';

import Applications from './pages/seeker/Applications.jsx';
import CareerGuide from './pages/seeker/CareerGuide.jsx';
import SeekerDashboard from './pages/seeker/Dashboard.jsx';
import Profile from './pages/seeker/Profile.jsx';
import ResumePage from './pages/seeker/Resume.jsx';
import SeekerPlans from './pages/seeker/Plans.jsx';

import Notifications from './pages/Notifications.jsx';

const guard = (role) => (
  <ProtectedRoute roles={[role]}>
    <DashboardLayout />
  </ProtectedRoute>
);

export default function App() {
  return (
    <Routes>

      {/* ================= PUBLIC ================= */}

      <Route element={<PublicLayout />}>
        <Route path="/" element={<Home />} />

        <Route
          path="/jobs"
          element={<Jobs />}
        />

        <Route
          path="/jobs/:slug"
          element={<JobDetail />}
        />

        <Route
          path="/login"
          element={<Login />}
        />

        <Route
          path="/register"
          element={<Register />}
        />

        <Route
          path="/join/:code"
          element={<Register />}
        />
      </Route>


      {/* ================= SEEKER / CANDIDATE ================= */}

      <Route element={guard('seeker')}>

        <Route
          path="/seeker/dashboard"
          element={<SeekerDashboard />}
        />

        <Route
          path="/seeker/resume"
          element={<ResumePage />}
        />

        <Route
          path="/seeker/profile"
          element={<Profile />}
        />

        <Route
          path="/seeker/applications"
          element={<Applications />}
        />

        <Route
          path="/seeker/career-guide"
          element={<CareerGuide />}
        />

        {/* Candidate Plans */}
        <Route
          path="/seeker/plans"
          element={<SeekerPlans />}
        />

        <Route
          path="/notifications"
          element={<Notifications />}
        />

      </Route>


      {/* ================= RECRUITER ================= */}

      <Route element={guard('recruiter')}>

        <Route
          path="/recruiter/dashboard"
          element={<RecruiterDashboard />}
        />

        <Route
          path="/recruiter/post-job"
          element={<PostJob />}
        />

        <Route
          path="/recruiter/applicants"
          element={<Applicants />}
        />

        <Route
          path="/recruiter/candidates"
          element={<Candidates />}
        />

        <Route
          path="/recruiter/interviews"
          element={<Interviews />}
        />

        <Route
          path="/notifications"
          element={<Notifications />}
        />

      </Route>


      {/* ================= ADMIN ================= */}

      <Route element={guard('admin')}>

        <Route
          path="/admin/dashboard"
          element={<AdminDashboard />}
        />

        <Route
          path="/notifications"
          element={<Notifications />}
        />

      </Route>


      {/* ================= 404 ================= */}

      <Route element={<PublicLayout />}>

        <Route
          path="*"
          element={<NotFound />}
        />

      </Route>

    </Routes>
  );
}
