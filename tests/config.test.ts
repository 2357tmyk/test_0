import { ConfigManager } from '../src/core/config';

describe('ConfigManager', () => {
  let configManager: ConfigManager;

  beforeEach(() => {
    // Clear environment variables for clean test state
    delete process.env.ANTHROPIC_API_KEY;
    delete process.env.GITHUB_TOKEN;
    delete process.env.AI_PROVIDER;
    
    configManager = new ConfigManager();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('getConfig', () => {
    it('should return default configuration when no environment variables are set', () => {
      const config = configManager.getConfig();
      
      expect(config.aiProvider.name).toBe('anthropic');
      expect(config.aiProvider.apiKey).toBe('');
      expect(config.features.codeAnalysis).toBe(true);
      expect(config.features.gitIntegration).toBe(true);
      expect(config.features.fileOperations).toBe(true);
    });

    it('should use environment variables when available', () => {
      process.env.ANTHROPIC_API_KEY = 'test-api-key';
      process.env.GITHUB_TOKEN = 'test-github-token';
      process.env.AI_PROVIDER = 'anthropic';
      
      const newConfigManager = new ConfigManager();
      const config = newConfigManager.getConfig();
      
      expect(config.aiProvider.apiKey).toBe('test-api-key');
      expect(config.github?.token).toBe('test-github-token');
    });
  });

  describe('validateConfig', () => {
    it('should return errors when required fields are missing', () => {
      const errors = configManager.validateConfig();
      
      expect(errors).toContain('AI provider API key is required');
    });

    it('should return no errors when configuration is valid', () => {
      process.env.ANTHROPIC_API_KEY = 'valid-api-key';
      process.env.GITHUB_TOKEN = 'valid-github-token';
      
      const newConfigManager = new ConfigManager();
      const errors = newConfigManager.validateConfig();
      
      expect(errors).toHaveLength(0);
    });

    it('should validate GitHub token when GitHub features are enabled', () => {
      process.env.ANTHROPIC_API_KEY = 'valid-api-key';
      // No GitHub token set
      
      const newConfigManager = new ConfigManager();
      const errors = newConfigManager.validateConfig();
      
      expect(errors).toContain('GitHub token is required for GitHub operations');
    });
  });

  describe('isGitHubActionsEnvironment', () => {
    it('should return false in local environment', () => {
      expect(configManager.isGitHubActionsEnvironment()).toBe(false);
    });

    it('should return true in GitHub Actions environment', () => {
      process.env.GITHUB_ACTIONS = 'true';
      
      expect(configManager.isGitHubActionsEnvironment()).toBe(true);
    });
  });

  describe('getEnvironmentType', () => {
    it('should return local for local development', () => {
      expect(configManager.getEnvironmentType()).toBe('local');
    });

    it('should return github-actions for CI environment', () => {
      process.env.GITHUB_ACTIONS = 'true';
      
      const newConfigManager = new ConfigManager();
      expect(newConfigManager.getEnvironmentType()).toBe('github-actions');
    });
  });
});