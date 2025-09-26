# Claude Code Project Configuration - Evaluace Filler

## I. Foundational Philosophy
- **KISS**: Keep all solutions simple and clear
- **DRY**: No code duplication - use reusable functions/modules
- **YAGNI**: Implement only current requirements, no speculative features
- **Record & Playback**: Separate recording of user actions from their automated playback

## II. Mandatory Procedures
- **Development Checklist**: Required for EVERY non-trivial task
- **English-Only Code**: ALL code artifacts in English (variables, functions, comments, etc.)
- **Exception**: GUI texts will be in Czech for end users
- **Virtual Environment**: ALWAYS use Python venv for this project

## III. Quality Standards
- Self-review for readability, bugs, and security
- Sufficient logging for debugging and monitoring
- Clear documentation and testing instructions
- Robust error handling with fallback strategies

## Development Checklist Template
Before implementing any feature, create a checklist:
```markdown
## Task: [Feature Name]
### Requirements/Features
- [ ] Requirement 1
- [ ] Requirement 2

### Key Design Decisions
- Decision 1: [Rationale]
- Decision 2: [Rationale]

### Applicable Principles
- [ ] KISS applied - Is this the simplest solution that works?
- [ ] DRY verified - Any code duplication to extract?
- [ ] YAGNI checked - Am I building only what's needed now?
- [ ] Real-world focused - Does this solve the actual problem?

### Implementation Steps
- [ ] Step 1
- [ ] Step 2

### Testing Steps
- [ ] Unit tests
- [ ] Integration tests
- [ ] Error cases

### Claude Code Integration
- [ ] Relevant files @-tagged in context
- [ ] Used /clear before starting new functionality
- [ ] Appropriate thinking level chosen (think/think harder)
```

## Claude Code Best Practices (MANDATORY)

### Context Management
- **Use /clear frequently**: Start each new feature/task with clean context
- **@-tag relevant files**: Include only necessary files in context
- **Think strategically**: Use appropriate thinking levels:
  - `think` - standard complexity
  - `think hard` - complex logic/architecture decisions  
  - `think harder` - very complex system design
  - `ultrathink` - maximum reasoning for critical decisions

### Project Navigation
- **Ask before coding**: Always understand the codebase first
- **Explore → Plan → Implement**: Don't jump straight to coding
- **Reference quotes**: Ask Claude to quote relevant code sections before changes


## Environment Setup (Windows 11 WSL2 Ubuntu)

### Prerequisites
```bash
# WSL2 Ubuntu with zsh shell
# Python 3.10+ with pip and venv
# Git configured with max.parez@seznam.cz

# Project structure
evaluace_filler/
├── .env                    # URLs dotazníků, konfigurace
├── .env.example           # Template for environment variables
├── .claude/               # Claude Code configuration
│   └── commands/          # Custom slash commands
├── CLAUDE.md              # This file - project context
├── requirements.txt       # Python dependencies (selenium, etc.)
├── src/
│   ├── recorder.py        # "Čmuchací" skript (Record fáze)
│   ├── player.py          # Hlavní vykonávač (Playback)
│   ├── session_manager.py # Persistent Browser↔Python connection
│   └── utils/            # Utility functions
│       ├── page_identifier.py
│       ├── navigation_manager.py
│       └── connection_recovery.py
├── scenarios/
│   ├── scenarios.json     # Hlavní databáze akcí
│   ├── recorded_sessions/ # Jednotlivé nahrané sessions
│   └── backup/           # Zálohy před úpravami
├── config/
│   ├── logging_config.py
│   └── session_config.json
├── logs/                 # Application logs
├── docs/                 # Dokumentace (včetně zadani.md)
└── tests/               # Unit a integration testy
```

### MCP Integration (.mcp.json)
```json
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/project"],
      "env": {}
    },
    "brave-search": {
      "command": "npx", 
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "${BRAVE_API_KEY}"
      }
    }
  }
}
```

### Environment Variables (.env)


