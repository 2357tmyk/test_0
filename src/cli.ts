#!/usr/bin/env node

import { Command } from 'commander';
import chalk from 'chalk';
import ora from 'ora';
import inquirer from 'inquirer';
import { ConfigManager } from './core/config.js';
import { FileOperationsManager } from './core/file-operations.js';
import { GitOperationsManager } from './core/git-operations.js';
import { AnthropicProvider } from './providers/anthropic.js';
import { CommandContext, TaskResult } from './types/index.js';

const program = new Command();
const configManager = new ConfigManager();

async function createContext(): Promise<CommandContext> {
  return {
    workingDirectory: process.cwd(),
    environment: configManager.getEnvironmentType(),
    verbose: false,
  };
}

program
  .name('claude-alt')
  .description('Open-source alternative to Claude Code with AI-powered development assistance')
  .version('1.0.0');

program
  .command('analyze')
  .description('Analyze code files with AI')
  .option('-f, --file <file>', 'specific file to analyze')
  .option('-d, --directory <directory>', 'directory to analyze', '.')
  .option('--format <format>', 'output format (json, text)', 'text')
  .action(async (options) => {
    const spinner = ora('Analyzing code...').start();
    
    try {
      const config = configManager.getConfig();
      const context = await createContext();
      const fileOps = new FileOperationsManager(context);
      const aiProvider = new AnthropicProvider(config.aiProvider.apiKey);

      if (options.file) {
        const content = await fileOps.readFile(options.file);
        const analysis = await aiProvider.analyzeCode(content, options.file);
        
        spinner.succeed('Analysis complete!');
        
        if (options.format === 'json') {
          console.log(JSON.stringify(analysis, null, 2));
        } else {
          console.log(chalk.blue('\\n📊 Code Analysis Results\\n'));
          console.log(chalk.yellow('Summary:'), analysis.summary);
          
          if (analysis.issues.length > 0) {
            console.log(chalk.red('\\n🚨 Issues:'));
            analysis.issues.forEach((issue, i) => {
              console.log(`${i + 1}. [${issue.severity.toUpperCase()}] ${issue.message}${issue.line ? ` (line ${issue.line})` : ''}`);
            });
          }
          
          if (analysis.suggestions.length > 0) {
            console.log(chalk.green('\\n💡 Suggestions:'));
            analysis.suggestions.forEach((suggestion, i) => {
              console.log(`${i + 1}. [${suggestion.type.toUpperCase()}] ${suggestion.message}${suggestion.line ? ` (line ${suggestion.line})` : ''}`);
            });
          }
        }
      } else {
        const files = await fileOps.findFiles('\\.(js|ts|py|java|cpp|c|go|rs)$', options.directory);
        const results = [];
        
        for (const file of files.slice(0, 10)) { // Limit to 10 files for demo
          try {
            const content = await fileOps.readFile(file);
            const analysis = await aiProvider.analyzeCode(content, file);
            results.push({ file, analysis });
          } catch (error) {
            console.warn(chalk.yellow(`Warning: Could not analyze ${file}`));
          }
        }
        
        spinner.succeed(`Analyzed ${results.length} files!`);
        
        if (options.format === 'json') {
          console.log(JSON.stringify(results, null, 2));
        } else {
          results.forEach(({ file, analysis }) => {
            console.log(chalk.blue(`\\n📁 ${file}`));
            console.log(chalk.gray(analysis.summary));
            
            if (analysis.issues.length > 0) {
              console.log(chalk.red(`  Issues: ${analysis.issues.length}`));
            }
            if (analysis.suggestions.length > 0) {
              console.log(chalk.green(`  Suggestions: ${analysis.suggestions.length}`));
            }
          });
        }
      }
    } catch (error) {
      spinner.fail('Analysis failed');
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

program
  .command('ask')
  .description('Ask AI a question about your code or project')
  .argument('<question>', 'question to ask')
  .option('-c, --context <file>', 'provide context from a specific file')
  .action(async (question, options) => {
    const spinner = ora('Thinking...').start();
    
    try {
      const config = configManager.getConfig();
      const context = await createContext();
      const aiProvider = new AnthropicProvider(config.aiProvider.apiKey);
      
      let contextContent = '';
      if (options.context) {
        const fileOps = new FileOperationsManager(context);
        contextContent = await fileOps.readFile(options.context);
      }
      
      const response = await aiProvider.generateResponse(question, contextContent);
      
      spinner.succeed('Response generated!');
      console.log(chalk.blue('\\n🤖 AI Response:\\n'));
      console.log(response);
    } catch (error) {
      spinner.fail('Failed to get response');
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

program
  .command('git')
  .description('Git operations with AI assistance')
  .option('-s, --status', 'show git status')
  .option('-d, --diff', 'show git diff')
  .option('-c, --commit <message>', 'commit with AI-generated message if not provided')
  .option('-p, --push', 'push changes')
  .action(async (options) => {
    try {
      const context = await createContext();
      const git = new GitOperationsManager(context);
      
      if (!(await git.isRepository())) {
        console.error(chalk.red('Error: Not in a git repository'));
        process.exit(1);
      }
      
      if (options.status) {
        const status = await git.getStatus();
        console.log(chalk.blue('📊 Git Status:\\n'));
        console.log(`Branch: ${chalk.green(status.current)}`);
        
        if (status.modified.length > 0) {
          console.log(chalk.yellow('Modified:'), status.modified.join(', '));
        }
        if (status.created.length > 0) {
          console.log(chalk.green('Added:'), status.created.join(', '));
        }
        if (status.deleted.length > 0) {
          console.log(chalk.red('Deleted:'), status.deleted.join(', '));
        }
      }
      
      if (options.diff) {
        const diff = await git.getDiff();
        console.log(chalk.blue('📝 Git Diff:\\n'));
        console.log(diff);
      }
      
      if (options.commit) {
        const changedFiles = await git.getChangedFiles();
        if (changedFiles.length === 0) {
          console.log(chalk.yellow('No changes to commit'));
          return;
        }
        
        await git.addFiles(changedFiles);
        
        let commitMessage = options.commit;
        if (commitMessage === true) {
          const config = configManager.getConfig();
          const aiProvider = new AnthropicProvider(config.aiProvider.apiKey);
          const diff = await git.getDiff({ staged: true });
          
          const spinner = ora('Generating commit message...').start();
          commitMessage = await aiProvider.generateResponse(
            'Generate a concise, conventional commit message for these changes:',
            diff
          );
          spinner.succeed('Commit message generated!');
        }
        
        await git.commit(commitMessage);
        console.log(chalk.green('✅ Committed successfully!'));
        
        if (options.push) {
          const pushSpinner = ora('Pushing changes...').start();
          await git.push();
          pushSpinner.succeed('Pushed successfully!');
        }
      }
    } catch (error) {
      console.error(chalk.red('Error:'), error);
      process.exit(1);
    }
  });

program
  .command('setup')
  .description('Set up claude-alt configuration')
  .action(async () => {
    console.log(chalk.blue('🔧 Claude Alt Setup\\n'));
    
    const answers = await inquirer.prompt([
      {
        type: 'list',
        name: 'aiProvider',
        message: 'Select AI provider:',
        choices: ['anthropic', 'openai'],
        default: 'anthropic',
      },
      {
        type: 'password',
        name: 'apiKey',
        message: 'Enter API key:',
        mask: '*',
      },
      {
        type: 'input',
        name: 'githubToken',
        message: 'GitHub token (optional):',
      },
      {
        type: 'confirm',
        name: 'saveConfig',
        message: 'Save configuration to file?',
        default: true,
      },
    ]);
    
    if (answers.saveConfig) {
      const config = {
        aiProvider: {
          name: answers.aiProvider,
          apiKey: answers.apiKey,
        },
        github: answers.githubToken ? {
          token: answers.githubToken,
          defaultBranch: 'main',
        } : undefined,
        features: {
          codeAnalysis: true,
          gitIntegration: true,
          fileOperations: true,
        },
      };
      
      const context = await createContext();
      const fileOps = new FileOperationsManager(context);
      await fileOps.writeFile('claude-alt.config.json', JSON.stringify(config, null, 2));
      
      console.log(chalk.green('✅ Configuration saved!'));
    }
    
    console.log(chalk.blue('\\n🚀 Setup complete! You can now use claude-alt commands.'));
  });

program
  .command('config')
  .description('Show current configuration')
  .action(() => {
    try {
      const config = configManager.getConfig();
      const errors = configManager.validateConfig();
      
      console.log(chalk.blue('📋 Current Configuration:\\n'));
      console.log(chalk.yellow('AI Provider:'), config.aiProvider.name);
      console.log(chalk.yellow('API Key:'), config.aiProvider.apiKey ? '***configured***' : 'not set');
      console.log(chalk.yellow('Environment:'), configManager.getEnvironmentType());
      
      if (config.github) {
        console.log(chalk.yellow('GitHub Token:'), config.github.token ? '***configured***' : 'not set');
        console.log(chalk.yellow('Default Branch:'), config.github.defaultBranch);
      }
      
      console.log(chalk.yellow('Features:'));
      Object.entries(config.features).forEach(([key, value]) => {
        console.log(`  ${key}: ${value ? chalk.green('enabled') : chalk.red('disabled')}`);
      });
      
      if (errors.length > 0) {
        console.log(chalk.red('\\n⚠️  Configuration Errors:'));
        errors.forEach(error => console.log(chalk.red(`  - ${error}`)));
      } else {
        console.log(chalk.green('\\n✅ Configuration is valid!'));
      }
    } catch (error) {
      console.error(chalk.red('Error reading configuration:'), error);
      process.exit(1);
    }
  });

if (process.argv.length === 2) {
  program.help();
}

program.parse();