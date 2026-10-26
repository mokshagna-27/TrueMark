import { useState } from "react";

type Finding = {
  rule: string;
  severity: string;
  message: string;
  suggestion: string;
  matched: boolean;
};

type AnalysisResult = {
  checked_characters: number;
  findings_count: number;
  high_severity_count: number;
  medium_severity_count: number;
  low_severity_count: number;
  overall_status: string;
  analysis_engine?: string;
  findings: Finding[];
};

type BrandGuidelinesData = {
  brandName?: string;
  tone?: string;
  requiredTerms?: string[];
  forbiddenTerms?: string[];
};

type AnalysisHistoryRecord = {
  id: string;
  date: string;
  status: string;
  findingsCount: number;
  high: number;
  medium: number;
  low: number;
};

const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000"
).replace(/\/$/, "");

const API_URL = `${API_BASE_URL}/api/v1/analysis/text`;

const STORAGE_KEY = "truemark-brand-guidelines";
const HISTORY_KEY = "truemark-analysis-history";

function loadSavedGuidelines(): BrandGuidelinesData {
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    return saved ? JSON.parse(saved) : {};
  } catch {
    return {};
  }
}

function formatStatus(status: string) {
  if (status === "passed") return "Passed";
  if (status === "needs_attention") return "Needs attention";
  if (status === "needs_review") return "Needs review";

  return status.replaceAll("_", " ");
}

function saveAnalysisHistory(result: AnalysisResult) {
  try {
    const stored = localStorage.getItem(HISTORY_KEY);
    const parsed: unknown = stored ? JSON.parse(stored) : [];

    const existing: AnalysisHistoryRecord[] = Array.isArray(parsed)
      ? parsed
      : [];

    const findings = Array.isArray(result.findings)
      ? result.findings
      : [];

    const countSeverity = (severity: string) =>
      findings.filter(
        (finding) =>
          finding.severity?.toLowerCase() === severity.toLowerCase()
      ).length;

    const record: AnalysisHistoryRecord = {
      id: `${Date.now()}-${Math.random().toString(36).slice(2, 9)}`,
      date: new Date().toISOString(),
      status: result.overall_status || "needs_review",
      findingsCount:
        typeof result.findings_count === "number"
          ? result.findings_count
          : findings.length,
      high:
        typeof result.high_severity_count === "number"
          ? result.high_severity_count
          : countSeverity("high"),
      medium:
        typeof result.medium_severity_count === "number"
          ? result.medium_severity_count
          : countSeverity("medium"),
      low:
        typeof result.low_severity_count === "number"
          ? result.low_severity_count
          : countSeverity("low"),
    };

    // Save the newest record first and retain at most 100 analyses.
    const updated = [record, ...existing].slice(0, 100);

    localStorage.setItem(HISTORY_KEY, JSON.stringify(updated));

    // Refresh Governance Insights in the current browser tab.
    window.dispatchEvent(new Event("truemark-analysis-updated"));
  } catch (error) {
    // A storage problem should not erase the successful analysis report.
    console.error("Unable to save analysis history:", error);
  }
}