## Technical Stack

- **Language**: Python 3.10+
- **Environment**: Windows 11 WSL2 Ubuntu with zsh
- **Package Management**: pip with venv
- **Core Libraries**:
  - **selenium**: Web browser automation
  - **webdriver-manager**: Automatic ChromeDriver management
  - **beautifulsoup4**: HTML parsing (auxiliary)
  - **requests**: HTTP requests (auxiliary)
  - **loguru**: Enhanced logging
- **Architecture**: Record & Playback Pattern
- **Data Format**: JSON for scenarios storage
- **Browser**: Chrome/Chromium (headless and GUI modes)


## Code Standards (MANDATORY)
- **ALL code in English**: variables, functions, classes, comments
- **File size**: Maximum 300 lines (KISS principle)
- **Style**: PEP 8 compliant
- **Reusability**: Extract common logic to utils/ (DRY principle)
- **Simplicity**: Choose simple solutions over clever ones

## Documentation Management (MANDATORY)

### **Required Documentation Files**
1. **CLAUDE.md** - Long-term project rules and configuration (this file)
2. **@NEXT_STEPS.md** - Overall project status and phase tracking (MANDATORY)
3. **PROGRESS.md** - Detailed chronological activity log (NEW - MANDATORY)

### **Documentation Update Rules**
- **@NEXT_STEPS.md**: Update after completing each major phase or milestone
- **PROGRESS.md**: Update for every significant task, problem solved, or decision made
- **CLAUDE.md**: Update when adding new tools, changing workflows, or project structure

### **PROGRESS.md Structure**
```markdown
## 📅 **[DATE] - [TASK DESCRIPTION]**

### Úkol: [Details]
**Čas začátku**: [HH:MM]
**Čas konce**: [HH:MM]
**Celková doba**: [minutes]
**Status**: [✅ COMPLETED / ⏳ IN PROGRESS / ❌ CANCELLED]

### Klíčová rozhodnutí
1. [Decision + rationale]

### Implementované komponenty
- [Component 1]: [description]

### Problémy a řešení
#### ❌ Problem 1: [Description]
**Chyba**: [Exact error]
**Řešení**: [Solution]
**Čas**: [minutes]

### Poučení
- [Lesson learned]
```

### **When to Update Documentation**
**PROGRESS.md** (Update frequently):
- Before starting new tasks (create entry with start time)
- When making significant technical decisions
- When encountering and solving problems
- After completing tasks (add end time, results, lessons)

**@NEXT_STEPS.md** (Update at milestones):
- After completing project phases
- When adding new data sources or major features
- When changing project scope or priorities
- Before major deployments or releases

## Git Workflow
### Mandatory Git Practices
- **Commit frequently**: Every 1 hour or after completing a feature
- **Use tags**: [feat-XXX], [fix-XXX], [refactor-XXX], [test-XXX], [docs-XXX]
- **Push to GitHub**: Minimum 2x per day, always before breaks
- **Always do commit & push**: Never leave uncommitted work

### Commit Message Format
```
[tag-XXX] brief description (max 50 chars)

Detailed explanation if needed (wrap at 72 chars)
```

Examples:
- `[feat-001] add contact regex parser`
- `[fix-023] handle missing website URLs`
- `[refactor-015] extract common HTTP logic`

### Branch Strategy
```
main (stable)
  └── develop (integration)
       ├── feature/contact-parser
       ├── fix/timeout-handling
       └── refactor/utils-module
```

### Git Configuration
```bash
# Configure Git for max.parez@seznam.cz
git config --global user.name "Max Parez"
git config --global user.email "max.parez@seznam.cz"

# SSH setup for GitHub
# Add to ~/.ssh/config:
Host github.com-maxparez
  HostName github.com
  User git
  IdentityFile /root/.ssh/id_25519_maxparez

# Clone with:
git clone git@github.com-maxparez:username/evaluace_filler.git
```

## Project-Specific Mandates (Evaluace Filler)

