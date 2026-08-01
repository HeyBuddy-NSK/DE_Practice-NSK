# 🚀 Data Ingestion Pipeline: HTTP to Local Workspace

## 📌 Overview
This Exercise is a production-grade Data Ingestion Pipeline built in Python. It is designed to reliably download and extract large, zipped datasets from remote HTTP servers into a local workspace. 

Rather than a simple flat script, this pipeline is built with enterprise architecture in mind, focusing on strict error handling, idempotency, modularity, and efficient memory management.

---

## 🏗️ Project Architecture

The codebase strictly adheres to the **Single Responsibility Principle**, separating configuration, orchestration, and business logic into modular components:

*   **`app.py`**: The Orchestrator. Manages the high-level execution flow and loops through target URLs.
*   **`config.py`**: The Configuration Layer. Acts as the single source of truth for URIs, timeouts, and local path definitions.
*   **`data_ingestion.py`**: The Worker. Contains the robust, self-sufficient functions for downloading, validating, and extracting files.
*   **`utils.py`**: The Utilities Layer. Houses the custom enterprise logger setup.

---

## ✨ Key Features & Engineering Principles

### 1. 🛡️ Idempotent Execution
The pipeline intelligently checks the state of the local target directory before initiating any network requests. If a target `.csv` or `.zip` file already exists, it skips the redundant download and extraction phases. This guarantees zero wasted compute and bandwidth on pipeline restarts.

### 2. 🧠 Optimized Memory Management
To prevent Out-Of-Memory (OOM) crashes on multi-gigabyte files, all network requests utilize chunked streaming (`iter_content(chunk_size=8192)`). Data is streamed directly from the socket to the disk without ever being fully loaded into RAM.

### 3. 🚨 Resilient Error Handling
A batch pipeline should never crash due to a single bad record. This pipeline includes:
*   Pre-flight validation for HTTP/HTTPS URLs.
*   Strict timeout thresholds to prevent hanging connections.
*   Graceful recovery from HTTP `404 Not Found` or `BadZipFile` exceptions. Errors are logged with tracebacks, and the pipeline seamlessly continues to the next URL.

### 4. 📝 Hierarchical Logging
Implements a strict "Manager vs. Worker" logging strategy:
*   **INFO Level:** High-level milestones (start/end of jobs, file successes) for clean console output.
*   **DEBUG Level:** Repetitive I/O operations (directory creation, file filtering) are hidden by default but preserved for deep-dive troubleshooting.

---

## ⚙️ Setup & Usage

### Prerequisites
*   Python 3.10+
*   `requests` library

### Execution
1. Clone the repository and navigate to the project root.
2. Run the pipeline manager:
   ```bash
   python app.py
   ```
3. Check the `logs/` directory for a dated, detailed execution history.
4. Extracted `.csv` files will be safely stored in the `downloads/` directory.

---

## 🚀 Roadmap & Future Scope
- [ ] **Concurrency:** Implement `ThreadPoolExecutor` for asynchronous, parallel file downloading.
- [ ] **Containerization:** Wrap the application in a Docker container for cross-platform consistency.
- [ ] **Testing:** Add a `tests/` directory utilizing `pytest` and `tmp_path` fixtures to mock file I/O and network requests.
