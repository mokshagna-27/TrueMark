import { useState } from "react";
import "./App.css";

const navigation = [
  { name: "Overview", icon: "◫" },
  { name: "Content Analysis", icon: "⌕" },
  { name: "Brand Guidelines", icon: "✳" },
  { name: "Brand Assets", icon: "▧" },
  { name: "Review & Approval", icon: "✓" },
  { name: "Version History", icon: "◷" },
  { name: "Governance Insights", icon: "▥" },
];

function App() {
  const [activePage, setActivePage] = useState("Overview");

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">I</div>
          <div>
            <h1>inkloom<span>AI</span></h1>
            <p>BRAND INTELLIGENCE</p>
          </div>
        </div>

        <button className="workspace">
          <div className="workspace-icon">T</div>
          <div className="workspace-copy">
            <strong>The Innovators</strong>
            <span>Workspace</span>
          </div>
          <span className="workspace-arrow">⌄</span>
        </button>

        <p className="nav-label">WORKSPACE</p>
        <nav className="navigation">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${activePage === item.name ? "active" : ""}`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>
              {item.name === "Review & Approval" && (
                <span className="nav-count">4</span>
              )}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="help-card">
            <div className="help-icon">✦</div>
            <strong>Need a hand?</strong>
            <p>Explore how to get the most out of Inkloom AI.</p>
            <button onClick={() => alert("Help center will be added soon.")}>
              Visit help center ↗
            </button>
          </div>

          <button className="profile">
            <div className="avatar">PG</div>
            <div className="profile-copy">
              <strong>Workspace Admin</strong>
              <span>Administrator</span>
            </div>
            <span className="profile-menu">•••</span>
          </button>
        </div>
      </aside>

      <main className="main-area">
        <header className="topbar">
          <div className="breadcrumbs">
            Workspace <span>/</span> <strong>{activePage}</strong>
          </div>
          <div className="topbar-actions">
            <div className="system-status">
              <span className="status-dot"></span>
              Workspace active
            </div>
            <button
              className="icon-button"
              aria-label="Notifications"
              onClick={() => alert("Notifications will be connected later.")}
            >
              ♧<span className="notification-dot"></span>
            </button>
            <div className="avatar top-avatar">PG</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === "Overview" ? (
            <Overview onNavigate={setActivePage} />
          ) : (
            <SectionPlaceholder
              title={activePage}
              onNavigate={setActivePage}
            />
          )}

          <footer className="footer">
            <span>© 2026 Inkloom AI</span>
            <span>Built for consistent, confident brand communication.</span>
            <span className="footer-status">
              <span className="status-dot"></span> All systems operational
            </span>
          </footer>
        </div>
      </main>
    </div>
  );
}

function Overview({
  onNavigate,
}: {
  onNavigate: (page: string) => void;
}) {
  return (
    <>
      <section className="welcome-row">
        <div>
          <div className="eyebrow">
            <span className="sparkle">✦</span> YOUR BRAND, IN SYNC
          </div>
          <h2>Good to see you.</h2>
          <p className="welcome-description">
            Keep every piece of content aligned with your brand standards.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => onNavigate("Content Analysis")}
        >
          <span>＋</span> New content review
        </button>
      </section>

      <section className="hero-card">
        <div className="hero-copy">
          <div className="hero-badge">
            <span>✦</span> YOUR BRAND GOVERNANCE HUB
          </div>
          <h3>Consistency isn't a guess.<br />It's your brand advantage.</h3>
          <p>
            Review content, catch inconsistencies, and keep your team's
            communication true to your brand—all in one place.
          </p>
          <button
            className="hero-button"
            onClick={() => onNavigate("Content Analysis")}
          >
            Analyze your content <span>→</span>
          </button>
        </div>
        <div className="hero-art" aria-hidden="true">
          <div className="orbit orbit-one"></div>
          <div className="orbit orbit-two"></div>
          <div className="orbit orbit-three"></div>
          <div className="art-core">
            <div className="art-core-inner">i</div>
          </div>
          <div className="floating-card floating-card-one">
            <span className="floating-check">✓</span>
            <div><strong>Brand aligned</strong><small>Content consistency</small></div>
          </div>
          <div className="floating-card floating-card-two">
            <span className="floating-sparkle">✦</span>
            <div><strong>Smart review</strong><small>Guideline insights</small></div>
          </div>
          <div className="art-dot dot-one"></div>
          <div className="art-dot dot-two"></div>
        </div>
      </section>

      <section className="metrics-grid">
        <MetricCard
          label="Content reviewed"
          value="—"
          note="Connect your first review"
          icon="▤"
          tone="purple"
        />
        <MetricCard
          label="Needs attention"
          value="—"
          note="Awaiting real analysis data"
          icon="⌕"
          tone="orange"
        />
        <MetricCard
          label="Pending approvals"
          value="—"
          note="Review queue not connected"
          icon="◷"
          tone="blue"
        />
        <MetricCard
          label="Brand guidelines"
          value="—"
          note="Configure your brand rules"
          icon="✳"
          tone="green"
        />
      </section>

      <section className="content-grid">
        <div className="panel quick-actions-panel">
          <div className="panel-heading">
            <div>
              <h3>Get things moving</h3>
              <p>Jump straight into your workflow.</p>
            </div>
            <span className="heading-decoration">✳</span>
          </div>

          <button
            className="action-row"
            onClick={() => onNavigate("Content Analysis")}
          >
            <span className="action-icon action-purple">⌕</span>
            <span className="action-copy">
              <strong>Review new content</strong>
              <small>Check copy against your brand guidelines</small>
            </span>
            <span className="action-arrow">→</span>
          </button>

          <button
            className="action-row"
            onClick={() => onNavigate("Brand Guidelines")}
          >
            <span className="action-icon action-green">✳</span>
            <span className="action-copy">
              <strong>Set up brand guidelines</strong>
              <small>Define your voice, rules, and terminology</small>
            </span>
            <span className="action-arrow">→</span>
          </button>

          <button
            className="action-row"
            onClick={() => onNavigate("Review & Approval")}
          >
            <span className="action-icon action-orange">✓</span>
            <span className="action-copy">
              <strong>Visit the review queue</strong>
              <small>Manage comments and approval workflows</small>
            </span>
            <span className="action-arrow">→</span>
          </button>

          <button
            className="action-row"
            onClick={() => onNavigate("Brand Assets")}
          >
            <span className="action-icon action-blue">▧</span>
            <span className="action-copy">
              <strong>Manage brand assets</strong>
              <small>Organize approved brand resources</small>
            </span>
            <span className="action-arrow">→</span>
          </button>
        </div>

        <div className="panel readiness-panel">
          <div className="panel-heading">
            <div>
              <h3>Workspace readiness</h3>
              <p>Prepare your brand for its first review.</p>
            </div>
            <span className="readiness-icon">✦</span>
          </div>

          <div className="readiness-banner">
            <div className="readiness-banner-icon">◎</div>
            <div>
              <strong>Let's get your workspace ready</strong>
              <p>Complete these steps to begin reviewing content.</p>
            </div>
          </div>

          <div className="checklist">
            <div className="checklist-item">
              <span className="check-empty"></span>
              <div>
                <strong>Define your brand guidelines</strong>
                <p>Set tone, terminology, and approved facts.</p>
              </div>
              <button onClick={() => onNavigate("Brand Guidelines")}>Set up →</button>
            </div>
            <div className="checklist-item">
              <span className="check-empty"></span>
              <div>
                <strong>Add approved brand assets</strong>
                <p>Organize logos and other brand resources.</p>
              </div>
              <button onClick={() => onNavigate("Brand Assets")}>Add →</button>
            </div>
            <div className="checklist-item">
              <span className="check-empty"></span>
              <div>
                <strong>Run your first content review</strong>
                <p>Test content against your brand rules.</p>
              </div>
              <button onClick={() => onNavigate("Content Analysis")}>Start →</button>
            </div>
          </div>

          <div className="privacy-note">
            <span>♧</span>
            Your brand content should stay protected. Configure storage and
            AI-service privacy before using confidential material.
          </div>
        </div>
      </section>
    </>
  );
}

function MetricCard({
  label,
  value,
  note,
  icon,
  tone,
}: {
  label: string;
  value: string;
  note: string;
  icon: string;
  tone: string;
}) {
  return (
    <div className="metric-card">
      <div className="metric-top">
        <span>{label}</span>
        <span className={"metric-icon " + tone}>{icon}</span>
    </div>
      <div className="metric-value">{value}</div>
      <p className="metric-note">{note}</p>
    </div>
  );
}

function SectionPlaceholder({
  title,
  onNavigate,
}: {
  title: string;
  onNavigate: (page: string) => void;
}) {
  const descriptions: Record<string, string> = {
    "Content Analysis":
      "Submit content for brand-rule checks, explanations, and suggested corrections.",
    "Brand Guidelines":
      "Define the approved voice, terminology, messaging, facts, and content rules for your brand.",
    "Brand Assets":
      "Organize approved logos, images, and other brand resources.",
    "Review & Approval":
      "Coordinate feedback, reviewer decisions, and content approval.",
    "Version History":
      "Track revisions and understand how reviewed content changes over time.",
    "Governance Insights":
      "Explore recurring content issues and discover where your brand rules need attention.",
  };

  return (
    <section className="section-placeholder">
      <div className="eyebrow"><span className="sparkle">✦</span> INKLOOM AI WORKSPACE</div>
      <div className="placeholder-icon">✳</div>
      <h2>{title}</h2>
      <p>{descriptions[title] ?? "Manage your brand governance workspace."}</p>
      <div className="coming-soon">
        <span className="status-dot"></span>
        Interface foundation ready · Feature implementation in progress
      </div>
      <button className="primary-button" onClick={() => onNavigate("Overview")}>
        ← Back to overview
      </button>
    </section>
  );
}

export default App;