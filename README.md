# 🤖 Refactoring Swarm - Multi-Agent Code Refactoring System

## 📝 Description

A multi-agent system that leverages swarm intelligence and Large Language Models (LLMs) to automatically analyze, refactor, and improve Python code. The system uses specialized AI agents that collaborate to audit code quality, propose fixes, generate tests, and enhance documentation.

## 🎯 Objectives

- **Autonomous Code Analysis**: Automatically detect code smells, bugs, and improvement opportunities
- **Multi-Agent Collaboration**: Specialized agents working together to refactor code
- **Experimental Tracking**: Log all interactions for scientific analysis
- **Quality Improvement**: Enhance code maintainability, readability, and performance

## 🏗️ Architecture

### Agent Roles (4 Required)

1. **Auditor Agent** 🔍
   - Analyzes code quality and complexity
   - Detects code smells and anti-patterns
   - Identifies potential bugs and security issues

2. **Fixer Agent** 🔧
   - Proposes and applies code refactoring
   - Implements fixes for detected issues
   - Ensures code follows best practices

3. **Tester Agent** ✅
   - Generates unit tests
   - Validates refactoring changes
   - Ensures code correctness

4. **Documenter Agent** 📚
   - Improves code documentation
   - Generates docstrings
   - Creates usage examples

### System Components

```
src/
├── agents/          # Specialized AI agents
├── llm/             # LLM API integration (Google Gemini)
├── analysis/        # Code parsing and metrics
├── swarm/           # Agent coordination and communication
├── refactoring/     # Refactoring operations
└── utils/           # Logging and utilities
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.10 or 3.11
- Google Gemini API Key
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd refactoring-swarm-template
```

2. **Create virtual environment**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure API Key**
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Google Gemini API key
# GOOGLE_API_KEY=your_actual_api_key_here
```

5. **Verify setup**
```bash
python check_setup.py
```

## 💻 Usage

### Basic Usage

```bash
python main.py --target_dir <path_to_code_to_refactor>
```

### Example

```bash
python main.py --target_dir ./sample_project
```

## 📊 Experimental Logging

All agent interactions are logged in `logs/experiment_data.json` for analysis:

- **Agent name**: Which agent performed the action
- **Model used**: LLM model identifier
- **Action type**: ANALYSIS, GENERATION, DEBUG, or FIX
- **Prompts and responses**: Full interaction data
- **Status**: SUCCESS or FAILURE
- **Timestamp**: When the action occurred

## 🌿 Git Workflow & Branch Naming Convention

### Branch Naming

Each collaborator must create their branch following this convention:

```
<CollaboratorName>/<Role>
```

**Examples:**
- `Alice/Auditor` - Alice working on the Auditor agent
- `Bob/Fixer` - Bob working on the Fixer agent
- `Charlie/Tester` - Charlie working on the Tester agent
- `Diana/Documenter` - Diana working on the Documenter agent

### Workflow

1. **Create your feature branch**
```bash
git checkout -b YourName/YourRole
```

2. **Work on your changes**
```bash
git add .
git commit -m "feat: implement YourRole agent"
```

3. **Push to remote**
```bash
git push -u origin YourName/YourRole
```

4. **Create a Pull Request** to merge into `main`

### Commit Message Convention

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `test:` - Test additions or modifications
- `refactor:` - Code refactoring
- `style:` - Formatting changes

## 📁 Project Structure

```
refactoring-swarm-template/
├── .env                    # Environment variables (API keys)
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
├── check_setup.py          # Setup verification script
├── main.py                 # Main entry point
├── README.md               # This file
├── docs/
│   └── interfaces.md       # Agent interfaces documentation
├── src/
│   ├── agents/             # AI agent implementations
│   ├── llm/                # LLM client wrappers
│   ├── analysis/           # Code analysis tools
│   ├── swarm/              # Swarm coordination
│   ├── refactoring/        # Refactoring operations
│   └── utils/
│       └── logger.py       # Experimental logging
├── logs/
│   └── experiment_data.json # Logged interactions
└── tests/                  # Unit tests
```

## 🔧 Technologies Used

- **Python 3.10+**: Core programming language
- **Google Gemini API**: Large Language Model backend
- **LangChain**: Agent orchestration framework
- **AST (Abstract Syntax Tree)**: Python code parsing
- **JSON**: Data logging and configuration

## 📈 Evaluation Criteria

- ✅ **4 specialized agents** with distinct roles
- ✅ **Autonomous decision-making** by agents
- ✅ **Inter-agent communication** and collaboration
- ✅ **Complete logging** of all interactions
- ✅ **Demonstrated code quality** improvements

## 🤝 Contributing

1. Create your feature branch following the naming convention
2. Implement your assigned agent role
3. Write tests for your implementation
4. Ensure all tests pass
5. Submit a Pull Request with clear description

## 📝 License

This project is part of an academic assignment (TP IGL 2025-2026).

## 👥 Team

- **Collaborator 1**: [Name] - Role: Auditor
- **Collaborator 2**: [Name] - Role: Fixer
- **Collaborator 3**: [Name] - Role: Tester
- **Collaborator 4**: [Name] - Role: Documenter

---

**Note**: Make sure to review `docs/interfaces.md` for detailed agent interface specifications.
