import { useState } from "react";
import {
    Sliders,
    Bell,
    Palette,
    Trash2,
    CheckCircle2,
    Info,
    Smartphone,
    Globe,
    Tv,
} from "lucide-react";

function Toggle({ checked, onChange }) {
    return (
        <button
            onClick={() => onChange(!checked)}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors shrink-0 ${checked ? "bg-blue-600" : "bg-gray-200"
                }`}
        >
            <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform shadow ${checked ? "translate-x-6" : "translate-x-1"
                    }`}
            />
        </button>
    );
}

function SettingRow({ icon: Icon, title, description, control }) {
    return (
        <div className="flex items-center justify-between gap-4 py-3.5 border-b border-gray-100 last:border-b-0">
            <div className="flex items-start gap-3 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-gray-50 text-gray-500 flex items-center justify-center shrink-0 mt-0.5">
                    <Icon size={15} />
                </div>
                <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-800">{title}</p>
                    {description && (
                        <p className="text-xs text-gray-400 mt-0.5">{description}</p>
                    )}
                </div>
            </div>
            {control}
        </div>
    );
}

export default function SettingsPage({
    theme,
    setTheme,
    accentColor,
    setAccentColor,
    density,
    setDensity,
    refreshInterval,
    setRefreshInterval,
    language,
    setLanguage,
    notifications,
    setNotifications
}) {
    // Cache clearing simulation state
    const [clearing, setClearing] = useState(false);
    const [clearedSuccess, setClearedSuccess] = useState(false);

    const updateNotification = (key, val) => {
        setNotifications((prev) => ({ ...prev, [key]: val }));
    };

    const handleClearCache = () => {
        setClearing(true);
        setClearedSuccess(false);
        setTimeout(() => {
            localStorage.clear();
            setTheme("light");
            setAccentColor("violet");
            setDensity("comfortable");
            setRefreshInterval("30");
            setLanguage("en");
            setNotifications({
                sound: true,
                email: false,
                desktop: true,
                updates: false,
            });
            setClearing(false);
            setClearedSuccess(true);
            // Hide the success message after 3 seconds
            setTimeout(() => setClearedSuccess(false), 3000);
        }, 1000);
    };


    return (
        <div className="space-y-6 max-w-3xl font-sans text-left">
            {/* Header */}
            <div>
                <h1 className="text-2xl font-bold text-gray-900 tracking-tight">Settings</h1>
                <p className="text-sm text-gray-500 mt-0.5">
                    Configure your display preferences and notifications.
                </p>
            </div>

            {/* Appearance Preferences */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                <h2 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Palette size={16} className="text-blue-600" />
                    Appearance & Theme
                </h2>
                
                {/* Theme Selector */}
                <div className="grid grid-cols-3 gap-3 mb-5">
                    {[
                        { id: "light", label: "Light Theme", icon: "☀️" },
                        { id: "dark", label: "Dark Theme", icon: "🌙" },
                        { id: "system", label: "System Auto", icon: "💻" },
                    ].map((item) => (
                        <button
                            key={item.id}
                            onClick={() => setTheme(item.id)}
                            className={`flex flex-col items-center gap-2 p-3 rounded-lg border text-xs font-medium transition-all ${theme === item.id
                                    ? "border-blue-600 bg-blue-50/50 text-blue-700 font-semibold"
                                    : "border-gray-200 hover:bg-gray-50 text-gray-600"
                                }`}
                        >
                            <span className="text-lg">{item.icon}</span>
                            {item.label}
                        </button>
                    ))}
                </div>

                {/* Accent Color Selection */}
                <div>
                    <label className="text-[10px] uppercase font-bold text-gray-400 tracking-wider">UI Accent Color</label>
                    <div className="flex gap-3 mt-2">
                        {[
                            { id: "blue", class: "bg-blue-600", label: "Blue" },
                            { id: "violet", class: "bg-violet-600", label: "Violet" },
                            { id: "emerald", class: "bg-emerald-600", label: "Emerald" },
                            { id: "amber", class: "bg-amber-600", label: "Amber" },
                        ].map((color) => (
                            <button
                                key={color.id}
                                onClick={() => setAccentColor(color.id)}
                                className={`flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-medium transition-all border ${accentColor === color.id
                                        ? "border-gray-900 bg-gray-900 text-white font-semibold"
                                        : "border-gray-200 bg-white hover:bg-gray-50 text-gray-600"
                                    }`}
                            >
                                <span className={`w-2.5 h-2.5 rounded-full ${color.class}`} />
                                {color.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Display & Layout Settings */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                <h2 className="text-sm font-semibold text-gray-800 mb-4 flex items-center gap-2">
                    <Sliders size={16} className="text-blue-600" />
                    Display Preferences
                </h2>

                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block">Layout Density</label>
                        <select
                            value={density}
                            onChange={(e) => setDensity(e.target.value)}
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                            <option value="comfortable">Comfortable</option>
                            <option value="compact">Compact</option>
                            <option value="cozy">Cozy</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block">Auto-Refresh Interval</label>
                        <select
                            value={refreshInterval}
                            onChange={(e) => setRefreshInterval(e.target.value)}
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                            <option value="off">Off (Manual)</option>
                            <option value="15">Every 15s</option>
                            <option value="30">Every 30s</option>
                            <option value="60">Every 60s</option>
                        </select>
                    </div>

                    <div>
                        <label className="text-xs text-gray-500 mb-1.5 block">Default Language</label>
                        <select
                            value={language}
                            onChange={(e) => setLanguage(e.target.value)}
                            className="w-full text-sm border border-gray-200 rounded-lg px-3 py-2 text-gray-700 bg-white focus:outline-none focus:ring-1 focus:ring-blue-500"
                        >
                            <option value="en">English (US)</option>
                            <option value="es">Español</option>
                            <option value="fr">Français</option>
                            <option value="de">Deutsch</option>
                        </select>
                    </div>
                </div>
            </div>

            {/* Notification Toggles */}
            <div className="bg-white rounded-xl border border-gray-200 shadow-sm p-5">
                <h2 className="text-sm font-semibold text-gray-800 mb-1 flex items-center gap-2">
                    <Bell size={16} className="text-blue-600" />
                    System Notifications
                </h2>
                <div className="divide-y divide-gray-50">
                    <SettingRow
                        icon={Tv}
                        title="Desktop Banner Notifications"
                        description="Show desktop slide-in alert notifications for P1/P2 tickets"
                        control={
                            <Toggle
                                checked={notifications.desktop}
                                onChange={(val) => updateNotification("desktop", val)}
                            />
                        }
                    />
                    <SettingRow
                        icon={Smartphone}
                        title="Sound Alerts"
                        description="Play a subtle chime sound whenever a new ticket arrives"
                        control={
                            <Toggle
                                checked={notifications.sound}
                                onChange={(val) => updateNotification("sound", val)}
                            />
                        }
                    />
                    <SettingRow
                        icon={Globe}
                        title="Weekly Performance Digests"
                        description="Receive automated email analytics reports on AI performance weekly"
                        control={
                            <Toggle
                                checked={notifications.updates}
                                onChange={(val) => updateNotification("updates", val)}
                            />
                        }
                    />
                </div>
            </div>

            {/* Danger Zone / Cache Management */}
            <div className="bg-white rounded-xl border border-red-100 shadow-sm p-5">
                <h2 className="text-sm font-semibold text-red-700 mb-2 flex items-center gap-2">
                    <Trash2 size={16} />
                    Maintenance
                </h2>
                <p className="text-xs text-gray-500 mb-4 leading-relaxed">
                    Clear local browser cookies and system storage tags associated with SupportPilot dashboard preferences. This action will reset theme, filters, and layouts back to defaults.
                </p>
                <div className="flex items-center gap-4">
                    <button
                        onClick={handleClearCache}
                        disabled={clearing}
                        className="px-4 py-2 bg-red-50 hover:bg-red-100 text-red-700 rounded-lg text-xs font-semibold border border-red-200 transition-colors disabled:opacity-60"
                    >
                        {clearing ? "Clearing Storage..." : "Reset System Preferences"}
                    </button>

                    {clearedSuccess && (
                        <span className="flex items-center gap-1.5 text-xs text-green-600 font-semibold animate-pulse">
                            <CheckCircle2 size={14} /> Local cache reset complete!
                        </span>
                    )}
                </div>
            </div>

            {/* Quick Info Box */}
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-4 flex gap-3 text-left">
                <Info className="text-gray-500 shrink-0 mt-0.5" size={16} />
                <div>
                    <h4 className="text-xs font-semibold text-gray-800">SupportPilot Client Info</h4>
                    <p className="text-[11px] text-gray-500 mt-0.5 leading-relaxed">
                        Client Version: v0.4.2 • Platform Mode: Frontend Sandbox • UI Library: React 19 / Lucide Icon Engine
                    </p>
                </div>
            </div>
        </div>
    );
}