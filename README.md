# AI Career Intelligence

FastAPI backend for PDF resume extraction, AI-assisted resume analysis and
improvement, career guidance, and skill-based job matching.

## Setup

1. Create and activate a Python virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. Create a `.env` file containing:

   ```text
   NVIDIA_API_KEY=your_key_here
   ```

4. Start the API from the project root:

   ```powershell
   python -m uvicorn backend.main:app --reload
   ```

Open `http://127.0.0.1:8000/app/` for the CareerOrbit dashboard, or
`http://127.0.0.1:8000/docs` for Swagger UI.

## Test

Run the local API tests (they do not call NVIDIA):

```powershell
python -m unittest discover -s tests
```

## Current limitations

Jobs are sample in-memory data. Resume analysis, improvement, and career
analysis require a configured NVIDIA API key and network access.
