import { ConfigManager } from './core/config.js';
import { FileOperationsManager } from './core/file-operations.js';
import { GitOperationsManager } from './core/git-operations.js';
import { GitHubIntegrationManager } from './core/github-integration.js';
import { AnthropicProvider } from './providers/anthropic.js';
import { CommandContext, GitHubContext, TaskResult } from './types/index.js';

interface GitHubActionContext {
  eventName: string;
  payload: any;
  repo: {
    owner: string;
    repo: string;
  };
  actor: string;
}

class GitHubActionRunner {
  private configManager: ConfigManager;
  private aiProvider: AnthropicProvider;
  private context: CommandContext;
  private githubContext: GitHubContext;
  private fileOps: FileOperationsManager;
  private gitOps: GitOperationsManager;
  private githubOps: GitHubIntegrationManager;

  constructor() {
    this.configManager = new ConfigManager();
    this.initializeContext();
  }

  private initializeContext(): void {
    const config = this.configManager.getConfig();
    
    this.context = {
      workingDirectory: process.env.GITHUB_WORKSPACE || process.cwd(),
      environment: 'github-actions',
      verbose: true,
    };

    this.githubContext = {
      owner: process.env.GITHUB_REPOSITORY?.split('/')[0] || '',
      repo: process.env.GITHUB_REPOSITORY?.split('/')[1] || '',
      eventType: process.env.GITHUB_EVENT_NAME || '',
      triggerUser: process.env.GITHUB_ACTOR || '',
      token: config.github?.token || process.env.GITHUB_TOKEN || '',
      issueNumber: this.getIssueNumber(),
      prNumber: this.getPRNumber(),
    };

    this.aiProvider = new AnthropicProvider(config.aiProvider.apiKey);
    this.fileOps = new FileOperationsManager(this.context);
    this.gitOps = new GitOperationsManager(this.context);
    this.githubOps = new GitHubIntegrationManager(this.githubContext);
  }

