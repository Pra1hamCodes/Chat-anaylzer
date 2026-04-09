.PHONY: help dev backend frontend test build up down clean

help:
	@echo "make dev       – run backend + frontend via docker compose"
	@echo "make backend   – run backend locally (uvicorn)"
	@echo "make frontend  – run frontend locally (next dev)"
	@echo "make test      – run backend tests"
	@echo "make up        – docker compose up --build"
	@echo "make down      – docker compose down"

dev: up

backend:
	cd backend && pip install -r requirements.txt && uvicorn app.main:app --reload --port 8000

frontend:
	cd frontend && npm install && npm run dev

test:
	cd backend && pytest -q

up:
	docker compose up --build

down:
	docker compose down

clean:
	rm -rf backend/data backend/.pytest_cache backend/**/__pycache__
