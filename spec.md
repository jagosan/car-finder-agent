# Project Plan: AI Car Finder Agent

This document outlines the goals, architecture, and development progress for the AI Car Finder Agent.

---

## 1. Project Goal & Core Components

The goal is to build a custom AI agent that finds used cars across multiple websites, analyzes them with an LLM, and delivers a daily digest of the best findings. The agent will also have a front-end to review cars, trigger on-demand scrapes, and provide feedback for model training.

*   **Web Scraping Engine:** Scrapes both static and dynamic websites for car listings.
*   **Data Standardization & Storage:** Cleans and stores listing data in a uniform SQLite database.
*   **AI-Powered Analysis:** Enriches raw data using either the Gemini API or a self-hosted open model.
*   **Containerization & Orchestration:** Runs the entire process reliably on a schedule within a GKE cluster.
*   **Digest Generation:** Creates and sends a daily HTML email summary.
*   **Front-end:** A web interface to review scraped cars, trigger on-demand scrapes, and provide feedback for model training.
*   **Back-end API:** An API to serve the front-end and handle user interactions.

---

## 2. Development Plan & Progress

This checklist tracks the implementation status of each component.

### Phase 1: Core Application Development

*   [x] **Source Control:** Set up GitHub repository and SSH keys.
*   [x] **Project Scolding:** Create Python project structure, `requirements.txt`, and `.gitignore`..
*   [x] **Web Scraping Engine:**
    *   [x] Implement static scraper (`requests`, `BeautifulSoup`) - **Deprecated due to bot detection.**
    *   [x] Implement dynamic scraper (`Selenium`, `webdriver-manager`) - **Primary scraping method.**
*   [x] **Data Storage:**
    *   [x] Implement SQLite database schema and connection logic.
*   [x] **AI-Powered Analysis:**
    *   [x] Implement Gemini API integration.
    *   [x] Implement self-hosted model integration (Ollama with `gemma3`) for in-cluster analysis.
*   [x] **Digest Generation:**
    *   [x] Create HTML email template (Jinja2).
    *   [x] Implement email sending logic.
*   [x] **Main Application Logic:**
    *   [x] Create `main.py` to orchestrate the scraping, analysis, and digest generation workflow.

### Phase 2: Containerization & Deployment

*   [x] **Containerization:**
    *   [x] Create `Dockerfile` for the application.
    *   [x] Build and test the Docker image locally.
*   [x] **Orchestration (GKE):**
    *   [x] Create GKE cluster.
    *   [x] Deploy Ollama with `gemma3` model to the GKE cluster.
    *   [x] Create Kubernetes `CronJob` manifest (`cronjob.yaml`).
    *   [x] Set up Google Artifact Registry for the container image.
    *   [x] Deploy the application to the GKE cluster.

### Phase 3: Front-end and API

*   [x] **Front-end:**
    *   [x] Create a new React application for the front-end.
    *   [x] Implement a UI to display scraped car listings.
    *   [x] Add a button to trigger on-demand scrapes.
    *   [x] Add a mechanism to provide feedback on car listings (e.g., like/dislike buttons).
*   [x] **Back-end API:**
    *   [x] Create a new Flask/FastAPI application for the back-end API.
    *   [x] Implement an endpoint to get car listings from the database.
    *   [x] Implement an endpoint to trigger a new scrape.
    *   [x] Implement an endpoint to store user feedback for model training.
*   [x] **Model Training:**
    *   [x] Research and implement a strategy for fine-tuning the Ollama model with user feedback. (Research done, implementation deferred)
*   [x] **Deployment:**
    *   [x] Create a new Dockerfile for the front-end.
    *   [x] Create a new Dockerfile for the back-end API.
    *   [x] Update Kubernetes manifests to include the new front-end and back-end deployments and services.
    *   [x] Expose the front-end service to the internet using an Ingress.
    *   [ ] Add SSL/443 support to the Ingress.

### Phase 4: Dev Environment & Tooling

*   [x] **Reproducible Dev Environment:**
    *   [x] Create a `.devcontainer` configuration for a consistent, container-based development environment.

---

## 3. Next Steps

The next step is to add SSL/443 support to the Ingress.

1.  **Add SSL/443 support:** I will update the Ingress to support SSL/443.
