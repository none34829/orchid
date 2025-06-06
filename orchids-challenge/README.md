# Orchids Website Cloning Application

This project implements a website cloning application that uses AI to replicate the visual design and structure of existing websites. It consists of a backend built with FastAPI and a frontend built with Next.js and TypeScript.

## Features

- Website scraping using Playwright and BeautifulSoup
- AI-powered website cloning with Claude or Gemini
- Modern and responsive UI
- Background job processing
- Caching for improved performance
- Job status tracking and results preview

## System Requirements

- Python 3.8+ for the backend
- Node.js 18+ for the frontend
- Playwright browser dependencies

## Setup Instructions

### Backend Setup

The backend uses `uv` for package management.

1. Navigate to the backend directory:

```bash
cd backend
```

2. Install dependencies:

```bash
uv sync
```

3. Install Playwright browsers:

```bash
python -m playwright install chromium
```

4. Set up environment variables by creating a `.env` file in the backend directory:

```
ANTHROPIC_API_KEY=your_anthropic_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

You need at least one of these API keys for the website cloning to work.

5. Create cache and jobs directories:

```bash
mkdir -p cache jobs
```

### Running the Backend

To run the backend development server, use the following command:

```bash
python -m app.main
# OR
uv run python -m app.main
```

The backend will start on http://localhost:8000.

### Frontend Setup

The frontend is built with Next.js and TypeScript.

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
```

### Running the Frontend

To start the frontend development server, run:

```bash
npm run dev
```

The frontend will start on http://localhost:3000.

## Using the Application

1. Open your browser and navigate to http://localhost:3000
2. Enter a public website URL in the form
3. Select the AI model to use (Claude or Gemini)
4. Submit the form and wait for the cloning process
5. The application will display the status of the cloning job
6. Once completed, you can view the cloned website

## Application Structure

### Backend

- `app/main.py`: Main FastAPI application and API endpoints
- `app/scraper.py`: Website scraping module using Playwright and BeautifulSoup
- `app/llm_clone.py`: AI integration for website cloning using Claude and Gemini

### Frontend

- `src/app/page.tsx`: Main landing page with clone form
- `src/app/components/`: React components for the UI
- `src/app/status/[jobId]/page.tsx`: Job status display page
- `src/app/preview/[jobId]/page.tsx`: Cloned website preview page

## Notes

- The application uses background tasks for processing to avoid timeouts
- Scraping results are cached to improve performance for repeated requests
- The LLM models require valid API keys to function
- Claude 4 Sonnet is recommended for best results, but Gemini 2.5 Pro is also supported
- The application is designed to handle various website structures
