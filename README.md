# client-agent

LINE Secretary Bot - AI-powered conversational assistant.

## Tech Stack

- **Backend**: Python / FastAPI (DDD + Clean Architecture)
- **Frontend**: TypeScript / React / Vite / Tailwind CSS
- **Tests**: pytest / httpx / Playwright

## Quick Start

```bash
docker compose up
```

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/health

## Development

### Backend

```bash
cd backend
pip install . ".[dev]"
cd src && uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
# Unit + Integration
pytest tests/unit tests/integration -v

# E2E (requires running servers)
cd tests/e2e
npx playwright test
```

## Project Structure

```
backend/src/
├── domain/           # Business core (entities, value objects, repositories)
├── application/      # Use cases, DTOs, services
├── infrastructure/   # External implementations (DB, APIs)
├── presentation/     # Controllers, routes, middleware
├── container/        # DI composition root
├── config/           # Environment config
├── constants/        # Magic numbers, HTTP status codes
└── utils/            # Pure utility functions

frontend/src/
├── pages/            # Page components (routing targets)
├── components/       # Reusable UI components
├── services/         # API clients (axios)
├── hooks/            # Logic extraction (React hooks)
├── types/            # Type definitions
├── constants/        # Constants, error messages, API paths
└── utils/            # Utility functions

tests/
├── unit/             # Unit tests (pytest)
├── integration/      # Integration tests (httpx)
└── e2e/              # E2E tests (Playwright)
```
