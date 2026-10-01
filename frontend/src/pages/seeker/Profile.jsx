import { useEffect, useState } from 'react';

import { api } from '../../api/client.js';
import { useAuth } from '../../context/AuthContext.jsx';

import { Alert, Spinner } from '../../components/ui.jsx';
import { EXP_LEVELS, errMsg } from '../../utils.js';

export default function Profile() {
  const { refreshUser } = useAuth();

  const [form, setForm] = useState(null);
  const [skillOptions, setSkillOptions] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [message, setMessage] = useState(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .get('/seeker/profile/')
      .then((res) => setForm(res.data))
      .catch((err) =>
        setMessage({
          ok: false,
          text: errMsg(err),
        })
      );

    api
      .get('/jobs/skills/')
      .then((res) => setSkillOptions(res.data))
      .catch(() => {});
  }, []);

  if (!form) {
    return message ? (
      <Alert>{message.text}</Alert>
    ) : (
      <Spinner />
    );
  }

  const set = (key) => (e) => {
    setForm({
      ...form,
      [key]: e.target.value,
    });
  };

  const addSkill = () => {
    const name = newSkill.trim();

    if (!name) return;

    const alreadyExists = form.skills.some(
      (s) => s.toLowerCase() === name.toLowerCase()
    );

    if (!alreadyExists) {
      setForm({
        ...form,
        skills: [...form.skills, name],
      });
    }

    setNewSkill('');
  };

  const removeSkill = (skillToRemove) => {
    setForm({
      ...form,
      skills: form.skills.filter((skill) => skill !== skillToRemove),
    });
  };

  const save = async (e) => {
    e.preventDefault();

    setBusy(true);
    setMessage(null);

    try {
      const payload = {
        full_name: form.full_name,
        phone: form.phone,
        location: form.location,
        education: form.education,
        grad_year: form.grad_year === null ? '' : form.grad_year,
        experience_level: form.experience_level,
        open_to_relocate: form.open_to_relocate,
        skills: form.skills,
      };

      const { data } = await api.patch(
        '/seeker/profile/',
        payload
      );

      setForm(data);

      // Refresh the logged-in user stored in AuthContext/localStorage.
      // This makes the Navbar name change immediately.
      await refreshUser();

      const ignored =
        data.ignored_skills && data.ignored_skills.length
          ? ` Skills not in our list were skipped: ${data.ignored_skills.join(
              ', '
            )}.`
          : '';

      setMessage({
        ok: true,
        text: `Profile saved.${ignored}`,
      });
    } catch (err) {
      setMessage({
        ok: false,
        text: errMsg(err),
      });
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-900">
          Your profile
        </h1>

        <p className="text-sm text-slate-500">
          {form.has_active_resume
            ? 'Filled from your resume. Check and correct anything that looks wrong.'
            : 'Upload a resume to fill this automatically.'}
        </p>
      </div>

      {message && (
        <Alert kind={message.ok ? 'success' : 'error'}>
          {message.text}
        </Alert>
      )}

      <form onSubmit={save} className="card space-y-5 p-6">
        <div className="grid gap-4 md:grid-cols-2">
          <div>
            <label className="label" htmlFor="p-name">
              Full name
            </label>

            <input
              id="p-name"
              className="input"
              value={form.full_name || ''}
              onChange={set('full_name')}
            />
          </div>

          <div>
            <label className="label" htmlFor="p-email">
              Email
            </label>

            <input
              id="p-email"
              className="input bg-slate-50"
              value={form.email || ''}
              disabled
            />
          </div>

          <div>
            <label className="label" htmlFor="p-phone">
              Phone
            </label>

            <input
              id="p-phone"
              className="input"
              value={form.phone || ''}
              onChange={set('phone')}
            />
          </div>

          <div>
            <label className="label" htmlFor="p-loc">
              City
            </label>

            <input
              id="p-loc"
              className="input"
              placeholder="Hyderabad"
              value={form.location || ''}
              onChange={set('location')}
            />
          </div>

          <div className="md:col-span-2">
            <label className="label" htmlFor="p-edu">
              Education
            </label>

            <input
              id="p-edu"
              className="input"
              placeholder="B.Tech in Computer Science"
              value={form.education || ''}
              onChange={set('education')}
            />
          </div>

          <div>
            <label className="label" htmlFor="p-year">
              Graduation year
            </label>

            <input
              id="p-year"
              type="number"
              className="input"
              value={form.grad_year || ''}
              onChange={(e) =>
                setForm({
                  ...form,
                  grad_year:
                    e.target.value === ''
                      ? null
                      : e.target.value,
                })
              }
            />
          </div>

          <div>
            <label className="label" htmlFor="p-exp">
              Experience level
            </label>

            <select
              id="p-exp"
              className="input"
              value={form.experience_level || ''}
              onChange={set('experience_level')}
            >
              {Object.entries(EXP_LEVELS).map(([key, value]) => (
                <option key={key} value={key}>
                  {value}
                </option>
              ))}
            </select>
          </div>
        </div>

        <label className="flex items-center gap-2 text-sm text-slate-700">
          <input
            type="checkbox"
            checked={Boolean(form.open_to_relocate)}
            onChange={(e) =>
              setForm({
                ...form,
                open_to_relocate: e.target.checked,
              })
            }
          />

          I am open to relocate (improves your location score for other
          cities)
        </label>

        <div>
          <label className="label" htmlFor="p-skill">
            Skills
          </label>

          <div className="flex flex-wrap gap-2">
            {form.skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center gap-1 rounded-md bg-indigo-50 px-2.5 py-1 text-xs font-medium text-indigo-700"
              >
                {skill}

                <button
                  type="button"
                  aria-label={`Remove ${skill}`}
                  className="text-indigo-400 hover:text-red-600"
                  onClick={() => removeSkill(skill)}
                >
                  &times;
                </button>
              </span>
            ))}

            {form.skills.length === 0 && (
              <span className="text-sm text-slate-500">
                No skills yet.
              </span>
            )}
          </div>

          <div className="mt-3 flex gap-2">
            <input
              id="p-skill"
              list="profile-skills"
              className="input"
              placeholder="Add a skill"
              value={newSkill}
              onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter') {
                  e.preventDefault();
                  addSkill();
                }
              }}
            />

            <datalist id="profile-skills">
              {skillOptions.map((skill) => (
                <option key={skill} value={skill} />
              ))}
            </datalist>

            <button
              type="button"
              className="btn btn-outline"
              onClick={addSkill}
            >
              Add
            </button>
          </div>
        </div>

        <div className="flex justify-end">
          <button
            className="btn btn-primary"
            disabled={busy}
          >
            {busy ? 'Saving...' : 'Save profile'}
          </button>
        </div>
      </form>
    </div>
  );
}