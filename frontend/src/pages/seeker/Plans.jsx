
import { useEffect, useState } from "react";
import { QRCodeSVG } from "qrcode.react";

import { api } from "../../api/client.js";
import {
    Alert,
    EmptyState,
    Spinner,
} from "../../components/ui.jsx";
import { errMsg } from "../../utils.js";

function loadRazorpayScript() {
    return new Promise((resolve) => {
        if (window.Razorpay) {
            resolve(true);
            return;
        }

        const script = document.createElement("script");

        script.src =
            "https://checkout.razorpay.com/v1/checkout.js";

        script.onload = () => resolve(true);
        script.onerror = () => resolve(false);

        document.body.appendChild(script);
    });
}

// Change this to your real UPI ID if required.
const UPI_ID = "9392524229@ybl";

export default function Plans() {
    const [plans, setPlans] = useState([]);
    const [current, setCurrent] = useState(null);

    const [loading, setLoading] = useState(true);
    const [busyId, setBusyId] = useState(null);

    const [error, setError] = useState(null);
    const [message, setMessage] = useState(null);

    const [upiPlan, setUpiPlan] = useState(null);

    // ---------------------------------------------------------
    // LOAD PLANS + CURRENT SUBSCRIPTION
    // ---------------------------------------------------------

    const load = async () => {
        setLoading(true);
        setError(null);

        try {
            const [plansResponse, currentResponse] =
                await Promise.all([
                    api.get("/billing/plans/"),
                    api.get("/billing/current/"),
                ]);

            setPlans(
                Array.isArray(plansResponse.data)
                    ? plansResponse.data
                    : []
            );

            setCurrent(currentResponse.data);
        } catch (e) {
            console.error("Failed to load billing data:", e);
            setError(errMsg(e));
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        load();
    }, []);

    // ---------------------------------------------------------
    // FREE PLAN
    // ---------------------------------------------------------

    const activateFree = async (planId) => {
        setBusyId(planId);
        setMessage(null);

        try {
            const { data } = await api.post(
                "/billing/activate/",
                {
                    plan_id: planId,
                }
            );

            // Immediately update current plan in UI.
            setCurrent(data);

            setMessage({
                ok: true,
                text: `Activated ${data.plan}.`,
            });
        } catch (e) {
            console.error("Free plan activation failed:", e);

            setMessage({
                ok: false,
                text: errMsg(e),
            });
        } finally {
            setBusyId(null);
        }
    };

    // ---------------------------------------------------------
    // RAZORPAY PAYMENT
    // ---------------------------------------------------------

    const payWithRazorpay = async (plan) => {
        setBusyId(plan.id);
        setMessage(null);

        try {
            // Safety check for free plan.
            if (Number(plan.price) <= 0) {
                await activateFree(plan.id);
                return;
            }

            // Load Razorpay checkout script.
            const loaded = await loadRazorpayScript();

            if (!loaded) {
                throw new Error(
                    "Razorpay checkout could not be loaded."
                );
            }

            // IMPORTANT:
            // This matches your Django URL:
            //
            // path(
            //     "razorpay/create-order/",
            //     CreateRazorpayOrderView.as_view(),
            // )
            //
            const { data: order } = await api.post(
                "/billing/razorpay/create-order/",
                {
                    plan_id: plan.id,
                }
            );

            // Create Razorpay checkout.
            const razorpay = new window.Razorpay({
                key: order.key_id,

                amount: order.amount,

                currency: order.currency,

                name: "FresherHire",

                description:
                    `${order.plan_name} candidate plan`,

                order_id: order.order_id,

                handler: async (response) => {
                    try {
                        // Verify payment on Django backend.
                        const { data } = await api.post(
                            "/billing/razorpay/verify/",
                            {
                                plan_id: plan.id,

                                razorpay_order_id:
                                    response.razorpay_order_id,

                                razorpay_payment_id:
                                    response.razorpay_payment_id,

                                razorpay_signature:
                                    response.razorpay_signature,
                            }
                        );

                        // IMPORTANT:
                        // Backend has now activated the subscription.
                        // Updating current makes the UI unlock immediately.
                        setCurrent(data);

                        setMessage({
                            ok: true,
                            text:
                                `Payment verified. ${data.plan} is now active.`,
                        });
                    } catch (e) {
                        console.error(
                            "Razorpay verification failed:",
                            e
                        );

                        setMessage({
                            ok: false,
                            text: errMsg(e),
                        });
                    } finally {
                        setBusyId(null);
                    }
                },

                modal: {
                    ondismiss: () => {
                        setBusyId(null);
                    },
                },
            });

            razorpay.on(
                "payment.failed",
                (response) => {
                    setMessage({
                        ok: false,
                        text:
                            response.error?.description ||
                            "Payment failed.",
                    });

                    setBusyId(null);
                }
            );

            razorpay.open();
        } catch (e) {
            console.error(
                "Razorpay payment error:",
                e
            );

            setMessage({
                ok: false,
                text: errMsg(e),
            });

            setBusyId(null);
        }
    };

    // ---------------------------------------------------------
    // UPI QR
    // ---------------------------------------------------------

    const openUPIPayment = (plan) => {
        setMessage(null);
        setUpiPlan(plan);
    };

    const getUPILink = (plan) => {
        const amount = Number(plan.price).toFixed(2);

        return (
            `upi://pay?pa=${encodeURIComponent(UPI_ID)}` +
            `&pn=${encodeURIComponent("FresherHire")}` +
            `&am=${amount}` +
            `&cu=INR`
        );
    };

    const closeUPIPopup = () => {
        setUpiPlan(null);
    };

    // ---------------------------------------------------------
    // LOADING
    // ---------------------------------------------------------

    if (loading) {
        return <Spinner label="Loading plans..." />;
    }

    // ---------------------------------------------------------
    // ERROR
    // ---------------------------------------------------------

    if (error) {
        return (
            <div className="space-y-4">
                <Alert>{error}</Alert>

                <button
                    className="btn btn-outline"
                    onClick={load}
                >
                    Retry
                </button>
            </div>
        );
    }

    // ---------------------------------------------------------
    // CHECK CURRENT PLAN
    // ---------------------------------------------------------

    const currentPlanName =
        current?.plan || "Free";

    const isFree =
        currentPlanName === "Free";

    // ---------------------------------------------------------
    // UI
    // ---------------------------------------------------------

    return (
        <>
            <div className="space-y-5">

                {/* HEADER */}

                <div>
                    <h1 className="text-2xl font-bold">
                        Candidate Plans
                    </h1>

                    <p className="text-sm text-slate-500">
                        Choose a plan to unlock additional
                        career and job application features.
                    </p>
                </div>

                {/* CURRENT PLAN */}

                {current && (
                    <div
                        className={
                            isFree
                                ? "card p-4"
                                : "card border-2 border-emerald-500 bg-emerald-50 p-4"
                        }
                    >
                        <div className="flex flex-wrap items-center justify-between gap-3">

                            <div>
                                <p className="text-sm text-slate-500">
                                    Current plan
                                </p>

                                <p className="text-xl font-bold text-slate-900">
                                    {currentPlanName}
                                </p>
                            </div>

                            {!isFree && (
                                <span className="rounded-full bg-emerald-100 px-3 py-1 text-sm font-semibold text-emerald-700">
                                    ✓ Active
                                </span>
                            )}
                        </div>

                        {!isFree && (
                            <div className="mt-3 text-sm text-emerald-700">
                                Your paid features are unlocked.
                            </div>
                        )}
                    </div>
                )}

                {/* MESSAGE */}

                {message && (
                    <Alert
                        kind={
                            message.ok
                                ? "success"
                                : "error"
                        }
                    >
                        {message.text}
                    </Alert>
                )}

                {/* PLANS */}

                {plans.length === 0 ? (
                    <EmptyState
                        title="No plans available"
                        text="No candidate plans are currently available."
                    />
                ) : (
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

                        {plans.map((plan) => {

                            const planIsCurrent =
                                currentPlanName === plan.name;

                            return (
                                <div
                                    className={
                                        planIsCurrent
                                            ? "card border-2 border-emerald-500 p-5"
                                            : "card p-5"
                                    }
                                    key={plan.id}
                                >

                                    {/* PLAN NAME */}

                                    <div className="flex items-center justify-between gap-2">

                                        <h2 className="text-lg font-bold">
                                            {plan.name}
                                        </h2>

                                        {planIsCurrent && (
                                            <span className="rounded-full bg-emerald-100 px-2 py-1 text-xs font-semibold text-emerald-700">
                                                Current
                                            </span>
                                        )}

                                    </div>

                                    {/* PRICE */}

                                    <p className="my-3 text-2xl font-bold">
                                        ₹
                                        {Number(
                                            plan.price
                                        ).toLocaleString(
                                            "en-IN"
                                        )}
                                    </p>

                                    {/* FEATURES */}

                                    <div className="space-y-2 text-sm">

                                        <p>
                                            ✓ Up to{" "}
                                            <b>
                                                {
                                                    plan.application_limit
                                                }
                                            </b>{" "}
                                            applications
                                        </p>

                                        <p>
                                            {plan.profile_boost
                                                ? "✓ Profile boost"
                                                : "✗ Profile boost"}
                                        </p>

                                        <p>
                                            {plan.priority_applications
                                                ? "✓ Priority applications"
                                                : "✗ Priority applications"}
                                        </p>

                                        <p>
                                            {plan.resume_review
                                                ? "✓ Resume review"
                                                : "✗ Resume review"}
                                        </p>

                                        {/* EXTRA FEATURES */}

                                        {plan.features_json &&
                                            Object.entries(
                                                plan.features_json
                                            ).map(
                                                (
                                                    [
                                                        key,
                                                        value,
                                                    ]
                                                ) => (
                                                    <p
                                                        key={
                                                            key
                                                        }
                                                    >
                                                        ✓{" "}
                                                        {
                                                            key
                                                        }
                                                        :{" "}
                                                        {String(
                                                            value
                                                        )}
                                                    </p>
                                                )
                                            )}

                                    </div>

                                    {/* PAYMENT BUTTONS */}

                                    {planIsCurrent ? (
                                        <div className="mt-5 rounded-lg bg-emerald-50 p-3 text-center text-sm font-semibold text-emerald-700">
                                            ✓ This plan is active
                                        </div>
                                    ) : Number(plan.price) > 0 ? (
                                        <>
                                            {/* RAZORPAY */}

                                            <button
                                                className="btn btn-primary mt-5 w-full"
                                                disabled={
                                                    busyId ===
                                                    plan.id
                                                }
                                                onClick={() =>
                                                    payWithRazorpay(
                                                        plan
                                                    )
                                                }
                                            >
                                                {busyId ===
                                                plan.id
                                                    ? "Processing..."
                                                    : `Pay ₹${Number(
                                                        plan.price
                                                    ).toLocaleString(
                                                        "en-IN"
                                                    )}`}
                                            </button>

                                            {/* UPI */}

                                            <button
                                                className="btn btn-outline mt-2 w-full"
                                                onClick={() =>
                                                    openUPIPayment(
                                                        plan
                                                    )
                                                }
                                            >
                                                Pay via UPI / Scan QR
                                            </button>
                                        </>
                                    ) : (
                                        /* FREE PLAN */

                                        <button
                                            className="btn btn-primary mt-5 w-full"
                                            disabled={
                                                busyId ===
                                                plan.id
                                            }
                                            onClick={() =>
                                                activateFree(
                                                    plan.id
                                                )
                                            }
                                        >
                                            {busyId ===
                                            plan.id
                                                ? "Activating..."
                                                : "Activate Free Plan"}
                                        </button>
                                    )}

                                </div>
                            );
                        })}

                    </div>
                )}
            </div>

            {/* UPI QR POPUP */}

            {upiPlan && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">

                    <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

                        {/* HEADER */}

                        <div className="flex items-center justify-between">

                            <h2 className="text-xl font-bold">
                                UPI Payment
                            </h2>

                            <button
                                type="button"
                                className="text-2xl text-slate-500"
                                onClick={
                                    closeUPIPopup
                                }
                            >
                                ×
                            </button>

                        </div>

                        {/* PLAN DETAILS */}

                        <div className="mt-4 rounded-lg bg-slate-50 p-4">

                            <p className="text-sm text-slate-500">
                                Selected plan
                            </p>

                            <p className="text-lg font-bold">
                                {upiPlan.name}
                            </p>

                            <p className="mt-1 text-xl font-bold">
                                ₹
                                {Number(
                                    upiPlan.price
                                ).toLocaleString(
                                    "en-IN"
                                )}
                            </p>

                        </div>

                        {/* QR CODE */}

                        <div className="mt-6 flex justify-center">

                            <div className="rounded-lg border bg-white p-4">

                                <QRCodeSVG
                                    value={getUPILink(
                                        upiPlan
                                    )}
                                    size={256}
                                    level="M"
                                    includeMargin={true}
                                />

                            </div>

                        </div>

                        {/* INSTRUCTIONS */}

                        <p className="mt-4 text-center text-sm text-slate-600">
                            Scan this QR using PhonePe,
                            Google Pay, Paytm, BHIM or
                            another supported UPI app.
                        </p>

                        <p className="mt-2 text-center text-xs text-slate-500">
                            Payment amount:
                            {" ₹"}
                            {Number(
                                upiPlan.price
                            ).toLocaleString(
                                "en-IN"
                            )}
                        </p>

                        {/* OPEN UPI */}

                        <a
                            href={getUPILink(
                                upiPlan
                            )}
                            className="btn btn-primary mt-5 block w-full text-center"
                        >
                            Open UPI Payment
                        </a>

                        {/* DEMO CONFIRMATION */}

                        <button
                            type="button"
                            className="btn btn-outline mt-2 w-full"
                            onClick={() => {
                                setUpiPlan(null);

                                setMessage({
                                    ok: true,
                                    text:
                                        "UPI payment submitted for verification.",
                                });
                            }}
                        >
                            I Have Paid
                        </button>

                        {/* CANCEL */}

                        <button
                            type="button"
                            className="mt-2 w-full text-sm text-slate-500"
                            onClick={
                                closeUPIPopup
                            }
                        >
                            Cancel
                        </button>

                    </div>
                </div>
            )}
        </>
    );
}
