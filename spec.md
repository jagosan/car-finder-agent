# Project Plan: AI Car Finder Agent

This document outlines the goals, architecture, and development progress for the AI Car Finder Agent.

---

## 1. Project Goal & Core Components

The goal is to build a custom AI agent that finds used cars across multiple websites, analyzes them with an LLM, and delivers a daily digest of the best findings.

*   **Web Scraping Engine:** Scrapes both static and dynamic websites for car listings.
*   **Data Standardization & Storage:** Cleans and stores listing data in a uniform SQLite database.
*   **AI-Powered Analysis:** Enriches raw data using either the Gemini API or a self-hosted open model.
*   **Containerization & Orchestration:** Runs the entire process reliably on a schedule within a GKE cluster.
*   **Digest Generation:** Creates and sends a daily HTML email summary.

---

## 2. Development Plan & Progress

This checklist tracks the implementation status of each component.

### Phase 1: Core Application Development

*   [x] **Source Control:** Set up GitHub repository and SSH keys.
*   [x] **Project Scaffolding:** Create Python project structure, `requirements.txt`, and `.gitignore`.
*   [x] **Web Scraping Engine:**
    *   [x] Implement static scraper (`requests`, `BeautifulSoup`).
    *   [x] Implement dynamic scraper (`Selenium`, `webdriver-manager`).
*   [x] **Data Storage:**
    *   [x] Implement SQLite database schema and connection logic.
*   [ ] **AI-Powered Analysis:**
    *   [ ] Implement Gemini API integration.
    *   [ ] Implement self-hosted model integration (e.g., via Ollama).
*   [ ] **Digest Generation:**
    *   [ ] Create HTML email template (Jinja2).
    *   [ ] Implement email sending logic.
*   [ ] **Main Application Logic:**
    *   [ ] Create `main.py` to orchestrate the scraping, analysis, and digest generation workflow.

### Phase 2: Containerization & Deployment

*   [x] **Containerization:**
    *   [x] Create `Dockerfile` for the application.
    *   [ ] **(Blocked)** Build and test the Docker image locally. *(Requires user to configure Docker permissions).*
*   [ ] **Orchestration (GKE):**
    *   [ ] Create Kubernetes `CronJob` manifest (`cronjob.yaml`).
    *   [ ] Set up Google Artifact Registry for the container image.
    *   [ ] Deploy the application to the GKE cluster.

### Phase 3: Dev Environment & Tooling

*   [ ] **Reproducible Dev Environment:**
    *   [ ] Create a `.devcontainer` configuration for a consistent, container-based development environment.