
import { useEffect, useState } from "react";

import { Link } from "react-router-dom";

import { api } from "../../api/client.js";

import {
  Alert,
  EmptyState,
  Spinner,
  StatusBadge,
} from "../../components/ui.jsx";

import {
  JOB_TYPES,
  errMsg,
  formatDate,
} from "../../utils.js";

export default function Applications() {
  const [apps, setApps] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(null);

  const loadApplications = async () => {
    try {
      setError(null);

      const response = await api.get("/applications/");

      setApps(
        Array.isArray(response.data)
          ? response.data
          : []
      );
    } catch (err) {
      console.error("Failed to load applications:", err);
      setError(errMsg(err));
    }
  };

  useEffect(() => {
    loadApplications();
  }, []);

  if (error && !apps) {
    return <Alert>{error}</Alert>;
  }

  if (!apps) {
    return <Spinner />;
  }

  const count = (statuses) =>
    apps.filter((application) =>
      statuses.includes(application.status)
    ).length;

  const confirmInterview = async (application) => {
    const interviewId = application.interview?.id;

    if (!interviewId) {
      setError("Interview ID is missing.");
      return;
    }

    try {
      setBusy(application.id);
      setError(null);

      /*
       * Backend URL:
       * path("interviews/<int:pk>/confirm/", InterviewConfirmView.as_view())
       *
       * config/urls.py includes applications.urls under /api/
       *
       * Therefore the final API URL is:
       * POST /api/interviews/<interview_id>/confirm/
       */
      await api.post(
        `/interviews/${interviewId}/confirm/`
      );

      await loadApplications();
    } catch (err) {
      console.error(
        "Failed to confirm interview:",
        err
      );

      setError(
        err.response?.data?.detail ||
          errMsg(err) ||
          "Failed to confirm interview."
      );
    } finally {
      setBusy(null);
    }
  };

  return (
    <div className="space-y-6">

      {/* Page heading */}
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          My applications
        </h1>

        <p className="text-sm text-slate-500">
          {apps.length} total
          {" · "}
          {count(["waitlisted"])} waitlisted
          {" · "}
          {count(["offered", "placed"])} placed
        </p>
      </div>

      {/* Error */}
      {error && (
        <Alert>
          {error}
        </Alert>
      )}

      {/* Empty state */}
      {apps.length === 0 ? (
        <EmptyState
          title="You have not applied yet"
          text="Find a job that matches your resume and apply in one click."
          action={
            <Link
              to="/jobs"
              className="btn btn-primary"
            >
              Browse jobs
            </Link>
          }
        />
      ) : (

        /* Applications */
        <div className="space-y-3">

          {apps.map((application) => (
            <div
              key={application.id}
              className="card p-5"
            >

              {/* Application header */}
              <div className="flex flex-wrap items-start justify-between gap-3">

                <div>

                  <Link
                    to={`/jobs/${application.job.slug}`}
                    className="font-semibold text-slate-900 hover:text-indigo-600"
                  >
                    {application.job?.title || "Job"}
                  </Link>

                  <p className="text-sm text-slate-600">
                    {application.job?.company || "-"}
                    {" · "}
                    {application.job?.location || "-"}
                    {" · "}
                    {JOB_TYPES[application.job?.job_type] ||
                      application.job?.job_type ||
                      "-"}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    Applied{" "}
                    {formatDate(application.applied_at)}
                    {" · "}
                    match{" "}
                    {application.match_score ?? "-"}
                  </p>

                </div>

                {/* Status */}
                <div className="flex items-center gap-2">

                  <StatusBadge
                    status={application.status}
                  />

                  <span
                    className={`rounded-full px-2 py-1 text-xs font-semibold ${
                      application.sla_status ===
                      "overdue"
                        ? "bg-red-100 text-red-700"
                        : application.sla_status ===
                          "responded"
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-slate-100 text-slate-600"
                    }`}
                  >
                    {application.sla_status ===
                    "overdue"
                      ? "SLA overdue"
                      : application.sla_status ===
                        "responded"
                      ? "Response received"
                      : "Within SLA"}
                  </span>

                </div>
              </div>

              {/* =========================
                  INTERVIEW SECTION
                  ========================= */}

              {application.interview && (
                <div className="mt-4 rounded-lg bg-sky-50 p-4 text-sm text-sky-900">

                  <p className="font-semibold text-sky-950">
                    Interview scheduled
                  </p>

                  <p className="mt-1">
                    <strong>Date & Time:</strong>{" "}
                    {application.interview.scheduled_at
                      ? new Date(
                          application.interview.scheduled_at
                        ).toLocaleString()
                      : "-"}
                  </p>

                  <p className="mt-1">
                    <strong>Mode:</strong>{" "}
                    {application.interview.mode || "-"}
                  </p>

                  {/* Seeker confirmation */}
                  {!application.interview
                    .seeker_confirmed ? (

                    <button
                      type="button"
                      className="btn btn-primary mt-3"
                      disabled={
                        busy === application.id
                      }
                      onClick={() =>
                        confirmInterview(application)
                      }
                    >
                      {busy === application.id
                        ? "Confirming..."
                        : "Confirm interview"}
                    </button>

                  ) : (

                    <div className="mt-3 rounded-lg bg-emerald-100 p-3 font-semibold text-emerald-700">
                      Interview confirmed.
                    </div>

                  )}

                </div>
              )}

              {/* =========================
                  FEEDBACK SECTION
                  ========================= */}

              {application.feedback && (
                <div className="mt-3 rounded-lg bg-violet-50 p-4 text-sm text-violet-900">

                  <p className="font-semibold">
                    {application.feedback
                      .is_system_generated
                      ? "Automatic feedback"
                      : "Recruiter feedback"}
                  </p>

                  <p className="mt-1">
                    {application.feedback.comments ||
                      application.feedback.reason_code ||
                      "No feedback provided."}
                  </p>

                  {/* Missing skills */}
                  {application.feedback
                    .missing_skills && (
                    <p className="mt-2">
                      <strong>
                        Missing skills:
                      </strong>{" "}
                      {
                        application.feedback
                          .missing_skills
                      }
                    </p>
                  )}

                </div>
              )}

              {/* =========================
                  REJECTION REASON
                  ========================= */}

              {application.status === "rejected" &&
                !application.feedback && (
                  <div className="mt-3 rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    Your application was not selected
                    for the next stage.
                  </div>
                )}

            </div>
          ))}

        </div>
      )}

    </div>
  );
}
