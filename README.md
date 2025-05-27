# TSA Item Checker Backend

A FastAPI-based backend service that helps travelers determine whether items are allowed in carry-on or must be checked baggage according to TSA regulations. The service combines database caching with AI-powered analysis for efficient and accurate responses.

## Features

- **Smart Caching System**: Checks Supabase database first for known items before using AI
- **AI-Powered Analysis**: Utilizes OpenRouter AI (GPT-3.5-turbo) for analyzing new items
- **Auto-Learning**: Automatically stores new AI responses in the database
- **CORS Support**: Configured for both production and development environments
- **RESTful API**: Clean and well-documented endpoints
- **Production Ready**: Deployed on Render with Gunicorn server

## Tech Stack

- **Framework**: FastAPI 0.109.0
- **Database**: Supabase
- **AI Service**: OpenRouter (GPT-3.5-turbo)
- **Python Version**: 3.11+
- **Dependencies**: See requirements.txt

## Prerequisites

- Python 3.11 or higher
- Supabase account and project
- OpenRouter API key

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_anon_key
OPENROUTER_API_KEY=your_openrouter_api_key
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd TSA_BackEnd
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

### Development
```bash
uvicorn main:app --reload
```

### Production
```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## API Endpoints

### GET /check/{item}
Checks if an item is allowed in carry-on luggage.

**Parameters**:
- `item` (path): The item to check

**Response**:
```json
{
    "item": "string",
    "allowed_carryon": boolean,
    "explanation": "string"
}
```

## CORS Configuration

The API allows requests from:
- https://brutalist-checkpoint-guide.lovable.app (Production)
- http://localhost:8080 (Development)

## Project Structure

- `main.py`: Main application file with FastAPI routes and core logic
- `check_table.py`: Database inspection utilities
- `test_api.py`: API endpoint testing
- `requirements.txt`: Project dependencies
- `runtime.txt`: Python runtime specification

## Database Schema

The Supabase database stores item check results with the following structure:
- `item`: Item name (string)
- `allowed_carryon`: Whether the item is allowed in carry-on (boolean)
- `explanation`: Detailed explanation of the decision (text)

## Testing

Run the test suite using:
```bash
python test_api.py
```

## Deployment

The application is configured for deployment on Render. Key considerations:
- Uses Gunicorn as the production server
- Configured with multiple workers for better performance
- Environment variables must be set in the deployment platform

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Add your license information here]
