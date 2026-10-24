import { useEffect, useMemo, useState, type FormEvent } from "react";
import AnalysisContent from "./components/analysis/analysiscontent";
import BrandGuidelines from "./components/brandguidelines";
import "./App.css";

/* =========================
   NAVIGATION
========================= */

const navigation = [
  { name: "Overview", icon: "◫" },
  { name: "Content Analysis", icon: "⌕" },
  { name: "Brand Guidelines", icon: "✳" },
  { name: "Brand Assets", icon: "▧" },
  { name: "Review & Approval", icon: "✓" },
  { name: "Version History", icon: "◷" },
  { name: "Governance Insights", icon: "▥" },
];

const descriptions: Record<string, string> = {
  "Version History":
    "Track content changes and maintain a clear history of brand-related decisions.",
};

/* =========================
   TYPES
========================= */

type BrandAsset = {
  id: string;
  name: string;
  category: string;
  description: string;
  fileName: string;
  fileType: string;
  fileSize: number;
  addedAt: string;
  dataUrl?: string;
};

type AnalysisRecord = {
  id: string;
  date: string;
  status: string;
  findingsCount: number;
  high: number;
  medium: number;
  low: number;
};

type ReviewStatus = "Pending" | "Approved" | "Rejected";

type ReviewRecord = {
  id: string;
  title: string;
  content: string;
  submittedAt: string;
  status: ReviewStatus;
  reviewer: string;
  decisionAt?: string;
  reason?: string;
  analysisStatus?: string;
  findingsCount?: number;
};

const ASSET_STORAGE_KEY = "truemark-brand-assets";
const ANALYSIS_HISTORY_KEY = "truemark-analysis-history";
const REVIEW_STORAGE_KEY = "truemark-review-records";
const VERSION_STORAGE_KEY = "truemark-content-versions";

type ContentVersion = {
  id: string;
  documentId: string;
  documentTitle: string;
  versionNumber: number;
  content: string;
  note: string;
  createdAt: string;
};

function readContentVersions(): ContentVersion[] {
  try {
    const saved = localStorage.getItem(VERSION_STORAGE_KEY);
    if (!saved) return [];

    const parsed: unknown = JSON.parse(saved);
    return Array.isArray(parsed) ? (parsed as ContentVersion[]) : [];
  } catch {
    return [];
  }
}


/* =========================
   STORAGE HELPERS
========================= */

function readAssets(): BrandAsset[] {
  try {
    const saved = localStorage.getItem(ASSET_STORAGE_KEY);
    if (!saved) return [];

    const parsed: unknown = JSON.parse(saved);
    return Array.isArray(parsed) ? (parsed as BrandAsset[]) : [];
  } catch {
    return [];
  }
}

function readAnalysisHistory(): AnalysisRecord[] {
  try {
    const saved = localStorage.getItem(ANALYSIS_HISTORY_KEY);
    if (!saved) return [];

    const parsed: unknown = JSON.parse(saved);
    return Array.isArray(parsed) ? (parsed as AnalysisRecord[]) : [];
  } catch {
    return [];
  }
}

function readReviews(): ReviewRecord[] {
  try {
    const saved = localStorage.getItem(REVIEW_STORAGE_KEY);
    if (!saved) return [];

    const parsed: unknown = JSON.parse(saved);
    return Array.isArray(parsed) ? (parsed as ReviewRecord[]) : [];
  } catch {
    return [];
  }
}

/* =========================
   MAIN APP
========================= */

