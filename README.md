# Modern Face Recognition Attendance System (Web)

A full-stack web application for real-time face recognition attendance tracking. The backend runs on FastAPI with OpenCV and face-recognition, and the frontend is a React single-page app with a dark 3D retro design.

## Features
- Student registration with live webcam capture
- Real-time face recognition and attendance marking
- MongoDB Atlas storage with binary face encodings
- Dashboard stats and recent activity
- Attendance records with date range filtering

## Tech Stack
- Backend: FastAPI, OpenCV, face-recognition, pymongo
- Frontend: React + Vite
- Database: MongoDB Atlas

## Setup

### Backend
1. Create and activate a Python 3.10+ environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the API from the repo root:
   ```bash
   uvicorn backend.app.main:app --reload --port 8000
   ```

### Frontend
1. Install Node.js 18+.
2. Install dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Run the UI:
   ```bash
   npm run dev
   ```
4. Open the app:
   - http://localhost:5173

## Configuration
- MongoDB connection is defined in `backend/app/utils/constants.py`.

## Notes
- The web app uses the client webcam for captures. Make sure your browser grants camera permissions.
- The backend expects clear face images; poor lighting or occlusion may reduce accuracy.

## Project Structure
```
backend/
  app/
    main.py
    services/
    utils/
    models/
frontend/
  src/
    views/
    services/
    styles.css
```