  private getIssueNumber(): number | undefined {
    try {
      const payload = JSON.parse(process.env.GITHUB_EVENT_PATH ? 
        require('fs').readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8') : '{}');
      
      return payload.issue?.number || payload.pull_request?.number;
    } catch {
      return undefined;
    }
  }

  private getPRNumber(): number | undefined {
    try {
      const payload = JSON.parse(process.env.GITHUB_EVENT_PATH ? 
        require('fs').readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8') : '{}');
      
      return payload.pull_request?.number;
    } catch {
      return undefined;
    }
  }

  private getEventPayload(): any {
    try {
      if (process.env.GITHUB_EVENT_PATH) {
        return JSON.parse(require('fs').readFileSync(process.env.GITHUB_EVENT_PATH, 'utf8'));
      }
    } catch {
      // Fallback to empty payload
    }
    return {};
  }

  private extractTriggerPhrase(text: string): string | null {
    const triggerPattern = /@claude(?:-alt)?\s+(.*)/i;
    const match = text.match(triggerPattern);
    return match ? match[1].trim() : null;
  }

  private async handleIssueComment(payload: any): Promise<TaskResult> {
    const comment = payload.comment;
    const triggerPhrase = this.extractTriggerPhrase(comment.body);
    
    if (!triggerPhrase) {
      return {
        success: false,
        message: 'No trigger phrase found',
      };
    }

    console.log(`Processing request: "${triggerPhrase}"`);
    
    try {
      if (triggerPhrase.toLowerCase().includes('analyze')) {
        return await this.handleAnalysisRequest(triggerPhrase);
      } else if (triggerPhrase.toLowerCase().includes('review')) {
        return await this.handleReviewRequest();
      } else {
        return await this.handleGeneralRequest(triggerPhrase);
      }
    } catch (error) {
      return {
        success: false,
        message: `Error processing request: ${error}`,
      };
    }
  }

  private async handleAnalysisRequest(request: string): Promise<TaskResult> {
    const files = await this.fileOps.findFiles('\\.(js|ts|py|java|cpp|c|go|rs)$');
    const results = [];
    
    for (const file of files.slice(0, 5)) { // Limit for performance
      try {
        const content = await this.fileOps.readFile(file);
        const analysis = await this.aiProvider.analyzeCode(content, file);
        results.push({ file, analysis });
      } catch (error) {
        console.warn(`Could not analyze ${file}: ${error}`);
      }
    }

    const summary = `## 📊 Code Analysis Results

Analyzed ${results.length} files:

${results.map(({ file, analysis }) => `
### ${file}
${analysis.summary}

${analysis.issues.length > 0 ? `**Issues (${analysis.issues.length}):**
${analysis.issues.map(issue => `- [${issue.severity}] ${issue.message}`).join('\\n')}` : ''}

${analysis.suggestions.length > 0 ? `**Suggestions (${analysis.suggestions.length}):**
${analysis.suggestions.map(suggestion => `- [${suggestion.type}] ${suggestion.message}`).join('\\n')}` : ''}
`).join('\\n')}

Generated with Claude Code Alternative`;

    await this.githubOps.createComment(summary);

    return {
      success: true,
      message: 'Analysis complete',
      details: results,
    };
  }

  private async handleReviewRequest(): Promise<TaskResult> {
    if (!this.githubContext.prNumber) {
      throw new Error('Review request requires a pull request context');
    }

    const files = await this.githubOps.listPullRequestFiles(this.githubContext.prNumber);
    const reviews = [];

    for (const file of files.slice(0, 10)) { // Limit for performance
      if (file.status === 'added' || file.status === 'modified') {
        try {
          const content = await this.githubOps.getFileContents(file.filename);
          const analysis = await this.aiProvider.analyzeCode(content, file.filename);
          reviews.push({ file: file.filename, analysis });
        } catch (error) {
          console.warn(`Could not review ${file.filename}: ${error}`);
        }
      }
    }

    const reviewSummary = `## 🔍 Code Review

Reviewed ${reviews.length} files:

${reviews.map(({ file, analysis }) => `
### ${file}
${analysis.summary}

${analysis.issues.length > 0 ? `**Issues Found:**
${analysis.issues.map(issue => `- 🚨 [${issue.severity}] ${issue.message}${issue.line ? ` (line ${issue.line})` : ''}`).join('\\n')}` : '✅ No issues found'}

${analysis.suggestions.length > 0 ? `**Suggestions:**
${analysis.suggestions.map(suggestion => `- 💡 [${suggestion.type}] ${suggestion.message}${suggestion.line ? ` (line ${suggestion.line})` : ''}`).join('\\n')}` : ''}
`).join('\\n')}

Generated with Claude Code Alternative`;

    await this.githubOps.createComment(reviewSummary);

    return {
      success: true,
      message: 'Review complete',
      details: reviews,
    };
  }

  private async handleGeneralRequest(request: string): Promise<TaskResult> {
    let context = '';
    
    if (request.toLowerCase().includes('repository') || request.toLowerCase().includes('repo')) {
      const files = await this.fileOps.listFiles();
      context = `Repository structure: ${files.join(', ')}`;
      
      if (await this.gitOps.isRepository()) {
        const status = await this.gitOps.getStatus();
        context += `\\nGit status: ${status.current} branch, ${status.files.length} changes`;
      }
    }

    const response = await this.aiProvider.generateResponse(request, context);

    const formattedResponse = `## 🤖 AI Assistant Response

**Request:** ${request}

${response}

---
Generated with Claude Code Alternative`;

    await this.githubOps.createComment(formattedResponse);

    return {
      success: true,
      message: 'Response generated',
      details: { request, response },
    };
  }

  private async handlePullRequestReview(payload: any): Promise<TaskResult> {
    const review = payload.review;
    const triggerPhrase = this.extractTriggerPhrase(review.body);
    
    if (!triggerPhrase) {
      return {
        success: false,
        message: 'No trigger phrase found in review',
      };
    }

    return await this.handleReviewRequest();
  }

  private async handleIssueCreated(payload: any): Promise<TaskResult> {
    const issue = payload.issue;
    const triggerPhrase = this.extractTriggerPhrase(issue.body);
    
    if (!triggerPhrase) {
      return {
        success: false,
        message: 'No trigger phrase found in issue',
      };
    }

    return await this.handleGeneralRequest(triggerPhrase);
  }

  public async run(): Promise<void> {
    console.log(`Running GitHub Action for event: ${this.githubContext.eventType}`);
    console.log(`Repository: ${this.githubContext.owner}/${this.githubContext.repo}`);
    console.log(`Triggered by: ${this.githubContext.triggerUser}`);

    const payload = this.getEventPayload();
    let result: TaskResult;

    try {
      switch (this.githubContext.eventType) {
        case 'issue_comment':
          result = await this.handleIssueComment(payload);
          break;
        case 'pull_request_review':
          result = await this.handlePullRequestReview(payload);
          break;
        case 'issues':
          if (payload.action === 'opened' || payload.action === 'assigned') {
            result = await this.handleIssueCreated(payload);
          } else {
            result = { success: false, message: `Unsupported issue action: ${payload.action}` };
          }
          break;
        default:
          result = { success: false, message: `Unsupported event: ${this.githubContext.eventType}` };
      }

      if (result.success) {
        console.log('✅ Task completed successfully:', result.message);
      } else {
        console.log('❌ Task failed:', result.message);
        process.exit(1);
      }
    } catch (error) {
      console.error('❌ Unexpected error:', error);
      
      try {
        await this.githubOps.createComment(`## ❌ Error

An error occurred while processing your request:

\`\`\`
${error}
\`\`\`

Please check the action logs for more details.

Generated with Claude Code Alternative`);
      } catch (commentError) {
        console.error('Failed to create error comment:', commentError);
      }
      
      process.exit(1);
    }
  }
}

// Run the action if called directly
if (import.meta.url === `file://${process.argv[1]}`) {
  const runner = new GitHubActionRunner();
  runner.run().catch(error => {
    console.error('Fatal error:', error);
    process.exit(1);
  });
}

export { GitHubActionRunner };