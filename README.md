# Claude Code Alternative

A professional-grade, open-source alternative to Claude Code that provides AI-powered development assistance through both command-line interface and GitHub Actions integration.

## 🚀 Features

- **Multi-Platform Support**: Works locally via CLI and in GitHub Actions
- **AI-Powered Analysis**: Intelligent code analysis and suggestions
- **Git Integration**: Seamless Git operations with AI assistance
- **GitHub Integration**: Automated PR reviews and issue responses
- **File Operations**: Comprehensive file system operations
- **Extensible Architecture**: Modular design supporting multiple AI providers
- **Security-First**: Robust authentication and permission management

## 📦 Installation

### Local Installation

```bash
npm install -g claude-code-alternative
```

### GitHub Actions Setup

1. Add this workflow to `.github/workflows/claude-alt.yml`:

```yaml
name: Claude Alt - AI Development Assistant

on:
  issue_comment:
    types: [created]
  pull_request_review:
    types: [submitted]
  issues:
    types: [opened, assigned]

permissions:
  contents: write
  issues: write
  pull-requests: write

jobs:
  claude-alt:
    runs-on: ubuntu-latest
    if: contains(github.event.comment.body, '@claude-alt') || contains(github.event.issue.body, '@claude-alt')
    
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - run: npm install claude-code-alternative
    - run: npx claude-alt-action
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

2. Add required secrets to your repository:
   - `ANTHROPIC_API_KEY`: Your Anthropic API key
   - `GITHUB_TOKEN`: Automatically provided by GitHub

## 🛠️ Usage

### Command Line Interface

#### Initial Setup
```bash
claude-alt setup
```

#### Analyze Code
```bash
# Analyze a specific file
claude-alt analyze -f src/index.js

# Analyze entire directory
claude-alt analyze -d src/

# Output as JSON
claude-alt analyze -f app.py --format json
```

#### Ask Questions
```bash
# General questions
claude-alt ask "How can I optimize this React component?"

# Questions with context
claude-alt ask "What design patterns are used here?" -c src/patterns.js
```

#### Git Operations
```bash
# Show status
claude-alt git --status

# Show diff
claude-alt git --diff

# AI-generated commit message
claude-alt git --commit

# Commit with custom message
claude-alt git --commit "feat: add new feature" --push
```

### GitHub Integration

Trigger Claude Alt in GitHub by mentioning `@claude-alt` in:

- **Issue Comments**: `@claude-alt analyze the codebase`
- **PR Reviews**: `@claude-alt review this pull request`  
- **Issue Creation**: Create issues with `@claude-alt` to get immediate assistance

#### Example Triggers

```markdown
@claude-alt analyze the codebase for potential security issues

@claude-alt review this pull request and suggest improvements

@claude-alt explain the architecture of this project

@claude-alt help me understand this error in the logs
```

## 📁 Project Structure

```
claude-code-alternative/
├── src/
│   ├── core/                 # Core functionality
│   │   ├── config.ts         # Configuration management
│   │   ├── file-operations.ts # File system operations
│   │   ├── git-operations.ts  # Git integration
│   │   └── github-integration.ts # GitHub API integration
│   ├── providers/            # AI provider implementations
│   │   └── anthropic.ts      # Anthropic Claude integration
│   ├── types/                # TypeScript type definitions
│   │   └── index.ts          # Core types
│   ├── cli.ts                # CLI application
│   └── github-action.ts      # GitHub Actions runner
├── tasks/                    # Project management
│   ├── todo.md               # Task tracking
│   └── lessons.md            # Lessons learned
├── tests/                    # Test files
├── dist/                     # Compiled JavaScript
├── package.json
├── tsconfig.json
└── README.md
```

## 🔧 Configuration

### Local Configuration File

Create `claude-alt.config.json` in your project root:

```json
{
  "aiProvider": {
    "name": "anthropic",
    "apiKey": "your-api-key-here"
  },
  "github": {
    "token": "your-github-token",
    "defaultBranch": "main"
  },
  "features": {
    "codeAnalysis": true,
    "gitIntegration": true,
    "fileOperations": true
  }
}
```

### Environment Variables

```bash
# AI Provider
ANTHROPIC_API_KEY=your-anthropic-api-key
AI_PROVIDER=anthropic

# GitHub Integration
GITHUB_TOKEN=your-github-token
DEFAULT_BRANCH=main

# Optional
AI_ENDPOINT=custom-endpoint-url
```

## 🏗️ Architecture

### Core Components

1. **Configuration Manager**: Handles environment and file-based configuration
2. **AI Provider Layer**: Abstracts different AI services (Anthropic, OpenAI, etc.)
3. **File Operations Manager**: Safe file system operations with proper error handling
4. **Git Operations Manager**: Git integration using simple-git
5. **GitHub Integration Manager**: GitHub API operations using Octokit

### Design Principles

- **Modular Architecture**: Each component is independently testable and replaceable
- **Security-First**: API keys and tokens are handled securely
- **Error Resilience**: Comprehensive error handling and graceful degradation
- **Performance**: Optimized for both local and CI/CD environments
- **Extensibility**: Easy to add new AI providers and integrations

## 🧪 Testing

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# Type checking
npm run typecheck

# Linting
npm run lint
```

## 🚀 Development

### Local Development Setup

1. Clone the repository:
```bash
git clone https://github.com/your-username/claude-code-alternative.git
cd claude-code-alternative
```

2. Install dependencies:
```bash
npm install
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Build the project:
```bash
npm run build
```

5. Test locally:
```bash
npm run dev -- analyze -f README.md
```

### Building and Publishing

```bash
# Build for production
npm run build

# Run tests
npm test

# Publish to npm
npm publish
```

## 📊 Supported File Types

Claude Alt provides enhanced analysis for:

- **JavaScript/TypeScript** (`.js`, `.ts`, `.jsx`, `.tsx`)
- **Python** (`.py`)
- **Java** (`.java`)
- **C/C++** (`.c`, `.cpp`, `.cc`, `.cxx`)
- **Go** (`.go`)
- **Rust** (`.rs`)
- **PHP** (`.php`)
- **Ruby** (`.rb`)
- **And more...**

## 🔒 Security

### API Key Management
- API keys are never logged or exposed
- Supports both environment variables and secure config files
- GitHub secrets integration for Actions

### Permissions
- Minimal required permissions for GitHub integration
- Scoped access tokens
- Safe file operations with path validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Add tests for new functionality
5. Run the test suite: `npm test`
6. Commit your changes: `git commit -m 'feat: add amazing feature'`
7. Push to the branch: `git push origin feature/amazing-feature`
8. Open a Pull Request

### Development Guidelines

- Follow the AI Engineering Policy outlined in the project
- Write tests for all new functionality
- Use conventional commit messages
- Update documentation for new features
- Ensure TypeScript types are properly defined

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by Claude Code's excellent development workflow integration
- Built with TypeScript for reliability and maintainability
- Uses industry-standard libraries for core functionality

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/claude-code-alternative/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/claude-code-alternative/discussions)
- **Documentation**: [Wiki](https://github.com/your-username/claude-code-alternative/wiki)

---

**Note**: This is an open-source alternative to Claude Code. It is not affiliated with or endorsed by Anthropic.