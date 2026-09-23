import { useState, useEffect } from "react";
import {
    FolderGit2,
    Mail,
    RefreshCw,
    CheckCircle2,
    AlertCircle,
    Eye,
    EyeOff,
    Save,
} from "lucide-react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

export default function IntegrationsPage() {
    // Configurations state
    const [configs, setConfigs] = useState({
        jiraUrl: "",
        jiraEmail: "",
        jiraApiToken: "",
        jiraProject: "",
        emailAddress: "",
        emailAppPassword: "",
    });

    const [loading, setLoading] = useState(true);
    
    // Testing connection states
    const [testingJira, setTestingJira] = useState(false);
    const [testingEmail, setTestingEmail] = useState(false);
    const [testRecipient, setTestRecipient] = useState("");

    // Test results
    const [jiraTestResult, setJiraTestResult] = useState(null);
    const [emailTestResult, setEmailTestResult] = useState(null);

    // Show/hide credentials state
    const [showJiraToken, setShowJiraToken] = useState(false);
    const [showEmailPassword, setShowEmailPassword] = useState(false);

    // Saving configurations states
    const [saving, setSaving] = useState({
        jira: false,
        email: false,
    });
    const [saveResult, setSaveResult] = useState({
        jira: null,
        email: null,
    });

    // Fetch config on load
    useEffect(() => {
        let isMounted = true;
        fetch(`${API_BASE_URL}/integrations/config`)
            .then((res) => (res.ok ? res.json() : null))
            .then((data) => {
                if (isMounted && data) {
                    setConfigs({
                        jiraUrl: data.jira_url || "",
                        jiraEmail: data.jira_email || "",
                        jiraApiToken: data.jira_api_token || "",
                        jiraProject: data.jira_project_key || "",
                        emailAddress: data.email_address || "",
                        emailAppPassword: data.email_app_password || "",
                    });
                }
            })
            .catch((err) => {
                console.error("Failed to load integrations configuration:", err);
            })
            .finally(() => {
                if (isMounted) setLoading(false);
            });

        return () => {
            isMounted = false;
        };
    }, []);

    const handleInputChange = (key, val) => {
        setConfigs((prev) => ({ ...prev, [key]: val }));
    };

    const handleSaveSettings = async (type) => {
        setSaving((prev) => ({ ...prev, [type]: true }));
        setSaveResult((prev) => ({ ...prev, [type]: null }));

        try {
            const payload = {
                jira_url: configs.jiraUrl,
                jira_email: configs.jiraEmail,
                jira_api_token: configs.jiraApiToken,
                jira_project_key: configs.jiraProject,
                email_address: configs.emailAddress,
                email_app_password: configs.emailAppPassword,
            };

            const res = await fetch(`${API_BASE_URL}/integrations/config`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify(payload),
            });

            const data = await res.json();
            if (res.ok) {
                setSaveResult((prev) => ({
                    ...prev,
                    [type]: { status: "success", message: "Configuration saved successfully!" },
                }));
                // Clear success message after 3 seconds
                setTimeout(() => {
                    setSaveResult((prev) => ({ ...prev, [type]: null }));
                }, 3000);
            } else {
                setSaveResult((prev) => ({
                    ...prev,
                    [type]: { status: "error", message: data.detail || "Failed to save configuration" },
                }));
            }
        } catch (err) {
            setSaveResult((prev) => ({
                ...prev,
                [type]: { status: "error", message: "Failed to connect to backend server" },
            }));
        } finally {
            setSaving((prev) => ({ ...prev, [type]: false }));
        }
    };

    const runTestJira = async () => {
        setTestingJira(true);
        setJiraTestResult(null);

        try {
            const res = await fetch(`${API_BASE_URL}/integrations/jira/test`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    jira_url: configs.jiraUrl,
                    jira_email: configs.jiraEmail,
                    jira_api_token: configs.jiraApiToken,
                    jira_project_key: configs.jiraProject,
                }),
            });

            const data = await res.json();
            if (res.ok) {
                setJiraTestResult({
                    status: "success",
                    message: data.message || "Connection verified successfully!",
                });
            } else {
                setJiraTestResult({
                    status: "error",
                    message: data.detail || "Connection failed. Check settings.",
                });
            }
        } catch (err) {
            setJiraTestResult({
                status: "error",
                message: "Failed to connect to backend server test endpoint.",
            });
        } finally {
            setTestingJira(false);
        }
    };

    const runTestEmail = async () => {
        if (!testRecipient) {
            setEmailTestResult({
                status: "error",
                message: "Please enter a test recipient email address.",
            });
            return;
        }

        setTestingEmail(true);
        setEmailTestResult(null);

        try {
            const res = await fetch(`${API_BASE_URL}/integrations/email/test`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    email_address: configs.emailAddress,
                    email_app_password: configs.emailAppPassword,
                    test_recipient: testRecipient,
                }),
            });

            const data = await res.json();
            if (res.ok) {
                setEmailTestResult({
                    status: "success",
                    message: data.message || "Test email sent successfully!",
                });
            } else {
                setEmailTestResult({
                    status: "error",
                    message: data.detail || "Failed to send email. Check credentials.",
                });
            }
        } catch (err) {
            setEmailTestResult({
                status: "error",
                message: "Failed to connect to backend server test endpoint.",
            });
        } finally {
            setTestingEmail(false);
        }
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center py-20 text-gray-500 dark:text-zinc-400">
                <RefreshCw className="animate-spin mb-4" size={24} />
                <p className="text-sm font-semibold">Loading integration configurations...</p>
            </div>
        );
    }

    return (
        <div className="space-y-6 max-w-5xl font-sans text-left">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-zinc-50 tracking-tight">Integrations</h1>
                <p className="text-sm text-gray-500 dark:text-zinc-450 mt-0.5">
                    Connect and verify third-party systems active in your support orchestration workspace.
                </p>
            </div>

            {/* Split layout for active integrations */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                
                {/* Jira Integration Card */}
                <div className="bg-white dark:bg-zinc-900 rounded-xl border border-gray-200 dark:border-zinc-800 shadow-sm p-5 flex flex-col justify-between transition-all hover:shadow-md">
                    <div>
                        <div className="flex items-start justify-between mb-4 border-b border-gray-50 dark:border-zinc-800/80 pb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-blue-50 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 flex items-center justify-center shrink-0 border border-blue-100 dark:border-blue-900/40">
                                    <FolderGit2 size={20} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold text-gray-800 dark:text-zinc-200">Jira Software</h2>
                                    <p className="text-[11px] text-gray-400 dark:text-zinc-500">Escalate and track engineering bug reports</p>
                                </div>
                            </div>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border text-emerald-600 bg-emerald-50/50 border-emerald-100 dark:text-emerald-400 dark:bg-emerald-950/20 dark:border-emerald-900/30">
                                Active Connector
                            </span>
                        </div>

                        {/* Config fields */}
                        <div className="space-y-4 pt-1">
                            <div>
                                <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Jira Instance URL</label>
                                <input
                                    type="text"
                                    placeholder="e.g. https://your-domain.atlassian.net"
                                    value={configs.jiraUrl}
                                    onChange={(e) => handleInputChange("jiraUrl", e.target.value)}
                                    className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg px-3 py-2.5 mt-1 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all font-mono"
                                />
                            </div>

                            <div className="grid grid-cols-3 gap-3">
                                <div className="col-span-2">
                                    <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Jira Email</label>
                                    <input
                                        type="email"
                                        placeholder="user@domain.com"
                                        value={configs.jiraEmail}
                                        onChange={(e) => handleInputChange("jiraEmail", e.target.value)}
                                        className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg px-3 py-2.5 mt-1 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all"
                                    />
                                </div>
                                <div>
                                    <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Project Key</label>
                                    <input
                                        type="text"
                                        placeholder="SUP"
                                        value={configs.jiraProject}
                                        onChange={(e) => handleInputChange("jiraProject", e.target.value)}
                                        className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg px-3 py-2.5 mt-1 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all uppercase font-bold text-center"
                                    />
                                </div>
                            </div>

                            <div>
                                <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Jira API Token</label>
                                <div className="relative mt-1">
                                    <input
                                        type={showJiraToken ? "text" : "password"}
                                        placeholder={configs.jiraApiToken ? "••••••••••••••••" : "Enter API token"}
                                        value={configs.jiraApiToken}
                                        onChange={(e) => handleInputChange("jiraApiToken", e.target.value)}
                                        className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg pl-3 pr-10 py-2.5 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all font-mono"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowJiraToken(!showJiraToken)}
                                        className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-zinc-200 transition-colors"
                                    >
                                        {showJiraToken ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Actions and Feedback */}
                    <div className="mt-6 pt-4 border-t border-gray-150 dark:border-zinc-800/80 space-y-3">
                        {jiraTestResult && (
                            <div className={`p-3 rounded-lg flex gap-2.5 text-xs ${
                                jiraTestResult.status === "success" 
                                    ? "bg-green-50 dark:bg-green-950/20 border border-green-100 dark:border-green-900/30 text-green-700 dark:text-green-400" 
                                    : "bg-red-50 dark:bg-red-950/20 border border-red-100 dark:border-red-900/30 text-red-700 dark:text-red-400"
                            }`}>
                                {jiraTestResult.status === "success" ? <CheckCircle2 size={16} className="shrink-0" /> : <AlertCircle size={16} className="shrink-0" />}
                                <span>{jiraTestResult.message}</span>
                            </div>
                        )}

                        {saveResult.jira && (
                            <div className={`p-2.5 rounded-lg text-center text-xs font-semibold ${
                                saveResult.jira.status === "success"
                                    ? "bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400"
                                    : "bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400"
                            }`}>
                                {saveResult.jira.message}
                            </div>
                        )}

                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={runTestJira}
                                disabled={testingJira || !configs.jiraUrl || !configs.jiraEmail || !configs.jiraProject}
                                className="flex items-center gap-1.5 px-3.5 py-2 rounded-lg border border-gray-200 dark:border-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-850 text-xs font-semibold text-gray-700 dark:text-zinc-300 disabled:opacity-50 disabled:hover:bg-transparent transition-colors"
                            >
                                <RefreshCw size={12} className={testingJira ? "animate-spin" : ""} />
                                {testingJira ? "Testing..." : "Test Connection"}
                            </button>
                            <button
                                onClick={() => handleSaveSettings("jira")}
                                disabled={saving.jira}
                                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors disabled:opacity-75"
                            >
                                <Save size={12} />
                                {saving.jira ? "Saving..." : "Save Settings"}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Email Automation Card */}
                <div className="bg-white dark:bg-zinc-900 rounded-xl border border-gray-200 dark:border-zinc-800 shadow-sm p-5 flex flex-col justify-between transition-all hover:shadow-md">
                    <div>
                        <div className="flex items-start justify-between mb-4 border-b border-gray-50 dark:border-zinc-800/80 pb-3">
                            <div className="flex items-center gap-3">
                                <div className="w-10 h-10 rounded-lg bg-purple-50 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0 border border-purple-100 dark:border-purple-900/40">
                                    <Mail size={20} />
                                </div>
                                <div>
                                    <h2 className="text-sm font-bold text-gray-800 dark:text-zinc-200">Email Automation</h2>
                                    <p className="text-[11px] text-gray-400 dark:text-zinc-500">Dispatch resolutions and escalation logs</p>
                                </div>
                            </div>
                            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full border text-emerald-600 bg-emerald-50/50 border-emerald-100 dark:text-emerald-400 dark:bg-emerald-950/20 dark:border-emerald-900/30">
                                Active Connector
                            </span>
                        </div>

                        {/* Config fields */}
                        <div className="space-y-4 pt-1">
                            <div>
                                <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">SMTP Server</label>
                                <input
                                    type="text"
                                    value="smtp.gmail.com (SSL Port 465)"
                                    disabled
                                    className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg px-3 py-2.5 mt-1 text-gray-400 dark:text-zinc-500 bg-gray-100 dark:bg-zinc-950 cursor-not-allowed font-medium"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Sender Email Address</label>
                                <input
                                    type="email"
                                    placeholder="your-app-email@gmail.com"
                                    value={configs.emailAddress}
                                    onChange={(e) => handleInputChange("emailAddress", e.target.value)}
                                    className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg px-3 py-2.5 mt-1 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all"
                                />
                            </div>

                            <div>
                                <label className="text-[10px] uppercase font-bold text-gray-400 dark:text-zinc-500 tracking-wider">Gmail App Password</label>
                                <div className="relative mt-1">
                                    <input
                                        type={showEmailPassword ? "text" : "password"}
                                        placeholder={configs.emailAppPassword ? "••••••••••••••••" : "Enter App Password"}
                                        value={configs.emailAppPassword}
                                        onChange={(e) => handleInputChange("emailAppPassword", e.target.value)}
                                        className="w-full text-xs border border-gray-200 dark:border-zinc-800 rounded-lg pl-3 pr-10 py-2.5 text-gray-700 dark:text-zinc-250 bg-gray-50 dark:bg-zinc-950 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600 focus:bg-white dark:focus:bg-zinc-900 transition-all font-mono"
                                    />
                                    <button
                                        type="button"
                                        onClick={() => setShowEmailPassword(!showEmailPassword)}
                                        className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-zinc-200 transition-colors"
                                    >
                                        {showEmailPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                                    </button>
                                </div>
                                <p className="text-[10px] text-gray-400 dark:text-zinc-500 mt-1 leading-normal">
                                    Requires a 16-character Gmail App Password. Enable 2-step verification in Google Account security to generate.
                                </p>
                            </div>
                        </div>

                        {/* Test Email Form Section */}
                        <div className="mt-5 p-3.5 bg-gray-50 dark:bg-zinc-950 border border-gray-150 dark:border-zinc-800/80 rounded-xl space-y-2.5">
                            <h3 className="text-xs font-bold text-gray-800 dark:text-zinc-300">Send Test Email</h3>
                            <div className="flex gap-2">
                                <input
                                    type="email"
                                    placeholder="recipient@domain.com"
                                    value={testRecipient}
                                    onChange={(e) => setTestRecipient(e.target.value)}
                                    className="flex-1 text-[11px] border border-gray-200 dark:border-zinc-800 rounded-lg px-2.5 py-1.5 text-gray-700 dark:text-zinc-250 bg-white dark:bg-zinc-900 focus:outline-none focus:ring-1 focus:ring-blue-500 dark:focus:ring-blue-600"
                                />
                                <button
                                    onClick={runTestEmail}
                                    disabled={testingEmail || !configs.emailAddress || !testRecipient}
                                    className="px-3 py-1.5 rounded-lg bg-purple-600 hover:bg-purple-700 text-white text-[11px] font-semibold transition-colors disabled:opacity-50 shrink-0"
                                >
                                    {testingEmail ? "Sending..." : "Send Test"}
                                </button>
                            </div>
                        </div>
                    </div>

                    {/* Actions and Feedback */}
                    <div className="mt-6 pt-4 border-t border-gray-150 dark:border-zinc-800/80 space-y-3">
                        {emailTestResult && (
                            <div className={`p-3 rounded-lg flex gap-2.5 text-xs ${
                                emailTestResult.status === "success" 
                                    ? "bg-green-50 dark:bg-green-950/20 border border-green-100 dark:border-green-900/30 text-green-700 dark:text-green-400" 
                                    : "bg-red-50 dark:bg-red-950/20 border border-red-100 dark:border-red-900/30 text-red-700 dark:text-red-400"
                            }`}>
                                {emailTestResult.status === "success" ? <CheckCircle2 size={16} className="shrink-0" /> : <AlertCircle size={16} className="shrink-0" />}
                                <span>{emailTestResult.message}</span>
                            </div>
                        )}

                        {saveResult.email && (
                            <div className={`p-2.5 rounded-lg text-center text-xs font-semibold ${
                                saveResult.email.status === "success"
                                    ? "bg-green-50 dark:bg-green-950/20 text-green-600 dark:text-green-400"
                                    : "bg-red-50 dark:bg-red-950/20 text-red-600 dark:text-red-400"
                            }`}>
                                {saveResult.email.message}
                            </div>
                        )}

                        <div className="flex gap-3 justify-end">
                            <button
                                onClick={() => handleSaveSettings("email")}
                                disabled={saving.email}
                                className="flex items-center gap-1.5 px-4 py-2 rounded-lg bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-colors disabled:opacity-75"
                            >
                                <Save size={12} />
                                {saving.email ? "Saving..." : "Save Settings"}
                            </button>
                        </div>
                    </div>
                </div>

            </div>

            {/* Note banner */}
            <div className="bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-900/30 rounded-xl p-4 flex gap-3 text-left">
                <AlertCircle className="text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" size={16} />
                <div>
                    <h4 className="text-xs font-semibold text-blue-900 dark:text-blue-400">Security & Storage Note</h4>
                    <p className="text-[11px] text-blue-700 dark:text-blue-500 mt-0.5 leading-relaxed">
                        These credentials are saved securely in the backend server config file (`integrations_config.json`) and used to run active integrations during the autonomous ticketing workflow. Credentials are never shared with client-side analytical reports.
                    </p>
                </div>
            </div>
        </div>
    );
}
