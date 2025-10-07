# Specification for Custom-Coded AI Car Finder Agent

This document outlines the components and steps required to build a custom AI agent for finding used cars across multiple websites.

---

## 1. Web Scraping Engine

This component is responsible for visiting websites and gathering raw listing data.

* **Technology:** Use Python.
* **For Static Sites:** Employ libraries like `requests` and `BeautifulSoup` to fetch and parse simple HTML.
* **For Dynamic/JS-Heavy Sites:** Use a browser automation library like `Selenium` or `Playwright`. This will control a real browser (e.g., Chrome) to mimic human interaction, handle infinite scroll, and click on elements to reveal data.

---

## 2. Data Standardization and Storage

Data from different sources must be cleaned and stored in a uniform structure.

* **Schema:** Define a standard data structure for each car listing. Key fields should include:
    * `make`
    * `model`
    * `year`
    * `price`
    * `mileage`
    * `vin`
    * `location`
    * `url` (link to the original listing)
    * `source_site` (e.g., cars.com)
    * `scraped_timestamp`
* **Storage:** Use a simple SQLite database to store the listings. This allows for easy querying and helps in tracking which listings have already been seen and processed.

---

## 3. AI-Powered Analysis

This is the core "agent" logic that enriches the raw data.

*   **LLM Integration Strategy:** The agent will support two modes of operation for comparison.
    *   **Option A: Managed LLM API:** Integrate with a commercial Large Language Model API (e.g., Gemini API) for high-quality analysis with minimal setup.
    *   **Option B: Self-Hosted Open Model:** Implement support for a self-hosted open-source model (e.g., Llama 3, Mistral). This provides more control and potentially lower costs. The model can be served using a framework like Ollama or a dedicated inference server.
*   **Key Functions:**
    *   **Summarize Descriptions:** Generate a concise, bullet-point summary of the seller's description, highlighting key features and potential issues.
    *   **Extract Unstructured Data:** Programmatically ask questions about the description text, such as "Does the description mention a clean title?" or "Are service records mentioned?".
    *   **Create a Relevance Score:** Based on a predefined set of user preferences (e.g., "low mileage is critical," "must have sunroof"), have the LLM score each listing on a scale of 1-10 for its suitability.

---

## 4. Containerization and Orchestration

The process will be containerized and deployed to a Kubernetes cluster to ensure scalability and reliable, automated execution.

*   **Containerization:**
    *   A `Dockerfile` will be created to package the Python application, its dependencies, and the scraping drivers into a portable container image.
    *   The image will be stored in a container registry (e.g., Google Artifact Registry).
*   **Orchestration:**
    *   **Platform:** The application will be deployed to a Google Kubernetes Engine (GKE) cluster.
    *   **Scheduling:** A Kubernetes `CronJob` resource will be defined in a YAML manifest. This will replace traditional cron jobs and trigger the scraping and analysis process on a defined schedule (e.g., daily at 7 AM).
*   **Digest Format:**
    *   Generate a daily email digest.
    *   Use a templating engine (like Jinja2) to create a clean HTML email containing the top-ranked cars found that day.
    *   Each entry in the digest should include the car's key details, the AI-generated summary, the relevance score, and a direct link to the listing.
