
import { useEffect, useState } from "react";
import { api } from "../../api/client.js";

export default function Candidates() {
    const [candidates, setCandidates] = useState([]);

    const [filters, setFilters] = useState({
        skills: "",
        education: "",
        grad_year: "",
        location: "",
        ats_min: "",
        experience: "",
        campus: "",
    });

    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const loadCandidates = async (customFilters = filters) => {
        try {
            setLoading(true);
            setError(null);

            const params = new URLSearchParams();

            Object.entries(customFilters).forEach(([key, value]) => {
                if (
                    value !== undefined &&
                    value !== null &&
                    value !== ""
                ) {
                    params.append(key, value);
                }
            });

            const query = params.toString();

            // IMPORTANT:
            // Backend URL is /recruiter/candidates/search/
            const response = await api.get(
                `/recruiter/candidates/search/${
                    query ? `?${query}` : ""
                }`
            );

            /*
             * Support both:
             *
             * 1. Backend returns:
             *    [...]
             *
             * 2. Backend returns:
             *    { results: [...] }
             *
             * 3. Backend returns:
             *    { candidates: [...] }
             */
            let data = response.data;

            if (Array.isArray(data)) {
                setCandidates(data);
            } else if (Array.isArray(data?.results)) {
                setCandidates(data.results);
            } else if (Array.isArray(data?.candidates)) {
                setCandidates(data.candidates);
            } else {
                setCandidates([]);
            }
        } catch (e) {
            console.error(
                "Failed to load candidates:",
                e.response?.data || e
            );

            setError(
                e.response?.data?.detail ||
                e.response?.data?.message ||
                "Failed to load candidates."
            );

            setCandidates([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadCandidates();
    }, []);

    const handleFilterChange = (event) => {
        const { name, value } = event.target;

        setFilters((previous) => ({
            ...previous,
            [name]: value,
        }));
    };

    const handleSearch = () => {
        loadCandidates(filters);
    };

    const handleClear = () => {
        const emptyFilters = {
            skills: "",
            education: "",
            grad_year: "",
            location: "",
            ats_min: "",
            experience: "",
            campus: "",
        };

        setFilters(emptyFilters);
        loadCandidates(emptyFilters);
    };

    return (
        <div className="space-y-5">

            {/* HEADER */}
            <div>
                <h1 className="text-2xl font-bold">
                    Candidates
                </h1>

                <p className="mt-1 text-sm text-slate-500">
                    Search and review candidates for your jobs.
                </p>
            </div>

            {/* ERROR */}
            {error && (
                <div className="rounded-lg bg-red-50 p-3 text-sm text-red-700">
                    {error}
                </div>
            )}

            {/* FILTERS */}
            <div className="card p-4">

                <h2 className="mb-4 text-lg font-semibold">
                    Candidate Filters
                </h2>

                <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">

                    <input
                        className="input"
                        name="skills"
                        value={filters.skills}
                        onChange={handleFilterChange}
                        placeholder="Skills"
                    />

                    <input
                        className="input"
                        name="education"
                        value={filters.education}
                        onChange={handleFilterChange}
                        placeholder="Education"
                    />

                    <input
                        className="input"
                        name="grad_year"
                        value={filters.grad_year}
                        onChange={handleFilterChange}
                        placeholder="Graduation year"
                        type="number"
                    />

                    <input
                        className="input"
                        name="location"
                        value={filters.location}
                        onChange={handleFilterChange}
                        placeholder="Location"
                    />

                    <input
                        className="input"
                        name="ats_min"
                        value={filters.ats_min}
                        onChange={handleFilterChange}
                        placeholder="Minimum ATS score"
                        type="number"
                        min="0"
                        max="100"
                    />

                    <select
                        className="input"
                        name="experience"
                        value={filters.experience}
                        onChange={handleFilterChange}
                    >
                        <option value="">
                            Any experience
                        </option>

                        <option value="fresher">
                            Fresher
                        </option>

                        <option value="0-2">
                            0-2 years
                        </option>

                        <option value="2-5">
                            2-5 years
                        </option>
                    </select>

                    <input
                        className="input"
                        name="campus"
                        value={filters.campus}
                        onChange={handleFilterChange}
                        placeholder="Campus"
                    />

                </div>

                <div className="mt-4 flex gap-3">

                    <button
                        type="button"
                        className="btn btn-primary"
                        onClick={handleSearch}
                        disabled={loading}
                    >
                        {loading ? "Searching..." : "Search"}
                    </button>

                    <button
                        type="button"
                        className="btn btn-outline"
                        onClick={handleClear}
                        disabled={loading}
                    >
                        Clear
                    </button>

                </div>
            </div>

            {/* CANDIDATES TABLE */}
            <div className="card overflow-hidden">

                <div className="border-b p-4">
                    <h2 className="font-semibold">
                        Candidates
                    </h2>
                </div>

                {loading ? (

                    <div className="p-6 text-sm text-slate-500">
                        Loading candidates...
                    </div>

                ) : candidates.length === 0 ? (

                    <div className="p-6 text-sm text-slate-500">
                        No candidates found.
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
                                        Education
                                    </th>

                                    <th className="p-3">
                                        Experience
                                    </th>

                                    <th className="p-3">
                                        Location
                                    </th>

                                    <th className="p-3">
                                        ATS
                                    </th>

                                    <th className="p-3">
                                        Skills
                                    </th>

                                </tr>

                            </thead>

                            <tbody>

                                {candidates.map((candidate) => (

                                    <tr
                                        key={candidate.id}
                                        className="border-t"
                                    >

                                        {/* CANDIDATE */}
                                        <td className="p-3">

                                            <div className="font-semibold">

                                                {candidate.name ||
                                                    candidate.full_name ||
                                                    candidate.candidate?.name ||
                                                    candidate.candidate?.full_name ||
                                                    "Candidate"}

                                            </div>

                                            {(candidate.email ||
                                                candidate.candidate?.email) && (

                                                <div className="text-xs text-slate-500">

                                                    {candidate.email ||
                                                        candidate.candidate?.email}

                                                </div>

                                            )}

                                        </td>

                                        {/* EDUCATION */}
                                        <td className="p-3">

                                            {candidate.education ||
                                                candidate.degree ||
                                                candidate.candidate?.education ||
                                                "-"}

                                        </td>

                                        {/* EXPERIENCE */}
                                        <td className="p-3">

                                            {candidate.experience_level ||
                                                candidate.experience ||
                                                candidate.candidate?.experience_level ||
                                                "-"}

                                        </td>

                                        {/* LOCATION */}
                                        <td className="p-3">

                                            {candidate.location ||
                                                candidate.candidate?.location ||
                                                "-"}

                                        </td>

                                        {/* ATS */}
                                        <td className="p-3">

                                            {candidate.ats_score ??
                                                candidate.match_score ??
                                                candidate.candidate?.ats_score ??
                                                "-"}

                                        </td>

                                        {/* SKILLS */}
                                        <td className="p-3">

                                            {Array.isArray(candidate.skills)
                                                ? candidate.skills.join(", ")
                                                : candidate.skills ||
                                                  candidate.candidate?.skills ||
                                                  "-"}

                                        </td>

                                    </tr>

                                ))}

                            </tbody>

                        </table>

                    </div>

                )}

            </div>

        </div>
    );
}
