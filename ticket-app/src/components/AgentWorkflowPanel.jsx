import { useState, useEffect } from "react";
import { Search, Wrench, ArrowUpCircle, Stethoscope, FileCode2, Mail, ExternalLink } from "lucide-react";

const ICON_MAP = {
    Stethoscope: Stethoscope,
    Search: Search,
    Wrench: Wrench,
    ArrowUpCircle: ArrowUpCircle,
    FileCode2: FileCode2,
    Mail: Mail
};

// ---- DEFAULT DUMMY DATA (fallback when no ticket is active) ----
const defaultAgents = [
    { key: "diagnosis", label: "Diagnosis", status: "Active", icon: Stethoscope, color: "text-indigo-600 bg-indigo-50 border-indigo-100 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/60" },
    { key: "retrieval", label: "Retrieval", status: "Active", icon: Search, color: "text-indigo-600 bg-indigo-50 border-indigo-100 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/60" },
    { key: "resolution", label: "Resolution", status: "Active", icon: Wrench, color: "text-indigo-600 bg-indigo-50 border-indigo-100 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/60" },
    { key: "escalation", label: "Escalation", status: "Standby", icon: ArrowUpCircle, color: "text-gray-400 bg-gray-50 border-gray-150 dark:bg-zinc-800/40 dark:text-zinc-500 dark:border-zinc-800" },
];

const defaultWorkflowActivity = [
    { time: "10:32 AM", actor: "Diagnosis Agent", action: "Identified VPN connection issue" },
    { time: "10:32 AM", actor: "Retrieval Agent", action: "Found 3 relevant knowledge articles" },
    { time: "10:33 AM", actor: "Resolution Agent", action: "Generated troubleshooting steps" },
    { time: "10:33 AM", actor: "System", action: "Resolution confidence: 87%" },
];

const defaultIntegrations = [
    {
        key: "jira",
        name: "Jira Integration",
        detail: "Connected • Last synced 2 mins ago",
        status: "Active",
        icon: FileCode2,
        color: "text-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-100/50 dark:border-indigo-900/40",
    },
    {
        key: "email",
        name: "Email Automation",
        detail: "Connected • 24 emails sent today",
        status: "Active",
        icon: Mail,
        color: "text-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-100/50 dark:border-indigo-900/40",
    },
];

const defaultJiraTicket = {
    ticketId: "IT-2023-4521",
    status: "In Progress",
    assignee: "Network Team",
    priority: "High",
};

