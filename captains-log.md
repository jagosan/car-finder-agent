# Captain's Log

## Stardate: 2025.10.15

### Mission: AI Car Finder Agent

**Objective:** To build a custom AI agent that finds used cars across multiple websites, analyzes them with an LLM, and delivers a daily digest of the best findings.

**Mission Summary:**

The project was a success. The AI Car Finder Agent is now fully operational, deployed on a GKE cluster and running on a daily schedule. The agent scrapes car listings, analyzes them using a self-hosted Ollama model, and sends a daily digest email.

**Key Events & Lessons Learned:**

1.  **Initial Scraping Strategy:**
    *   **What happened:** The initial attempt to use a static scraper with `requests` and `BeautifulSoup` was quickly thwarted by bot detection mechanisms on the target websites.
    *   **Resolution:** We pivoted to a dynamic scraping approach using `Selenium` and a headless Chrome browser, which proved to be more resilient.
    *   **Lesson Learned:** For modern, dynamic websites, a simple static scraper is often insufficient. A more robust solution like Selenium is necessary to handle JavaScript-heavy pages and bot detection.

2.  **Dockerization and Environment:**
    *   **What happened:** We encountered several issues while trying to run the application inside a Docker container. These included permission errors with the Docker daemon and import errors due to incorrect file paths and outdated images.
    *   **Resolution:** We resolved the Docker permission issues by ensuring the user was in the `docker` group. The import errors were resolved by carefully checking the file paths and using the `--no-cache` option during the Docker build to ensure the latest code was included in the image.
    *   **Lesson Learned:** Dockerization can be tricky. It's important to have a solid understanding of Docker concepts like image layers, caching, and file permissions. Using `--no-cache` can be a useful debugging tool to ensure the image is being built from scratch.

3.  **AI Model Integration:**
    *   **What happened:** The initial plan was to use either the Gemini API or a self-hosted Ollama model. The Gemini API integration failed due to a missing API key. The Ollama integration also faced several challenges.
    *   **Resolution:** We decided to focus on the self-hosted Ollama model. We deployed Ollama to the GKE cluster using a Helm chart. We encountered several issues with this process:
        *   **Helm installation:** The `helm` command was not found, so we had to install it first.
        *   **Ollama model pulling:** The Ollama server was not pulling the specified model. We resolved this by creating a separate Kubernetes Job to pull the model.
        *   **Ollama service connectivity:** The application was getting a 404 error when trying to connect to the Ollama service. We debugged this by using a `curl` command from a separate pod and found that the model name was incorrect.
        *   **Ollama memory:** The Ollama server was crashing due to insufficient memory. We resolved this by increasing the memory resources for the Ollama pod.
    *   **Lesson Learned:** Deploying and configuring a self-hosted AI model in a Kubernetes cluster can be complex. It requires careful attention to details like resource allocation, service discovery, and model management. Using a Helm chart can simplify the deployment, but it's important to understand the chart's configuration options.

4.  **Kubernetes Deployment:**
    *   **What happened:** The `car-finder-agent` pod was in a `CrashLoopBackOff` state due to an OOMKilled error.
    *   **Resolution:** We increased the memory limits for the container in the `cronjob.yaml` file.
    *   **Lesson Learned:** It's important to carefully consider the resource requirements of the application and set the appropriate resource requests and limits in the Kubernetes manifests.

**Conclusion:**

This project was a valuable learning experience. We successfully built and deployed a complex AI agent, overcoming several technical challenges along the way. The lessons learned from this project will be invaluable for future projects involving web scraping, AI model integration, and Kubernetes deployment.

## Stardate: 2025.10.16

### Mission: Frontend and Backend Deployment & Debugging

**Objective:** Deploy the frontend and backend services to GKE, enable SSL, and resolve any operational issues.

**Key Events & Lessons Learned:**