export default function AnalysisContent() {
  const [guidelines, setGuidelines] =
    useState<BrandGuidelinesData>(loadSavedGuidelines);

  const [content, setContent] = useState("");

  const [requiredInput, setRequiredInput] = useState(() => {
    const saved = loadSavedGuidelines();

    return saved.requiredTerms?.join(", ") || saved.brandName || "TrueMark";
  });

  const [forbiddenInput, setForbiddenInput] = useState(() => {
    return loadSavedGuidelines().forbiddenTerms?.join(", ") || "";
  });

  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  function reloadGuidelines() {
    const saved = loadSavedGuidelines();

    setGuidelines(saved);
    setRequiredInput(
      saved.requiredTerms?.join(", ") || saved.brandName || ""
    );
    setForbiddenInput(saved.forbiddenTerms?.join(", ") || "");

    setNotice("Saved brand guidelines loaded.");
    setError("");
  }

  async function analyzeContent() {
    if (!content.trim()) {
      setError("Please enter some content before running an analysis.");
      setResult(null);
      return;
    }

    const requiredTerms = requiredInput
      .split(",")
      .map((term) => term.trim())
      .filter(Boolean);

    const forbiddenTerms = forbiddenInput
      .split(",")
      .map((term) => term.trim())
      .filter(Boolean);

    setLoading(true);
    setError("");
    setNotice("");
    setResult(null);

    try {
      const response = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          text: content,
          required_terms: requiredTerms,
          forbidden_terms: forbiddenTerms,
        }),
      });

      if (!response.ok) {
        const details = await response.text();

        throw new Error(
          `Analysis failed (${response.status}): ${details.slice(0, 250)}`
        );
      }

      const data = await response.json();

      if (!data.result || !Array.isArray(data.result.findings)) {
        throw new Error(
          "The backend returned an unexpected analysis report."
        );
      }

      const analysisResult = data.result as AnalysisResult;

      setResult(analysisResult);

      // Record every successful analysis for Governance Insights.
      saveAnalysisHistory(analysisResult);

      setNotice("Analysis completed successfully. History updated.");
    } catch (err) {
      setError(
        err instanceof Error
          ? err.message
          : "Unable to analyze the content. Please try again."
      );
    } finally {
      setLoading(false);
    }
  }

  function clearAnalysis() {
    setContent("");
    setResult(null);
    setError("");
    setNotice("");
  }

  function loadSample() {
    setContent(
      "OMG!!! Our cheap products are the best ever! Buy now for guaranteed results."
    );

    setResult(null);
    setError("");
    setNotice("");
  }

  return (
    <section className="analysis-studio">
      <div className="analysis-heading">
        <div>
          <div className="eyebrow">CONTENT INTELLIGENCE</div>

          <h2>
            Content <span className="gradient-text">Analysis</span>
          </h2>

          <p>
            Evaluate content against your brand rules, identify
            inconsistencies, and review suggested improvements.
          </p>
        </div>

        <div className="analysis-engine-badge">
          <span className="status-dot" />
          Rule-based analysis
        </div>
      </div>

      <div className="analysis-layout">
        <div className="analysis-editor-card">
          <div className="analysis-card-heading">
            <div>
              <span className="section-kicker">01 / INPUT</span>
              <h3>Your content</h3>
            </div>

            <span className="character-count">
              {content.length.toLocaleString()} characters
            </span>
          </div>

          <div className="analysis-field">
            <label className="analysis-label" htmlFor="content-input">
              Content to review
            </label>

            <textarea
              id="content-input"
              className="analysis-textarea"
              value={content}
              onChange={(event) => setContent(event.target.value)}
              placeholder="Paste marketing copy, product descriptions, campaign messages, or other brand content..."
              maxLength={50000}
            />
          </div>

          <div className="guidelines-summary">
            <div>
              <span className="section-kicker">ACTIVE BRAND PROFILE</span>
              <h4>{guidelines.brandName || "Custom brand rules"}</h4>
              <p>Tone: {guidelines.tone || "Not specified"}</p>
            </div>

            <button
              type="button"
              className="secondary-button"
              onClick={reloadGuidelines}
              disabled={loading}
            >
              Reload Guidelines
            </button>
          </div>

          <div className="analysis-field">
            <label className="analysis-label" htmlFor="required-terms">
              Required brand terms
            </label>

            <input
              id="required-terms"
              className="analysis-input"
              value={requiredInput}
              onChange={(event) => setRequiredInput(event.target.value)}
              placeholder="TrueMark, trusted quality"
            />

            <span className="analysis-help">
              Separate multiple terms with commas.
            </span>
          </div>

          <div className="analysis-field">
            <label className="analysis-label" htmlFor="forbidden-terms">
              Forbidden terms
            </label>

            <input
              id="forbidden-terms"
              className="analysis-input"
              value={forbiddenInput}
              onChange={(event) => setForbiddenInput(event.target.value)}
              placeholder="cheap, guaranteed, risk-free"
            />

            <span className="analysis-help">
              Terms that should not appear in your content.
            </span>
          </div>

          {notice && (
            <div className="honesty-note" role="status">
              {notice}
            </div>
          )}

          {error && (
            <div className="analysis-error" role="alert">
              <strong>Analysis unavailable</strong>
              <p>{error}</p>
              <span>
                Confirm that your backend is running at 127.0.0.1:8000.
              </span>
            </div>
          )}

          <div className="analysis-actions">
            <button
              className="secondary-button"
              type="button"
              onClick={clearAnalysis}
              disabled={loading}
            >
              Clear
            </button>

            <button
              className="secondary-button"
              type="button"
              onClick={loadSample}
              disabled={loading}
            >
              Load sample
            </button>

            <button
              className="primary-button"
              type="button"
              onClick={analyzeContent}
              disabled={loading}
            >
              {loading ? "Analyzing..." : "Analyze content"}
              {!loading && <span> ↗</span>}
            </button>
          </div>
        </div>

        <div className="analysis-results-card">
          <div className="analysis-card-heading">
            <div>
              <span className="section-kicker">02 / RESULTS</span>
              <h3>Analysis report</h3>
            </div>
          </div>

          {!result && !loading && !error && (
            <div className="analysis-empty">
              <div className="analysis-empty-icon">⌕</div>
              <h4>Your report will appear here</h4>
              <p>
                Enter content and run an analysis to view findings,
                severity levels, and recommended actions.
              </p>
            </div>
          )}

          {loading && (
            <div className="analysis-empty" aria-live="polite">
              <div className="analysis-loading-indicator" />
              <h4>Analyzing your content</h4>
              <p>Running configured checks against the backend.</p>
            </div>
          )}

          {result && (
            <div className="analysis-report" aria-live="polite">
              <div
                className={`analysis-status status-${result.overall_status}`}
              >
                <span className="status-dot" />

                <div>
                  <span className="section-kicker">OVERALL STATUS</span>
                  <h4>{formatStatus(result.overall_status)}</h4>
                </div>
              </div>

              <div className="analysis-stat-grid">
                <div className="analysis-stat">
                  <span>Total findings</span>
                  <strong>{result.findings_count}</strong>
                </div>

                <div className="analysis-stat">
                  <span>High severity</span>
                  <strong>{result.high_severity_count}</strong>
                </div>

                <div className="analysis-stat">
                  <span>Medium severity</span>
                  <strong>{result.medium_severity_count}</strong>
                </div>

                <div className="analysis-stat">
                  <span>Low severity</span>
                  <strong>{result.low_severity_count ?? 0}</strong>
                </div>

                <div className="analysis-stat">
                  <span>Characters checked</span>
                  <strong>
                    {Number(result.checked_characters || 0).toLocaleString()}
                  </strong>
                </div>
              </div>

              <div className="analysis-findings-heading">
                <h4>Findings</h4>
                <span>{result.findings.length} reported</span>
              </div>

              {result.findings.length === 0 ? (
                <div className="analysis-no-findings">
                  <span className="status-dot" />
                  No issues were detected by the configured rules.
                </div>
              ) : (
                <div className="analysis-findings-list">
                  {result.findings.map((finding, index) => (
                    <article
                      className="analysis-finding"
                      key={`${finding.rule}-${index}`}
                    >
                      <div className="finding-topline">
                        <span
                          className={`severity-badge severity-${finding.severity}`}
                        >
                          {finding.severity}
                        </span>

                        <span className="finding-rule">
                          {finding.rule.replaceAll("_", " ")}
                        </span>
                      </div>

                      <p>{finding.message}</p>

                      <div className="finding-suggestion">
                        <strong>Suggested action</strong>
                        <span>{finding.suggestion}</span>
                      </div>
                    </article>
                  ))}
                </div>
              )}

              <p className="analysis-disclaimer">
                This report uses configurable terminology rules and basic
                wording patterns. Results may require human review and do not
                represent a complete understanding of brand context.
              </p>
            </div>
          )}

          {error && !result && (
            <div className="analysis-empty">
              <div className="analysis-empty-icon">!</div>
              <h4>Report not available</h4>
              <p>Resolve the error above and run the analysis again.</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
}
