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
    *   [ ] Add SSL/443 support to the Ingress. **(Blocked by GKE Ingress POST request issue)**

### Phase 4: Dev Environment & Tooling

*   [x] **Reproducible Dev Environment:**
    *   [x] Create a `.devcontainer` configuration for a consistent, container-based development environment.

---

## 3. Debug and Polish Plan

The following two-phase plan was established to first stabilize the application and then refactor it for long-term quality and scalability.

### Phase 1: Stabilize the Current System

The goal of this phase is to get the existing application working reliably to provide a stable foundation for future improvements.

1.  **Pinpoint the Current Bug:**
    *   **Status:** Complete. The root cause of the backend failure was identified as an `OOMKilled` error in the `ollama` pod.

2.  **Implement a Targeted Fix:**
    *   **Status:** Complete. The `ollama` pod's memory limit has been increased to `8Gi` and the pod is now stable.

3.  **Resolve Frontend-to-Backend Communication:**
    *   **Status:** Complete. The `proxy_pass` configuration in `frontend/nginx.conf` was corrected, resolving the communication breakdown between the frontend and backend pods.

4.  **Resolve the Ingress Issue:**
    *   **Action:** Investigate GKE Load Balancer logs and Ingress controller configurations to fix the issue preventing POST requests from working correctly.
    *   **Goal:** Enable SSL/TLS (HTTPS) for the frontend, securing the application.

### Phase 2: Architectural Refactoring

After the application is stable, this phase will address underlying architectural issues to make the system more robust, scalable, and maintainable.

1.  **Transition to Asynchronous Jobs:**
    *   **Action:** Modify the `/scrape` endpoint to be asynchronous. It will use the Kubernetes Python client to programmatically create a `Job` resource, which will run the scraper in the background.
    *   **Goal:** Provide an immediate API response and prevent HTTP timeouts. Decouple the API from the heavy-lifting scraper process.

2.  **Implement Status Polling:**
    *   **Action:** Create a new `/scrape-status/<job_id>` endpoint. The frontend will be updated to poll this endpoint to get the real-time status of a scraping job.
    *   **Goal:** Provide a responsive user experience with clear feedback on the progress of the scraping task.

3.  **Implement a PersistentVolumeClaim (PVC):**
    *   **Action:** Replace the current `hostPath` volume with a `PersistentVolumeClaim` for the SQLite database.
    *   **Goal:** Ensure data persistence and prevent data loss if the backend pod is rescheduled to a different node.

4.  **Optimize Container Images:**
    *   **Action:** Refactor the `backend/Dockerfile` and create a dedicated `scraper/Dockerfile` to ensure each container image is minimal, containing only the necessary code and dependencies.
    *   **Goal:** Improve security, reduce image size, and speed up build/deployment times.

---

## 4. Current Debugging Focus

**Problem:** Persistent `404 Client Error` from backend to Ollama service, despite the backend and Ollama pods running in the cluster and the backend image being up-to-date.

**Root Cause Investigation:**
*   The backend pod is unable to resolve or connect to the Ollama service, resulting in a `404 Client Error`. This is happening despite the debug pod being able to connect to the service successfully using `curl` with the exact same request parameters.
*   The issue is likely not with the network configuration, but with the backend application itself, possibly with the `requests` library.

**Current Status:**
*   The backend and Ollama deployments are stable and running.
*   The backend code is being updated correctly in the running pods.
*   The `404 Client Error` persists, blocking the completion of the Ollama integration.
*   The "unexpected token error" in the frontend remains to be investigated.

**Next Steps:**

1.  **User Assistance:** The issue has been escalated to the user for further investigation. It has been suggested that the user attempt to reproduce the issue locally and to double-check the versions of all relevant libraries and dependencies.
2.  **Frontend Error:** The "unexpected token error" reported by the user still needs to be investigated once the backend is stable.