1.  **Initial Deployment:**
    *   **What happened:** Attempted to deploy frontend and backend services to GKE.
    *   **Resolution:** Created `backend-service.yaml`, `frontend-service.yaml`, and `ingress.yaml`. Configured frontend Nginx to proxy API requests to the backend. Updated `frontend/Dockerfile` and `frontend/src/App.js`.
    *   **Lesson Learned:** Proper service and ingress configuration is crucial for inter-service communication and external access in Kubernetes.

2.  **GKE Authentication Issue:**
    *   **What happened:** `kubectl apply` failed with authentication errors (`gcloud auth login` required).
    *   **Resolution:** User re-authenticated `gcloud`.
    *   **Lesson Learned:** GKE deployments require up-to-date `gcloud` authentication.

3.  **ImagePullBackOff Error:**
    *   **What happened:** Frontend and backend pods were stuck in `ImagePullBackOff` status.
    *   **Resolution:** Built and pushed new Docker images for both frontend and backend to Google Artifact Registry.
    *   **Lesson Learned:** Ensure Docker images are built and pushed to the registry after code changes, and that GKE nodes have permissions to pull them.

4.  **Database Connection Error (`sqlite3.OperationalError: unable to open database file`):**
    *   **What happened:** Backend pod failed to start due to an inability to open the SQLite database file. This was caused by an incorrect `hostPath` volume mount and a `car_finder.db` directory conflict.
    *   **Resolution:**
        *   Changed `hostPath` in `kubernetes/backend-deployment.yaml` from `/data/car-finder-agent` to `/mnt/stateful_partition/car-finder-agent` (a writable location on GKE nodes).
        *   Removed `subPath: car_finder.db` from the volume mount and changed `mountPath` to `/app/database` to mount the entire directory.
        *   Updated `DATABASE` path in `backend/app.py` to `/app/database/car_finder.db`.
        *   Manually removed the conflicting `car_finder.db` directory from the host via `kubectl exec`.
    *   **Lesson Learned:** Careful configuration of `hostPath` volumes and understanding how `subPath` interacts with file vs. directory mounts is critical. `hostPath` is suitable for development but PersistentVolumeClaims are recommended for production.

5.  **Database Table Not Found Error (`sqlite3.OperationalError: no such table: listings`):**
    *   **What happened:** After resolving the database connection, the backend failed because the `listings` table did not exist in the newly created database.
    *   **Resolution:** Added an `init_db()` function to `backend/app.py` to create the necessary tables on application startup.
    *   **Lesson Learned:** Database schema initialization should be handled by the application, especially when dealing with ephemeral or newly created databases.

6.  **Scraping Failed (Silent Error):**
    *   **What happened:** The frontend reported "Scraping failed", but backend logs showed no specific error from the `subprocess.run` call. This indicated a silent failure within the `main.py` script.
    *   **Debugging Steps & Resolutions:**
        *   **Initial Logging Attempt:** Added `print(e.stderr)` to `backend/app.py` to capture subprocess errors, but it didn't appear in logs.
        *   **Dockerfile Correction:** Realized `main.py` and `src` were not correctly copied into the backend container. Modified `backend/Dockerfile` to copy the entire project from the root build context and merged `backend/requirements.txt` into the root `requirements.txt`.
        *   **Logging Module Integration:** Replaced `print` statements with `logging.error` for more robust error capture.
        *   **`subprocess.run` Argument Conflict:** Discovered `capture_output=True` and `stderr=subprocess.STDOUT` were mutually exclusive. Corrected `subprocess.run` to use `stdout=subprocess.PIPE` and `stderr=subprocess.PIPE` and manually check `result.returncode`.
        *   **`xvfb` Installation:** Identified that `chromedriver` was failing to start due to missing `xvfb` (X Virtual Framebuffer). Added `xvfb` installation to `backend/Dockerfile`.
        *   **Current Blocker:** Despite all these changes, the `main.py` script still fails silently when executed as a subprocess. The logs do not show any output from the script, even with `stdout` and `stderr` being captured. This suggests the script might be hanging or encountering an issue that prevents it from producing any output before a timeout.

