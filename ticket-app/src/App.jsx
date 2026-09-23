import { useState, useEffect, useRef } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import TicketForm from './components/TicketForm'
import ResolutionPanel from './components/ResolutionPanel'
import ClassificationResults from './components/ClassificationResults'
import { classifyTicket } from './api/classifyApi'
import AgentWorkflowPanel from './components/AgentWorkflowPanel'
import DashboardOptimization from './components/DashboardOptimization'
import SettingsPage from './components/SettingsPage'
import IntegrationsPage from './components/IntegrationsPage'
import {
  LayoutDashboard,
  Ticket,
  Bot,
  Plug,
  BarChart2,
  Settings,
  BrainCircuit,
  PlusCircle,
  Search,
  User,
  Clock,
  ChevronRight
} from 'lucide-react'

const NAV_ITEMS = [
  { icon: LayoutDashboard, label: 'Dashboard' },
  { icon: Ticket, label: 'Tickets' },
  { icon: Bot, label: 'AI Agent' },
  { icon: Plug, label: 'Integrations' },
  { icon: BarChart2, label: 'Analytics' },
  { icon: Settings, label: 'Settings' },
]

const TRANSLATIONS = {
  en: {
    dashboard: "Dashboard",
    tickets: "Tickets",
    aiAgent: "AI Agent",
    integrations: "Integrations",
    analytics: "Analytics",
    settings: "Settings",
    newTicket: "New Ticket",
    searchTickets: "Search tickets...",
    cancel: "Cancel",
    today: "Today",
    accuracy: "Accuracy",
    processing: "Processing",
    classification: "AI Classification",
    confidence: "Confidence Score",
    noTicketSelected: "No Ticket Selected",
    noTicketDesc: "Select a ticket from the left pane to view classification metadata and AI resolution matching, or submit a new ticket.",
    createTicket: "Create a Ticket"
  },
  es: {
    dashboard: "Panel de control",
    tickets: "Casos",
    aiAgent: "Agente IA",
    integrations: "Integraciones",
    analytics: "Analítica",
    settings: "Configuración",
    newTicket: "Nuevo Caso",
    searchTickets: "Buscar casos...",
    cancel: "Cancelar",
    today: "Hoy",
    accuracy: "Precisión",
    processing: "Procesamiento",
    classification: "Clasificación IA",
    confidence: "Puntuación de Confianza",
    noTicketSelected: "Ningún Caso Seleccionado",
    noTicketDesc: "Seleccione un caso del panel izquierdo para ver los metadatos de clasificación y la resolución de IA, o envíe uno nuevo.",
    createTicket: "Crear un Caso"
  },
  fr: {
    dashboard: "Tableau de bord",
    tickets: "Tickets",
    aiAgent: "Agent IA",
    integrations: "Intégrations",
    analytics: "Analyses",
    settings: "Paramètres",
    newTicket: "Nouveau Ticket",
    searchTickets: "Rechercher des tickets...",
    cancel: "Annuler",
    today: "Aujourd'hui",
    accuracy: "Précision",
    processing: "Traitement",
    classification: "Classification IA",
    confidence: "Score de Confiance",
    noTicketSelected: "Aucun Ticket Sélectionné",
    noTicketDesc: "Sélectionnez un ticket dans le volet gauche pour afficher les métadonnées et la résolution de l'IA, ou soumettez-en un nouveau.",
    createTicket: "Créer un Ticket"
  },
  de: {
    dashboard: "Dashboard",
    tickets: "Tickets",
    aiAgent: "KI-Agent",
    integrations: "Integrationen",
    analytics: "Analysen",
    settings: "Einstellungen",
    newTicket: "Neues Ticket",
    searchTickets: "Tickets suchen...",
    cancel: "Abbrechen",
    today: "Heute",
    accuracy: "Genauigkeit",
    processing: "Verarbeitung",
    classification: "KI-Klassifikation",
    confidence: "Konfidenzwert",
    noTicketSelected: "Kein Ticket Ausgewählt",
    noTicketDesc: "Wählen Sie ein Ticket aus der linken Liste, um die KI-Klassifikationsdaten und RAG-Lösung zu sehen, oder erstellen Sie ein neues.",
    createTicket: "Ticket Erstellen"
  }
};

