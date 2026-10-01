import { useEffect, useState } from 'react';
import { QRCodeSVG } from 'qrcode.react';
import { api } from '../../api/client.js';
import { Alert, EmptyState, Spinner } from '../../components/ui.jsx';
import { errMsg } from '../../utils.js';

function loadRazorpayScript() {
  return new Promise((resolve) => {
    if (window.Razorpay) {
      resolve(true);
      return;
    }

    const script = document.createElement('script');
    script.src = 'https://checkout.razorpay.com/v1/checkout.js';

    script.onload = () => resolve(true);
    script.onerror = () => resolve(false);

    document.body.appendChild(script);
  });
}

export default function Plans() {
  const [plans, setPlans] = useState([]);
  const [current, setCurrent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState(null);
  const [error, setError] = useState(null);
  const [message, setMessage] = useState(null);
  const [upiPlan, setUpiPlan] = useState(null);

  const UPI_ID = '9392524229@ybl';

  const load = async () => {
    setLoading(true);
    setError(null);

    try {
      const [plansResponse, currentResponse] = await Promise.all([
        api.get('/billing/plans/'),
        api.get('/billing/current/'),
      ]);

      setPlans(plansResponse.data);
      setCurrent(currentResponse.data);
    } catch (e) {
      setError(errMsg(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
  }, []);

  const activateFree = async (id) => {
    try {
      const { data } = await api.post('/billing/activate/', {
        plan_id: id,
      });

      setCurrent(data);

      setMessage({
        ok: true,
        text: `Activated ${data.plan}.`,
      });
    } catch (e) {
      setMessage({
        ok: false,
        text: errMsg(e),
      });
    }
  };

  const payWithRazorpay = async (plan) => {
    setBusyId(plan.id);
    setMessage(null);

    try {
      if (Number(plan.price) <= 0) {
        await activateFree(plan.id);
        setBusyId(null);
        return;
      }

      const loaded = await loadRazorpayScript();

      if (!loaded) {
        throw new Error('Razorpay checkout could not be loaded.');
      }

      const { data: order } = await api.post(
        '/billing/razorpay/order/',
        {
          plan_id: plan.id,
        }
      );

      const razorpay = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: 'FresherHire',
        description: `${order.plan_name} plan`,
        order_id: order.order_id,

        handler: async (response) => {
          try {
            const { data } = await api.post(
              '/billing/razorpay/verify/',
              {
                plan_id: plan.id,
                razorpay_order_id: response.razorpay_order_id,
                razorpay_payment_id: response.razorpay_payment_id,
                razorpay_signature: response.razorpay_signature,
              }
            );

            setCurrent(data);

            setMessage({
              ok: true,
              text: `Payment verified. ${data.plan} is active.`,
            });
          } catch (e) {
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

      razorpay.on('payment.failed', (response) => {
        setMessage({
          ok: false,
          text:
            response.error?.description ||
            'Payment failed.',
        });

        setBusyId(null);
      });

      razorpay.open();
    } catch (e) {
      setMessage({
        ok: false,
        text: errMsg(e),
      });

      setBusyId(null);
    }
  };

  const openUPIPayment = (plan) => {
    setMessage(null);
    setUpiPlan(plan);
  };

  const getUPILink = (plan) => {
    const amount = Number(plan.price).toFixed(2);

    return (
      `upi://pay?pa=${encodeURIComponent(UPI_ID)}` +
      `&pn=${encodeURIComponent('FresherHire')}` +
      `&am=${amount}` +
      `&cu=INR`
    );
  };

  const closeUPIPopup = () => {
    setUpiPlan(null);
  };

  if (loading) {
    return <Spinner label="Loading plans..." />;
  }

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

  return (
    <>
      <div className="space-y-5">

        <div>
          <h1 className="text-2xl font-bold">
            Membership Plans
          </h1>

          <p className="text-sm text-slate-500">
            Choose a plan that suits you.
          </p>
        </div>

        {current && (
          <div className="card p-4">
            Current plan:{' '}
            <b>{current.plan}</b>
          </div>
        )}

        {message && (
          <Alert kind={message.ok ? 'success' : 'error'}>
            {message.text}
          </Alert>
        )}

        {plans.length === 0 ? (
          <EmptyState
            title="No plans available"
            text="No membership plans are currently available."
          />
        ) : (
          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

            {plans.map((plan) => (
              <div
                className="card p-5"
                key={plan.id}
              >
                <h2 className="font-bold">
                  {plan.name}
                </h2>

                <p className="my-3 text-2xl font-bold">
                  ₹{Number(plan.price).toLocaleString('en-IN')}
                </p>

                {plan.features && (
                  <div className="mt-3 text-sm text-slate-600">
                    {Object.entries(plan.features).map(
                      ([key, value]) => (
                        <p key={key}>
                          ✓ {key}: {String(value)}
                        </p>
                      )
                    )}
                  </div>
                )}

                {Number(plan.price) > 0 ? (
                  <>
                    <button
                      className="btn btn-primary mt-4 w-full"
                      disabled={busyId === plan.id}
                      onClick={() => payWithRazorpay(plan)}
                    >
                      {busyId === plan.id
                        ? 'Processing...'
                        : 'Pay with Razorpay'}
                    </button>

                    <button
                      className="btn btn-outline mt-2 w-full"
                      onClick={() => openUPIPayment(plan)}
                    >
                      Pay via UPI / Scan QR
                    </button>
                  </>
                ) : (
                  <button
                    className="btn btn-primary mt-4 w-full"
                    onClick={() => activateFree(plan.id)}
                  >
                    Activate Free Plan
                  </button>
                )}
              </div>
            ))}

          </div>
        )}
      </div>

      {upiPlan && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">

          <div className="w-full max-w-md rounded-xl bg-white p-6 shadow-xl">

            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold">
                UPI Payment
              </h2>

              <button
                type="button"
                className="text-2xl text-slate-500"
                onClick={closeUPIPopup}
              >
                ×
              </button>
            </div>

            <div className="mt-4 rounded-lg bg-slate-50 p-4">
              <p className="text-sm text-slate-500">
                Selected plan
              </p>

              <p className="text-lg font-bold">
                {upiPlan.name}
              </p>

              <p className="mt-1 text-xl font-bold">
                ₹{Number(upiPlan.price).toLocaleString('en-IN')}
              </p>
            </div>

            <div className="mt-6 flex justify-center">
              <div className="rounded-lg border bg-white p-4">
                <QRCodeSVG
                  value={getUPILink(upiPlan)}
                  size={256}
                  level="M"
                  includeMargin
                />
              </div>
            </div>

            <p className="mt-4 text-center text-sm text-slate-600">
              Scan this QR using PhonePe, Google Pay,
              Paytm, BHIM or another UPI app.
            </p>

            <p className="mt-2 text-center text-xs text-slate-500">
              Amount: ₹
              {Number(upiPlan.price).toLocaleString('en-IN')}
            </p>

            <a
              href={getUPILink(upiPlan)}
              className="btn btn-primary mt-5 block w-full text-center"
            >
              Open UPI Payment
            </a>

            <button
              type="button"
              className="btn btn-outline mt-2 w-full"
              onClick={closeUPIPopup}
            >
              Close
            </button>

          </div>
        </div>
      )}
    </>
  );
}