function App() {
  const [entered, setEntered] = useState(false);
  const [activePage, setActivePage] = useState("Overview");

  if (!entered) {
    return <WelcomeScreen onEnter={() => setEntered(true)} />;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar-brand">
          <div className="brand-logo">T</div>
          <div className="brand-name">
            <h2>TrueMark AI</h2>
            <p>Brand Intelligence</p>
          </div>
        </div>

        <div className="sidebar-section-label">WORKSPACE</div>

        <nav className="sidebar-navigation">
          {navigation.map((item) => (
            <button
              key={item.name}
              className={`nav-item ${
                activePage === item.name ? "active" : ""
              }`}
              onClick={() => setActivePage(item.name)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.name}</span>
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="sidebar-status">
            <span className="status-dot" />
            <span>AI System Ready</span>
          </div>
          <p className="sidebar-version">TrueMark AI · Demo Environment</p>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div className="breadcrumb">
            <span>TrueMark AI</span>
            <span className="breadcrumb-divider">/</span>
            <strong>{activePage}</strong>
          </div>

          <div className="topbar-right">
            <span className="system-indicator">
              <span className="status-dot" />
              System Online
            </span>
            <div className="user-avatar">T</div>
          </div>
        </header>

        <div className="page-content">
          {activePage === "Overview" ? (
            <Overview onNavigate={setActivePage} />
          ) : activePage === "Content Analysis" ? (
            <AnalysisContent />
          ) : activePage === "Brand Guidelines" ? (
            <BrandGuidelines />
          ) : activePage === "Brand Assets" ? (
            <BrandAssets />
          ) : activePage === "Review & Approval" ? (
            <ReviewApproval />
          ) : activePage === "Version History" ? (
            <VersionHistory
            />
          ) : activePage === "Governance Insights" ? (
            <GovernanceInsights />
          ) : (
            <FeaturePage
              page={activePage}
              onBack={() => setActivePage("Overview")}
            />
          )}
        </div>
      </main>
    </div>
  );
}

/* =========================
   WELCOME SCREEN
========================= */

function WelcomeScreen({ onEnter }: { onEnter: () => void }) {
  return (
    <div className="welcome-screen">
      <div className="welcome-background-glow" />

      <div className="welcome-content">
        <div className="welcome-logo">T</div>
        <p className="welcome-eyebrow">INTELLIGENT BRAND GOVERNANCE</p>

        <h1>
          TrueMark <span>AI</span>
        </h1>

        <p className="welcome-description">
          Maintain brand consistency. Detect content deviations.
          Build trust in every communication.
        </p>

        <button className="welcome-enter-button" onClick={onEnter}>
          Enter Workspace <span>→</span>
        </button>

        <p className="welcome-footer">AI-POWERED CONTENT INTELLIGENCE</p>
      </div>
    </div>
  );
}

/* =========================
   OVERVIEW DASHBOARD
========================= */

function Overview({
  onNavigate,
}: {
  onNavigate: (page: string) => void;
}) {
  const [assetCount, setAssetCount] = useState(0);
  const [analysisCount, setAnalysisCount] = useState(0);
  const [pendingCount, setPendingCount] = useState(0);

  useEffect(() => {
    const updateCounts = () => {
      setAssetCount(readAssets().length);
      setAnalysisCount(readAnalysisHistory().length);
      setPendingCount(
        readReviews().filter((review) => review.status === "Pending").length
      );
    };

    updateCounts();
    window.addEventListener("storage", updateCounts);
    window.addEventListener("truemark-reviews-updated", updateCounts);
    window.addEventListener("truemark-analysis-updated", updateCounts);

    return () => {
      window.removeEventListener("storage", updateCounts);
      window.removeEventListener("truemark-reviews-updated", updateCounts);
      window.removeEventListener("truemark-analysis-updated", updateCounts);
    };
  }, []);

  const features = [
    {
      icon: "⌕",
      title: "Content Analysis",
      description:
        "Analyze content for brand consistency, tone, terminology, and potential violations.",
      action: "Analyze Content",
      page: "Content Analysis",
    },
    {
      icon: "✳",
      title: "Brand Guidelines",
      description:
        "Define your brand voice, required terminology, and restricted words.",
      action: "Manage Guidelines",
      page: "Brand Guidelines",
    },
    {
      icon: "▧",
      title: "Brand Assets",
      description:
        "Organize approved logos, reference files, and important brand resources.",
      action: "View Assets",
      page: "Brand Assets",
    },
    {
      icon: "▥",
      title: "Governance Insights",
      description:
        "Review analysis history, compliance indicators, findings, and recommendations.",
      action: "View Insights",
      page: "Governance Insights",
    },
  ];

  return (
    <div className="overview-page">
      <section className="workspace-welcome">
        <div>
          <p className="section-eyebrow">YOUR BRAND WORKSPACE</p>
          <h1>
            Welcome to <span>TrueMark AI</span>
          </h1>
          <p>
            Your intelligent workspace for brand consistency,
            content quality, and brand governance.
          </p>
        </div>

        <button
          className="primary-button"
          onClick={() => onNavigate("Content Analysis")}
        >
          + Analyze Content
        </button>
      </section>

      <section className="overview-stat-grid">
        <div className="overview-stat-card">
          <div className="overview-stat-icon">⌕</div>
          <p>Recorded Analyses</p>
          <h2>{analysisCount}</h2>
          <span>Saved analysis records</span>
        </div>

        <div className="overview-stat-card">
          <div className="overview-stat-icon">▧</div>
          <p>Brand Assets</p>
          <h2>{assetCount}</h2>
          <span>Stored brand resources</span>
        </div>

        <div className="overview-stat-card">
          <div className="overview-stat-icon">✓</div>
          <p>Pending Reviews</p>
          <h2>{pendingCount}</h2>
          <span>Awaiting a decision</span>
        </div>

        <div className="overview-stat-card">
          <div className="overview-stat-icon">▥</div>
          <p>Governance</p>
          <h2>AI</h2>
          <span>Consistency monitoring workspace</span>
        </div>
      </section>

      <section className="overview-section">
        <div className="overview-section-heading">
          <div>
            <p className="section-eyebrow">WORKSPACE TOOLS</p>
            <h2>Explore Your Workspace</h2>
          </div>
        </div>

        <div className="overview-feature-grid">
          {features.map((feature) => (
            <article className="overview-feature-card" key={feature.title}>
              <div className="overview-feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
              <button
                className="text-button"
                onClick={() => onNavigate(feature.page)}
              >
                {feature.action} <span>→</span>
              </button>
            </article>
          ))}
        </div>
      </section>

      <section className="overview-bottom-panel">
        <div>
          <span className="status-dot" />
          <strong>Your workspace is ready</strong>
        </div>
        <p>
          Configure your brand guidelines, analyze content, and submit
          completed analyses for review.
        </p>
      </section>
    </div>
  );
}

/* =========================
   BRAND ASSETS
========================= */

function BrandAssets() {
  const [assets, setAssets] = useState<BrandAsset[]>(readAssets);
  const [name, setName] = useState("");
  const [category, setCategory] = useState("Logo");
  const [description, setDescription] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [search, setSearch] = useState("");
  const [filter, setFilter] = useState("All");
  const [notice, setNotice] = useState("");

  useEffect(() => {
    try {
      localStorage.setItem(ASSET_STORAGE_KEY, JSON.stringify(assets));
    } catch {
      setNotice(
        "Storage limit reached. Try removing a large asset and uploading it again."
      );
    }
  }, [assets]);

  const categories = [
    "Logo",
    "Typography",
    "Color Palette",
    "Image",
    "Document",
    "Other",
  ];

  const filteredAssets = useMemo(() => {
    const query = search.trim().toLowerCase();

    return assets.filter((asset) => {
      const matchesSearch =
        asset.name.toLowerCase().includes(query) ||
        asset.description.toLowerCase().includes(query) ||
        asset.fileName.toLowerCase().includes(query);

      return matchesSearch && (filter === "All" || asset.category === filter);
    });
  }, [assets, search, filter]);

  function handleFileChange(file: File | null) {
    setNotice("");

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (file.size > 1.5 * 1024 * 1024) {
      setNotice("Please choose a file smaller than 1.5 MB.");
      setSelectedFile(null);
      return;
    }

    setSelectedFile(file);
  }

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");

    if (!name.trim()) {
      setNotice("Please enter an asset name.");
      return;
    }

    const createAsset = (dataUrl?: string) => {
      const newAsset: BrandAsset = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`,
        name: name.trim(),
        category,
        description: description.trim(),
        fileName: selectedFile?.name ?? "No file attached",
        fileType: selectedFile?.type ?? "",
        fileSize: selectedFile?.size ?? 0,
        addedAt: new Date().toISOString(),
        dataUrl,
      };

      setAssets((previous) => [newAsset, ...previous]);
      setName("");
      setCategory("Logo");
      setDescription("");
      setSelectedFile(null);

      const input = document.getElementById(
        "brand-asset-file"
      ) as HTMLInputElement | null;

      if (input) input.value = "";

      setNotice("Brand asset added successfully.");
    };

    if (selectedFile && selectedFile.type.startsWith("image/")) {
      const reader = new FileReader();

      reader.onload = () => {
        createAsset(
          typeof reader.result === "string" ? reader.result : undefined
        );
      };

      reader.onerror = () => {
        setNotice("Unable to read this image. Please try another file.");
      };

      reader.readAsDataURL(selectedFile);
    } else {
      createAsset();
    }
  }

  function deleteAsset(id: string) {
    setAssets((previous) => previous.filter((asset) => asset.id !== id));
    setNotice("Asset removed.");
  }

  function formatFileSize(bytes: number) {
    if (bytes === 0) return "No file attached";
    if (bytes < 1024) return `${bytes} B`;
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return (
    <div className="brand-assets-page">
      <section className="workspace-welcome">
        <div>
          <p className="section-eyebrow">BRAND RESOURCE MANAGEMENT</p>
          <h1>
            Brand <span>Assets</span>
          </h1>
          <p>Keep your approved brand resources organized in one place.</p>
        </div>
      </section>

      <section className="asset-stat-grid">
        <div className="asset-stat-card">
          <span>Total Assets</span>
          <strong>{assets.length}</strong>
        </div>
        <div className="asset-stat-card">
          <span>Logos</span>
          <strong>
            {assets.filter((asset) => asset.category === "Logo").length}
          </strong>
        </div>
        <div className="asset-stat-card">
          <span>Documents</span>
          <strong>
            {assets.filter((asset) => asset.category === "Document").length}
          </strong>
        </div>
        <div className="asset-stat-card">
          <span>Images</span>
          <strong>
            {assets.filter((asset) => asset.category === "Image").length}
          </strong>
        </div>
      </section>

      <div className="asset-layout">
        <section className="asset-form">
          <div className="asset-library-heading">
            <div>
              <p className="section-eyebrow">NEW RESOURCE</p>
              <h2>Add Brand Asset</h2>
            </div>
          </div>

          <form onSubmit={handleSubmit}>
            <label className="asset-field">
              <span>Asset Name *</span>
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                placeholder="e.g. Primary Brand Logo"
                required
              />
            </label>

            <label className="asset-field">
              <span>Category</span>
              <select
                value={category}
                onChange={(event) => setCategory(event.target.value)}
              >
                {categories.map((item) => (
                  <option key={item} value={item}>
                    {item}
                  </option>
                ))}
              </select>
            </label>

            <label className="asset-field">
              <span>Description</span>
              <textarea
                value={description}
                onChange={(event) => setDescription(event.target.value)}
                placeholder="Describe the asset and how it should be used..."
                rows={4}
              />
            </label>

            <label className="asset-field">
              <span>Upload File (Optional)</span>
              <input
                id="brand-asset-file"
                type="file"
                onChange={(event) =>
                  handleFileChange(event.target.files?.[0] ?? null)
                }
              />
              <small>Maximum file size: 1.5 MB</small>
            </label>

            {selectedFile && (
              <div className="asset-selected-file">
                Selected: {selectedFile.name}
              </div>
            )}

            {notice && <div className="asset-notice">{notice}</div>}

            <button type="submit" className="asset-submit">
              + Add Asset
            </button>
          </form>
        </section>

        <section className="asset-library">
          <div className="asset-library-heading">
            <div>
              <p className="section-eyebrow">RESOURCE LIBRARY</p>
              <h2>Your Brand Assets</h2>
            </div>
            <span>{filteredAssets.length} items</span>
          </div>

          <input
            className="asset-search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search assets..."
          />

          <div className="asset-filters">
            {["All", ...categories].map((item) => (
              <button
                key={item}
                className={`asset-filter ${filter === item ? "active" : ""}`}
                onClick={() => setFilter(item)}
                type="button"
              >
                {item}
              </button>
            ))}
          </div>

          {filteredAssets.length === 0 ? (
            <div className="asset-empty">
              <div>▧</div>
              <h3>No assets found</h3>
              <p>Add your first brand resource or adjust your search filters.</p>
            </div>
          ) : (
            <div className="asset-list">
              {filteredAssets.map((asset) => (
                <article className="asset-card" key={asset.id}>
                  <div className="asset-preview">
                    {asset.dataUrl ? (
                      <img src={asset.dataUrl} alt={asset.name} />
                    ) : (
                      <span>▧</span>
                    )}
                  </div>

                  <div className="asset-details">
                    <div className="asset-card-title">
                      <h3>{asset.name}</h3>
                      <span className="asset-category">{asset.category}</span>
                    </div>

                    <p>{asset.description || "No description provided."}</p>
                    <small>
                      {asset.fileName} · {formatFileSize(asset.fileSize)}
                    </small>
                    <small>
                      Added {new Date(asset.addedAt).toLocaleDateString()}
                    </small>
                  </div>

                  <button
                    className="asset-delete"
                    onClick={() => deleteAsset(asset.id)}
                    type="button"
                    aria-label={`Delete ${asset.name}`}
                  >
                    Delete
                  </button>
                </article>
              ))}
            </div>
          )}

          <p className="asset-storage-note">
            Assets are stored in this browser. Uploaded non-image files are
            listed by filename and are not uploaded to a remote server.
          </p>
        </section>
      </div>
    </div>
  );
}

/* =========================
   REVIEW & APPROVAL
========================= */

function ReviewApproval() {
  const [reviews, setReviews] = useState<ReviewRecord[]>(readReviews);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [reviewer, setReviewer] = useState("Brand Reviewer");
  const [filter, setFilter] = useState("All");
  const [notice, setNotice] = useState("");
  const [rejectingId, setRejectingId] = useState<string | null>(null);
  const [rejectionReason, setRejectionReason] = useState("");

  useEffect(() => {
    try {
      localStorage.setItem(REVIEW_STORAGE_KEY, JSON.stringify(reviews));
      window.dispatchEvent(new Event("truemark-reviews-updated"));
    } catch {
      setNotice("Unable to save reviews. Browser storage may be full.");
    }
  }, [reviews]);

  const pendingCount = reviews.filter(
    (review) => review.status === "Pending"
  ).length;

  const approvedCount = reviews.filter(
    (review) => review.status === "Approved"
  ).length;

  const rejectedCount = reviews.filter(
    (review) => review.status === "Rejected"
  ).length;

  const filteredReviews = reviews.filter(
    (review) => filter === "All" || review.status === filter
  );

  function submitReview(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");

    if (!title.trim() || !content.trim()) {
      setNotice("Enter both a title and the content to submit.");
      return;
    }

    const record: ReviewRecord = {
      id: crypto.randomUUID(),
      title: title.trim(),
      content: content.trim(),
      submittedAt: new Date().toISOString(),
      status: "Pending",
      reviewer: reviewer.trim() || "Brand Reviewer",
    };

    setReviews((previous) => [record, ...previous]);
    setTitle("");
    setContent("");
    setNotice("Content submitted for review successfully.");
  }

  function approveReview(id: string) {
    setReviews((previous) =>
      previous.map((review) =>
        review.id === id
          ? {
              ...review,
              status: "Approved",
              decisionAt: new Date().toISOString(),
              reason: undefined,
            }
          : review
      )
    );

    setNotice("Content approved successfully.");
  }

  function rejectReview(id: string) {
    if (!rejectionReason.trim()) {
      setNotice("Enter a rejection reason before rejecting this content.");
      return;
    }

    setReviews((previous) =>
      previous.map((review) =>
        review.id === id
          ? {
              ...review,
              status: "Rejected",
              decisionAt: new Date().toISOString(),
              reason: rejectionReason.trim(),
            }
          : review
      )
    );

    setRejectingId(null);
    setRejectionReason("");
    setNotice("Content rejected. The reason has been recorded.");
  }

  return (
    <div className="review-page">
      <section className="workspace-welcome">
        <div>
          <p className="section-eyebrow">CONTENT GOVERNANCE WORKFLOW</p>
          <h1>
            Review <span>& Approval</span>
          </h1>
          <p>
            Submit content for review, record decisions, and track approval
            history before publication.
          </p>
        </div>
      </section>

      <section className="review-stat-grid">
        <article className="review-stat-card">
          <span>Pending Reviews</span>
          <strong>{pendingCount}</strong>
          <small>Waiting for a decision</small>
        </article>
        <article className="review-stat-card">
          <span>Approved</span>
          <strong>{approvedCount}</strong>
          <small>Approved in this workspace</small>
        </article>
        <article className="review-stat-card">
          <span>Rejected</span>
          <strong>{rejectedCount}</strong>
          <small>Returned for changes</small>
        </article>
        <article className="review-stat-card">
          <span>Total Submissions</span>
          <strong>{reviews.length}</strong>
          <small>Saved review records</small>
        </article>
      </section>

      <div className="review-layout">
        <section className="review-form-panel">
          <div className="review-panel-heading">
            <p className="section-eyebrow">NEW SUBMISSION</p>
            <h2>Submit Content</h2>
            <p>
              Add content that needs a review. This demo stores the submission
              in this browser.
            </p>
          </div>

          <form onSubmit={submitReview} className="review-form">
            <label className="review-field">
              <span>Content Title *</span>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="e.g. Product launch announcement"
                maxLength={120}
                required
              />
            </label>

            <label className="review-field">
              <span>Content to Review *</span>
              <textarea
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="Paste the content you want reviewed..."
                rows={7}
                maxLength={20000}
                required
              />
              <small>{content.length.toLocaleString()} / 20,000 characters</small>
            </label>

            <label className="review-field">
              <span>Assigned Reviewer</span>
              <input
                value={reviewer}
                onChange={(event) => setReviewer(event.target.value)}
                placeholder="Reviewer name or role"
                maxLength={100}
              />
            </label>

            {notice && (
              <div className="review-notice" role="status">
                {notice}
              </div>
            )}

            <button className="primary-button" type="submit">
              Submit for Review →
            </button>
          </form>
        </section>

        <section className="review-list-panel">
          <div className="review-panel-heading">
            <p className="section-eyebrow">DECISION WORKSPACE</p>
            <h2>Review Queue</h2>
            <p>Review submitted content and record a decision.</p>
          </div>

          <div className="review-filters">
            {["All", "Pending", "Approved", "Rejected"].map((status) => (
              <button
                key={status}
                type="button"
                className={`review-filter ${
                  filter === status ? "active" : ""
                }`}
                onClick={() => setFilter(status)}
              >
                {status}
              </button>
            ))}
          </div>

          {filteredReviews.length === 0 ? (
            <div className="review-empty">
              <div>✓</div>
              <h3>No reviews found</h3>
              <p>
                Submit content using the form to create your first review
                record.
              </p>
            </div>
          ) : (
            <div className="review-list">
              {filteredReviews.map((review) => (
                <article className="review-card" key={review.id}>
                  <div className="review-card-top">
                    <div>
                      <span className="section-kicker">
                        REVIEW #{review.id.slice(0, 8)}
                      </span>
                      <h3>{review.title}</h3>
                    </div>

                    <span
                      className={`review-status review-status-${review.status.toLowerCase()}`}
                    >
                      {review.status}
                    </span>
                  </div>

                  <p className="review-content-preview">{review.content}</p>

                  <div className="review-metadata">
                    <span>Reviewer: {review.reviewer}</span>
                    <span>
                      Submitted: {new Date(review.submittedAt).toLocaleString()}
                    </span>
                  </div>

                  {review.decisionAt && (
                    <div className="review-decision-info">
                      <strong>
                        {review.status} on{" "}
                        {new Date(review.decisionAt).toLocaleString()}
                      </strong>

                      {review.reason && (
                        <p>Reason: {review.reason}</p>
                      )}
                    </div>
                  )}

                  {review.status === "Pending" && (
                    <div className="review-actions">
                      <button
                        type="button"
                        className="review-approve-button"
                        onClick={() => approveReview(review.id)}
                      >
                        ✓ Approve
                      </button>

                      <button
                        type="button"
                        className="review-reject-button"
                        onClick={() => {
                          setRejectingId(review.id);
                          setRejectionReason("");
                          setNotice("");
                        }}
                      >
                        Reject
                      </button>
                    </div>
                  )}

                  {rejectingId === review.id && (
                    <form
                      className="review-rejection-form"
                      onSubmit={(event) => {
                        event.preventDefault();
                        rejectReview(review.id);
                      }}
                    >
                      <label className="review-field">
                        <span>Reason for rejection *</span>
                        <textarea
                          value={rejectionReason}
                          onChange={(event) =>
                            setRejectionReason(event.target.value)
                          }
                          placeholder="Explain what needs to change..."
                          rows={3}
                          required
                        />
                      </label>

                      <div className="review-actions">
                        <button
                          type="submit"
                          className="review-reject-button"
                        >
                          Confirm Rejection
                        </button>

                        <button
                          type="button"
                          className="secondary-button"
                          onClick={() => {
                            setRejectingId(null);
                            setRejectionReason("");
                          }}
                        >
                          Cancel
                        </button>
                      </div>
                    </form>
                  )}
                </article>
              ))}
            </div>
          )}

          <p className="review-storage-note">
            Demo limitation: review records are stored in this browser's
            localStorage. This is not a multi-user approval system, and
            reviewer names are entered manually rather than authenticated.
          </p>
        </section>
      </div>
    </div>
  );
}

/* =========================
   GOVERNANCE INSIGHTS
========================= */

function GovernanceInsights() {
  const [history, setHistory] = useState<AnalysisRecord[]>([]);
  const [lastUpdated, setLastUpdated] = useState("");

  function refreshHistory() {
    setHistory(readAnalysisHistory());
    setLastUpdated(new Date().toLocaleTimeString());
  }

  useEffect(() => {
    refreshHistory();

    const handleUpdate = () => refreshHistory();

    window.addEventListener("storage", handleUpdate);
    window.addEventListener("truemark-analysis-updated", handleUpdate);

    return () => {
      window.removeEventListener("storage", handleUpdate);
      window.removeEventListener("truemark-analysis-updated", handleUpdate);
    };
  }, []);

  const metrics = useMemo(() => {
    const totalHigh = history.reduce(
      (total, record) => total + (Number(record.high) || 0),
      0
    );

    const totalMedium = history.reduce(
      (total, record) => total + (Number(record.medium) || 0),
      0
    );

    const totalLow = history.reduce(
      (total, record) => total + (Number(record.low) || 0),
      0
    );

    const totalFindings = history.reduce(
      (total, record) => total + (Number(record.findingsCount) || 0),
      0
    );

    const weightedRisk = totalHigh * 10 + totalMedium * 5 + totalLow * 2;

    const indicativeScore =
      totalFindings === 0
        ? 100
        : Math.max(
            0,
            Math.round(
              (1 - weightedRisk / Math.max(totalFindings * 10, 1)) * 100
            )
          );

    return {
      totalAnalyses: history.length,
      totalHigh,
      totalMedium,
      totalLow,
      totalFindings,
      indicativeScore,
    };
  }, [history]);

  const recommendations = useMemo(() => {
    const items: string[] = [];

    if (history.length === 0) {
      return [
        "Run your first content analysis to begin building governance insights.",
        "Configure your brand voice and terminology in Brand Guidelines.",
        "Add approved brand resources to Brand Assets.",
      ];
    }

    if (metrics.totalHigh > 0) {
      items.push(`Review ${metrics.totalHigh} high-severity finding(s) first.`);
    }

    if (metrics.totalMedium > 0) {
      items.push(
        `Review ${metrics.totalMedium} medium-severity finding(s) and clarify brand rules if necessary.`
      );
    }

    if (metrics.totalLow > 0) {
      items.push(
        `Review ${metrics.totalLow} low-severity finding(s) to improve consistency.`
      );
    }

    if (metrics.totalFindings === 0) {
      items.push("No findings are recorded. Continue checking new content.");
    }

    items.push(
      "Keep Brand Guidelines updated so future analyses reflect your current standards."
    );

    return items;
  }, [history, metrics]);

  return (
    <div className="governance-page">
      <section className="governance-header">
        <div>
          <p className="section-eyebrow">BRAND PERFORMANCE MONITORING</p>
          <h1>
            Governance <span>Insights</span>
          </h1>
          <p>
            Understand recorded analysis results, identify recurring issues,
            and prioritize brand consistency improvements.
          </p>
        </div>

        <button className="primary-button" onClick={refreshHistory}>
          ↻ Refresh Insights
        </button>
      </section>

      <div className="governance-disclaimer">
        <span>ⓘ</span>
        <p>
          These indicative demo metrics use locally recorded analyses. They
          are not a certified compliance score or a substitute for human review.
        </p>
      </div>

      <section className="governance-stats">
        <article className="governance-stat">
          <span>Recorded Analyses</span>
          <strong>{metrics.totalAnalyses}</strong>
          <small>Total saved analysis records</small>
        </article>
        <article className="governance-stat">
          <span>Indicative Score</span>
          <strong>
            {metrics.totalAnalyses > 0
              ? `${metrics.indicativeScore}%`
              : "—"}
          </strong>
          <small>Weighted demo indicator</small>
        </article>
        <article className="governance-stat">
          <span>Total Findings</span>
          <strong>{metrics.totalFindings}</strong>
          <small>Across recorded analyses</small>
        </article>
        <article className="governance-stat">
          <span>High Severity</span>
          <strong>{metrics.totalHigh}</strong>
          <small>Findings to prioritize</small>
        </article>
      </section>

      <div className="governance-columns">
        <section className="governance-panel">
          <div className="governance-panel-heading">
            <div>
              <p className="section-eyebrow">FINDINGS OVERVIEW</p>
              <h2>Severity Breakdown</h2>
            </div>
          </div>

          {[
            { label: "High", count: metrics.totalHigh, className: "high" },
            { label: "Medium", count: metrics.totalMedium, className: "medium" },
            { label: "Low", count: metrics.totalLow, className: "low" },
          ].map((severity) => {
            const percentage =
              metrics.totalFindings > 0
                ? (severity.count / metrics.totalFindings) * 100
                : 0;

            return (
              <div className="severity-row" key={severity.label}>
                <div className="severity-label">
                  <span>{severity.label} Severity</span>
                  <strong>{severity.count}</strong>
                </div>
                <div className="severity-track">
                  <div
                    className={`severity-fill ${severity.className}`}
                    style={{ width: `${percentage}%` }}
                  />
                </div>
              </div>
            );
          })}

          {metrics.totalFindings === 0 && (
            <p className="governance-muted">
              No findings recorded yet. Run a content analysis to populate
              this breakdown.
            </p>
          )}
        </section>

        <section className="governance-panel">
          <div className="governance-panel-heading">
            <div>
              <p className="section-eyebrow">NEXT STEPS</p>
              <h2>Recommendations</h2>
            </div>
          </div>

          <div className="recommendation-list">
            {recommendations.map((recommendation, index) => (
              <div className="recommendation-item" key={recommendation}>
                <span>{String(index + 1).padStart(2, "0")}</span>
                <p>{recommendation}</p>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="governance-panel governance-history-panel">
        <div className="governance-panel-heading">
          <div>
            <p className="section-eyebrow">AUDIT OVERVIEW</p>
            <h2>Recent Analysis History</h2>
          </div>
          <span className="governance-record-count">
            {history.length} records
          </span>
        </div>

        {history.length === 0 ? (
          <div className="governance-empty">
            <div>◷</div>
            <h3>No recorded analyses yet</h3>
            <p>
              Saved Content Analysis results will appear here.
            </p>
          </div>
        ) : (
          <div className="governance-table-wrapper">
            <table className="governance-table">
              <thead>
                <tr>
                  <th>Analysis ID</th>
                  <th>Date</th>
                  <th>Status</th>
                  <th>Findings</th>
                  <th>High</th>
                  <th>Medium</th>
                  <th>Low</th>
                </tr>
              </thead>

              <tbody>
                {[...history].slice(0, 10).map((record, index) => (
                  <tr key={record.id || `${record.date}-${index}`}>
                    <td>{record.id ? record.id.slice(0, 12) : "Analysis"}</td>
                    <td>
                      {record.date
                        ? new Date(record.date).toLocaleString()
                        : "Date unavailable"}
                    </td>
                    <td>
                      <span
                        className={`governance-status ${
                          record.status === "passed" ? "compliant" : "review"
                        }`}
                      >
                        {record.status || "Recorded"}
                      </span>
                    </td>
                    <td>{Number(record.findingsCount) || 0}</td>
                    <td>{Number(record.high) || 0}</td>
                    <td>{Number(record.medium) || 0}</td>
                    <td>{Number(record.low) || 0}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        <div className="governance-last-updated">
          {lastUpdated ? `Last refreshed: ${lastUpdated}` : "Refresh to update insights"}
        </div>
      </section>
    </div>
  );
}

/* =========================
   PLACEHOLDER PAGES
========================= */

function FeaturePage({
  page,
  onBack,
}: {
  page: string;
  onBack: () => void;
}) {
  return (
    <div className="feature-placeholder">
      <div className="feature-placeholder-icon">◷</div>
      <p className="section-eyebrow">WORKSPACE MODULE</p>
      <h1>{page}</h1>
      <p>
        {descriptions[page] ||
          "Manage your brand governance workflow from this workspace."}
      </p>

      <div className="feature-placeholder-notice">
        <span>ⓘ</span>
        <p>
          This module is planned for a future iteration of the TrueMark AI
          workspace.
        </p>
      </div>

      <button className="primary-button" onClick={onBack}>
        ← Back to Overview
      </button>
    </div>
  );
}

/* =========================
   VERSION HISTORY
========================= */

function VersionHistory() {
  const [versions, setVersions] =
    useState<ContentVersion[]>(readContentVersions);

  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [note, setNote] = useState("");
  const [search, setSearch] = useState("");
  const [selectedDocument, setSelectedDocument] = useState("All");
  const [compareIds, setCompareIds] = useState<string[]>([]);
  const [editingDocumentId, setEditingDocumentId] =
    useState<string | null>(null);
  const [notice, setNotice] = useState("");

  useEffect(() => {
    try {
      localStorage.setItem(VERSION_STORAGE_KEY, JSON.stringify(versions));
    } catch {
      setNotice("Unable to save versions. Browser storage may be full.");
    }
  }, [versions]);

  const documents = useMemo(() => {
    const unique = new Map<string, string>();

    versions.forEach((version) => {
      unique.set(version.documentId, version.documentTitle);
    });

    return Array.from(unique, ([id, documentTitle]) => ({
      id,
      title: documentTitle,
    }));
  }, [versions]);

  const filteredVersions = useMemo(() => {
    const query = search.trim().toLowerCase();

    return [...versions]
      .filter((version) => {
        const matchesSearch =
          version.documentTitle.toLowerCase().includes(query) ||
          version.note.toLowerCase().includes(query) ||
          version.content.toLowerCase().includes(query);

        const matchesDocument =
          selectedDocument === "All" ||
          version.documentId === selectedDocument;

        return matchesSearch && matchesDocument;
      })
      .sort(
        (a, b) =>
          new Date(b.createdAt).getTime() -
          new Date(a.createdAt).getTime()
      );
  }, [versions, search, selectedDocument]);

  const selectedVersions = versions
    .filter((version) => compareIds.includes(version.id))
    .sort((a, b) => a.versionNumber - b.versionNumber);

  function saveVersion(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setNotice("");

    if (!title.trim() || !content.trim()) {
      setNotice("Enter a document title and content before saving.");
      return;
    }

    const documentTitle = title.trim();

    const existingDocument = editingDocumentId
      ? versions.find(
          (version) => version.documentId === editingDocumentId
        )
      : versions.find(
          (version) =>
            version.documentTitle.toLowerCase() ===
            documentTitle.toLowerCase()
        );

    const documentId =
      existingDocument?.documentId ?? crypto.randomUUID();

    const documentVersions = versions.filter(
      (version) => version.documentId === documentId
    );

    const nextVersionNumber =
      documentVersions.reduce(
        (highest, version) =>
          Math.max(highest, version.versionNumber),
        0
      ) + 1;

    const newVersion: ContentVersion = {
      id: crypto.randomUUID(),
      documentId,
      documentTitle,
      versionNumber: nextVersionNumber,
      content: content.trim(),
      note: note.trim() || "Content updated",
      createdAt: new Date().toISOString(),
    };

    setVersions((previous) => [newVersion, ...previous]);
    setEditingDocumentId(documentId);
    setNote("");
    setNotice(`Version ${nextVersionNumber} saved successfully.`);
  }

  function startNewDocument() {
    setTitle("");
    setContent("");
    setNote("");
    setEditingDocumentId(null);
    setNotice("");
  }

  function restoreVersion(version: ContentVersion) {
    setTitle(version.documentTitle);
    setContent(version.content);
    setNote(`Restored from version ${version.versionNumber}`);
    setEditingDocumentId(version.documentId);
    setNotice(
      `Version ${version.versionNumber} loaded into the editor. Save it to create a new version.`
    );

    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  function deleteVersion(version: ContentVersion) {
    const confirmed = window.confirm(
      `Delete version ${version.versionNumber} of "${version.documentTitle}"?`
    );

    if (!confirmed) return;

    setVersions((previous) =>
      previous.filter((item) => item.id !== version.id)
    );

    setCompareIds((previous) =>
      previous.filter((id) => id !== version.id)
    );

    setNotice("Version deleted.");
  }

  function toggleCompare(id: string) {
    setCompareIds((previous) => {
      if (previous.includes(id)) {
        return previous.filter((item) => item !== id);
      }

      if (previous.length >= 2) {
        setNotice("Select only two versions to compare.");
        return previous;
      }

      setNotice("");
      return [...previous, id];
    });
  }

  const documentCount = documents.length;
  const versionCount = versions.length;

  return (
    <div className="version-history-page">
      <section className="workspace-welcome">
        <div>
          <p className="section-eyebrow">CONTENT GOVERNANCE</p>
          <h1>
            Version <span>History</span>
          </h1>
          <p>
            Track content changes, preserve earlier versions, and
            compare revisions before approving brand communications.
          </p>
        </div>

        <button
          className="primary-button"
          type="button"
          onClick={startNewDocument}
        >
          + New Document
        </button>
      </section>

      <section className="version-stat-grid">
        <article className="version-stat-card">
          <span>Saved Versions</span>
          <strong>{versionCount}</strong>
          <small>All recorded revisions</small>
        </article>

        <article className="version-stat-card">
          <span>Documents</span>
          <strong>{documentCount}</strong>
          <small>Unique tracked documents</small>
        </article>

        <article className="version-stat-card">
          <span>Selected for Comparison</span>
          <strong>{compareIds.length}/2</strong>
          <small>Choose two versions below</small>
        </article>
      </section>

      <div className="version-history-layout">
        <section className="version-editor-panel">
          <div className="version-panel-heading">
            <p className="section-eyebrow">VERSION WORKSPACE</p>
            <h2>Create a Version</h2>
            <p>
              Save content revisions with a title and a description
              of what changed.
            </p>
          </div>

          <form className="version-editor-form" onSubmit={saveVersion}>
            <label className="version-field">
              <span>Document Title *</span>
              <input
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                placeholder="e.g. Product Launch Announcement"
                maxLength={150}
                required
              />
            </label>

            <label className="version-field">
              <span>Content *</span>
              <textarea
                value={content}
                onChange={(event) => setContent(event.target.value)}
                placeholder="Write or paste the content to save..."
                rows={9}
                maxLength={50000}
                required
              />
              <small>
                {content.length.toLocaleString()} / 50,000 characters
              </small>
            </label>

            <label className="version-field">
              <span>Change Summary</span>
              <input
                value={note}
                onChange={(event) => setNote(event.target.value)}
                placeholder="e.g. Updated product terminology"
                maxLength={500}
              />
            </label>

            {notice && (
              <div className="version-notice" role="status">
                {notice}
              </div>
            )}

            <div className="version-form-actions">
              <button className="primary-button" type="submit">
                Save New Version
              </button>

              <button
                className="secondary-button"
                type="button"
                onClick={startNewDocument}
              >
                Clear Editor
              </button>
            </div>
          </form>
        </section>

        <section className="version-list-panel">
          <div className="version-panel-heading">
            <p className="section-eyebrow">REVISION RECORDS</p>
            <h2>Saved Versions</h2>
            <p>
              Search documents, restore previous content, or select
              two versions to compare.
            </p>
          </div>

          <input
            className="version-search"
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search titles, content, or change summaries..."
          />

          <label className="version-filter-field">
            <span>Filter by document</span>
            <select
              value={selectedDocument}
              onChange={(event) => setSelectedDocument(event.target.value)}
            >
              <option value="All">All documents</option>
              {documents.map((document) => (
                <option key={document.id} value={document.id}>
                  {document.title}
                </option>
              ))}
            </select>
          </label>

          <p className="version-compare-hint">
            Select up to two versions using the checkboxes to compare them.
          </p>

          {filteredVersions.length === 0 ? (
            <div className="version-empty">
              <div>◷</div>
              <h3>No versions found</h3>
              <p>
                Save your first document version or change your search.
              </p>
            </div>
          ) : (
            <div className="version-list">
              {filteredVersions.map((version) => (
                <article className="version-card" key={version.id}>
                  <div className="version-card-top">
                    <div>
                      <span className="version-number-badge">
                        Version {version.versionNumber}
                      </span>
                      <h3 className="version-card-title">
                        {version.documentTitle}
                      </h3>
                    </div>

                    <label className="version-compare-checkbox">
                      <input
                        type="checkbox"
                        checked={compareIds.includes(version.id)}
                        onChange={() => toggleCompare(version.id)}
                        aria-label={`Select version ${version.versionNumber} to compare`}
                      />
                      Compare
                    </label>
                  </div>

                  <p className="version-note">
                    {version.note || "No change summary"}
                  </p>

                  <p className="version-content-preview">
                    {version.content.length > 240
                      ? `${version.content.slice(0, 240)}…`
                      : version.content}
                  </p>

                  <div className="version-card-bottom">
                    <span>
                      {new Date(version.createdAt).toLocaleString()}
                    </span>

                    <div className="version-card-actions">
                      <button
                        className="text-button"
                        type="button"
                        onClick={() => restoreVersion(version)}
                      >
                        Restore to Editor
                      </button>

                      <button
                        className="version-delete-button"
                        type="button"
                        onClick={() => deleteVersion(version)}
                      >
                        Delete
                      </button>
                    </div>
                  </div>
                </article>
              ))}
            </div>
          )}

          <p className="version-storage-note">
            Demo limitation: versions are stored in this browser's
            localStorage. They are not synced between users or devices.
          </p>
        </section>
      </div>

      {selectedVersions.length === 2 && (
        <section className="version-comparison-panel">
          <div className="version-panel-heading">
            <p className="section-eyebrow">REVISION REVIEW</p>
            <h2>Compare Versions</h2>
            <p>
              Review the saved content and change summaries side by side.
            </p>
          </div>

          <div className="version-comparison-grid">
            {selectedVersions.map((version) => (
              <article className="version-comparison-card" key={version.id}>
                <span className="version-number-badge">
                  Version {version.versionNumber}
                </span>

                <h3>{version.documentTitle}</h3>

                <p className="version-note">{version.note}</p>

                <p className="version-comparison-date">
                  Saved {new Date(version.createdAt).toLocaleString()}
                </p>

                <pre>{version.content}</pre>
              </article>
            ))}
          </div>

          <button
            className="secondary-button"
            type="button"
            onClick={() => setCompareIds([])}
          >
            Clear Comparison
          </button>
        </section>
      )}
    </div>
  );
}

export default App;