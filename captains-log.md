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