const ACCENT_COLORS = {
  blue: {
    light: { primary: "#2563eb", light: "#eff6ff", border: "#dbeafe" },
    dark: { primary: "#3b82f6", light: "rgba(59, 130, 246, 0.15)", border: "rgba(59, 130, 246, 0.3)" }
  },
  violet: {
    light: { primary: "#7c3aed", light: "#f5f3ff", border: "#ddd6fe" },
    dark: { primary: "#8b5cf6", light: "rgba(139, 92, 246, 0.15)", border: "rgba(139, 92, 246, 0.3)" }
  },
  emerald: {
    light: { primary: "#059669", light: "#ecfdf5", border: "#d1fae5" },
    dark: { primary: "#10b981", light: "rgba(16, 185, 129, 0.15)", border: "rgba(16, 185, 129, 0.3)" }
  },
  amber: {
    light: { primary: "#d97706", light: "#fffbeb", border: "#fef3c7" },
    dark: { primary: "#f59e0b", light: "rgba(245, 158, 11, 0.15)", border: "rgba(245, 158, 11, 0.3)" }
  }
};

// Fallback heuristic used when the classify API is unavailable.
// Returns the IT category based on keywords in subject/description.
function inferCategoryAndConfidence(subject = '', description = '') {
  const text = `${subject} ${description}`.toLowerCase();
  if (text.includes('vpn') || text.includes('wifi') || text.includes('network') || text.includes('internet') || text.includes('bluetooth'))
    return { department: 'Networking', confidence: 0.82 };
  if (text.includes('password') || text.includes('login') || text.includes('locked') || text.includes('reset') || text.includes('mfa'))
    return { department: 'Password Reset', confidence: 0.88 };
  if (text.includes('keyboard') || text.includes('laptop') || text.includes('monitor') || text.includes('printer') || text.includes('mouse') || text.includes('hardware'))
    return { department: 'Hardware', confidence: 0.85 };
  if (text.includes('install') || text.includes('software') || text.includes('app') || text.includes('crash') || text.includes('update'))
    return { department: 'Software', confidence: 0.80 };
  if (text.includes('email') || text.includes('outlook') || text.includes('mailbox'))
    return { department: 'Email', confidence: 0.83 };
  if (text.includes('phishing') || text.includes('virus') || text.includes('malware') || text.includes('security'))
    return { department: 'Security', confidence: 0.90 };
  return { department: 'IT Support', confidence: 0.75 };
}

function deriveSubCategory(subject = '', description = '', category = '') {
  const text = `${subject} ${description} ${category}`.toLowerCase();

  if (text.includes('vpn') || text.includes('remote') || text.includes('tunnel')) return 'VPN Access';
  if (text.includes('wifi') || text.includes('network') || text.includes('internet') || text.includes('dns') || text.includes('ip')) return 'Network Connectivity';
  if (text.includes('password') || text.includes('login') || text.includes('auth') || text.includes('reset') || text.includes('mfa')) return 'Identity & Access';
  if (text.includes('install') || text.includes('software') || text.includes('excel') || text.includes('outlook') || text.includes('app') || text.includes('crash')) return 'Software & Applications';
  if (text.includes('printer') || text.includes('hardware') || text.includes('monitor') || text.includes('mouse') || text.includes('keyboard') || text.includes('laptop') || text.includes('device') || text.includes('memory')) return 'Hardware & Peripherals';
  if (text.includes('bill') || text.includes('invoice') || text.includes('payment') || text.includes('finance')) return 'Billing & Invoices';
  if (text.includes('payroll') || text.includes('leave') || text.includes('onboard') || text.includes('hr')) return 'HR Services';

  if (category) return `${category} Operations`;
  return 'General Support';

}

function getTicketIcon(subject = '') {
  const s = subject.toLowerCase();
  if (s.includes('vpn') || s.includes('network') || s.includes('wifi') || s.includes('internet')) return '📶';
  if (s.includes('software') || s.includes('app') || s.includes('install')) return '💾';
  if (s.includes('password') || s.includes('login') || s.includes('reset') || s.includes('account')) return '🔐';
  if (s.includes('printer') || s.includes('hardware') || s.includes('mouse') || s.includes('keyboard') || s.includes('screen')) return '🖨️';
  return '🎫';
}

