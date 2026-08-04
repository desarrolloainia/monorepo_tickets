.DEFAULT_GOAL := help

.PHONY: help install dev web api build clean

help:
	@echo make install  Install frontend and backend dependencies
	@echo make dev      Start the Nuxt development server
	@echo make api      Run the backend entry point
	@echo make build    Build the frontend
	@echo make clean    Remove generated files

install:
	pnpm --dir frontend install
	uv sync --directory backend

dev web:
	pnpm --dir frontend dev

api:
	uv run --directory backend uvicorn main:app --app-dir src --reload

build:
	pnpm --dir frontend build

clean:
	powershell -NoProfile -Command "Remove-Item -Recurse -Force -ErrorAction SilentlyContinue frontend/.nuxt,frontend/.output,frontend/dist,backend/.venv"
