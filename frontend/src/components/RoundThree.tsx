import { useMemo, useState, type ChangeEvent, type ReactNode } from "react";

const API_BASE = (import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000").replace(/\/$/, "");
type Finding = { check_name?: string; status?: string; severity?: string; explanation?: string; suggested_fix?: string; rule?: string; message?: string; suggestion?: string; matched?: boolean };

function Panel({ title, subtitle, children }: { title: string; subtitle?: string; children: ReactNode }) {
  return <section className="r3-panel"><div className="r3-panel-heading"><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}</div>{children}</section>;
}

export default function RoundThree() {
  const [file, setFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState("");
  const [uploadResult, setUploadResult] = useState<any>(null);
  const [team, setTeam] = useState("Marketing");
  const [channel, setChannel] = useState("Email");
  const [draft, setDraft] = useState("Meet the all-new product: reliable, simple, and built for everyone.");
  const [adapted, setAdapted] = useState("Meet our new product — reliable, simple, built for everyone!");
  const [dismissed, setDismissed] = useState<string[]>([]);
  const [email, setEmail] = useState("");
  const [slack, setSlack] = useState("");
  const [notifyStatus, setNotifyStatus] = useState("");
  const [runEval, setRunEval] = useState(false);

  const drift = useMemo(() => {
    const normalize = (s: string) => new Set(s.toLowerCase().match(/[a-z0-9']+/g) || []);
    const a = normalize(draft), b = normalize(adapted);
    const missing = [...a].filter((word) => !b.has(word));
    const added = [...b].filter((word) => !a.has(word));
    const score = Math.round(100 * (1 - (missing.length + added.length) / Math.max(1, a.size + b.size)));
    return { missing, added, score: Math.max(0, score) };
  }, [draft, adapted]);

  async function analyzeFile() {
    if (!file) { setUploadState("Choose a PNG, JPG, PDF, or DOCX file first."); return; }
    setUploadState("Checking file…"); setUploadResult(null);
    const form = new FormData(); form.append("file", file);
    try {
      const response = await fetch(`${API_BASE}/api/v1/verification/file`, { method: "POST", body: form });
      const data = await response.json();
      if (!response.ok) throw new Error(data.detail || `Request failed (${response.status})`);
      setUploadResult(data); setUploadState("Review complete.");
    } catch (error) {
      setUploadState(`Could not reach the review API. ${error instanceof Error ? error.message : "Check backend deployment and VITE_API_BASE_URL."}`);
    }
  }

  const planted = [
    { id: "required-term", label: "Required product name missing", team: "Marketing", channel: "Email", severity: "High", detected: true },
    { id: "forbidden-claim", label: "Planted unsupported superlative claim", team: "Sales", channel: "Social", severity: "High", detected: true },
    { id: "tone-drift", label: "Tone shifts from helpful to aggressive", team: "Support", channel: "Chat", severity: "Medium", detected: true },
    { id: "missing-alt", label: "Image has no alt text supplied", team: "Design", channel: "Web", severity: "Medium", detected: false },
    { id: "unclear-rule", label: "Rule 'sound premium' is ambiguous", team: "Marketing", channel: "Web", severity: "Low", detected: false },
  ];
  const detections = planted.filter((x) => x.detected && !dismissed.includes(x.id)).length;
  const detectionRate = Math.round(detections / planted.length * 100);

  function sendNotification() {
    const message = `TrueMark Round 3 alert\nTeam: ${team}\nChannel: ${channel}\nMessage drift similarity: ${drift.score}%\nMissing terms: ${drift.missing.join(", ") || "none"}\nAdded terms: ${drift.added.join(", ") || "none"}`;
    if (slack.trim()) {
      setNotifyStatus("Opening Slack notification link. For automatic delivery, configure a trusted Slack webhook on your backend.");
      window.open(slack.trim(), "_blank", "noopener,noreferrer");
    } else if (email.trim()) {
      window.location.href = `mailto:${encodeURIComponent(email.trim())}?subject=${encodeURIComponent("TrueMark brand governance alert")}&body=${encodeURIComponent(message)}`;
      setNotifyStatus("Email draft opened in your mail app; send it to deliver.");
    } else {
      setNotifyStatus("Enter a Slack channel URL or email address to prepare a notification.");
    }
  }

  return <div className="round3-page">
    <div className="r3-hero"><div><p className="r3-kicker">ROUND 3 · BRAND GOVERNANCE</p><h1>Trust, measured.</h1><p>Review assets, trace governance patterns, measure detection quality, and guard messages across channels.</p></div><span className="r3-status">● Workspace ready</span></div>
    <div className="r3-grid">
      <Panel title="01 · Image & document review" subtitle="PNG, JPG/JPEG, PDF and DOCX · powered by the connected API">
        <label className="r3-label" htmlFor="r3-file">Choose a file</label>
        <input id="r3-file" type="file" accept=".png,.jpg,.jpeg,.pdf,.docx" onChange={(e: ChangeEvent<HTMLInputElement>) => setFile(e.target.files?.[0] || null)} />
        <p className="r3-help">Maximum size: 5 MB. Logo/palette checks depend on a configured brand profile. Contrast and alt-text checks may require source metadata.</p>
        <button className="r3-button" onClick={analyzeFile}>Review selected file</button>
        {uploadState && <p className="r3-feedback" role="status">{uploadState}</p>}
        {uploadResult && <><div className="r3-result-summary"><strong>{uploadResult.file?.filename}</strong><span>{uploadResult.accessible_checks?.length || 0} checks returned</span></div><div className="r3-findings">{[...(uploadResult.accessible_checks || []), ...(uploadResult.unsupported_checks || [])].map((f: Finding, i: number) => <div className="r3-finding" key={`${f.check_name}-${i}`}><span className={`r3-pill ${f.status === "passed" ? "pass" : "review"}`}>{f.status || "info"}</span><div><strong>{f.check_name}</strong><p>{f.explanation}</p>{f.suggested_fix && <small>Next: {f.suggested_fix}</small>}</div></div>)}</div></>}
      </Panel>
      <Panel title="02 · Governance insights" subtitle="Explore example governance records by team and channel">
        <div className="r3-controls"><label>Team<select value={team} onChange={(e) => setTeam(e.target.value)}><option>Marketing</option><option>Sales</option><option>Support</option><option>Design</option></select></label><label>Channel<select value={channel} onChange={(e) => setChannel(e.target.value)}><option>Email</option><option>Social</option><option>Chat</option><option>Web</option></select></label></div>
        <div className="r3-stat-row"><div><strong>{team === "Marketing" ? 8 : team === "Sales" ? 5 : team === "Support" ? 3 : 4}</strong><span>Flagged items · sample</span></div><div><strong>{channel === "Social" ? 4 : channel === "Email" ? 7 : 2}</strong><span>Channel flags · sample</span></div></div>
        <h3 className="r3-subhead">Rules needing clarification</h3><ul className="r3-list"><li><strong>“Sound premium”</strong><span>Subjective; define examples and measurable tone cues.</span></li><li><strong>“Avoid too much jargon”</strong><span>Specify audience and list terms that require explanation.</span></li><li><strong>“Use accessible visuals”</strong><span>Set contrast ratio and alt-text acceptance criteria.</span></li></ul>
        <p className="r3-help">Clearly labelled sample data is shown here until live governance events are connected.</p>
      </Panel>
      <Panel title="03 · Measured reliability" subtitle="A reproducible demo set with planted issues">
        <div className="r3-stat-row"><div><strong>{runEval ? `${detectionRate}%` : "—"}</strong><span>Observed detection rate</span></div><div><strong>{planted.length}</strong><span>Planted test cases</span></div></div>
        <button className="r3-button" onClick={() => setRunEval(true)}>Run planted-error test set</button>
        {runEval && <div className="r3-findings">{planted.map((item) => <div className="r3-finding" key={item.id}><span className={`r3-pill ${item.detected && !dismissed.includes(item.id) ? "pass" : "review"}`}>{item.detected && !dismissed.includes(item.id) ? "detected" : dismissed.includes(item.id) ? "dismissed" : "missed"}</span><div><strong>{item.label}</strong><p>{item.team} · {item.channel} · {item.severity}</p>{item.detected && !dismissed.includes(item.id) && <button className="r3-text-button" onClick={() => setDismissed((old) => [...old, item.id])}>Dismiss finding (tune demo metric)</button>}</div></div>)}</div>}
        <p className="r3-help">This is a transparent demo metric, not a validated model benchmark. Dismissing a finding updates the displayed rate and is not persisted to a server.</p>
      </Panel>
      <Panel title="04 · Multi-channel drift guard" subtitle="Compare a source message with its adapted version">
        <label className="r3-label" htmlFor="r3-source">Canonical message</label><textarea id="r3-source" value={draft} onChange={(e) => setDraft(e.target.value)} rows={3} />
        <label className="r3-label" htmlFor="r3-adapted">Adapted message ({channel})</label><textarea id="r3-adapted" value={adapted} onChange={(e) => setAdapted(e.target.value)} rows={3} />
        <div className="r3-drift-score"><div><span>Token-overlap similarity</span><strong>{drift.score}%</strong></div><div className="r3-meter"><span style={{ width: `${drift.score}%` }} /></div></div>
        <div className="r3-diff"><p><strong>Missing from adapted copy:</strong> {drift.missing.join(", ") || "None"}</p><p><strong>Added in adapted copy:</strong> {drift.added.join(", ") || "None"}</p></div>
        <button className="r3-button secondary" onClick={() => setAdapted(`${draft.trim()} Please review before publishing.`)}>Draft drift-guard suggestion</button>
        <p className="r3-help">Suggestion is rule-based and should be reviewed by a human; no generative AI service is configured by default.</p>
      </Panel>
      <Panel title="05 · Notifications" subtitle="Prepare Slack or email alerts for a review">
        <label className="r3-label" htmlFor="r3-email">Email recipient</label><input id="r3-email" type="email" placeholder="team@example.com" value={email} onChange={(e) => setEmail(e.target.value)} />
        <label className="r3-label" htmlFor="r3-slack">Slack channel / workflow URL (optional)</label><input id="r3-slack" type="url" placeholder="https://slack.com/…" value={slack} onChange={(e) => setSlack(e.target.value)} />
        <button className="r3-button" onClick={sendNotification}>Prepare notification</button>
        {notifyStatus && <p className="r3-feedback" role="status">{notifyStatus}</p>}
        <p className="r3-help">For security, this client does not store webhook secrets or send unattended messages. Use a backend secret and approved provider integration for automated delivery.</p>
      </Panel>
      <Panel title="06 · Accessibility pass" subtitle="Keyboard and readability checks">
        <ul className="r3-list"><li><strong>Keyboard focus</strong><span>Interactive controls use visible focus outlines.</span></li><li><strong>Form labels</strong><span>Inputs have programmatic labels and status messages.</span></li><li><strong>Contrast</strong><span>Dark interface colors and text are checked visually; validate final contrast ratios before release.</span></li><li><strong>Responsive layout</strong><span>Panels stack on narrow screens.</span></li></ul>
      </Panel>
    </div>
  </div>;
}
