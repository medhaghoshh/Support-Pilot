import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import {
  Inbox,
  FolderOpen,
  CheckCircle2,
  AlertTriangle,
  AlertCircle,
  ShieldCheck,
  Search,
  Eye,
  X,
  Bot,
  Tag,
  Flag,
  Percent,
  Calendar,
  AlignLeft,
  Hash,
} from "lucide-react";

const TICKETS_API_URL = `${import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api"}/tickets`;
const CLASSIFICATION_API_URL = `${import.meta.env.VITE_CLASSIFY_API_BASE_URL || "http://localhost:8001"}/diagnose`;

function inferCategoryAndConfidence(subject = "", description = "") {
  const text = `${subject} ${description}`.toLowerCase();
  let dept = "IT Support";
  let conf = 0.88;

  if (text.includes("vpn") || text.includes("remote") || text.includes("tunnel")) {
    dept = "Network Connectivity";
    conf = 0.94;
  } else if (text.includes("wifi") || text.includes("network") || text.includes("internet") || text.includes("dns") || text.includes("ip")) {
    dept = "Network Connectivity";
    conf = 0.92;
  } else if (text.includes("password") || text.includes("login") || text.includes("auth") || text.includes("reset") || text.includes("mfa")) {
    dept = "Identity & Access";
    conf = 0.95;
  } else if (text.includes("install") || text.includes("software") || text.includes("excel") || text.includes("outlook") || text.includes("app") || text.includes("crash")) {
    dept = "Software & Applications";
    conf = 0.89;
  } else if (text.includes("printer") || text.includes("hardware") || text.includes("monitor") || text.includes("mouse") || text.includes("keyboard") || text.includes("laptop") || text.includes("device") || text.includes("memory") || text.includes("cpu") || text.includes("heating") || text.includes("screen")) {
    dept = "Hardware & Devices";
    conf = 0.91;
  }

  return { department: dept, confidence: conf };
}

function normalizeTicket(ticket) {
  // NOTE: ticket.department is the user's work department (Finance, HR, etc.)
  // NOT the IT category. We always derive the category from the AI classifier.
  return {
    ticket_id: ticket.ticket_id ?? ticket.id,
    subject: ticket.subject || "Untitled Ticket",
    description: ticket.description || "",
    department: "Classifying...",   // placeholder; replaced after API call
    category: "Classifying...",
    severity: ticket.severity || "Low",
    priority: ticket.priority || "P4",
    confidence: null,               // filled after API call
    status: ticket.status || "Open",
    created_at: ticket.created_at || "",
  };
}

function formatConfidence(value) {
  if (value === null || value === undefined || value === "") return "—";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return String(value);
  const pct = numeric > 1 ? numeric : numeric * 100;
  return `${Math.max(0, Math.min(100, pct)).toFixed(0)}%`;
}

function SeverityBadge({ severity }) {
  const s = String(severity || "").toLowerCase();
  if (s.includes("high") || s.includes("critical"))
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">High</span>;
  if (s.includes("medium"))
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-800">Medium</span>;
  return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">Low</span>;
}

function StatusBadge({ status }) {
  const s = String(status || "").toLowerCase();
  if (s.includes("closed") || s.includes("resolved"))
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-100 text-emerald-800">Closed</span>;
  if (s.includes("in_progress") || s.includes("open"))
    return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">Open</span>;
  return <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800">Pending</span>;
}

function ConfidenceBar({ score }) {
  let pct = 0;
  if (typeof score === "string" && score.includes("%")) {
    pct = parseInt(score, 10);
  } else {
    pct = Number(score) || 0;
  }
  pct = pct > 1 ? Math.min(pct, 100) : Math.max(0, Math.min(100, pct * 100));

  return (
    <div className="flex items-center gap-2">
      <div className="w-20 bg-gray-200 rounded-full h-2 overflow-hidden">
        <div className="bg-blue-600 h-2 rounded-full transition-all duration-500" style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-medium text-gray-600">{pct.toFixed(0)}%</span>
    </div>
  );
}

