# CloudVault

A local academic prototype demonstrating file management through a Flask web application and MinIO S3-compatible object storage. It does **not** use AWS or a public cloud account.

## Requirements
- Python 3.10+
- Docker Desktop / Docker Engine with Compose
- A modern browser

## Run MinIO
From this folder:
```bash
docker compose up -d
```
MinIO console: http://localhost:9001  
Local demo credentials: `cloudvault` / `cloudvault-local-secret`

These credentials are for a local demonstration only. Change them before any non-local use.

## Run Flask
Create and activate a virtual environment, then:
```bash
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and adjust values if needed. Then:
```bash
python app.py
```
Open http://127.0.0.1:5000

The app creates the `cloudvault-files` bucket on startup if it does not exist.

## Features
- Upload files (25 MB request limit)
- List objects with file size and last-modified time
- Download objects
- Delete objects
- Search visible filenames in the dashboard

## Important
This project demonstrates S3-compatible object storage locally using MinIO. It should be described accurately in the report as a local object-storage implementation, not an AWS deployment or a production public-cloud deployment. Do not expose the MinIO console publicly or commit `.env` credentials.
