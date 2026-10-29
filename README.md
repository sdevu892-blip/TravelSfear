# TravelSfear Flask Project

A BCA-friendly Kerala tourism web application built with Flask, SQLite/MySQL-ready database, Bootstrap, HTML, CSS and JavaScript.

## Features

- User registration and login
- Password hashing
- Tourist places
- Restaurant listings
- Search
- Favourite places
- User profile and travel preferences
- AI chatbot demo endpoint
- Weather endpoint with optional OpenWeather API
- Emergency contacts
- JSON API endpoints for future Android/mobile frontend
- MySQL-ready configuration

## Run in VS Code

### 1. Open this folder in VS Code

Open the `TravelSfear` folder.

### 2. Create virtual environment

Windows:

    py -m venv .venv
    .venv\Scripts\activate

macOS/Linux:

    python3 -m venv .venv
    source .venv/bin/activate

### 3. Install packages

    pip install -r requirements.txt

### 4. Create `.env`

Copy `.env.example` to `.env`.

For the first run, leave:

    DATABASE_URL=sqlite:///travelsfear.db

### 5. Run

    python app.py

Open:

    http://127.0.0.1:5000

The SQLite database and sample data are created automatically.

## MySQL

Create a database named `travelsfear`, then change `.env`:

    DATABASE_URL=mysql+pymysql://root:YOUR_PASSWORD@localhost/travelsfear

Restart the app.

## Optional weather

Create an OpenWeather API key and put it in `.env`:

    OPENWEATHER_API_KEY=your_key

## API examples

GET `/api/places`

GET `/api/restaurants`

GET `/api/emergency`

POST `/api/chatbot`

JSON:

    {
      "message": "I need a vegetarian restaurant under ₹500 near Fort Kochi"
    }

## Important project note

The chatbot included here is a working demo/rule-based assistant. For a real AI chatbot, connect OpenAI or Gemini using a server-side API key. Do not expose API keys in HTML or JavaScript.

Google Maps/Places, ride booking and translation should be connected using their current official APIs and credentials after checking their terms and availability.