### Architecture Rules (CRITICAL)
1. **Record & Playback Pattern** - Clear separation between recording actions and playing them back
2. **Selenium as Primary Tool** - For handling CSRF tokens and dynamic content
3. **JavaScript Injection** - For fast form manipulation and event capture
4. **JSON for Scenarios** - Human-readable, version-controllable action database
5. **Persistent Connection** - Maintain Browser↔Python communication across page navigation
6. **Progressive Enhancement** - Start simple, add complexity only when needed

### Key Technical Constraints
- **Page Identification**: Use `.question-text .ls-label-question` selector consistently
- **Navigation**: Use `#ls-button-submit` (next) and `#ls-button-previous` (back) selectors
- **Error Recovery**: Always provide fallback strategies and interactive mode
- **Connection Recovery**: Handle browser navigation and connection loss gracefully


## Core Components (Record & Playback Architecture)

### 1. Record Phase Components
- **recorder.py**: Main recording script with JavaScript injection
- **PageIdentifier**: Consistent page identification using `.question-text .ls-label-question`
- **NavigationManager**: Handle forward/back navigation with button detection
- **ConnectionRecovery**: Maintain persistent Browser↔Python communication

### 2. Playback Phase Components
- **player.py**: Smart scenario execution engine
- **ScenarioMatcher**: Match current page to recorded scenarios (exact + fuzzy matching)
- **ActionExecutor**: Execute recorded actions with fallback strategies
- **InteractiveMode**: User intervention for unknown pages

### 3. Data & Configuration
- **scenarios.json**: Main action database (version controlled)
- **session_config.json**: Recording session configurations
- **logging_config.py**: Structured logging for debugging

### 4. Development Workflow
```bash
# 1. Recording new scenarios
python src/recorder.py --url "https://dotaznik.cz" --persistent

# 2. Playing back scenarios
python src/player.py --scenarios scenarios/main.json --urls config/targets.txt

# 3. Testing navigation
python src/test_navigation.py --test-back-forward
```

## Reporting Structure
When providing updates:
1. Reference checklist progress
2. Explain design decisions
3. Flag any deviations from principles
4. Include running/testing instructions

## Remember

### Decision Framework
- If unclear about requirements → ASK
- If tempted to add "nice to have" → DON'T (YAGNI)
- If copying code → REFACTOR (DRY)
- If solution seems complex → SIMPLIFY (KISS)
- If considering new library → Can we use existing ones?
- All code artifacts → IN ENGLISH

### Project-Specific Rules
- **Log everything**: Every request, every error, every decision
- **Test manually first**: Validate approach before automation

### When to Ask for Help
- Unclear about website structure patterns
- Considering architectural changes
- Data quality issues

### Red Flags
- Adding machine learning for simple page matching
- Complex async/await patterns before basic recording works
- Database storage before validating JSON scenarios approach
- Parallel browser instances before single-browser stability
- Complex configuration systems for simple settings
- Custom JavaScript frameworks instead of simple injection

### Development Environment Setup
- [ ] Initialize git repo with proper .gitignore
- [ ] Set up virtual environment with Python 3.10+



### Initial Development Checklist
- [ ] Create basic project structure (src/, scenarios/, config/, logs/, tests/)
- [ ] Set up Python virtual environment with requirements.txt
- [ ] Implement core utilities: PageIdentifier, NavigationManager
- [ ] Create Enhanced Recorder with JavaScript injection
- [ ] Implement Smart Player with scenario matching
- [ ] Create scenarios.json template and structure
- [ ] Add comprehensive logging with loguru
- [ ] Write unit tests for core components

### Development Commands
```bash
# Setup virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run recorder
python src/recorder.py --url "URL_DOTAZNIKU" --output scenarios/session.json

# Run player
python src/player.py --scenarios scenarios/main.json --url "URL_DOTAZNIKU"

# Run tests
python -m pytest tests/ -v

# Lint and format
python -m black src/ tests/
python -m flake8 src/ tests/
```

---
