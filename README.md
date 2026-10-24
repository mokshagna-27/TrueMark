TrueMark — Brand Consistency AI

Team Name: The Innovators
Hackathon: Inkloom AI — Round 2
Project Type: AI-powered Brand Governance Platform
Status: In Development

---

1. Project Overview

TrueMark is an AI-powered brand consistency and governance platform that helps organizations check whether their digital content follows their official brand guidelines before publication.

Organizations create content across websites, advertisements, social media, presentations, and other marketing channels. When different people create this content, inconsistencies in brand messaging, terminology, tone, and visual identity can occur.

TrueMark aims to identify these inconsistencies, explain why they matter, and suggest improvements so that teams can review and correct content before publishing it.

2. Problem Statement

Organizations often struggle to maintain consistent branding across multiple content formats and communication channels.

Manual brand reviews can be time-consuming, subjective, and difficult to scale. Teams need a centralized solution that can interpret brand guidelines, detect violations, explain findings, and support a structured review process.

TrueMark addresses this problem through automated brand-rule validation, AI-assisted content analysis, explainable findings, and human approval workflows.

3. Project Objectives

- Centralize brand guidelines and brand-specific rules.
- Analyze submitted content for brand consistency.
- Detect potential violations of tone, terminology, messaging, and other configured rules.
- Explain each detected issue with supporting evidence.
- Recommend corrections that align with brand guidelines.
- Generate structured analysis reports.
- Support human review and approval before publication.
- Maintain a consistent, traceable review process.

4. Proposed Features

4.1 Brand Guidelines Management

Allow authorized users to define and manage brand rules, preferred terminology, prohibited terms, tone-of-voice requirements, and messaging guidelines.

4.2 Content Analysis

Accept content for analysis and evaluate it against the relevant brand guidelines.

4.3 Rule-Based Validation

Use deterministic checks for clearly defined requirements, such as prohibited phrases, required terminology, and configured wording rules.

4.4 AI-Assisted Analysis

Use language-model-based analysis to identify contextual inconsistencies, tone mismatches, and potential messaging problems that require deeper interpretation.

4.5 Explainable Findings

Return structured findings containing the issue, its severity, relevant content evidence, the applicable rule where available, and a recommended correction.

4.6 Review and Approval

Provide a workflow for reviewers to examine findings, make decisions, request changes, and record approval status.

4.7 Reports and Governance Insights

Present analysis summaries, issue counts, recurring violations, and historical review information.

Implementation note: These are the intended system capabilities. Each feature should be marked complete only after it has been implemented and tested.

5. Technology Stack

Component| Technology| Purpose
Frontend| React, TypeScript| User interface and application logic
Frontend tooling| Vite| Development server and build tooling
Styling| Tailwind CSS| Responsive interface styling
Backend| Python, FastAPI| REST API and application services
Database| PostgreSQL| Persistent application data
Vector search| pgvector| Semantic retrieval of relevant guideline content
AI analysis| LLM API| Contextual analysis and explanations
Rule engine| Python| Deterministic brand-rule checks
Authentication| JWT-based authentication, planned RBAC| Secure access and role-based permissions
Testing| pytest| Backend tests
Containerization| Docker, Docker Compose| Consistent development and deployment environments

Database clarification: PostgreSQL with pgvector is the proposed database architecture. Confirm that the database and extension have actually been configured before describing them as operational.

6. System Architecture

The planned request flow is:

## System Architecture

```text
User
  |
  v
React + TypeScript Frontend
  |
  v
FastAPI Backend
  |
  +---- Authentication and Authorization
  |
  +---- Content Validation
  |
  +---- Brand Rules Engine
  |
  +---- AI Analysis Service
  |         |
  |         +---- LLM API
  |         |
  |         +---- Guideline Retrieval
  |
  +---- Finding Aggregation and Scoring
  |
  +---- Review and Approval Workflow
  |
  v
PostgreSQL + pgvector
  |
  v
Structured Analysis Results
  |
  v
Frontend Results, Recommendations and Reports
```


The rule engine and AI analysis service have complementary responsibilities. Deterministic rules handle explicit requirements, while the AI service helps interpret contextual issues. The backend combines their outputs into a structured result for users to review.

7. Project Structure

The following is the target repository structure, based on the backend files already started and the frontend architecture planned for the project.

## Project Structure

```text
TrueMark/
├── README.md
├── .gitignore
├── .env.example
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── router.py
│   │   │   └── analysis.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── brand_rules.py
│   │   │   ├── consistency.py
│   │   │   ├── ai_analysis.py
│   │   │   └── scoring.py
│   │   ├── db/
│   │   └── utils/
│   ├── tests/
│   │   ├── test_analysis.py
│   │   └── test_brand_rules.py
│   └── uploads/
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   └── tsconfig.json
├── docker-compose.yml
└── Dockerfile
```
Important: The tree describes the intended organization, not proof that every file exists. Your current backend has included "main.py", "requirements.txt", "app/api/analysis.py", "app/api/router.py", "app/core/config.py", and a brand-rules service in progress. Add the other files as you implement them, and retain the actual paths used by your repository.

