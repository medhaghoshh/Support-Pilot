import { useState } from "react";
import { Loader2, CheckCircle2, AlertCircle } from "lucide-react";

const DEPARTMENTS = ["IT", "HR", "Finance", "Operations", "Engineering", "Other"];
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const initialValues = { title: "", description: "", requesterEmail: "", department: "" };

function validate(values) {
  const errors = {};
  if (!values.title.trim()) errors.title = "Ticket title is required.";
  else if (values.title.trim().length < 5) errors.title = "Title must be at least 5 characters.";

  if (!values.description.trim()) errors.description = "Description is required.";
  else if (values.description.trim().length < 20)
    errors.description = "Add a bit more detail (min 20 characters).";

  if (!values.requesterEmail.trim()) errors.requesterEmail = "Requester email is required.";
  else if (!EMAIL_REGEX.test(values.requesterEmail.trim()))
    errors.requesterEmail = "Enter a valid email address.";

  if (!values.department) errors.department = "Please select a department.";
  return errors;
}

// Mocked network call — in the real app this is replaced by the axios call
// in src/api/ticketApi.js (see the production files).
function mockSubmitTicket(payload) {
  return new Promise((resolve, reject) => {
    setTimeout(() => {
      if (Math.random() < 0.15) reject(new Error("Network error reaching the ticket API."));
      else resolve({ ticketId: `T-2026-${Math.floor(1000 + Math.random() * 9000)}` });
    }, 900);
  });
}

export default function TicketFormPreview() {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [status, setStatus] = useState("idle"); // idle | loading | success | error
  const [result, setResult] = useState(null);
  const [errorMsg, setErrorMsg] = useState("");

  function handleChange(field, value) {
    setValues((prev) => ({ ...prev, [field]: value }));
    if (errors[field]) setErrors((prev) => ({ ...prev, [field]: undefined }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    const validationErrors = validate(values);
    setErrors(validationErrors);
    if (Object.keys(validationErrors).length > 0) return;

    setStatus("loading");
    try {
      const data = await mockSubmitTicket(values);
      setResult(data);
      setStatus("success");
      setValues(initialValues);
    } catch (err) {
      setErrorMsg(err.message);
      setStatus("error");
    }
  }

  const inputClass = (field) =>
    `w-full rounded-md border px-3 py-2 text-sm outline-none transition focus:ring-2 focus:ring-blue-500 ${
      errors[field] ? "border-red-400" : "border-gray-300"
    }`;

  return (
    <div className="flex items-center justify-center p-6 bg-gray-50 min-h-[560px]">
      <div className="w-full max-w-lg rounded-xl border border-gray-200 bg-white shadow-sm">
        <div className="border-b border-gray-100 px-6 py-4">
          <h2 className="text-base font-semibold text-gray-900">Submit New Ticket</h2>
          <p className="text-sm text-gray-500 mt-0.5">
            Describe your issue and SupportPilot will classify and route it automatically.
          </p>
        </div>

        <form onSubmit={handleSubmit} noValidate className="px-6 py-5 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Ticket Title</label>
            <input
              className={inputClass("title")}
              placeholder="e.g. VPN Connection Failing on Corporate Network"
              value={values.title}
              onChange={(e) => handleChange("title", e.target.value)}
            />
            {errors.title && <p className="mt-1 text-xs text-red-600">{errors.title}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              rows={4}
              className={inputClass("description")}
              placeholder="Include error messages, what you already tried, and when it started."
              value={values.description}
              onChange={(e) => handleChange("description", e.target.value)}
            />
            {errors.description && (
              <p className="mt-1 text-xs text-red-600">{errors.description}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Requester Email
            </label>
            <input
              type="email"
              className={inputClass("requesterEmail")}
              placeholder="john.doe@company.com"
              value={values.requesterEmail}
              onChange={(e) => handleChange("requesterEmail", e.target.value)}
            />
            {errors.requesterEmail && (
              <p className="mt-1 text-xs text-red-600">{errors.requesterEmail}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
            <select
              className={inputClass("department")}
              value={values.department}
              onChange={(e) => handleChange("department", e.target.value)}
            >
              <option value="">Select department</option>
              {DEPARTMENTS.map((d) => (
                <option key={d} value={d}>
                  {d}
                </option>
              ))}
            </select>
            {errors.department && (
              <p className="mt-1 text-xs text-red-600">{errors.department}</p>
            )}
          </div>

          {status === "error" && (
            <div className="flex items-start gap-2 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
              <AlertCircle className="h-4 w-4 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium">Couldn't submit ticket</p>
                <p className="text-red-600">{errorMsg}</p>
              </div>
            </div>
          )}

          {status === "success" && result && (
            <div className="flex items-start gap-2 rounded-md border border-green-200 bg-green-50 px-3 py-2 text-sm text-green-700">
              <CheckCircle2 className="h-4 w-4 mt-0.5 shrink-0" />
              <div>
                <p className="font-medium">Ticket submitted</p>
                <p>Ticket #{result.ticketId} was created. You'll get an email update soon.</p>
              </div>
            </div>
          )}

          <button
            type="submit"
            disabled={status === "loading"}
            className="w-full flex items-center justify-center gap-2 rounded-md bg-blue-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-blue-700 disabled:opacity-60"
          >
            {status === "loading" && <Loader2 className="h-4 w-4 animate-spin" />}
            {status === "loading" ? "Submitting..." : "Submit Ticket"}
          </button>
        </form>
      </div>
    </div>
  );
}
