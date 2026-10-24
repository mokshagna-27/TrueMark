import { useState } from "react";

export default function BrandGuidelines() {
  const [brandName, setBrandName] = useState("TrueMark AI");
  const [industry, setIndustry] = useState("Artificial Intelligence");
  const [tone, setTone] = useState("Professional");
  const [personality, setPersonality] = useState(
    "Trustworthy, innovative, clear, and consistent"
  );
  const [writingStyle, setWritingStyle] = useState(
    "Use clear language, short sentences, and a consistent brand voice."
  );
  const [requiredTerms, setRequiredTerms] = useState(
    "TrueMark AI, trusted"
  );
  const [forbiddenTerms, setForbiddenTerms] = useState(
    "cheap, guaranteed"
  );
  const [primaryColor, setPrimaryColor] = useState("#4F46E5");
  const [secondaryColor, setSecondaryColor] = useState("#0F172A");
  const [logoRules, setLogoRules] = useState(
    "Use the approved logo. Do not stretch, recolor, or distort it."
  );
  const [message, setMessage] = useState("");

  function saveGuidelines() {
    const guidelines = {
      brandName,
      tone,
      requiredTerms: requiredTerms
        .split(",")
        .map((term) => term.trim())
        .filter(Boolean),
      forbiddenTerms: forbiddenTerms
        .split(",")
        .map((term) => term.trim())
        .filter(Boolean),

      // Additional brand identity settings
      industry,
      personality,
      writingStyle,
      primaryColor,
      secondaryColor,
      logoRules,
    };

    localStorage.setItem(
      "truemark-brand-guidelines",
      JSON.stringify(guidelines)
    );

    setMessage("Guidelines saved successfully!");
  }

  function loadGuidelines() {
    const saved = localStorage.getItem("truemark-brand-guidelines");

    if (!saved) {
      setMessage("No saved guidelines found. Save your guidelines first.");
      return;
    }

    try {
      const guidelines = JSON.parse(saved);

      setBrandName(guidelines.brandName ?? "TrueMark AI");
      setTone(guidelines.tone ?? "Professional");
      setRequiredTerms(
        Array.isArray(guidelines.requiredTerms)
          ? guidelines.requiredTerms.join(", ")
          : "TrueMark AI, trusted"
      );
      setForbiddenTerms(
        Array.isArray(guidelines.forbiddenTerms)
          ? guidelines.forbiddenTerms.join(", ")
          : "cheap, guaranteed"
      );

      setIndustry(guidelines.industry ?? "Artificial Intelligence");
      setPersonality(
        guidelines.personality ??
          "Trustworthy, innovative, clear, and consistent"
      );
      setWritingStyle(
        guidelines.writingStyle ??
          "Use clear language, short sentences, and a consistent brand voice."
      );
      setPrimaryColor(guidelines.primaryColor ?? "#4F46E5");
      setSecondaryColor(guidelines.secondaryColor ?? "#0F172A");
      setLogoRules(
        guidelines.logoRules ??
          "Use the approved logo. Do not stretch, recolor, or distort it."
      );

      setMessage("Saved guidelines loaded successfully!");
    } catch {
      setMessage("Could not load saved guidelines.");
    }
  }

  return (
    <section className="brand-guidelines">
      <header className="guidelines-header">
        <div>
          <p className="guidelines-eyebrow">BRAND GOVERNANCE</p>
          <h1>Brand Guidelines</h1>
          <p>
            Define your brand identity, communication style, content rules,
            and visual standards in one place.
          </p>
        </div>

        <div className="guidelines-badge">✦ AI Brand Standards</div>
      </header>

      <form
        onSubmit={(event) => {
          event.preventDefault();
          saveGuidelines();
        }}
      >
        <div className="guideline-section">
          <div className="guideline-section-heading">
            <span className="guideline-icon">🏢</span>
            <div>
              <h2>Brand Identity</h2>
              <p>Define the core information about your brand.</p>
            </div>
          </div>

          <div className="guideline-grid">
            <div className="guideline-field">
              <label htmlFor="brandName">Brand name</label>
              <input
                id="brandName"
                value={brandName}
                onChange={(event) => setBrandName(event.target.value)}
                placeholder="Enter brand name"
                required
              />
            </div>

            <div className="guideline-field">
              <label htmlFor="industry">Industry</label>
              <select
                id="industry"
                value={industry}
                onChange={(event) => setIndustry(event.target.value)}
              >
                <option>Artificial Intelligence</option>
                <option>Technology</option>
                <option>Education</option>
                <option>Healthcare</option>
                <option>Finance</option>
                <option>Retail and E-commerce</option>
                <option>Agriculture</option>
                <option>Other</option>
              </select>
            </div>
          </div>
        </div>

        <div className="guideline-section">
          <div className="guideline-section-heading">
            <span className="guideline-icon">🎯</span>
            <div>
              <h2>Brand Voice</h2>
              <p>Specify how your brand should communicate.</p>
            </div>
          </div>

          <div className="guideline-grid">
            <div className="guideline-field">
              <label htmlFor="tone">Communication tone</label>
              <select
                id="tone"
                value={tone}
                onChange={(event) => setTone(event.target.value)}
              >
                <option>Professional</option>
                <option>Friendly</option>
                <option>Formal</option>
                <option>Playful</option>
                <option>Confident</option>
                <option>Minimalist</option>
                <option>Empathetic</option>
                <option>Authoritative</option>
              </select>
            </div>

            <div className="guideline-field">
              <label htmlFor="personality">Brand personality</label>
              <input
                id="personality"
                value={personality}
                onChange={(event) => setPersonality(event.target.value)}
                placeholder="e.g. Clear, reliable, innovative"
              />
            </div>
          </div>

          <div className="guideline-field">
            <label htmlFor="writingStyle">Writing style instructions</label>
            <textarea
              id="writingStyle"
              value={writingStyle}
              onChange={(event) => setWritingStyle(event.target.value)}
              rows={3}
              placeholder="Describe how content should be written..."
            />
          </div>
        </div>

        <div className="guideline-section">
          <div className="guideline-section-heading">
            <span className="guideline-icon">📝</span>
            <div>
              <h2>Content Rules</h2>
              <p>Define words and phrases that content should follow.</p>
            </div>
          </div>

          <div className="guideline-field">
            <label htmlFor="requiredTerms">
              Required words or phrases
            </label>
            <textarea
              id="requiredTerms"
              value={requiredTerms}
              onChange={(event) => setRequiredTerms(event.target.value)}
              placeholder="Example: TrueMark AI, trusted"
              rows={3}
            />
            <small>Separate multiple terms with commas.</small>
          </div>

          <div className="guideline-field">
            <label htmlFor="forbiddenTerms">
              Forbidden words or phrases
            </label>
            <textarea
              id="forbiddenTerms"
              value={forbiddenTerms}
              onChange={(event) => setForbiddenTerms(event.target.value)}
              placeholder="Example: cheap, guaranteed"
              rows={3}
            />
            <small>
              Content Analysis uses these terms to flag potential violations.
            </small>
          </div>
        </div>

        <div className="guideline-section">
          <div className="guideline-section-heading">
            <span className="guideline-icon">🎨</span>
            <div>
              <h2>Visual Identity</h2>
              <p>Record the brand colors and logo usage standards.</p>
            </div>
          </div>

          <div className="guideline-grid">
            <div className="guideline-field">
              <label htmlFor="primaryColor">Primary brand color</label>
              <div className="color-input-row">
                <input
                  id="primaryColor"
                  type="color"
                  value={primaryColor}
                  onChange={(event) => setPrimaryColor(event.target.value)}
                />
                <span>{primaryColor.toUpperCase()}</span>
              </div>
            </div>

            <div className="guideline-field">
              <label htmlFor="secondaryColor">Secondary brand color</label>
              <div className="color-input-row">
                <input
                  id="secondaryColor"
                  type="color"
                  value={secondaryColor}
                  onChange={(event) =>
                    setSecondaryColor(event.target.value)
                  }
                />
                <span>{secondaryColor.toUpperCase()}</span>
              </div>
            </div>
          </div>

          <div className="guideline-field">
            <label htmlFor="logoRules">Logo usage guidelines</label>
            <textarea
              id="logoRules"
              value={logoRules}
              onChange={(event) => setLogoRules(event.target.value)}
              rows={3}
              placeholder="Describe the approved logo usage rules..."
            />
          </div>

          <div className="brand-color-preview">
            <span
              className="brand-color-swatch"
              style={{ backgroundColor: primaryColor }}
            />
            <span
              className="brand-color-swatch"
              style={{ backgroundColor: secondaryColor }}
            />
            <div>
              <strong>{brandName || "Your Brand"}</strong>
              <p>Brand color preview</p>
            </div>
          </div>
        </div>

        <div className="guideline-actions">
          <button type="submit">Save Guidelines</button>
          <button type="button" onClick={loadGuidelines}>
            Load Saved Guidelines
          </button>
        </div>
      </form>

      {message && (
        <p className="guidelines-message" role="status">
          {message}
        </p>
      )}

      <div className="guidelines-note">
        <strong>Storage information</strong>
        <p>
          Guidelines are currently saved in this browser on this device.
          Required and forbidden terms are also used by the Content Analysis
          feature.
        </p>
      </div>
    </section>
  );
}
