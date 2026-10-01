import { STATUS_LABELS, scoreColor } from '../utils.js';

export function Spinner({ label = 'Loading...' }) {
  return (
    <div className="flex items-center justify-center gap-3 py-16 text-slate-500">
      <span className="h-5 w-5 animate-spin rounded-full border-2 border-indigo-600 border-t-transparent" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function Alert({ kind = 'error', children }) {
  const styles = {
    error: 'border-red-200 bg-red-50 text-red-700',
    success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
    info: 'border-indigo-200 bg-indigo-50 text-indigo-700',
    warn: 'border-amber-200 bg-amber-50 text-amber-800',
  };
  return <div className={`rounded-lg border px-4 py-3 text-sm ${styles[kind]}`}>{children}</div>;
}

export function EmptyState({ title, text, action }) {
  return (
    <div className="card px-6 py-12 text-center">
      <p className="text-base font-semibold text-slate-800">{title}</p>
      {text && <p className="mx-auto mt-1 max-w-md text-sm text-slate-500">{text}</p>}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}

export function StatCard({ label, value, hint, accent = 'text-indigo-600' }) {
  return (
    <div className="card p-5">
      <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{label}</p>
      <p className={`mt-2 text-3xl font-bold ${accent}`}>{value}</p>
      {hint && <p className="mt-1 text-xs text-slate-500">{hint}</p>}
    </div>
  );
}

const STATUS_STYLES = {
  applied: 'bg-indigo-50 text-indigo-700',
  waitlisted: 'bg-amber-50 text-amber-700',
  shortlisted: 'bg-sky-50 text-sky-700',
  interview_scheduled: 'bg-sky-50 text-sky-700',
  interview_completed: 'bg-sky-50 text-sky-700',
  feedback_given: 'bg-violet-50 text-violet-700',
  offered: 'bg-emerald-50 text-emerald-700',
  placed: 'bg-emerald-50 text-emerald-700',
  rejected: 'bg-red-50 text-red-700',
  withdrawn: 'bg-slate-100 text-slate-600',
};

export function StatusBadge({ status }) {
  return (
    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-semibold ${STATUS_STYLES[status] || 'bg-slate-100 text-slate-700'}`}>
      {STATUS_LABELS[status] || status}
    </span>
  );
}

export function ScoreRing({ value, size = 64, label }) {
  const v = Math.max(0, Math.min(100, Math.round(value || 0)));
  const r = (size - 8) / 2;
  const c = 2 * Math.PI * r;
  const color = scoreColor(v);
  return (
    <div className="inline-flex flex-col items-center">
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke="#e2e8f0" strokeWidth="6" />
          <circle cx={size / 2} cy={size / 2} r={r} fill="none" stroke={color.stroke} strokeWidth="6"
            strokeLinecap="round" strokeDasharray={c} strokeDashoffset={c - (c * v) / 100} />
        </svg>
        <span className={`absolute inset-0 flex items-center justify-center font-bold ${color.text}`}
          style={{ fontSize: size / 3.2 }}>{v}</span>
      </div>
      {label && <span className="mt-1 text-xs text-slate-500">{label}</span>}
    </div>
  );
}

export function Bar({ value, max, label, detail }) {
  const pct = max ? Math.round((value / max) * 100) : 0;
  const color = scoreColor(pct);
  return (
    <div>
      <div className="flex items-center justify-between text-sm">
        <span className="font-medium text-slate-700">{label}</span>
        <span className="text-slate-500">{Number(value).toFixed(value % 1 ? 1 : 0)} / {max}</span>
      </div>
      <div className="mt-1 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className={`h-full rounded-full ${color.bg}`} style={{ width: `${pct}%` }} />
      </div>
      {detail && <p className="mt-1 text-xs text-slate-500">{detail}</p>}
    </div>
  );
}
