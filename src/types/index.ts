export interface AIProvider {
  name: string;
  generateResponse(prompt: string, context?: string): Promise<string>;
  analyzeCode(code: string, filePath?: string): Promise<CodeAnalysis>;
}

export interface CodeAnalysis {
  issues: Issue[];
  suggestions: Suggestion[];
  summary: string;
}

export interface Issue {
  severity: 'error' | 'warning' | 'info';
  message: string;
  line?: number;
  column?: number;
  file?: string;
}

export interface Suggestion {
  type: 'refactor' | 'optimization' | 'style' | 'security';
  message: string;
  line?: number;
  column?: number;
  file?: string;
}

export interface GitHubContext {
  owner: string;
  repo: string;
  issueNumber?: number;
  prNumber?: number;
  eventType: string;
  triggerUser: string;
  token: string;
}

export interface FileOperation {
  type: 'read' | 'write' | 'delete' | 'create';
  path: string;
  content?: string;
  encoding?: string;
}

export interface CommandContext {
  workingDirectory: string;
  gitRepository?: string;
  environment: 'local' | 'github-actions';
  verbose?: boolean;
}

export interface Config {
  aiProvider: {
    name: string;
    apiKey: string;
    endpoint?: string;
  };
  github?: {
    token: string;
    defaultBranch: string;
  };
  features: {
    codeAnalysis: boolean;
    gitIntegration: boolean;
    fileOperations: boolean;
  };
}

export interface TaskResult {
  success: boolean;
  message: string;
  details?: any;
  changes?: FileOperation[];
}