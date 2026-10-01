
import { useEffect, useState } from "react";
import { api } from "../../api/client.js";

export default function Applicants() {
    const [applicants, setApplicants] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [actionLoading, setActionLoading] = useState(null);

    const [rejectingId, setRejectingId] = useState(null);
    const [rejectionReason, setRejectionReason] = useState("");

    const [interviewId, setInterviewId] = useState(null);
    const [scheduledAt, setScheduledAt] = useState("");
    const [interviewMode, setInterviewMode] = useState("online");

    const [feedbackId, setFeedbackId] = useState(null);
    const [feedbackReason, setFeedbackReason] = useState("");
    const [feedbackComments, setFeedbackComments] = useState("");
    const [missingSkills, setMissingSkills] = useState("");

    const loadApplicants = async () => {
        try {
            setLoading(true);
            setError(null);

            const response = await api.get("/recruiter/applicants/");

            setApplicants(
                Array.isArray(response.data)
                    ? response.data
                    : []
            );
        } catch (e) {
            console.error("Failed to load applicants:", e);

            setError(
                e.response?.data?.detail ||
                "Failed to load applicants."
            );

            setApplicants([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadApplicants();
    }, []);

    // -----------------------------------------
    // SHORTLIST
    // -----------------------------------------

    const handleShortlist = async (applicant) => {
        try {
            setActionLoading(applicant.id);
            setError(null);

            await api.patch(
                `/applications/${applicant.id}/decision/`,
                {
                    status: "shortlisted",
                }
            );

            await loadApplicants();
        } catch (e) {
            console.error("Failed to shortlist:", e);

            setError(
                e.response?.data?.detail ||
                e.response?.data?.status?.[0] ||
                "Failed to shortlist applicant."
            );
        } finally {
            setActionLoading(null);
        }
    };

    // -----------------------------------------
    // REJECT
    // -----------------------------------------

    const openRejectModal = (applicant) => {
        setRejectingId(applicant.id);
        setRejectionReason("");
        setError(null);
    };

    const closeRejectModal = () => {
        setRejectingId(null);
        setRejectionReason("");
    };

    const handleReject = async (applicant) => {
        if (!rejectionReason.trim()) {
            setError("Please enter a rejection reason.");
            return;
        }

        try {
            setActionLoading(applicant.id);
            setError(null);

            await api.patch(
                `/applications/${applicant.id}/decision/`,
                {
                    status: "rejected",
                    reason_code: rejectionReason.trim(),
                    comments: rejectionReason.trim(),
                }
            );

            closeRejectModal();
            await loadApplicants();
        } catch (e) {
            console.error("Failed to reject:", e);

            setError(
                e.response?.data?.detail ||
                e.response?.data?.reason_code?.[0] ||
                "Failed to reject applicant."
            );
        } finally {
            setActionLoading(null);
        }
    };

    // -----------------------------------------
    // SCHEDULE INTERVIEW
    // -----------------------------------------

    const openInterviewModal = (applicant) => {
        setInterviewId(applicant.id);
        setScheduledAt("");
        setInterviewMode("online");
        setError(null);
    };

    const closeInterviewModal = () => {
        setInterviewId(null);
        setScheduledAt("");
        setInterviewMode("online");
    };

    const handleScheduleInterview = async (applicant) => {
        if (!scheduledAt) {
            setError("Please select an interview date and time.");
            return;
        }

        try {
            setActionLoading(applicant.id);
            setError(null);

            await api.post(
                `/applications/${applicant.id}/interview/`,
                {
                    scheduled_at: scheduledAt,
                    mode: interviewMode,
                }
            );

            closeInterviewModal();
            await loadApplicants();
        } catch (e) {
            console.error("Failed to schedule interview:", e);

            setError(
                e.response?.data?.detail ||
                e.response?.data?.scheduled_at?.[0] ||
                "Failed to schedule interview."
            );
        } finally {
            setActionLoading(null);
        }
    };

    // -----------------------------------------
    // MARK INTERVIEW DONE
    // -----------------------------------------

    const handleInterviewDone = async (applicant) => {
        if (!applicant.interview?.id) {
            setError("Interview not found.");
            return;
        }

        try {
            setActionLoading(applicant.id);
            setError(null);

            await api.post(
                `/interviews/${applicant.interview.id}/done/`
            );

            await loadApplicants();
        } catch (e) {
            console.error("Failed to mark interview done:", e);

            setError(
                e.response?.data?.detail ||
                "Failed to mark interview as completed."
            );
        } finally {
            setActionLoading(null);
        }
    };

    // -----------------------------------------
    // FEEDBACK
    // -----------------------------------------

    const openFeedbackModal = (applicant) => {
        setFeedbackId(applicant.id);
        setFeedbackReason("");
        setFeedbackComments("");
        setMissingSkills("");
        setError(null);
    };

    const closeFeedbackModal = () => {
        setFeedbackId(null);
        setFeedbackReason("");
        setFeedbackComments("");
        setMissingSkills("");
    };

    const handleFeedback = async (applicant) => {
        try {
            setActionLoading(applicant.id);
            setError(null);

            const skills = missingSkills
                .split(",")
                .map((skill) => skill.trim())
                .filter(Boolean);

            await api.post(
                `/applications/${applicant.id}/feedback/`,
                {
                    reason_code: feedbackReason.trim(),
                    comments: feedbackComments.trim(),
                    missing_skills: skills,
                }
            );

            closeFeedbackModal();
            await loadApplicants();
        } catch (e) {
            console.error("Failed to submit feedback:", e);

            setError(
                e.response?.data?.detail ||
                "Failed to submit feedback."
            );
        } finally {
            setActionLoading(null);
        }
    };

    // -----------------------------------------
    // STATUS DISPLAY
    // -----------------------------------------

    const getStatusClass = (status) => {
        switch (status) {
            case "applied":
                return "bg-blue-100 text-blue-700";

            case "shortlisted":
                return "bg-green-100 text-green-700";

            case "interview_scheduled":
                return "bg-purple-100 text-purple-700";

            case "interview_completed":
                return "bg-indigo-100 text-indigo-700";

            case "feedback_given":
                return "bg-yellow-100 text-yellow-700";

            case "offered":
                return "bg-emerald-100 text-emerald-700";

            case "placed":
                return "bg-green-200 text-green-800";

            case "rejected":
                return "bg-red-100 text-red-700";

            case "withdrawn":
                return "bg-slate-100 text-slate-700";

            default:
                return "bg-slate-100 text-slate-700";
        }
    };

    const formatStatus = (status) => {
        if (!status) {
            return "-";
        }

        return status
            .replaceAll("_", " ")
            .replace(/\b\w/g, (letter) =>
                letter.toUpperCase()
            );
    };

    const formatInterviewDate = (date) => {
        if (!date) {
            return "Not scheduled";
        }

        try {
            return new Date(date).toLocaleString();
        } catch {
            return date;
        }
    };

    // -----------------------------------------
    // UI
    // -----------------------------------------

    return (
        <div className="space-y-5">

            <div>
                <h1 className="text-2xl font-bold">
                    Applicants
                </h1>

                <p className="mt-1 text-sm text-slate-500">
                    Review candidates who applied to your jobs.
                </p>
            </div>

            {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            <div className="card overflow-hidden">

                {loading ? (
                    <div className="p-6 text-sm text-slate-500">
                        Loading applicants...
                    </div>
                ) : applicants.length === 0 ? (
                    <div className="p-6 text-sm text-slate-500">
                        No applicants found.
                    </div>
                ) : (
                    <div className="overflow-x-auto">

                        <table className="w-full text-left text-sm">

                            <thead className="bg-slate-50">
                                <tr>
                                    <th className="p-3">
                                        Candidate
                                    </th>

                                    <th className="p-3">
                                        Email
                                    </th>

                                    <th className="p-3">
                                        Job
                                    </th>

                                    <th className="p-3">
                                        Status
                                    </th>

                                    <th className="p-3">
                                        ATS Score
                                    </th>

                                    <th className="p-3">
                                        Interview
                                    </th>

                                    <th className="p-3">
                                        Actions
                                    </th>
                                </tr>
                            </thead>

                            <tbody>

                                {applicants.map((applicant) => {

                                    const candidate =
                                        applicant.candidate || {};

                                    const isLoading =
                                        actionLoading === applicant.id;

                                    const status =
                                        applicant.status;

                                    return (
                                        <tr
                                            key={applicant.id}
                                            className="border-t"
                                        >

                                            {/* Candidate */}
                                            <td className="p-3">
                                                <div className="font-semibold">
                                                    {candidate.name ||
                                                        candidate.full_name ||
                                                        applicant.name ||
                                                        applicant.full_name ||
                                                        "Candidate"}
                                                </div>
                                            </td>

                                            {/* Email */}
                                            <td className="p-3">
                                                {candidate.email ||
                                                    applicant.email ||
                                                    "-"}
                                            </td>

                                            {/* Job */}
                                            <td className="p-3">
                                                {applicant.job?.title ||
                                                    applicant.job_title ||
                                                    "-"}
                                            </td>

                                            {/* Status */}
                                            <td className="p-3">
                                                <span
                                                    className={`rounded-full px-2 py-1 text-xs font-medium ${getStatusClass(
                                                        status
                                                    )}`}
                                                >
                                                    {formatStatus(status)}
                                                </span>
                                            </td>

                                            {/* ATS */}
                                            <td className="p-3 font-semibold">
                                                {applicant.match_score ??
                                                    applicant.ats_score ??
                                                    "-"}
                                            </td>

                                            {/* Interview */}
                                            <td className="p-3">

                                                {applicant.interview ? (
                                                    <div className="space-y-1">

                                                        <div className="font-medium">
                                                            {formatInterviewDate(
                                                                applicant
                                                                    .interview
                                                                    .scheduled_at
                                                            )}
                                                        </div>

                                                        <div className="text-xs text-slate-500">
                                                            Mode:{" "}
                                                            {applicant
                                                                .interview
                                                                .mode || "online"}
                                                        </div>

                                                        {applicant
                                                            .interview
                                                            .seeker_confirmed && (
                                                            <div className="text-xs text-green-600">
                                                                Candidate confirmed
                                                            </div>
                                                        )}
                                                    </div>
                                                ) : (
                                                    <span className="text-slate-500">
                                                        Not scheduled
                                                    </span>
                                                )}

                                            </td>

                                            {/* Actions */}
                                            <td className="p-3">

                                                <div className="flex flex-wrap gap-2">

                                                    {/* APPLIED */}
                                                    {status === "applied" && (
                                                        <>
                                                            <button
                                                                type="button"
                                                                className="btn btn-primary"
                                                                disabled={isLoading}
                                                                onClick={() =>
                                                                    handleShortlist(
                                                                        applicant
                                                                    )
                                                                }
                                                            >
                                                                {isLoading
                                                                    ? "Processing..."
                                                                    : "Shortlist"}
                                                            </button>

                                                            <button
                                                                type="button"
                                                                className="btn btn-outline"
                                                                disabled={isLoading}
                                                                onClick={() =>
                                                                    openRejectModal(
                                                                        applicant
                                                                    )
                                                                }
                                                            >
                                                                Reject
                                                            </button>
                                                        </>
                                                    )}

                                                    {/* SHORTLISTED */}
                                                    {status === "shortlisted" && (
                                                        <>
                                                            <button
                                                                type="button"
                                                                className="btn btn-primary"
                                                                disabled={isLoading}
                                                                onClick={() =>
                                                                    openInterviewModal(
                                                                        applicant
                                                                    )
                                                                }
                                                            >
                                                                Schedule Interview
                                                            </button>

                                                            <button
                                                                type="button"
                                                                className="btn btn-outline"
                                                                disabled={isLoading}
                                                                onClick={() =>
                                                                    openRejectModal(
                                                                        applicant
                                                                    )
                                                                }
                                                            >
                                                                Reject
                                                            </button>
                                                        </>
                                                    )}

                                                    {/* INTERVIEW SCHEDULED */}
                                                    {status ===
                                                        "interview_scheduled" &&
                                                        applicant.interview && (
                                                            <>
                                                                <button
                                                                    type="button"
                                                                    className="btn btn-primary"
                                                                    disabled={isLoading}
                                                                    onClick={() =>
                                                                        handleInterviewDone(
                                                                            applicant
                                                                        )
                                                                    }
                                                                >
                                                                    {isLoading
                                                                        ? "Processing..."
                                                                        : "Mark Interview Done"}
                                                                </button>
                                                            </>
                                                        )}

                                                    {/* INTERVIEW COMPLETED */}
                                                    {status ===
                                                        "interview_completed" && (
                                                            <button
                                                                type="button"
                                                                className="btn btn-primary"
                                                                disabled={isLoading}
                                                                onClick={() =>
                                                                    openFeedbackModal(
                                                                        applicant
                                                                    )
                                                                }
                                                            >
                                                                Give Feedback
                                                            </button>
                                                        )}

                                                    {/* FEEDBACK GIVEN */}
                                                    {status === "feedback_given" && (
                                                        <span className="text-xs text-slate-500">
                                                            Feedback submitted
                                                        </span>
                                                    )}

                                                    {/* OFFERED */}
                                                    {status === "offered" && (
                                                        <span className="text-xs text-green-600">
                                                            Offer stage
                                                        </span>
                                                    )}

                                                    {/* REJECTED */}
                                                    {status === "rejected" && (
                                                        <span className="text-xs text-red-600">
                                                            Rejected
                                                        </span>
                                                    )}

                                                </div>

                                            </td>

                                        </tr>
                                    );
                                })}

                            </tbody>

                        </table>

                    </div>
                )}

            </div>

            {/* =========================================
                REJECT MODAL
            ========================================= */}

            {rejectingId !== null && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">

                    <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

                        <h2 className="text-lg font-semibold">
                            Reject Applicant
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Please provide a reason for rejecting this applicant.
                        </p>

                        <textarea
                            className="input mt-4 min-h-28 w-full"
                            value={rejectionReason}
                            onChange={(event) =>
                                setRejectionReason(event.target.value)
                            }
                            placeholder="Example: Required Django experience is missing."
                        />

                        <div className="mt-4 flex justify-end gap-3">

                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={closeRejectModal}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={
                                    actionLoading === rejectingId
                                }
                                onClick={() => {
                                    const applicant =
                                        applicants.find(
                                            (item) =>
                                                item.id === rejectingId
                                        );

                                    if (applicant) {
                                        handleReject(applicant);
                                    }
                                }}
                            >
                                {actionLoading === rejectingId
                                    ? "Rejecting..."
                                    : "Reject Applicant"}
                            </button>

                        </div>

                    </div>

                </div>
            )}

            {/* =========================================
                INTERVIEW MODAL
            ========================================= */}

            {interviewId !== null && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">

                    <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

                        <h2 className="text-lg font-semibold">
                            Schedule Interview
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Select the interview date, time and mode.
                        </p>

                        <div className="mt-4 space-y-4">

                            <div>
                                <label className="mb-1 block text-sm font-medium">
                                    Date & Time
                                </label>

                                <input
                                    type="datetime-local"
                                    className="input w-full"
                                    value={scheduledAt}
                                    onChange={(event) =>
                                        setScheduledAt(
                                            event.target.value
                                        )
                                    }
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium">
                                    Interview Mode
                                </label>

                                <select
                                    className="input w-full"
                                    value={interviewMode}
                                    onChange={(event) =>
                                        setInterviewMode(
                                            event.target.value
                                        )
                                    }
                                >
                                    <option value="online">
                                        Online
                                    </option>

                                    <option value="offline">
                                        Offline
                                    </option>

                                    <option value="phone">
                                        Phone
                                    </option>
                                </select>
                            </div>

                        </div>

                        <div className="mt-6 flex justify-end gap-3">

                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={closeInterviewModal}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={
                                    actionLoading === interviewId
                                }
                                onClick={() => {
                                    const applicant =
                                        applicants.find(
                                            (item) =>
                                                item.id === interviewId
                                        );

                                    if (applicant) {
                                        handleScheduleInterview(
                                            applicant
                                        );
                                    }
                                }}
                            >
                                {actionLoading === interviewId
                                    ? "Scheduling..."
                                    : "Schedule Interview"}
                            </button>

                        </div>

                    </div>

                </div>
            )}

            {/* =========================================
                FEEDBACK MODAL
            ========================================= */}

            {feedbackId !== null && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">

                    <div className="w-full max-w-lg rounded-xl bg-white p-6 shadow-xl">

                        <h2 className="text-lg font-semibold">
                            Interview Feedback
                        </h2>

                        <p className="mt-1 text-sm text-slate-500">
                            Add feedback after completing the interview.
                        </p>

                        <div className="mt-4 space-y-4">

                            <div>
                                <label className="mb-1 block text-sm font-medium">
                                    Feedback / Reason
                                </label>

                                <input
                                    className="input w-full"
                                    value={feedbackReason}
                                    onChange={(event) =>
                                        setFeedbackReason(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Example: Strong technical skills"
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium">
                                    Comments
                                </label>

                                <textarea
                                    className="input min-h-28 w-full"
                                    value={feedbackComments}
                                    onChange={(event) =>
                                        setFeedbackComments(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Enter interview feedback..."
                                />
                            </div>

                            <div>
                                <label className="mb-1 block text-sm font-medium">
                                    Missing Skills
                                </label>

                                <input
                                    className="input w-full"
                                    value={missingSkills}
                                    onChange={(event) =>
                                        setMissingSkills(
                                            event.target.value
                                        )
                                    }
                                    placeholder="Example: Docker, AWS"
                                />

                                <p className="mt-1 text-xs text-slate-500">
                                    Separate multiple skills with commas.
                                </p>
                            </div>

                        </div>

                        <div className="mt-6 flex justify-end gap-3">

                            <button
                                type="button"
                                className="btn btn-outline"
                                onClick={closeFeedbackModal}
                            >
                                Cancel
                            </button>

                            <button
                                type="button"
                                className="btn btn-primary"
                                disabled={
                                    actionLoading === feedbackId
                                }
                                onClick={() => {
                                    const applicant =
                                        applicants.find(
                                            (item) =>
                                                item.id === feedbackId
                                        );

                                    if (applicant) {
                                        handleFeedback(
                                            applicant
                                        );
                                    }
                                }}
                            >
                                {actionLoading === feedbackId
                                    ? "Submitting..."
                                    : "Submit Feedback"}
                            </button>

                        </div>

                    </div>

                </div>
            )}

        </div>
    );
}