export default function ClassificationResults() {
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [modalOpen, setModalOpen] = useState(false);

  const { data: tickets = [], isLoading: loading } = useQuery({
    queryKey: ['tickets'],
    queryFn: async () => {
      const response = await fetch(TICKETS_API_URL);
      if (!response.ok) throw new Error("Unable to fetch tickets");
      const data = await response.json();
      const normalized = Array.isArray(data) ? data.map(normalizeTicket) : [];

      // Always classify every ticket using the AI diagnosis endpoint
      // so the Category column shows the real IT category (Networking,
      // Password Reset, Hardware, etc.) not the user's work department.
      const classified = await Promise.all(
        normalized.map(async (ticket) => {
          // Combine subject + description for better keyword matching.
          // A short description like "can't connect" alone may miss keywords
          // that are clearly visible in the subject ("Wifi Connection issue").
          const combinedText = `${ticket.subject} ${ticket.description}`.trim();
          const classification = await getClassification(combinedText, ticket.subject);
          return {
            ...ticket,
            department: classification.department,
            category: classification.department,
            confidence: classification.confidence,
          };
        })
      );

      return classified;
    },
    // No staleTime — always re-fetch fresh classifications on page load
  });

  // Keyword-based fallback for when the API can't match a category
  function localInfer(text = "") {
    const t = text.toLowerCase();
    if (t.includes("wifi") || t.includes("network") || t.includes("bluetooth") || t.includes("vpn") || t.includes("internet") || t.includes("connect"))
      return { department: "Networking", confidence: 0.82 };
    if (t.includes("password") || t.includes("login") || t.includes("locked") || t.includes("reset") || t.includes("auth"))
      return { department: "Password Reset", confidence: 0.88 };
    if (t.includes("keyboard") || t.includes("laptop") || t.includes("monitor") || t.includes("printer") || t.includes("mouse") || t.includes("broken") || t.includes("hardware"))
      return { department: "Hardware", confidence: 0.85 };
    if (t.includes("software") || t.includes("app") || t.includes("install") || t.includes("crash") || t.includes("update") || t.includes("third party") || t.includes("third-party"))
      return { department: "Software", confidence: 0.80 };
    if (t.includes("email") || t.includes("outlook") || t.includes("mailbox"))
      return { department: "Email", confidence: 0.83 };
    if (t.includes("security") || t.includes("phishing") || t.includes("virus") || t.includes("malware") || t.includes("unauthorized"))
      return { department: "Security", confidence: 0.90 };
    return { department: "IT Support", confidence: 0.75 };
  }

  async function getClassification(text, subject = "") {
    if (!text && !subject) return localInfer("");
    try {
      const url = new URL(CLASSIFICATION_API_URL);
      url.searchParams.append("text", text);
      const response = await fetch(url.toString(), {
        method: "GET",
        headers: { "Accept": "application/json" },
      });
      if (!response.ok) throw new Error("Classification unavailable");
      const payload = await response.json();

      // If the API matched no symptoms (confidence 0.0 or empty category),
      // fall back to the local heuristic which handles fuzzier text.
      if (!payload.predicted_category || payload.confidence === 0 || payload.confidence === 0.0) {
        return localInfer(text);
      }

      return {
        department: payload.predicted_category,
        confidence: payload.confidence,
        matched_symptoms: payload.matched_symptoms || [],
        suggested_priority: payload.suggested_priority || "Medium",
        needs_clarification: payload.needs_clarification || false,
        clarifying_questions: payload.clarifying_questions || []
      };
    } catch (error) {
      console.warn("Classification API unavailable:", error);
      return localInfer(text || subject);
    }
  }

  async function handleViewTicket(ticket) {
    setModalOpen(true);
    setSelectedTicket({ loading: true });

    const classification = await getClassification(ticket.description);
    const merged = { ...ticket, ...classification };
    if (ticket.department && ticket.department !== "Pending") {
      merged.department = ticket.department;
    }
    if (ticket.confidence !== null && ticket.confidence !== undefined) {
      merged.confidence = ticket.confidence;
    }
    setSelectedTicket(merged);
  }

  function closeModal() {
    setModalOpen(false);
    setSelectedTicket(null);
  }

  const filteredTickets = tickets.filter((t) => {
    const value = searchTerm.trim().toLowerCase();
    if (!value) return true;
    return (
      (t.ticket_id && String(t.ticket_id).toLowerCase().includes(value)) ||
      (t.subject && t.subject.toLowerCase().includes(value)) ||
      (t.department && t.department.toLowerCase().includes(value)) ||
      (t.status && t.status.toLowerCase().includes(value)) ||
      (t.severity && t.severity.toLowerCase().includes(value)) ||
      (t.priority && t.priority.toLowerCase().includes(value))
    );
  });

  const total = filteredTickets.length;
  const open = filteredTickets.filter((t) =>
    String(t.status).toLowerCase().includes("open") ||
    String(t.status).toLowerCase().includes("in_progress")
  ).length;
  const closed = total - open;
  const high = filteredTickets.filter((t) => String(t.severity).toLowerCase().includes("high")).length;
  const medium = filteredTickets.filter((t) => String(t.severity).toLowerCase().includes("medium")).length;
  const low = filteredTickets.filter((t) => String(t.severity).toLowerCase().includes("low")).length;

  return (
    <div className="space-y-6 text-left">
      {/* Header */}
      <div className="flex items-center justify-between bg-white p-6 rounded-xl border border-gray-200 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Bot size={22} />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900 tracking-tight">AI Ticket Classification Analytics</h1>
            <p className="text-xs text-gray-500">Real-time enterprise classification &amp; ticket performance analytics</p>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4">
        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <Inbox size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Total Tickets</p>
            <p className="text-lg font-bold text-gray-900">{total}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center shrink-0">
            <FolderOpen size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Open Tickets</p>
            <p className="text-lg font-bold text-gray-900">{open}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <CheckCircle2 size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Closed Tickets</p>
            <p className="text-lg font-bold text-gray-900">{closed}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-red-50 text-red-600 flex items-center justify-center shrink-0">
            <AlertTriangle size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">High Severity</p>
            <p className="text-lg font-bold text-gray-900">{high}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center shrink-0">
            <AlertCircle size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Medium Severity</p>
            <p className="text-lg font-bold text-gray-900">{medium}</p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-4 flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-green-50 text-green-600 flex items-center justify-center shrink-0">
            <ShieldCheck size={18} />
          </div>
          <div>
            <p className="text-xs font-medium text-gray-500">Low Severity</p>
            <p className="text-lg font-bold text-gray-900">{low}</p>
          </div>
        </div>
      </div>

      {/* Table Section */}
      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        {/* Search Input */}
        <div className="p-4 border-b border-gray-200 bg-gray-50/50">
          <div className="relative max-w-md">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              type="text"
              placeholder="Search by ticket ID, subject, department or status..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 bg-white border border-gray-200 rounded-lg text-sm text-gray-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent placeholder:text-gray-400"
            />
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse text-sm">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                <th className="py-3 px-4">Ticket ID</th>
                <th className="py-3 px-4">Subject</th>
                <th className="py-3 px-4">Category</th>
                <th className="py-3 px-4">Severity</th>
                <th className="py-3 px-4">Priority</th>
                <th className="py-3 px-4">Confidence</th>
                <th className="py-3 px-4">Status</th>
                <th className="py-3 px-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 bg-white">
              {filteredTickets.map((ticket) => (
                <tr key={ticket.ticket_id} className="hover:bg-gray-50 transition-colors">
                  <td className="py-3.5 px-4 font-semibold text-blue-600">#{ticket.ticket_id}</td>
                  <td className="py-3.5 px-4 font-medium text-gray-900">{ticket.subject}</td>
                  <td className="py-3.5 px-4 text-gray-600">{ticket.department}</td>
                  <td className="py-3.5 px-4"><SeverityBadge severity={ticket.severity} /></td>
                  <td className="py-3.5 px-4 font-medium text-gray-700">{ticket.priority}</td>
                  <td className="py-3.5 px-4"><ConfidenceBar score={ticket.confidence} /></td>
                  <td className="py-3.5 px-4"><StatusBadge status={ticket.status} /></td>
                  <td className="py-3.5 px-4 text-right">
                    <button
                      onClick={() => handleViewTicket(ticket)}
                      className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-gray-100 hover:bg-blue-50 text-gray-700 hover:text-blue-600 text-xs font-medium transition-colors"
                    >
                      <Eye size={14} /> View
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {loading && (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mb-3"></div>
              <p className="text-xs">Loading tickets...</p>
            </div>
          )}

          {!loading && filteredTickets.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <Inbox size={32} className="mb-2 text-gray-300" />
              <p className="text-sm font-medium text-gray-600">No tickets found</p>
              <p className="text-xs text-gray-400">Try adjusting your search criteria</p>
            </div>
          )}
        </div>
      </div>

      {/* Modal */}
      {modalOpen && (
        <div
          className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
          onClick={(e) => e.target === e.currentTarget && closeModal()}
        >
          <div className="bg-white rounded-2xl border border-gray-200 shadow-xl w-full max-w-lg overflow-hidden animate-in fade-in zoom-in-95 duration-200">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
              <h3 className="text-base font-semibold text-gray-900">Ticket Details</h3>
              <button
                onClick={closeModal}
                className="text-gray-400 hover:text-gray-600 rounded-lg p-1 transition-colors"
              >
                <X size={18} />
              </button>
            </div>

            <div className="p-6 space-y-4 max-h-[80vh] overflow-y-auto">
              {selectedTicket?.loading ? (
                <div className="flex flex-col items-center justify-center py-8 text-gray-400">
                  <div className="w-6 h-6 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mb-2"></div>
                  <p className="text-xs">Analyzing ticket details...</p>
                </div>
              ) : (
                selectedTicket && (
                  <div className="space-y-3 divide-y divide-gray-100">
                    <DetailRow icon={Hash} label="Ticket ID" value={`#${selectedTicket.ticket_id}`} />
                    <DetailRow icon={Tag} label="Subject" value={selectedTicket.subject} />
                    <DetailRow icon={AlignLeft} label="Description" value={selectedTicket.description} />
                    <DetailRow icon={Bot} label="Department / Category" value={selectedTicket.department} />
                    <DetailRow icon={AlertTriangle} label="Severity" value={selectedTicket.severity} />
                    <DetailRow icon={Flag} label="Priority" value={selectedTicket.priority} />
                    <DetailRow icon={Percent} label="Confidence" value={formatConfidence(selectedTicket.confidence)} />
                    {selectedTicket.matched_symptoms && selectedTicket.matched_symptoms.length > 0 && (
                      <DetailRow icon={CheckCircle2} label="Matched Symptoms" value={selectedTicket.matched_symptoms.join(", ")} />
                    )}
                    {selectedTicket.suggested_priority && (
                      <DetailRow icon={Flag} label="Suggested Priority" value={selectedTicket.suggested_priority} />
                    )}
                    {selectedTicket.needs_clarification && selectedTicket.clarifying_questions?.length > 0 && (
                      <DetailRow icon={AlertCircle} label="Clarifying Question" value={selectedTicket.clarifying_questions[0]} />
                    )}
                    <DetailRow icon={CheckCircle2} label="Status" value={selectedTicket.status} />
                    <DetailRow icon={Calendar} label="Created At" value={selectedTicket.created_at ? new Date(selectedTicket.created_at).toLocaleString() : "—"} />
                  </div>
                )
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function DetailRow({ icon: Icon, label, value }) {
  return (
    <div className="flex items-start gap-3 pt-3 first:pt-0">
      <div className="w-7 h-7 rounded-lg bg-gray-100 text-gray-500 flex items-center justify-center shrink-0 mt-0.5">
        <Icon size={14} />
      </div>
      <div>
        <p className="text-[10px] font-semibold text-gray-400 uppercase tracking-wider">{label}</p>
        <p className="text-sm font-medium text-gray-800 mt-0.5 leading-relaxed">{value || "—"}</p>
      </div>
    </div>
  );
}