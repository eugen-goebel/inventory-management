# Contributing

Thanks for your interest! This is primarily a personal portfolio project, but contributions are welcome.

## Getting Started

This is a full-stack project. You will need both Python and Node.js installed.

### Backend (FastAPI)

1. Fork the repository and clone your fork.
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env.example` to `.env` and fill in values.
5. Run the backend:
   ```bash
   cd backend && uvicorn main:app --reload
   ```
6. Run the test suite:
   ```bash
   pytest -v
   ```

### Frontend (React + Vite)

1. Install Node.js dependencies:
   ```bash
   cd frontend && npm install
   ```
2. Start the dev server:
   ```bash
   npm run dev
   ```

## Submitting Changes

1. Create a feature branch from `main`:
   ```bash
   git checkout -b feature/your-feature
   ```
2. Make focused, well-described commits.
3. Make sure both the backend tests pass (`pytest -v`) and the frontend builds (`npm run build`).
4. Open a pull request against `main` with a clear description of what you changed and why. Reference any related issues.

## Code Style

- **Backend:** Follow PEP 8 for Python code.
- **Frontend:** TypeScript-strict; follow the existing component/hook patterns.
- Add tests for any new behavior.
- Update the README if user-facing behavior changes.
- Keep changes focused — one PR, one concern.
