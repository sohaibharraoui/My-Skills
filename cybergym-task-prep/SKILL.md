---
name: cybergym-task-prep
description: Prepare and download CyberGym tasks from the manifest for AutoExploit scan investigations. Trigger whenever a CyberGym task ID (e.g., 24633, arvo:24633, arvo-18356) is provided to download and extract the archive, then stop.
---

# CyberGym Task Preparation Skill

Use this skill whenever given a CyberGym task ID to download the task archive from Hugging Face and extract it, then stop.

## Paths and Context

- **Manifest & Dataset Info**: `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/manifest.csv`
- **Task Destination**: `/home/sohaib-harraoui/Desktop/workspace/agent_auto_exploit/CyberGym/tasks/arvo-<TASK_ID>`
- **Hugging Face Base URL**: `https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>`

---

## Workflow Steps

### 1. Parse and Look Up Task ID
- Normalize the task ID by stripping any `arvo:` or `arvo-` prefix (e.g., `arvo:24633` -> `24633`).
- Retrieve metadata from `/home/sohaib-harraoui/Desktop/workspace/Research/CyberGym/manifest.csv`:
  - `project_name`
  - `project_language`
  - `vulnerability_description`
  - `cwe_id` / `cwe_name`

### 2. Download Task Assets
Create directory `$TASK_DIR` at `/home/sohaib-harraoui/Desktop/workspace/agent_auto_exploit/CyberGym/tasks/arvo-<TASK_ID>`:
- Download `repo-vul.tar.gz`:
  ```bash
  curl -fL --retry 3 -o "$TASK_DIR/repo-vul.tar.gz" "https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>/repo-vul.tar.gz"
  ```
- Download `description.txt`:
  ```bash
  curl -fL --retry 3 -o "$TASK_DIR/description.txt" "https://huggingface.co/datasets/sunblaze-ucb/cybergym/resolve/main/data/arvo/<TASK_ID>/description.txt"
  ```

### 3. Extract Archive and Stop
- Extract `repo-vul.tar.gz` into `$TASK_DIR/repo-vul`:
  ```bash
  mkdir -p "$TASK_DIR/repo-vul"
  tar -xzf "$TASK_DIR/repo-vul.tar.gz" -C "$TASK_DIR/repo-vul"
  ```
- Do not create `agent_group.<TASK_ID>.yaml`. Stop at extraction.
- Output a concise summary of the downloaded task and extracted source files.
