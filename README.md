# Shelby

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Shelby is a safety-first, AI-powered natural language terminal assistant. It translates plain English requests into executable shell commands, providing detailed explanations and risk assessments before anything runs.

---

### Demo
![Shelby Demo](demo/demo-2.gif)

---

### Getting Started (Step-by-Step)

#### 1. Installation
The easiest way to install Shelby is via pip:

```bash
pip install shelby-ai
```

If you are a developer and want to install it from source:
```bash
git clone https://github.com/sk16er/shelby.git
cd shelby
pip install -e .
```

#### 2. Configuration
Before your first use, you need to configure an AI provider. Shelby supports OpenAI, Anthropic, Google Gemini, and local models via Ollama.

Run the setup wizard:
```bash
shelby --setup
```
Follow the prompts to select your provider and enter your API key. Keys are stored securely in your system's keyring.

#### 3. Your First Command
Try asking Shelby to do something simple:
```bash
shelby "list all files in the current directory"
```
Shelby will generate the command, explain it, and ask for your confirmation.

---

### Usage Modes

#### Inline Query
Run a single command directly:
```bash
shelby "recursively find all .log files and delete them"
```

#### Interactive REPL
Type `shelby` without arguments to enter a persistent session. The REPL remembers the output of previous commands, allowing for follow-up requests:
```bash
shelby > list the largest files here
...
shelby > now move the top 3 to /tmp
```

#### Pipe Mode
Shelby can process input from other commands:
```bash
echo "list docker containers" | shelby
```

---

### Safety System
Shelby classifies every command into one of three risk tiers to prevent accidental damage:

| Tier | Behavior | Examples |
| :--- | :--- | :--- |
| **SAFE** | Press Enter to execute | `ls`, `grep`, `cat`, `git status` |
| **CAUTION** | Type `y` to confirm | `cp`, `mv`, `chmod`, `pip install` |
| **DANGER** | Retype the command name to confirm | `rm -rf`, `dd`, `DROP TABLE` |

**Safety Flags:**
- `--dry-run`: Display the command and explanation without executing it.
- `--safe`: Block all **DANGER** tier commands entirely.
- `--yes`: Skip all confirmation prompts (use with caution).

---

### Advanced Features
![Shelby Demo](demo/demo.gif)

- **Explain**: Break down any existing command without running it.
  ```bash
  shelby explain "tar -xzvf archive.tar.gz"
  ```
- **Fix**: Analyze a failed command and suggest a correction.
  ```bash
  shelby fix
  ```
- **History**: Perform semantic search over your past Shelby commands.
  ```bash
  shelby history "how did I list those docker images?"
  ```
  

---

### License
MIT License. See [LICENSE](LICENSE) for details.
