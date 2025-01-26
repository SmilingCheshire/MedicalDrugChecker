# Drug Compatibility Checker

A web-based application that uses a GenAI-powered backend to analyze drug ingredient compatibility. The project consists of a Python Flask backend and an HTML/JavaScript-based frontend served through nginx.

---

## Features

- Search for medications using the FDA Open API.
- Add medications to a checker list for compatibility analysis.
- Analyze drug ingredient compatibility using GenAI (Ollama LLM API).
- Frontend built with Bootstrap and jQuery, and backend powered by Flask.

---

## Prerequisites

- **Docker** installed on your machine.
- FDA Open API key (if applicable).
- Access to Ollama's API server.

---

## Directory Structure
```bash
MedicalDrugChecker/
├── frontend_app/           # Frontend files
│   ├── index.html          # Main HTML file
│   ├── drug-checker.js     # JavaScript file
│   ├── styles.css          # Optional CSS file
│   └── project_logo.png    # Logo image
├── app.py                  # Flask backend application
├── config.yaml             # Backend configuration file
├── requirements.txt        # Backend dependencies
├── nginx.conf              # Nginx configuration file
├── supervisord.conf        # Supervisord configuration to run Flask and Nginx
├── Dockerfile              # Combined Dockerfile for backend and frontend
└── README.md               # Project documentation
```
---

## Installation and Usage

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/drug-compatibility-checker.git
   cd drug-compatibility-checker

---

2. **Build the Docker Image: Run the following command to build the Docker image**:
   ```bash
   docker build -t drug-checker-app .

---

3. **Run the Docker Container: Start the container**:
   ```bash
   docker run -d 8080:80 drug-checker-app

---

4. **Access the Application**:

- **Frontend:** Open your browser and go to http://localhost:8080.
- **Backend API:** Test endpoints at http://localhost:3000.