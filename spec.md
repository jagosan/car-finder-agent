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
*   [ ] **Web Scraping Engine:**
    *   [x] Implement static scraper (`requests`, `BeautifulSoup`) - **Deprecated due to bot detection.**
    *   [ ] Implement dynamic scraper (`Selenium`, `webdriver-manager`) - **Primary scraping method.**
    *   [x] Implement Marketcheck API integration.
*   [x] **Data Storage:**
    *   [x] Implement SQLite database schema and connection logic.
*   [x] **AI-Powered Analysis:**
    *   [x] Implement Gemini API integration.
    *   [ ] Implement self-hosted model integration (Ollama with `gemma3`) for in-cluster analysis. **(Blocked)**
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
    *   [x] Create Kubernetes `Job` manifest (`scraper-job.yaml`) for Marketcheck API.
    *   [x] Create Kubernetes Service Account and Role-based Access Control (RBAC) for scraper Job creation.
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
    *   [x] Implement an endpoint to receive scraped data from the scraper job.
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
    *   **Status:** Complete. The `/scrape` endpoint is now asynchronous, using a background thread to run the scraper.

2.  **Implement Status Polling:**
    *   **Status:** Complete. A `/scrape-status` endpoint has been implemented, and the frontend now polls for real-time status updates.

3.  **Implement a PersistentVolumeClaim (PVC):**
    *   **Status:** Complete. The `hostPath` volume has been replaced with a `PersistentVolumeClaim` for the SQLite database, ensuring data persistence.

4.  **Optimize Container Images:**
    *   **Status:** Complete. Refactored the `backend/Dockerfile` and created a dedicated `scraper/Dockerfile` for the Marketcheck API to ensure each container image is minimal.
    *   **Goal:** Improve security, reduce image size, and speed up build/deployment times.

### Phase 5: UI Modernization

*   [x] **Modernize the UI:**
    *   [x] **Mobile UI:**
        *   [x] Display a preview image of the car.
        *   [x] Display an overview with:
            *   [x] Mileage
            *   [x] Exterior and Interior colors
            *   [x] Year
            *   [x] Accidents
            *   [x] Other standard information like AWD vs. RWD.
    - [x] **Tinder-like swiping:**
        *   [x] Implement swipe left/right to like/dislike.
    - [x] **Modern input fields:**
        *   [x] Update input fields to be more modern and pleasing.
*   [x] **Data model changes:**
    *   [x] **Marketcheck API:**
        *   [x] Check what data is available from the Marketcheck API.
    *   [x] **Database:**
        *   [x] Update the database schema to store the new data.
    *   [x] **Backend:**
        *   [x] Update the backend to serve the new data.

---

## 4. Current Debugging Focus

**Problem:** The scraper job is unable to resolve the hostname `marketcheck-prod.apigee.net`, leading to `NameResolutionError`. This indicates a potential DNS configuration issue or network restriction within the Kubernetes cluster for outbound connections.

**Current Status:**
*   The backend and frontend are stable and running.
*   The scraper is now configured to use the Marketcheck API.
*   Asynchronous scraping with status polling is implemented.
*   The database is persistent using a PVC.
*   A Kubernetes Service Account and RBAC have been created for job creation.

**Next Steps:**

1.  **Debug DNS Resolution:** Investigate the `NameResolutionError` in the scraper pod by executing `curl -v https://marketcheck-prod.apigee.net` from within the pod.
2.  **Verify Kubernetes DNS:** Check Kubernetes DNS settings and ensure pods can resolve external hostnames. This might involve `kubectl exec` into a pod and trying `nslookup marketcheck-prod.apigee.net`.
3.  **Network Policy Review:** If DNS resolution is confirmed, review any existing network policies that might be restricting outbound traffic from the scraper pods.
