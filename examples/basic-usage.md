# Claude Alt - Basic Usage Examples

This document provides practical examples of using Claude Code Alternative in various scenarios.

## 🚀 Getting Started

### 1. Initial Setup

```bash
# Install globally
npm install -g claude-code-alternative

# Setup configuration
claude-alt setup
```

Follow the interactive prompts to configure your API keys and preferences.

### 2. Basic Analysis

Analyze a single JavaScript file:

```bash
claude-alt analyze -f src/components/Header.jsx
```

Example output:
```
📊 Code Analysis Results

Summary: React functional component with proper JSX structure and prop handling

💡 Suggestions:
1. [OPTIMIZATION] Consider memoizing the component with React.memo for better performance
2. [STYLE] Add PropTypes or TypeScript for better type safety
3. [ACCESSIBILITY] Add aria-labels to improve accessibility
```

### 3. Project-Wide Analysis

Analyze an entire project directory:

```bash
claude-alt analyze -d src/
```

This will analyze all supported files in the `src/` directory and provide a comprehensive report.

## 💬 Interactive AI Assistant

### Ask General Questions

```bash
claude-alt ask "What are the best practices for React component organization?"
```

### Ask Context-Specific Questions

```bash
claude-alt ask "How can I optimize this database query?" -c models/User.js
```

### Code Architecture Questions

```bash
claude-alt ask "What design patterns are used in this codebase?" -c src/patterns/
```

## 🔄 Git Integration

### Smart Git Operations

```bash
# Show current status with AI insights
claude-alt git --status

# Show diff with analysis
claude-alt git --diff

# Generate intelligent commit message
claude-alt git --commit

# Commit with AI message and push
claude-alt git --commit --push
```

### Example AI-Generated Commit Messages

Input changes:
- Added validation to user input form
- Fixed typo in error message
- Updated tests

AI-generated message:
```
feat(validation): add user input validation and fix error message typo

- Implement client-side validation for user registration form
- Correct spelling in authentication error message
- Update corresponding unit tests for validation logic
```

## 🐙 GitHub Integration

### Issue Comments

In GitHub issue comments, trigger Claude Alt with:

```markdown
@claude-alt analyze the codebase for potential performance bottlenecks
```

Response example:
```markdown
## 📊 Code Analysis Results

I've analyzed your codebase and found several potential performance bottlenecks:

### High Priority Issues
- **Database N+1 queries** in `UserController.js:42` - Consider using eager loading
- **Large bundle size** - Main bundle is 2.3MB, recommend code splitting

### Suggestions
- Implement React.lazy() for route-based code splitting
- Add database query optimization with proper indexing
- Consider using React.memo for expensive components

Would you like me to provide specific implementation details for any of these optimizations?
```

### Pull Request Reviews

In PR comments:

```markdown
@claude-alt review this pull request for security vulnerabilities
```

Response example:
```markdown
## 🔍 Security Review Results

### ✅ Security Assessment: GOOD

**Files Reviewed:** 5
**Vulnerabilities Found:** 1 Low Priority

### Issues Found:
- **Input Validation** (Low) - `api/auth.js:28` - Email input not sanitized before database query

### Recommendations:
1. Add input sanitization using a library like `validator.js`
2. Implement rate limiting for authentication endpoints
3. Consider adding CSRF protection for state-changing operations

### Code Quality:
- Proper error handling implemented ✅
- Secrets properly externalized ✅  
- Dependencies up to date ✅
```

## 📋 Advanced Configuration

### Custom Configuration File

Create `claude-alt.config.json`:

```json
{
  "aiProvider": {
    "name": "anthropic",
    "apiKey": "sk-ant-...",
    "endpoint": "https://api.anthropic.com"
  },
  "github": {
    "token": "ghp_...",
    "defaultBranch": "develop"
  },
  "features": {
    "codeAnalysis": true,
    "gitIntegration": true,
    "fileOperations": true
  },
  "analysis": {
    "maxFiles": 20,
    "excludePatterns": ["node_modules", ".git", "dist"],
    "includedExtensions": [".js", ".ts", ".jsx", ".tsx", ".py"]
  }
}
```

### Environment Variables

For CI/CD or multiple projects:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
export GITHUB_TOKEN="ghp_..."
export AI_PROVIDER="anthropic"
export DEFAULT_BRANCH="main"

claude-alt analyze -d .
```

## 🔧 Workflow Integration

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/sh
echo "Running Claude Alt analysis..."
claude-alt analyze -d src/ --format json > analysis.json

# Check for critical issues
if grep -q '"severity":"error"' analysis.json; then
    echo "❌ Critical issues found. Commit blocked."
    exit 1
fi

echo "✅ Code analysis passed."
exit 0
```

### CI/CD Pipeline

#### GitHub Actions

```yaml
name: Code Quality Check

on: [push, pull_request]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-node@v4
      with:
        node-version: '18'
    - run: npm install claude-code-alternative
    - name: Analyze Code
      run: npx claude-alt analyze -d src/ --format json
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

#### Jenkins Pipeline

```groovy
pipeline {
    agent any
    environment {
        ANTHROPIC_API_KEY = credentials('anthropic-api-key')
    }
    stages {
        stage('Code Analysis') {
            steps {
                sh 'npm install claude-code-alternative'
                sh 'npx claude-alt analyze -d src/ --format json > analysis.json'
                publishHTML([
                    allowMissing: false,
                    alwaysLinkToLastBuild: true,
                    keepAll: true,
                    reportDir: '.',
                    reportFiles: 'analysis.json',
                    reportName: 'Claude Alt Analysis Report'
                ])
            }
        }
    }
}
```

## 🎯 Use Case Examples

### 1. Legacy Code Assessment

```bash
# Analyze legacy codebase
claude-alt analyze -d legacy-app/

# Ask for modernization strategy
claude-alt ask "How should I modernize this jQuery-based application to React?" -c legacy-app/js/main.js
```

### 2. Security Audit

```bash
# Security-focused analysis
claude-alt ask "Analyze this codebase for security vulnerabilities" -c .

# Specific file security check
claude-alt ask "Are there any security issues in this authentication code?" -c auth/login.js
```

### 3. Performance Optimization

```bash
# Performance analysis
claude-alt analyze -d src/ | grep -i "performance\|optimization"

# Get specific optimization advice
claude-alt ask "How can I optimize the loading performance of this React app?" -c src/App.js
```

### 4. Code Review Automation

```bash
# Review changes before commit
git diff --name-only | xargs -I {} claude-alt analyze -f {}

# Review specific pull request files
gh pr view 123 --json files | jq -r '.files[].filename' | xargs -I {} claude-alt analyze -f {}
```

## 🏆 Best Practices

### 1. Regular Analysis
- Run analysis before major releases
- Integrate into your development workflow
- Use in code review process

### 2. Contextual Questions
- Always provide relevant context files
- Be specific in your questions
- Ask for actionable advice

### 3. Configuration Management
- Use project-specific configuration files
- Keep API keys secure
- Version control your claude-alt.config.json

### 4. Team Integration
- Share configuration across team members
- Establish consistent analysis practices
- Use GitHub integration for collaborative reviews

---

This covers the basic usage patterns of Claude Code Alternative. For more advanced features and customization options, refer to the main README.md file.