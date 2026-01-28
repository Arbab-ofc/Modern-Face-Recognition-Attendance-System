# Modern Face Recognition Attendance System

A production-ready desktop application for real-time face recognition attendance tracking. Built with PyQt6, OpenCV, and MongoDB Atlas, it provides fast registration, live recognition, and clear reporting with a modern dark UI.

## Features
- Real-time face recognition and automatic attendance marking
- Student registration with live camera capture
- MongoDB-backed storage with binary face encodings
- Dashboard with statistics and recent activity
- Records view with filters and CSV export
- Responsive layout optimized for 800x600, 1366x768, and 1920x1080

## Technology Stack
| Layer | Technology |
| --- | --- |
| Language | Python 3.10+ |
| GUI | PyQt6 |
| Computer Vision | OpenCV |
| Face Recognition | face_recognition (dlib) |
| Database | MongoDB Atlas |
| Driver | pymongo + dnspython |
| Icons | QtAwesome (fa5s) |
| Image Processing | NumPy, Pillow |
| Serialization | pickle |

## Installation
1. Clone the repository.
2. Create and activate a Python 3.10+ virtual environment.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
- Database settings are defined in `FaceAttendance/utils/constants.py`.
- Update the MongoDB URI only inside `constants.py`.

## Usage
1. Run the application:
   ```bash
   python FaceAttendance/main.py
   ```
2. Register students in the Register view.
3. Use Attendance view to mark attendance in real-time.
4. Review records and export from Records view.

## Project Structure
```
FaceAttendance/
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
├── ui/
├── vision/
├── database/
├── models/
└── utils/
```

## Screenshots
Add screenshots here:
- Dashboard
- Registration
- Attendance
- Records

## Contributing
1. Fork the repository.
2. Create a feature branch.
3. Commit changes with clear messages.
4. Open a pull request.

## License
Specify the license for this project.

## Integration Checklist
- Database connection works
- Camera captures frames
- Face detection works
- Face encoding storage works
- Face recognition matches correctly
- Attendance marking prevents duplicates
- All views navigate correctly
- Responsive design works at all sizes
- No emojis anywhere in codebase
- All icons render correctly
- Error handling shows user-friendly messages

## Release
- v1.0.0
