# TrueMark — Run Guide

**The original project files from the supplied ZIP have been preserved unchanged.** The only added files are this guide and `RUN_TRUEMARK.bat`, a convenience launcher.

## Requirements
- Windows 10/11
- Python 3.11 or newer (with Python added to PATH)
- Node.js 22 LTS (npm is included)
- Internet access for the first dependency installation

## Start the application
1. Extract the entire `TrueMark-Ready-to-Run.zip` folder.
2. Open the extracted `TrueMark-main` folder.
3. Double-click `RUN_TRUEMARK.bat`.
4. Wait for the dependency installation and startup to finish.
5. Open **http://127.0.0.1:5173** in your browser.
6. Backend API documentation is at **http://127.0.0.1:8000/docs**.

Keep both backend and frontend terminal windows open while using the application. To stop the services, close those two terminal windows.

## What is implemented in the supplied source
- React + TypeScript + Vite frontend.
- FastAPI backend.
- Rule-based text analysis for required and forbidden terms.
- In-memory brand profiles in the backend.
- Several frontend workspace features persist in the browser's local storage.

## Important limitations in the supplied source
This launcher does not change or add application functionality. The source README describes some capabilities as planned or in development. For example, the current backend exposes rule-based analysis; an external LLM integration, a production database, authentication, and cross-user persistence are not made functional by this launcher. Browser-local data is specific to that browser/device. No API key is required for the current rule-based text-analysis endpoint.

## Troubleshooting
- **`python` not found:** reinstall Python and enable “Add Python to PATH”.
- **`node` or `npm` not found:** install Node.js 22 LTS and reopen the launcher.
- **Dependency install fails:** check internet access and rerun `RUN_TRUEMARK.bat`.
- **Port already in use:** close any other app using port `5173` or `8000`, then retry.
- **Frontend opens but analysis fails:** confirm the backend window is running and visit `http://127.0.0.1:8000/health`.

Existing project files have not been edited to address or hide any limitations.