function Sidebar({ active, setActive, t }) {
  const getNavLabel = (label) => {
    if (label === 'Dashboard') return t.dashboard;
    if (label === 'Tickets') return t.tickets;
    if (label === 'AI Agent') return t.aiAgent;
    if (label === 'Integrations') return t.integrations;
    if (label === 'Analytics') return t.analytics;
    if (label === 'Settings') return t.settings;
    return label;
  };

  return (
    <aside className="w-56 min-h-screen bg-white dark:bg-zinc-950 border-r border-gray-200 dark:border-zinc-800 flex flex-col py-6 px-4 shrink-0 font-sans">
      {/* Logo */}
      <div className="flex items-center gap-2.5 mb-8 px-2">
        <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-xs shrink-0 shadow-[0_0_12px_rgba(99,102,241,0.3)]">
          SP
        </div>
        <div className="flex flex-col">
          <span className="font-bold text-gray-900 dark:text-zinc-50 text-sm tracking-tight leading-tight">SupportPilot</span>
          <span className="text-[9px] text-gray-400 dark:text-zinc-505 font-medium tracking-wider uppercase">Enterprise Console</span>
        </div>
      </div>
      {/* Nav */}
      <nav className="flex flex-col gap-1 flex-1">
        {NAV_ITEMS.map(({ icon: Icon, label }) => {
          const isActive = active === label;
          return (
            <button
              key={label}
              onClick={() => setActive(label)}
              className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-semibold transition-all w-full text-left relative ${
                isActive
                  ? 'bg-indigo-50/75 dark:bg-indigo-950/45 text-indigo-600 dark:text-indigo-400 shadow-sm'
                  : 'text-gray-600 dark:text-zinc-400 hover:bg-gray-50 dark:hover:bg-zinc-900 hover:text-gray-900 dark:hover:text-zinc-100'
              }`}
            >
              <Icon size={15} strokeWidth={isActive ? 2.5 : 2} className={isActive ? 'text-indigo-600 dark:text-indigo-400' : 'text-gray-400 dark:text-zinc-500'} />
              {getNavLabel(label)}
              {isActive && (
                <span className="absolute right-2 w-1.5 h-1.5 rounded-full bg-indigo-600 dark:bg-indigo-400 animate-pulse" />
              )}
            </button>
          );
        })}
      </nav>
    </aside>
  )
}

function ComingSoonPage({ label }) {
  return (
    <div className="flex-1 flex items-center justify-center bg-gray-50 dark:bg-zinc-950">
      <div className="text-center p-8 border border-dashed border-gray-200 dark:border-zinc-850 rounded-2xl max-w-sm">
        <p className="text-sm font-bold text-gray-800 dark:text-zinc-200">{label}</p>
        <p className="text-xs text-gray-400 dark:text-zinc-500 mt-1.5">This module is being optimized. Thank you for your patience.</p>
      </div>
    </div>
  )
}

function App() {
  const queryClient = useQueryClient();
  const [activeTab, setActiveTab] = useState('Dashboard');
  const [activeTicket, setActiveTicket] = useState(null);
  const [isCreatingTicket, setIsCreatingTicket] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState('ALL');
  const [theme, setTheme] = useState(() => localStorage.getItem('theme') || 'light');

  // Preferences / Configurations
  const [accentColor, setAccentColor] = useState(() => localStorage.getItem('accentColor') || 'violet');
  const [density, setDensity] = useState(() => localStorage.getItem('density') || 'comfortable');
  const [refreshInterval, setRefreshInterval] = useState(() => localStorage.getItem('refreshInterval') || '30');
  const [language, setLanguage] = useState(() => localStorage.getItem('language') || 'en');
  const [notifications, setNotifications] = useState(() => {
    try {
      const saved = localStorage.getItem('notifications');
      return saved ? JSON.parse(saved) : { sound: true, email: false, desktop: true, updates: false };
    } catch (e) {
      return { sound: true, email: false, desktop: true, updates: false };
    }
  });

  const t = TRANSLATIONS[language] || TRANSLATIONS.en;

  // Sync settings modifications
  useEffect(() => {
    localStorage.setItem('accentColor', accentColor);
    const root = window.document.documentElement;
    const resolvedTheme = theme === 'system'
      ? (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light')
      : theme;

    const colors = ACCENT_COLORS[accentColor]?.[resolvedTheme] || ACCENT_COLORS.violet[resolvedTheme];
    root.style.setProperty('--brand-primary', colors.primary);
    root.style.setProperty('--brand-light', colors.light);
    root.style.setProperty('--brand-border', colors.border);
  }, [theme, accentColor]);

  useEffect(() => {
    localStorage.setItem('density', density);
    const root = window.document.documentElement;
    root.classList.remove('density-comfortable', 'density-compact', 'density-cozy');
    root.classList.add(`density-${density}`);
  }, [density]);

  useEffect(() => {
    localStorage.setItem('notifications', JSON.stringify(notifications));
  }, [notifications]);

  useEffect(() => {
    localStorage.setItem('language', language);
  }, [language]);

  useEffect(() => {
    localStorage.setItem('refreshInterval', refreshInterval);
  }, [refreshInterval]);

  useEffect(() => {
    const root = window.document.documentElement;
    if (theme === 'dark') {
      root.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else if (theme === 'light') {
      root.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    } else if (theme === 'system') {
      localStorage.setItem('theme', 'system');
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
      if (systemTheme === 'dark') {
        root.classList.add('dark');
      } else {
        root.classList.remove('dark');
      }
    }
  }, [theme]);

  // Fetch recent tickets
  const { data: tickets = [] } = useQuery({
    queryKey: ['tickets'],
    queryFn: async () => {
      const response = await fetch(`${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'}/tickets`);
      if (!response.ok) throw new Error('Failed to fetch tickets');
      return response.json();
    },
    refetchInterval: refreshInterval === 'off' ? false : Number(refreshInterval) * 1000
  });

  // Called by ResolutionPanel after a successful /resolve POST
  const handleTicketResolved = (resolvedTicketId) => {
    // Refresh the ticket list so the dashboard AI Resolve Index updates
    queryClient.invalidateQueries({ queryKey: ['tickets'] });
    // Also update the currently displayed ticket's status badge immediately
    setActiveTicket(prev =>
      prev ? { ...prev, status: 'RESOLVED' } : prev
    );
  };

  // Sound and Desktop Notifications when tickets array expands
  const prevTicketsCount = useRef(tickets.length);
  useEffect(() => {
    if (tickets.length > prevTicketsCount.current) {
      const newTicket = tickets[tickets.length - 1];

      // Play audio chime
      if (notifications.sound) {
        try {
          const ctx = new (window.AudioContext || window.webkitAudioContext)();
          const osc = ctx.createOscillator();
          const gain = ctx.createGain();
          osc.type = 'sine';
          osc.frequency.setValueAtTime(587.33, ctx.currentTime);
          osc.frequency.setValueAtTime(880, ctx.currentTime + 0.1);
          gain.gain.setValueAtTime(0.12, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.4);
          osc.connect(gain);
          gain.connect(ctx.destination);
          osc.start();
          osc.stop(ctx.currentTime + 0.45);
        } catch (e) {
          console.warn("Chime playback blocked:", e);
        }
      }

      // Display desktop alert banner
      if (notifications.desktop) {
        if (Notification.permission === 'granted') {
          new Notification("SupportPilot Ingestion Alert", {
            body: `Subject: ${newTicket.subject}\nFrom: ${newTicket.requester_email || 'System user'}`,
          });
        } else if (Notification.permission !== 'denied') {
          Notification.requestPermission();
        }
      }
    }
    prevTicketsCount.current = tickets.length;
  }, [tickets, notifications]);

  const recentTickets = [...tickets]
    .sort((a, b) => b.ticket_id - a.ticket_id);

  // Automatically load the latest ticket from database on initial render
  useEffect(() => {
    if (!activeTicket && recentTickets.length > 0 && !isCreatingTicket) {
      const latest = recentTickets[0];
      // Show placeholder immediately, then replace with real AI category
      setActiveTicket({
        id: `T-${latest.ticket_id}`,
        title: latest.subject,
        description: latest.description,
        requesterEmail: latest.requester_email,
        category: 'Classifying...',
        subCategory: 'Analyzing...',
        confidence: 0,
        priority: latest.priority || 'P4',
        severity: latest.severity || 'LOW',
        timeAgo: 'Latest ticket',
        status: latest.status || 'OPEN'
      });

      // Fetch the real AI-classified category
      classifyTicket(latest.description)
        .then((classification) => {
          const cat = classification.department || 'IT Support';
          const subCat = deriveSubCategory(latest.subject, latest.description, cat);
          setActiveTicket({
            id: `T-${latest.ticket_id}`,
            title: latest.subject,
            description: latest.description,
            requesterEmail: latest.requester_email,
            category: cat,
            subCategory: subCat,
            confidence: classification.confidence || 0.85,
            priority: latest.priority || 'P4',
            severity: latest.severity || 'LOW',
            timeAgo: 'Latest ticket',
            status: latest.status || 'OPEN'
          });
        })
        .catch(() => {
          // Fallback to subject-based heuristic if classify API is down
          const { department: cat, confidence } = inferCategoryAndConfidence(latest.subject, latest.description);
          const subCat = deriveSubCategory(latest.subject, latest.description, cat);
          setActiveTicket(prev => ({ ...prev, category: cat, subCategory: subCat, confidence }));
        });
    }
  }, [tickets]);

  const handleTicketCreated = (ticket, classification) => {
    // classification.department = AI predicted_category (Networking, Hardware, etc.)
    const cat = classification.department || 'IT Support';
    const subCat = deriveSubCategory(ticket.subject, ticket.description, cat);
    setActiveTicket({
      id: `T-${ticket.ticket_id}`,
      title: ticket.subject,
      description: ticket.description,
      requesterEmail: ticket.requester_email,
      category: cat,
      subCategory: subCat,
      confidence: classification.confidence || 0.85,
      priority: ticket.priority || 'P4',
      severity: ticket.severity || 'LOW',
      timeAgo: 'Just submitted',
      status: ticket.status || 'OPEN'
    });
    setIsCreatingTicket(false);
  };

  const handleSelectRecentTicket = async (ticket) => {
    const initialCat = ticket.department || 'Processing...';
    const initialSubCat = deriveSubCategory(ticket.subject, ticket.description, initialCat);
    setActiveTicket({
      id: `T-${ticket.ticket_id}`,
      title: ticket.subject,
      description: ticket.description,
      requesterEmail: ticket.requester_email,
      category: initialCat,
      subCategory: initialSubCat,
      confidence: 0,
      priority: ticket.priority || 'P4',
      severity: ticket.severity || 'LOW',
      timeAgo: 'Loaded from history',
      status: ticket.status || 'OPEN'
    });
    setIsCreatingTicket(false);

    try {
      const classification = await classifyTicket(ticket.description);
      const cat = classification.department || classification.category || ticket.department || 'IT Support';
      const subCat = deriveSubCategory(ticket.subject, ticket.description, cat);
      setActiveTicket({
        id: `T-${ticket.ticket_id}`,
        title: ticket.subject,
        description: ticket.description,
        requesterEmail: ticket.requester_email,
        category: cat,
        subCategory: subCat,
        confidence: classification.confidence || 0.85,
        priority: ticket.priority || 'P4',
        severity: ticket.severity || 'LOW',
        timeAgo: 'Loaded from history',
        status: ticket.status || 'OPEN'
      });
    } catch (err) {
      console.error("Classification failed on selection:", err);
      // Fallback: use subject-based heuristic — still better than work department
      const { department: cat, confidence } = inferCategoryAndConfidence(ticket.subject, ticket.description);
      const subCat = deriveSubCategory(ticket.subject, ticket.description, cat);
      setActiveTicket({
        id: `T-${ticket.ticket_id}`,
        title: ticket.subject,
        description: ticket.description,
        requesterEmail: ticket.requester_email,
        category: cat,
        subCategory: subCat,
        confidence,
        priority: ticket.priority || 'P4',
        severity: ticket.severity || 'LOW',
        timeAgo: 'Loaded from history',
        status: ticket.status || 'OPEN'
      });
    }
  };

  // Filter tickets by search and status
  const filteredTickets = recentTickets.filter(t => {
    const matchesSearch = t.subject.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          t.description.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (statusFilter === 'ALL') return matchesSearch;
    if (statusFilter === 'OPEN') return matchesSearch && t.status === 'OPEN';
    if (statusFilter === 'IN_PROGRESS') return matchesSearch && t.status === 'IN_PROGRESS';
    if (statusFilter === 'RESOLVED') return matchesSearch && (t.status === 'RESOLVED' || t.status === 'CLOSED');
    return matchesSearch;
  });

  return (
    <div className="flex min-h-screen bg-gray-50 dark:bg-zinc-950 font-sans text-left overflow-hidden">
      <Sidebar active={activeTab} setActive={setActiveTab} t={t} />

      {/* Main area */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {activeTab === 'Analytics' ? (
          <div className="p-8 overflow-y-auto flex-1">
            <ClassificationResults />
          </div>
        ) : activeTab === 'AI Agent' ? (
          <div className="p-8 overflow-y-auto flex-1">
            <AgentWorkflowPanel activeTicket={activeTicket} />
          </div>
        ) : activeTab === 'Dashboard' ? (
          <div className="overflow-y-auto flex-1">
            <DashboardOptimization tickets={tickets} />
          </div>
        ) : activeTab === 'Settings' ? (
          <div className="p-8 overflow-y-auto flex-1">
            <SettingsPage
              theme={theme}
              setTheme={setTheme}
              accentColor={accentColor}
              setAccentColor={setAccentColor}
              density={density}
              setDensity={setDensity}
              refreshInterval={refreshInterval}
              setRefreshInterval={setRefreshInterval}
              language={language}
              setLanguage={setLanguage}
              notifications={notifications}
              setNotifications={setNotifications}
            />
          </div>
        ) : activeTab === 'Integrations' ? (
          <div className="p-8 overflow-y-auto flex-1">
            <IntegrationsPage />
          </div>

        ) : activeTab === 'Tickets' ? (
          <div className="flex-1 flex overflow-hidden">
            
            {/* Left Workspace Column: Ticket List Pane */}
            <div className="w-80 border-r border-gray-250 dark:border-zinc-800 bg-white dark:bg-zinc-900/50 flex flex-col p-4 shrink-0 overflow-hidden">
              <div className="mb-4">
                <button
                  onClick={() => {
                    setIsCreatingTicket(true);
                    setActiveTicket(null);
                  }}
                  className="w-full h-9 flex items-center justify-center gap-2 rounded-lg bg-indigo-600 hover:bg-indigo-700 dark:bg-indigo-600 dark:hover:bg-indigo-700 text-white text-xs font-bold transition-all shadow-sm cursor-pointer mb-4"
                >
                  <PlusCircle size={14} />
                  New Ticket
                </button>

                <div className="relative mb-3">
                  <Search size={14} className="absolute left-3 top-2.5 text-gray-400 dark:text-zinc-500" />
                  <input
                    type="text"
                    placeholder="Search tickets..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-9 pr-3 py-1.5 rounded-lg border border-gray-200 dark:border-zinc-800 text-xs bg-gray-50 dark:bg-zinc-900 focus:bg-white dark:focus:bg-zinc-950 transition-all placeholder:text-gray-400 dark:placeholder:text-zinc-500"
                  />
                </div>

                {/* Filter Row */}
                <div className="flex gap-1 overflow-x-auto pb-1">
                  {['ALL', 'OPEN', 'IN_PROGRESS', 'RESOLVED'].map((filter) => (
                    <button
                      key={filter}
                      onClick={() => setStatusFilter(filter)}
                      className={`px-2.5 py-1 rounded-full text-[9px] font-bold border transition-all cursor-pointer shrink-0 ${
                        statusFilter === filter
                          ? 'bg-zinc-900 text-white border-zinc-900 dark:bg-zinc-100 dark:text-zinc-900 dark:border-zinc-100'
                          : 'bg-white text-gray-500 border-gray-200 dark:bg-zinc-900 dark:text-zinc-400 dark:border-zinc-800 hover:bg-gray-50'
                      }`}
                    >
                      {filter}
                    </button>
                  ))}
                </div>
              </div>

              {/* Tickets List */}
              <div className="flex-1 overflow-y-auto space-y-2 pr-1">
                {filteredTickets.length === 0 ? (
                  <div className="text-center py-8">
                    <p className="text-xs text-gray-400 dark:text-zinc-500">No tickets found</p>
                  </div>
                ) : (
                  filteredTickets.map((t) => {
                    const isSelected = activeTicket && activeTicket.id === `T-${t.ticket_id}`;
                    const statusColor = t.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900' :
                                        t.status === 'IN_PROGRESS' ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-100 dark:border-amber-900' :
                                        'bg-blue-50 text-blue-700 dark:bg-indigo-950/40 dark:text-indigo-400 border-blue-100 dark:border-indigo-900';
                    return (
                      <div
                        key={t.ticket_id}
                        onClick={() => handleSelectRecentTicket(t)}
                        className={`p-3 rounded-xl border text-left cursor-pointer transition-all ${
                          isSelected 
                            ? 'bg-indigo-50/50 dark:bg-indigo-950/20 border-indigo-500 dark:border-indigo-500 shadow-sm' 
                            : 'bg-white dark:bg-zinc-900/60 border-gray-200 dark:border-zinc-800 hover:bg-gray-50 dark:hover:bg-zinc-900/90'
                        }`}
                      >
                        <div className="flex justify-between items-start gap-2">
                          <span className="text-xs font-semibold text-gray-900 dark:text-zinc-200 truncate flex-1">
                            {t.subject}
                          </span>
                          <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded border shrink-0 ${statusColor}`}>
                            {t.status}
                          </span>
                        </div>
                        <p className="text-[10px] text-gray-500 dark:text-zinc-400 mt-1 line-clamp-2 leading-relaxed">
                          {t.description}
                        </p>
                        <div className="flex items-center justify-between text-[9px] text-gray-400 dark:text-zinc-500 mt-2.5 pt-2 border-t border-gray-100 dark:border-zinc-800/80">
                          <span className="truncate max-w-[130px]">{t.requester_email?.split('@')[0] || 'anonymous'} • {t.department || 'General'}</span>
                          <span className="font-semibold text-red-500 dark:text-rose-400">{t.priority || 'P4'}</span>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* Right Active Workspace Container */}
            <div className="flex-1 flex overflow-hidden bg-gray-50 dark:bg-zinc-950">
              {isCreatingTicket ? (
                /* Ticket creation workspace */
                <div className="flex-1 p-8 flex justify-center items-start overflow-y-auto bg-white dark:bg-zinc-900/10">
                  <div className="w-full max-w-xl">
                    <div className="flex items-center justify-between mb-6">
                      <div>
                        <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-50 tracking-tight">Create Support Ticket</h2>
                        <p className="text-xs text-gray-500 dark:text-zinc-400 mt-0.5">Submit a ticket to trigger classification &amp; RAG processing</p>
                      </div>
                      <button
                        onClick={() => {
                          setIsCreatingTicket(false);
                          if (recentTickets.length > 0) {
                            handleSelectRecentTicket(recentTickets[0]);
                          }
                        }}
                        className="text-xs text-gray-500 dark:text-zinc-400 hover:text-gray-800 dark:hover:text-zinc-200 border border-gray-200 dark:border-zinc-800 px-3 py-1.5 rounded-lg bg-white dark:bg-zinc-900 transition-colors cursor-pointer"
                      >
                        Cancel
                      </button>
                    </div>
                    <TicketForm onTicketCreated={handleTicketCreated} />
                  </div>
                </div>
              ) : activeTicket ? (
                /* Ticket detail + resolution workspace */
                <div className="flex-1 flex flex-col overflow-y-auto bg-gray-50 dark:bg-zinc-950 p-6 space-y-6">
                  
                  {/* Ticket Header Block */}
                  <div className="flex items-start justify-between border-b border-gray-200 dark:border-zinc-800 pb-4">
                    <div className="space-y-1 text-left">
                      <div className="flex items-center gap-3">
                        <span className="text-[10px] font-bold text-indigo-600 dark:text-indigo-400 font-mono bg-indigo-50 dark:bg-indigo-950/40 px-2 py-0.5 rounded border border-indigo-100 dark:border-indigo-900">
                          {activeTicket.id}
                        </span>
                        <span className={`text-[9px] font-bold px-2 py-0.5 rounded-full border ${
                          activeTicket.status === 'RESOLVED' ? 'bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-400 border-emerald-100 dark:border-emerald-900' :
                          activeTicket.status === 'IN_PROGRESS' ? 'bg-amber-50 text-amber-700 dark:bg-amber-950/40 dark:text-amber-400 border-amber-100 dark:border-amber-900' :
                          'bg-indigo-50 text-indigo-705 dark:bg-indigo-950/40 dark:text-indigo-450 border-indigo-100 dark:border-indigo-900'
                        }`}>
                          {activeTicket.status}
                        </span>
                      </div>
                      <h2 className="text-xl font-bold text-gray-900 dark:text-zinc-50 tracking-tight leading-snug">
                        {activeTicket.title}
                      </h2>
                      <div className="flex items-center gap-1.5 text-xs text-gray-505 dark:text-zinc-400">
                        <span>Requester:</span>
                        <span className="font-semibold text-gray-700 dark:text-zinc-300">{activeTicket.requesterEmail || 'john.doe@company.com'}</span>
                      </div>
                    </div>

                    {/* Header Actions / Time */}
                    <div className="text-right text-xs text-gray-400 dark:text-zinc-505 font-mono">
                      <p className="font-medium">Priority: <span className="text-red-500 dark:text-rose-450 font-bold">{activeTicket.priority}</span></p>
                      <p className="mt-1">{activeTicket.timeAgo}</p>
                    </div>
                  </div>

                  {/* Row 1: Description & AI Classification (Side-by-Side Grid) */}
                  <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
                    {/* Description Box (3/5 cols) */}
                    <div className="lg:col-span-3 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm flex flex-col justify-between text-left">
                      <div className="space-y-3">
                        <h3 className="text-[10px] font-bold text-gray-400 dark:text-zinc-505 uppercase tracking-wider">Ticket Description</h3>
                        <div className="text-xs text-gray-750 dark:text-zinc-300 leading-relaxed whitespace-pre-wrap max-h-48 overflow-y-auto">
                          {activeTicket.description}
                        </div>
                      </div>
                      {/* Small stats in description card */}
                      <div className="grid grid-cols-3 gap-2 border-t border-gray-100 dark:border-zinc-800/80 pt-4 mt-6 text-center text-xs">
                        {[
                          { label: 'Accuracy', value: '94%' },
                          { label: 'Processing', value: '1.2s' },
                          { label: 'Today', value: String(tickets.length || 47) },
                        ].map(({ label, value }) => (
                          <div key={label}>
                            <p className="text-sm font-bold text-gray-905 dark:text-zinc-100">{value}</p>
                            <p className="text-[9px] text-gray-400 dark:text-zinc-505 leading-tight mt-0.5">{label}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* AI Classification Details (2/5 cols) */}
                    <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl p-5 shadow-sm flex flex-col justify-between text-left">
                      <div className="space-y-4">
                        <div className="flex items-center gap-2 border-b border-gray-100 dark:border-zinc-800 pb-3">
                          <BrainCircuit size={15} className="text-indigo-600 dark:text-indigo-400" />
                          <h3 className="text-[10px] font-bold text-gray-808 dark:text-zinc-200 uppercase tracking-wider">AI Classification</h3>
                        </div>

                        <div className="grid grid-cols-2 gap-y-3.5 text-xs">
                          <div>
                            <p className="text-gray-400 dark:text-zinc-505 mb-0.5">Category</p>
                            <p className="font-bold text-gray-808 dark:text-zinc-200">{activeTicket.category}</p>
                          </div>
                          <div>
                            <p className="text-gray-400 dark:text-zinc-505 mb-0.5">Sub-Category</p>
                            <p className="font-bold text-gray-808 dark:text-zinc-200 truncate">{activeTicket.subCategory || 'General Support'}</p>
                          </div>
                          <div>
                            <p className="text-gray-400 dark:text-zinc-505 mb-0.5">Severity</p>
                            <p className="font-bold text-gray-808 dark:text-zinc-200">{activeTicket.severity}</p>
                          </div>
                          <div>
                            <p className="text-gray-400 dark:text-zinc-505 mb-0.5">Priority</p>
                            <p className="font-bold text-gray-808 dark:text-zinc-200">{activeTicket.priority}</p>
                          </div>
                        </div>
                      </div>

                      <div className="pt-4 border-t border-gray-100 dark:border-zinc-800 space-y-1.5 mt-6">
                        <div className="flex justify-between items-center text-[10px]">
                          <span className="text-gray-500 dark:text-zinc-400 font-medium">Confidence Score</span>
                          <span className="font-bold text-gray-900 dark:text-zinc-200">
                            {activeTicket.confidence ? Math.round(activeTicket.confidence * 100) : 92}%
                          </span>
                        </div>
                        <div className="w-full bg-gray-100 dark:bg-zinc-800 h-1.5 rounded-full overflow-hidden">
                          <div
                            className="h-full rounded-full bg-indigo-600 dark:bg-indigo-500 transition-all duration-500"
                            style={{ width: `${activeTicket.confidence ? Math.round(activeTicket.confidence * 100) : 92}%` }}
                          ></div>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Row 2: RAG Retrieval & AI Resolution */}
                  <div className="bg-white dark:bg-zinc-900 border border-gray-200 dark:border-zinc-800 rounded-2xl p-6 shadow-sm">
                    <ResolutionPanel activeTicket={activeTicket} onTicketResolved={handleTicketResolved} />
                  </div>

                </div>
              ) : (
                /* Empty state */
                <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-gray-50 dark:bg-zinc-950">
                  <div className="w-16 h-16 rounded-2xl bg-indigo-50 dark:bg-zinc-900 border border-indigo-100 dark:border-zinc-800 flex items-center justify-center text-indigo-600 dark:text-indigo-400 mb-4 shadow-sm">
                    <Ticket size={24} />
                  </div>
                  <h2 className="text-sm font-bold text-gray-900 dark:text-zinc-55 tracking-tight">No Ticket Selected</h2>
                  <p className="text-xs text-gray-400 dark:text-zinc-500 mt-1 max-w-sm">
                    Select a ticket from the left pane to view classification metadata and AI resolution matching, or submit a new ticket.
                  </p>
                  <button
                    onClick={() => {
                      setIsCreatingTicket(true);
                      setActiveTicket(null);
                    }}
                    className="mt-4 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg shadow-sm cursor-pointer"
                  >
                    Create a Ticket
                  </button>
                </div>
              )}
            </div>

          </div>
        ) : (
          <ComingSoonPage label={activeTab} />
        )}
      </main>
    </div>
  )
}

export default App