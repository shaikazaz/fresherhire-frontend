export const JOB_TYPES = { full_time: 'Full-time', internship: 'Internship', part_time: 'Part-time', hiring_drive: 'Hiring drive' };
export const EXP_LEVELS = { fresher: 'Fresher', junior: '0-2 years', mid: '2-5 years' };
export const STATUS_LABELS = {
  applied: 'Applied', waitlisted: 'Waitlisted', shortlisted: 'Shortlisted', interview_scheduled: 'Interview scheduled',
  interview_completed: 'Interview completed', feedback_given: 'Feedback given', offered: 'Offered', placed: 'Placed',
  rejected: 'Rejected', withdrawn: 'Withdrawn',
};

export function homePath(role) {
  if (role === 'seeker') return '/seeker/dashboard';
  if (role === 'recruiter') return '/recruiter/dashboard';
  return '/admin/dashboard';
}

export function errMsg(err, fallback = 'Something went wrong. Please try again.') {
  if (!err) return fallback;
  const d = err.response && err.response.data;
  if (!d) return err.message === 'Network Error' ? 'Cannot reach the server. Is the backend running?' : fallback;
  if (typeof d === 'string') return d.length > 200 ? fallback : d;
  if (d.detail) return typeof d.detail === 'string' ? d.detail : fallback;
  const first = Object.entries(d)[0];
  if (first) {
    const [key, value] = first;
    const msg = Array.isArray(value) ? value[0] : typeof value === 'string' ? value : fallback;
    return key === 'non_field_errors' ? msg : `${key.replace(/_/g, ' ')}: ${msg}`;
  }
  return fallback;
}

export function formatSalary(job) {
  const fmt = (n) => (n >= 100000 ? `${(n / 100000).toFixed(1)} LPA` : `${Math.round(n / 1000)}k`);
  if (job.salary_min && job.salary_max) return `₹${fmt(job.salary_min)} - ${fmt(job.salary_max)}`;
  if (job.salary_max) return `Up to ₹${fmt(job.salary_max)}`;
  if (job.salary_min) return `From ₹${fmt(job.salary_min)}`;
  return 'Not disclosed';
}

export function timeAgo(iso) {
  const diff = (Date.now() - new Date(iso).getTime()) / 1000;
  if (diff < 3600) return `${Math.max(1, Math.floor(diff / 60))} min ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)} h ago`;
  return `${Math.floor(diff / 86400)} d ago`;
}

export function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' });
}

export function scoreColor(value) {
  if (value >= 75) return { text: 'text-emerald-600', stroke: '#059669', bg: 'bg-emerald-500' };
  if (value >= 50) return { text: 'text-amber-600', stroke: '#d97706', bg: 'bg-amber-500' };
  return { text: 'text-red-600', stroke: '#dc2626', bg: 'bg-red-500' };
}
