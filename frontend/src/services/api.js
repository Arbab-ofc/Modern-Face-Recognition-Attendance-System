const API_BASE = "http://localhost:8000/api";

async function apiGet(path) {
  const response = await fetch(`${API_BASE}${path}`);
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }
  return response.json();
}

async function apiPost(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    body
  });
  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Request failed");
  }
  return response.json();
}

export async function fetchStudents() {
  return apiGet("/students");
}

export async function fetchAttendance(date) {
  const query = date ? `?date=${date}` : "";
  return apiGet(`/attendance${query}`);
}

export async function fetchAttendanceRange(start, end) {
  return apiGet(`/attendance?start=${start}&end=${end}`);
}

export async function registerStudent(formData) {
  return apiPost("/students", formData);
}

export async function recognizeAndMark(formData) {
  return apiPost("/attendance/mark", formData);
}

export async function recognizeFaces(formData) {
  return apiPost("/recognize", formData);
}
