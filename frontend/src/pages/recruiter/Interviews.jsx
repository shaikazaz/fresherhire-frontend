
import { useEffect, useState } from "react";

import { api } from "../../api/client.js";

export default function Interviews() {
    const [a, setA] = useState([]);
    const [d, setD] = useState({});
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);

    const load = async () => {
        try {
            setLoading(true);
            setError(null);

            const r = await api.get("/recruiter/applicants/");

            const interviews = Array.isArray(r.data)
                ? r.data.filter((x) =>
                      [
                          "shortlisted",
                          "interview_scheduled",
                          "interview_completed",
                      ].includes(x.status)
                  )
                : [];

            setA(interviews);
        } catch (e) {
            console.error("Failed to load interviews:", e);

            setError(
                e.response?.data?.detail ||
                    "Failed to load interviews."
            );
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    const schedule = async (id) => {
        try {
            setError(null);

            if (!d[id]) {
                setError(
                    "Please select interview date and time."
                );
                return;
            }

            await api.post(
                `/applications/${id}/interview/`,
                {
                    scheduled_at: d[id],
                    mode: "online",
                }
            );

            setD((previous) => ({
                ...previous,
                [id]: "",
            }));

            await load();
        } catch (e) {
            console.error(
                "Could not schedule interview:",
                e
            );

            setError(
                e.response?.data?.detail ||
                    "Could not schedule interview."
            );
        }
    };

    const done = async (interviewId) => {
        try {
            setError(null);

            await api.post(
                `/interviews/${interviewId}/done/`
            );

            await load();
        } catch (e) {
            console.error(
                "Could not mark interview done:",
                e
            );

            setError(
                e.response?.data?.detail ||
                    "Could not mark interview done."
            );
        }
    };

    return (
        <div className="space-y-5">
            <div>
                <h1 className="text-2xl font-bold">
                    Interviews
                </h1>

                <p className="mt-1 text-sm text-slate-500">
                    Schedule and manage candidate interviews.
                </p>
            </div>

            {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="card p-6 text-sm text-slate-500">
                    Loading interviews...
                </div>
            ) : a.length === 0 ? (
                <div className="card p-6 text-sm text-slate-500">
                    No interviews yet.
                </div>
            ) : (
                <div className="space-y-4">
                    {a.map((x) => (
                        <div
                            className="card p-4"
                            key={x.id}
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div>
                                    <h2 className="font-semibold">
                                        {x.candidate?.name ||
                                            x.candidate?.full_name ||
                                            "Candidate"}
                                    </h2>

                                    <p className="text-sm text-slate-500">
                                        {x.candidate?.email ||
                                            "-"}
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Job:</strong>{" "}
                                        {x.job?.title ||
                                            "Job"}
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Status:</strong>{" "}
                                        {x.status}
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Match Score:</strong>{" "}
                                        {x.match_score ?? "-"}
                                    </p>
                                </div>
                            </div>

                            {/* Scheduled interview */}
                            {x.interview?.scheduled_at ? (
                                <div className="mt-4 rounded-lg bg-slate-50 p-4">
                                    <p className="font-semibold">
                                        Interview Scheduled
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Date & Time:</strong>{" "}
                                        {new Date(
                                            x.interview.scheduled_at
                                        ).toLocaleString()}
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Mode:</strong>{" "}
                                        {x.interview.mode}
                                    </p>

                                    <p className="mt-1 text-sm">
                                        <strong>Seeker Confirmation:</strong>{" "}
                                        {x.interview.seeker_confirmed
                                            ? "Confirmed"
                                            : "Waiting for confirmation"}
                                    </p>

                                    {!x.interview
                                        .recruiter_marked_done && (
                                        <button
                                            type="button"
                                            className="btn btn-outline mt-3"
                                            onClick={() =>
                                                done(
                                                    x.interview.id
                                                )
                                            }
                                        >
                                            Mark Interview Done
                                        </button>
                                    )}

                                    {x.interview
                                        .recruiter_marked_done && (
                                        <p className="mt-3 text-sm font-semibold text-emerald-700">
                                            Interview completed
                                        </p>
                                    )}
                                </div>
                            ) : (
                                /* Schedule interview */
                                <div className="mt-4 rounded-lg border p-4">
                                    <p className="font-semibold">
                                        Schedule Interview
                                    </p>

                                    <p className="mt-1 text-sm text-slate-500">
                                        Select a date and time for
                                        this candidate.
                                    </p>

                                    <input
                                        className="input mt-3"
                                        type="datetime-local"
                                        value={d[x.id] || ""}
                                        onChange={(e) =>
                                            setD(
                                                (
                                                    previous
                                                ) => ({
                                                    ...previous,
                                                    [x.id]:
                                                        e
                                                            .target
                                                            .value,
                                                })
                                            )
                                        }
                                    />

                                    <div className="mt-3">
                                        <button
                                            type="button"
                                            className="btn btn-primary"
                                            onClick={() =>
                                                schedule(x.id)
                                            }
                                        >
                                            Schedule Interview
                                        </button>
                                    </div>
                                </div>
                            )}

                            {/* Seeker confirmation */}
                            {x.interview
                                ?.seeker_confirmed && (
                                <div className="mt-3 rounded-lg bg-emerald-50 p-3 text-sm font-semibold text-emerald-700">
                                    Seeker confirmed the
                                    interview.
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
