"""FastAPI application entry point."""
from __future__ import annotations

import logging
from typing import List

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from backend.app.models.schemas import (
    AttendanceRecordResponse,
    RecognitionFace,
    RecognitionResponse,
    StatusResponse,
    StudentResponse,
)
from backend.app.services.mongo_service import get_db_service
from backend.app.services.recognition_service import FaceRecognitionService
from backend.app.utils.constants import APP_NAME, APP_VERSION
from backend.app.utils.helpers import (
    get_current_date,
    image_bytes_to_bgr,
    numpy_to_binary,
    validate_name,
    validate_student_id,
)


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

app = FastAPI(title=APP_NAME, version=APP_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_db_service = get_db_service()
_db_service.connect()
_recognition_service = FaceRecognitionService()


@app.get("/api/health", response_model=StatusResponse)
def health_check() -> StatusResponse:
    return StatusResponse(success=True, message="Service is running")


@app.post("/api/students", response_model=StatusResponse)
async def register_student(
    student_id: str = Form(...),
    name: str = Form(...),
    image: UploadFile = File(...),
) -> StatusResponse:
    valid_id, id_message = validate_student_id(student_id)
    if not valid_id:
        raise HTTPException(status_code=400, detail=id_message)

    valid_name, name_message = validate_name(name)
    if not valid_name:
        raise HTTPException(status_code=400, detail=name_message)

    if _db_service.student_exists(student_id):
        raise HTTPException(status_code=409, detail="Student ID already exists in the system.")

    image_bytes = await image.read()
    frame = image_bytes_to_bgr(image_bytes)

    results = _recognition_service.recognize_faces(frame)
    if not results:
        raise HTTPException(status_code=400, detail="No face detected in the image.")

    encoding = _recognition_service.encode_faces(frame, [results[0].location])[0]
    student_doc = {
        "student_id": student_id.strip(),
        "name": name.strip(),
        "face_encoding": numpy_to_binary(encoding),
        "created_at": __import__("datetime").datetime.utcnow(),
    }
    success, message = _db_service.add_student(student_doc)
    if not success:
        raise HTTPException(status_code=500, detail=message)

    _recognition_service.load_known_faces()
    return StatusResponse(success=True, message=message)


@app.get("/api/students", response_model=List[StudentResponse])
def list_students() -> List[StudentResponse]:
    students = _db_service.get_students()
    return [
        StudentResponse(
            student_id=doc["student_id"],
            name=doc["name"],
            created_at=doc.get("created_at"),
        )
        for doc in students
    ]


@app.post("/api/recognize", response_model=RecognitionResponse)
async def recognize_faces(image: UploadFile = File(...)) -> RecognitionResponse:
    image_bytes = await image.read()
    frame = image_bytes_to_bgr(image_bytes)
    _recognition_service.load_known_faces()
    results = _recognition_service.recognize_faces(frame)
    response_faces = [
        RecognitionFace(
            student_id=result.student_id,
            name=result.name,
            confidence=result.confidence,
            location=list(result.location),
            is_match=result.is_match,
        )
        for result in results
    ]
    return RecognitionResponse(results=response_faces)


@app.post("/api/attendance/mark", response_model=RecognitionResponse)
async def recognize_and_mark(image: UploadFile = File(...)) -> RecognitionResponse:
    image_bytes = await image.read()
    frame = image_bytes_to_bgr(image_bytes)
    _recognition_service.load_known_faces()
    results = _recognition_service.recognize_faces(frame)

    for result in results:
        if result.is_match and result.student_id:
            _db_service.mark_attendance(result.student_id, result.name)

    response_faces = [
        RecognitionFace(
            student_id=result.student_id,
            name=result.name,
            confidence=result.confidence,
            location=list(result.location),
            is_match=result.is_match,
        )
        for result in results
    ]
    return RecognitionResponse(results=response_faces)


@app.get("/api/attendance", response_model=List[AttendanceRecordResponse])
def get_attendance(date: str | None = None, start: str | None = None, end: str | None = None):
    if start and end:
        records = _db_service.get_attendance_by_range(start, end)
    else:
        records = _db_service.get_attendance_by_date(date or get_current_date())

    return [
        AttendanceRecordResponse(
            student_id=doc["student_id"],
            name=doc["name"],
            date=doc["date"],
            time=doc["time"],
            status=doc["status"],
            created_at=doc.get("created_at"),
        )
        for doc in records
    ]