**Current Blocker:** The `main.py` scraping script is not producing any output when executed as a subprocess from the backend Flask application. This is preventing further debugging of the scraping logic, as no errors or success messages are being logged, even after implementing comprehensive error handling and logging mechanisms.

**Next Steps:** The immediate next step is to debug the silent failure of the `main.py` scraping script. This involves further investigation into why the script is not producing any output when run as a subprocess, and how to capture its execution details.

## Stardate: 2025.10.26

### Mission: Architectural Review and Planning

**Objective:** Address the ongoing silent scraping failure, conduct a thorough architectural review, and establish a clear plan for debugging and improving the application.

**Mission Summary:**

The previous debugging efforts were based on an incorrect premise: that the backend was executing `main.py` as a subprocess. We have now confirmed that the `main.py` script was removed and its logic was integrated directly into the `/scrape` endpoint in `backend/app.py`. This synchronous execution model is the source of many of the application's issues.

A full architectural review was conducted, leading to the following key findings:

*   **Problem:** The synchronous, long-running API endpoint is fragile and not scalable.
*   **Problem:** Data persistence using `hostPath` is not robust for a Kubernetes environment.
*   **Problem:** The backend API process is overloaded, handling both web requests and heavy data processing.
*   **Problem:** Docker images are inefficient and contain unnecessary code.
*   **Problem:** The frontend provides poor feedback for long-running tasks.

Based on this analysis, a new two-phase **Debug and Polish Plan** was created and approved. This plan is now the official road map and has been documented in `spec.md`.

**Key Decisions:**

1.  **Acknowledge Architectural Flaws:** We will move away from the synchronous API model.
2.  **Adopt a Two-Phase Approach:**
    *   **Phase 1 (Stabilize):** First, we will get the current system working by pinpointing and fixing the immediate bug in the `scrape_cars` function.
    *   **Phase 2 (Refactor):** Second, we will perform a proper architectural refactoring, focusing on asynchronous job execution, robust data persistence (PVCs), and improved UX.

**Next Steps:**

Proceeding with **Phase 1, Step 1** of the new plan: Re-deploy the backend with enhanced logging to capture the root cause of the failure within the `scrape_cars` function.

## Stardate: 2025.10.27

### Mission: Debugging and Stabilization

**Objective:** Isolate and fix the root cause of the application failure.

**Mission Summary:**

Today's session was a deep dive into debugging the Kubernetes deployment. We successfully navigated a complex series of issues to identify the primary blocker.

1.  **Ingress & Routing:** We discovered and fixed multiple issues with the Ingress configuration, which was preventing the frontend from communicating with the backend correctly. This involved correcting API paths and simplifying the Ingress rules to properly align with the frontend's Nginx proxy configuration.
2.  **Ollama Memory Crash:** After fixing the Ingress, we successfully triggered the backend and discovered the true root cause: the `ollama` pod was crashing. We diagnosed this as an Out of Memory (`OOMKilled`) error.
3.  **Helm & Deployment Issues:** Attempts to fix the memory issue via `helm upgrade` were blocked by a series of environmental problems (deprecated GCR, incorrect project ID, incorrect Helm repo URLs, OCI authentication). 
4.  **Direct Intervention:** We pivoted to a more direct solution by modifying the live Kubernetes `Deployment` object for `ollama` and successfully increased its memory limit to `8Gi`.
5.  **Current Status:** The `ollama` pod is now stable and running correctly. However, a new issue has surfaced where the frontend is unable to fetch initial data from the backend, resulting in an "HTTP error!" message.

**Current Blocker:** The final remaining issue is the communication breakdown between the frontend and backend pods. The frontend is unable to successfully make a `GET` request to `/api/cars`.

**Next Steps:** The immediate next step is to inspect the Nginx logs within the `frontend` pod to diagnose why the proxy is failing. This will be the first action upon resuming the session.