7.1 Backend Responsibilities by Module

Module| Responsibility
"main.py"| Create and start the FastAPI application
"api/router.py"| Register and organize API routes
"api/analysis.py"| Handle content-analysis requests
"core/config.py"| Read application settings and environment variables
"models/"| Define database entities
"schemas/"| Validate API inputs and outputs
"services/brand_rules.py"| Apply deterministic brand rules
"services/consistency.py"| Coordinate consistency checks
"services/ai_analysis.py"| Integrate AI-based analysis
"services/scoring.py"| Calculate finding scores or severity
"db/"| Manage database connections and sessions
"tests/"| Verify expected application behavior

7.2 Frontend Responsibilities by Module

Module| Responsibility
"components/"| Reusable UI elements
"pages/"| Dashboard, guidelines, analysis, results, and review screens
"services/"| Communicate with backend APIs
"types/"| Define TypeScript data types
"App.tsx"| Configure the main application interface
"main.tsx"| Mount the React application
"index.css"| Global styling

8. Team Members and Responsibilities

Team: The Innovators — 6 members

Responsibilities are assigned according to the team's previously discussed division. The exact deliverables below are proposed task ownership, so the team can adjust them based on availability and progress.

Member 1 — S. Guru Poojitha

Role: Backend Development and Integration

- Develop the FastAPI backend structure.
- Implement API routes and request/response validation.
- Develop brand-rule validation and consistency-checking services.
- Integrate the analysis pipeline and frontend APIs.
- Coordinate backend debugging and integration testing.

Primary deliverables: Working analysis API, rule-validation service, structured responses, and backend integration.

Member 2 — M. Spurthi

Role: Data and AI Support

- Help prepare representative brand-guideline and content examples.
- Organize sample inputs and expected analysis outputs.
- Support evaluation of AI-generated findings.
- Assist with checking the relevance and quality of recommendations.
- Document test scenarios and observed results.

Primary deliverables: Test datasets, sample guidelines, evaluation cases, and AI-quality feedback.

Member 3 — P. Sudeshna

Role: Frontend Development

- Build the React and TypeScript interface.
- Create the dashboard and content-submission screens.
- Display findings, severity levels, explanations, and recommendations.
- Connect the frontend to the backend API.
- Handle loading states, empty results, and error messages.

Primary deliverables: Functional frontend screens and API-connected analysis results.

Member 4 — V. Mokshagna

Role: AI Analysis and Explainability

- Research and implement the AI-assisted analysis workflow.
- Design prompts and structured model outputs.
- Help identify contextual tone and messaging inconsistencies.
- Support retrieval of relevant brand guidelines.
- Evaluate findings for accuracy and explainability.

Primary deliverables: AI-analysis service, structured findings, and evaluation examples.

Member 5 — S. Rahul Bangar

Role: Brand Rules and Quality Assurance

- Define examples of brand rules and policy categories.
- Implement or support deterministic validation checks.
- Prepare positive, negative, and edge-case tests.
- Check whether detected issues match the configured rules.
- Report false positives, missed violations, and integration defects.

Primary deliverables: Rule definitions, validation tests, and quality reports.

Member 6 — S. Sarasij Reddy

Role: Scoring, Evaluation and Documentation

- Help design a consistent finding-severity framework.
- Support analysis summaries and governance metrics.
- Review the clarity of explanations and recommendations.
- Maintain technical documentation and diagrams.
- Help prepare the demonstration, presentation, and final submission.

Primary deliverables: Scoring criteria, evaluation summaries, documentation, and demo materials.

Team Collaboration

All members should contribute to testing, integration, and the final demonstration. Role ownership means a member leads a component; it does not mean that the component can be developed or validated without coordination with the rest of the team.

9. Main Application Workflow

1. Configure brand guidelines: An authorized user enters brand-specific rules and requirements.
2. Submit content: A user provides content for review.
3. Validate the request: The backend checks the input and required fields.
4. Run deterministic checks: The rules engine identifies violations of explicit requirements.
5. Run AI-assisted analysis: The AI service examines contextual consistency and relevant guideline information.
6. Combine findings: The backend organizes the results, evidence, severity, and suggested corrections.
7. Review the results: The frontend presents the issues to the user.
8. Approve or request changes: A reviewer makes the final decision.
9. Record the outcome: The system stores review information when persistence is implemented.

10. Getting Started

Prerequisites

Install the following tools before running the complete application:

- Python
- Node.js and npm
- Git
- VS Code or another code editor

PostgreSQL, Docker, and an AI provider's API credentials are needed for the corresponding features once those integrations are configured.

Step 1: Clone the Repository

git clone <YOUR_GITHUB_REPOSITORY_URL>
cd TrueMark

Replace the placeholder with the actual repository URL.

Step 2: Set Up the Backend

Open a terminal in the repository root:

cd backend
python -m venv .venv