const defaultEmailNotification = {
    title: "Escalation Notice Email",
    message:
        "Your support ticket #T-2023-4521 has been received. We're working on resolving your VPN connection issue. Our AI system has identified potential solutions and assigned this to the Network Team. You'll receive updates as we progress.",
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export default function AgentWorkflowPanel({ activeTicket }) {
    const [workflowData, setWorkflowData] = useState(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        if (!activeTicket || !activeTicket.id) {
            setWorkflowData(null);
            return;
        }

        const rawId = String(activeTicket.id).replace(/\D/g, "");
        if (!rawId) return;

        let isMounted = true;
        setLoading(true);

        fetch(`${API_BASE_URL}/tickets/${rawId}/workflow`)
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (isMounted && data) {
                    setWorkflowData(data);
                }
            })
            .catch((err) => {
                console.warn("Failed to fetch dynamic agent workflow data:", err);
            })
            .finally(() => {
                if (isMounted) setLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, [activeTicket]);

    // Choose either backend data or default mockup fallbacks
    const hasData = workflowData !== null;
    
    const agents = hasData
        ? workflowData.agents.map(a => {
            const isActive = a.status === "Active";
            return {
                ...a,
                icon: ICON_MAP[a.icon] || Stethoscope,
                color: isActive 
                    ? "text-indigo-600 bg-indigo-50 border-indigo-150 dark:bg-indigo-950/40 dark:text-indigo-400 dark:border-indigo-900/60"
                    : "text-gray-400 bg-gray-50 border-gray-150 dark:bg-zinc-800/40 dark:text-zinc-500 dark:border-zinc-800"
            };
        })
        : defaultAgents;
        
    const workflowActivity = hasData
        ? workflowData.workflowActivity
        : defaultWorkflowActivity;
        
    const integrations = hasData
        ? workflowData.integrations.map(i => ({
            ...i,
            icon: ICON_MAP[i.icon] || Mail,
            color: "text-indigo-600 bg-indigo-50/50 dark:bg-indigo-950/30 border-indigo-100/50 dark:border-indigo-900/40"
        }))
        : defaultIntegrations;
        
    const jiraTicket = hasData
        ? workflowData.jiraTicket
        : defaultJiraTicket;
        
    const emailNotification = hasData
        ? workflowData.emailNotification
        : defaultEmailNotification;

    return (
        <div className="space-y-6 text-left">
            {/* Header Block */}
            <div className="flex items-center justify-between border-b border-gray-200 dark:border-zinc-800 pb-4">
                <div className="space-y-1">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-50 tracking-tight leading-snug">
                        AI Orchestrator Workflows
                    </h2>
                    <p className="text-xs text-gray-500 dark:text-zinc-450 mt-0.5">
                        {activeTicket 
                            ? `Autonomous agent execution paths and pipeline logs for ${activeTicket.id}`
                            : "Autonomous agent execution paths and pipeline logs"
                        }
                    </p>
                </div>
                {loading && (
                    <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 animate-pulse bg-indigo-50 dark:bg-indigo-950/40 border border-indigo-100 dark:border-indigo-900 px-3 py-1.5 rounded-full shadow-sm">
                        Synchronizing pipeline...
                    </span>
                )}
            </div>

            {/* Split Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* LEFT PANEL — Multi-Agent Workflow */}
                <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
                    <div>
                        <div className="flex items-center gap-2 mb-6 border-b border-gray-100 dark:border-zinc-800/80 pb-3.5">
                            <Stethoscope size={14} className="text-indigo-600 dark:text-indigo-400" />
                            <h3 className="text-xs font-bold text-gray-800 dark:text-zinc-200 uppercase tracking-wider">
                                Pipeline Agent Topology
                            </h3>
                        </div>

                        {/* Agent icons row */}
                        <div className="grid grid-cols-4 gap-3 mb-6">
                            {agents.map((agent) => {
                                const Icon = agent.icon;
                                const isActive = agent.status === "Active";
                                return (
                                    <div key={agent.key} className="flex flex-col items-center text-center p-3.5 border border-gray-150 dark:border-zinc-800 bg-gray-50/30 dark:bg-zinc-900/40 rounded-xl hover:border-gray-200 dark:hover:border-zinc-700 transition-colors duration-150">
                                        <div
                                            className={`w-9 h-9 rounded-full border flex items-center justify-center mb-2.5 ${agent.color}`}
                                        >
                                            <Icon size={15} />
                                        </div>
                                        <p className="text-[11px] font-bold text-gray-800 dark:text-zinc-250">{agent.label}</p>
                                        <p
                                            className={`text-[9px] font-bold mt-1 uppercase tracking-wider px-2 py-0.5 rounded-full border ${
                                                isActive 
                                                    ? "text-emerald-600 bg-emerald-50/50 border-emerald-100/50 dark:text-emerald-400 dark:bg-emerald-950/20 dark:border-emerald-900/30" 
                                                    : "text-gray-400 bg-gray-50 border-gray-200 dark:text-zinc-500 dark:bg-zinc-800/40 dark:border-zinc-800/80"
                                            }`}
                                        >
                                            {agent.status}
                                        </p>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Workflow activity feed (Interactive Terminal look) */}
                    <div className="border-t border-gray-150 dark:border-zinc-800 pt-5 mt-4">
                        <p className="text-[10px] font-bold text-gray-400 dark:text-zinc-505 uppercase tracking-wider mb-3">
                            Pipeline Stderr/Stdout Logs
                        </p>
                        {workflowActivity.length === 0 ? (
                            <div className="bg-zinc-950 border border-zinc-850 p-6 rounded-xl font-mono text-[10px] text-zinc-500 text-center">
                                {"[SYSTEM_DAEMON] No activity traces logged. Select a ticket to mount console."}
                            </div>
                        ) : (
                            <div className="bg-zinc-950 border border-zinc-850/80 p-4.5 rounded-xl font-mono text-[11px] leading-relaxed text-zinc-300 space-y-1.5 max-h-[220px] overflow-y-auto pr-1">
                                {workflowActivity.map((item, i) => (
                                    <div key={i} className="flex items-start gap-2.5 hover:bg-zinc-900/50 p-1 rounded transition-colors">
                                        <span className="text-zinc-600 shrink-0 select-none">[{item.time.split(" ")[0]}]</span>{" "}
                                        <span className="text-indigo-400 shrink-0 select-none">{item.actor.replace(/\s+/g, "")}:</span>{" "}
                                        <span className="text-zinc-200">{item.action}</span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>

                {/* RIGHT PANEL — Enterprise Integrations */}
                <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm space-y-6">
                    <div>
                        <div className="flex items-center gap-2 mb-6 border-b border-gray-100 dark:border-zinc-800/80 pb-3.5">
                            <FileCode2 size={14} className="text-indigo-600 dark:text-indigo-400" />
                            <h3 className="text-xs font-bold text-gray-800 dark:text-zinc-200 uppercase tracking-wider">
                                Third-Party Connectors
                            </h3>
                        </div>

                        {/* Integration status cards */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {integrations.map((integration) => {
                                const Icon = integration.icon;
                                return (
                                    <div
                                        key={integration.key}
                                        className="flex items-center justify-between border border-gray-200 dark:border-zinc-800 rounded-xl p-3.5 bg-gray-50/20 dark:bg-zinc-900/40 hover:border-gray-300 dark:hover:border-zinc-700 transition-colors duration-150"
                                    >
                                        <div className="flex items-center gap-3">
                                            <div
                                                className={`w-7 h-7 rounded-lg border flex items-center justify-center shrink-0 ${integration.color}`}
                                            >
                                                <Icon size={14} />
                                            </div>
                                            <div className="min-w-0">
                                                <p className="text-xs font-bold text-gray-800 dark:text-zinc-200 truncate">{integration.name}</p>
                                                <p className="text-[10px] text-gray-400 dark:text-zinc-500 truncate mt-0.5">{integration.detail}</p>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Jira Ticket Details block */}
                    <div>
                        <p className="text-[10px] font-bold text-gray-400 dark:text-zinc-505 uppercase tracking-wider mb-2.5">
                            Jira Orchestrator Output
                        </p>
                        {jiraTicket ? (
                            <div className="border border-gray-150 dark:border-zinc-800 bg-gray-50/20 dark:bg-zinc-900/40 rounded-xl p-4.5 space-y-4 shadow-sm text-xs">
                                <div className="flex justify-between items-center border-b border-gray-150 dark:border-zinc-800/80 pb-3">
                                    <div className="flex items-center gap-1.5">
                                        <span className="font-bold text-gray-900 dark:text-zinc-100">{jiraTicket.ticketId}</span>
                                        <a href="#jira" className="text-gray-400 hover:text-indigo-600 transition-colors">
                                            <ExternalLink size={11} />
                                        </a>
                                    </div>
                                    <span className="text-[9px] font-bold text-indigo-700 bg-indigo-50 border border-indigo-100 dark:text-indigo-400 dark:bg-indigo-950/40 dark:border-indigo-900 px-2 py-0.5 rounded-full">
                                        {jiraTicket.status}
                                    </span>
                                </div>
                                <div className="grid grid-cols-2 gap-x-4 gap-y-3.5">
                                    <div>
                                        <p className="text-gray-400 dark:text-zinc-500 text-[10px]">Assignee Group</p>
                                        <p className="font-semibold text-gray-700 dark:text-zinc-350 mt-0.5">{jiraTicket.assignee}</p>
                                    </div>
                                    <div>
                                        <p className="text-gray-400 dark:text-zinc-500 text-[10px]">Priority Severity</p>
                                        <p className="font-semibold text-gray-700 dark:text-zinc-350 mt-0.5">{jiraTicket.priority}</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div className="border border-dashed border-gray-200 dark:border-zinc-800 rounded-xl p-4.5 text-center text-xs text-gray-400 dark:text-zinc-500">
                                No Jira task mounted (escalation state: false)
                            </div>
                        )}
                    </div>

                    {/* Email Notification Sent card (Mock mail preview) */}
                    <div>
                        <p className="text-[10px] font-bold text-gray-400 dark:text-zinc-505 uppercase tracking-wider mb-2.5">
                            Automated Email Dispatch
                        </p>
                        {emailNotification ? (
                            <div className="border border-gray-150 dark:border-zinc-800 rounded-xl overflow-hidden shadow-sm">
                                {/* Email Header */}
                                <div className="bg-gray-50/80 dark:bg-zinc-900/60 border-b border-gray-150 dark:border-zinc-800 px-4 py-2.5 text-[10px] text-gray-500 dark:text-zinc-400 font-mono space-y-0.5">
                                    <div className="truncate"><span className="text-gray-400">Subject:</span> {emailNotification.title}</div>
                                    <div className="truncate"><span className="text-gray-400">Sender:</span> support-daemon@supportpilot.ai</div>
                                    {activeTicket?.requesterEmail && (
                                        <div className="truncate"><span className="text-gray-400">Recipient:</span> {activeTicket.requesterEmail}</div>
                                    )}
                                </div>
                                {/* Email Body */}
                                <div className="p-4 bg-white dark:bg-zinc-950 font-mono text-[11px] text-gray-600 dark:text-zinc-450 leading-relaxed max-h-[140px] overflow-y-auto">
                                    {emailNotification.message}
                                </div>
                            </div>
                        ) : (
                            <div className="border border-dashed border-gray-200 dark:border-zinc-800 rounded-xl p-4.5 text-center text-xs text-gray-400 dark:text-zinc-500">
                                No email dispatched (queue status: empty)
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}