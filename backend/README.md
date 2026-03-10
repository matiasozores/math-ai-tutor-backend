# AI Math Tutor Backend

Backend API for the AI Math Tutor application that analyzes student math solutions and provides step-by-step feedback.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Configure your API key in `.env`:
   - For OpenAI: Set `AI_API_KEY` to your OpenAI API key
   - For Groq: Set `AI_API_KEY` and uncomment `AI_BASE_URL` and `AI_MODEL`

## Running the Server

Start the development server:
```bash
uvicorn main:app --reload
```

Or run with Python:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Documentation

Visit `http://localhost:8000/docs` for interactive API documentation.

## Environment Variables

- `AI_API_KEY`: Your AI provider API key (required)
- `AI_BASE_URL`: Base URL for alternative AI providers (optional)
- `AI_MODEL`: AI model to use (default: gpt-3.5-turbo)
- `API_HOST`: Server host (default: 0.0.0.0)
- `API_PORT`: Server port (default: 8000)
- `APP_NAME`: Application name (default: AI Math Tutor)
- `DEBUG`: Debug mode (default: false)

## API Endpoints

- `POST /api/solve`: Analyze math solution
- `GET /`: Welcome message
- `GET /health`: Health check

## Example Request

```bash
curl -X POST "http://localhost:8000/api/solve" \
     -H "Content-Type: application/json" \
     -d '{
       "problem": "Solve for x: 2x + 5 = 15",
       "student_solution": "2x + 5 = 15\n2x = 10\nx = 5"
     }'
```