Activate the virtual environment.

Windows PowerShell:

.\.venv\Scripts\Activate.ps1

If your existing virtual environment is located in the repository root, activate that environment instead.

Install dependencies:

pip install -r requirements.txt

Start the backend, assuming "main.py" exposes an application object named "app":

uvicorn main:app --reload

If your application object or module path differs, use the actual import path.

Open the following addresses in your browser:

- API: "http://127.0.0.1:8000"
- Interactive API documentation: "http://127.0.0.1:8000/docs"

The API documentation will be available when the FastAPI application starts successfully.

Step 3: Set Up the Frontend

Open a second terminal:

cd frontend
npm install
npm run dev

Open the local URL printed by Vite.

The frontend commands require the "frontend" directory and its "package.json" to exist.

Step 4: Configure Environment Variables

Create a local ".env" file based on ".env.example".

Example placeholders:

APP_NAME=TrueMark
DATABASE_URL=
LLM_API_KEY=
JWT_SECRET_KEY=

Use the environment-variable names expected by the actual application configuration. Keep real credentials in local environment variables or an approved secrets manager. Never commit ".env" or actual API keys to GitHub.

Step 5: Verify the Integration

- Start the backend and confirm it runs without import errors.
- Check the available endpoints in "/docs".
- Start the frontend and confirm it loads.
- Configure the backend URL in the frontend service.
- Submit a sample content-analysis request.
- Verify the response structure and error handling.
- Test the analysis against known brand-rule examples.

11. Testing Strategy

The project should be tested at several levels.

Unit testing

- Brand-rule validation
- Consistency-checking logic
- Severity and scoring logic
- Request and response validation

Integration testing

- API-to-service communication
- AI service integration
- Database reads and writes
- Frontend-to-backend communication

Functional testing

- Valid content submission
- Empty or malformed requests
- Content with clear rule violations
- Content that follows the guidelines
- AI service failures and timeouts
- Review and approval status changes

Evaluation metrics

- Precision and recall of detected violations
- False-positive and missed-violation rates
- Relevance of recommended corrections
- Response time
- API error rate

The evaluation results should be measured using a documented test dataset rather than estimated or invented.

12. Security and Reliability

- Validate and sanitize incoming content.
- Keep API credentials and secrets outside source control.
- Enforce authentication and role-based authorization where implemented.
- Restrict access to sensitive brand information.
- Handle external AI-provider errors and timeouts.
- Apply upload limits if document or image uploads are supported.
- Avoid logging sensitive content unnecessarily.
- Store only the information required by the application.
- Treat AI findings as recommendations that a human can review, not guaranteed facts.

13. Development Roadmap

- [x] Define the project concept and initial technical direction.
- [x] Start organizing the FastAPI backend.
- [x] Create initial API and brand-rule files.
- [ ] Stabilize imports, configuration, and application startup.
- [ ] Complete deterministic rule validation.
- [ ] Define consistent request and response schemas.
- [ ] Connect a persistent PostgreSQL database.
- [ ] Implement AI-assisted analysis and guideline retrieval.
- [ ] Add finding aggregation, evidence, and severity scoring.
- [ ] Build and integrate the frontend.
- [ ] Add authentication and permissions.
- [ ] Implement review, approval, and report workflows.
- [ ] Add automated tests and error handling.
- [ ] Containerize and validate the complete application.
- [ ] Prepare the final demonstration and submission.

The checked items reflect the previously discussed project progress, not an independent verification of the current repository.

14. Expected Impact

TrueMark aims to help organizations:

- Reduce repetitive manual brand reviews.
- Identify inconsistent messaging before publication.
- Apply brand rules more consistently.
- Give content creators actionable explanations and corrections.
- Improve traceability of review decisions.
- Scale content governance across teams and channels.

The actual impact will depend on the quality of the implemented checks, evaluation results, and usability of the final system.

15. Limitations

- AI analysis can produce incorrect or incomplete findings.
- Results depend on the quality and completeness of the configured brand guidelines.
- Contextual interpretation may vary between content types.
- The initial prototype may support only a subset of file formats and content channels.
- Production deployment requires additional security, performance, and reliability testing.

16. Future Enhancements

- Support additional document and media formats.
- Add OCR and visual-brand checks for supported images.
- Improve semantic guideline retrieval.
- Introduce organization-specific roles and permissions.
- Provide analytics for recurring brand violations.
- Support versioned brand guidelines and audit history.
- Integrate with content-management and publishing workflows.

17. Project Team

The Innovators

Name| Primary responsibility
S. Guru Poojitha| Backend and integration
M. Spurthi| Data and AI evaluation
P. Sudeshna| Frontend development
V. Mokshagna| AI analysis and explainability
S. Rahul Bangar| Brand rules and QA
S. Sarasij Reddy| Scoring, evaluation and documentation

18. Acknowledgements

Developed as part of the Inkloom AI hackathon.

TrueMark — Make every brand interaction consistent, clear, and accountable.
