import { Config } from '../types/index.js';
import { config as dotenvConfig } from 'dotenv';
import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

dotenvConfig();

export class ConfigManager {
  private config: Config | null = null;

  constructor() {
    this.loadConfig();
  }

  private loadConfig(): void {
    const configPath = resolve(process.cwd(), 'claude-alt.config.json');
    
    this.config = {
      aiProvider: {
        name: process.env.AI_PROVIDER || 'anthropic',
        apiKey: process.env.ANTHROPIC_API_KEY || process.env.OPENAI_API_KEY || '',
        endpoint: process.env.AI_ENDPOINT,
      },
      github: {
        token: process.env.GITHUB_TOKEN || '',
        defaultBranch: process.env.DEFAULT_BRANCH || 'main',
      },
      features: {
        codeAnalysis: true,
        gitIntegration: true,
        fileOperations: true,
      },
    };

    if (existsSync(configPath)) {
      try {
        const fileConfig = JSON.parse(readFileSync(configPath, 'utf-8'));
        this.config = { ...this.config, ...fileConfig };
      } catch (error) {
        console.warn('Failed to load config file:', error);
      }
    }
  }

  public getConfig(): Config {
    if (!this.config) {
      throw new Error('Config not loaded');
    }
    return this.config;
  }

  public validateConfig(): string[] {
    const errors: string[] = [];
    const config = this.getConfig();

    if (!config.aiProvider.apiKey) {
      errors.push('AI provider API key is required');
    }

    if (config.github && !config.github.token) {
      errors.push('GitHub token is required for GitHub operations');
    }

    return errors;
  }

  public isGitHubActionsEnvironment(): boolean {
    return process.env.GITHUB_ACTIONS === 'true';
  }

  public getEnvironmentType(): 'local' | 'github-actions' {
    return this.isGitHubActionsEnvironment() ? 'github-actions' : 'local';
  }
}