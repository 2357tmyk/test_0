#!/usr/bin/env node

/**
 * Validation script for Claude Code Alternative
 * Performs basic validation without requiring npm install
 */

const fs = require('fs');
const path = require('path');

class Validator {
  constructor() {
    this.errors = [];
    this.warnings = [];
    this.checks = [];
  }

  addError(message) {
    this.errors.push(message);
    console.error('❌', message);
  }

  addWarning(message) {
    this.warnings.push(message);
    console.warn('⚠️ ', message);
  }

  addCheck(message) {
    this.checks.push(message);
    console.log('✅', message);
  }

  validateFileExists(filePath, isRequired = true) {
    const fullPath = path.join(__dirname, '..', filePath);
    if (fs.existsSync(fullPath)) {
      this.addCheck(`File exists: ${filePath}`);
      return true;
    } else {
      if (isRequired) {
        this.addError(`Required file missing: ${filePath}`);
      } else {
        this.addWarning(`Optional file missing: ${filePath}`);
      }
      return false;
    }
  }

  validateDirectoryExists(dirPath, isRequired = true) {
    const fullPath = path.join(__dirname, '..', dirPath);
    if (fs.existsSync(fullPath) && fs.statSync(fullPath).isDirectory()) {
      this.addCheck(`Directory exists: ${dirPath}`);
      return true;
    } else {
      if (isRequired) {
        this.addError(`Required directory missing: ${dirPath}`);
      } else {
        this.addWarning(`Optional directory missing: ${dirPath}`);
      }
      return false;
    }
  }

  validatePackageJson() {
    const packagePath = path.join(__dirname, '..', 'package.json');
    if (!fs.existsSync(packagePath)) {
      this.addError('package.json not found');
      return;
    }

    try {
      const packageJson = JSON.parse(fs.readFileSync(packagePath, 'utf8'));
      
      // Check required fields
      const requiredFields = ['name', 'version', 'description', 'main', 'bin'];
      requiredFields.forEach(field => {
        if (!packageJson[field]) {
          this.addError(`package.json missing required field: ${field}`);
        } else {
          this.addCheck(`package.json has ${field}`);
        }
      });

      // Check dependencies
      const requiredDeps = [
        '@anthropic-ai/sdk',
        '@octokit/rest', 
        'commander',
        'simple-git',
        'dotenv'
      ];

      requiredDeps.forEach(dep => {
        if (!packageJson.dependencies || !packageJson.dependencies[dep]) {
          this.addError(`Missing required dependency: ${dep}`);
        } else {
          this.addCheck(`Has dependency: ${dep}`);
        }
      });

      // Check scripts
      const requiredScripts = ['build', 'test', 'lint', 'typecheck'];
      requiredScripts.forEach(script => {
        if (!packageJson.scripts || !packageJson.scripts[script]) {
          this.addWarning(`Missing recommended script: ${script}`);
        } else {
          this.addCheck(`Has script: ${script}`);
        }
      });

    } catch (error) {
      this.addError(`Failed to parse package.json: ${error.message}`);
    }
  }

  validateTsConfig() {
    const tsConfigPath = path.join(__dirname, '..', 'tsconfig.json');
    if (!fs.existsSync(tsConfigPath)) {
      this.addError('tsconfig.json not found');
      return;
    }

    try {
      const tsConfig = JSON.parse(fs.readFileSync(tsConfigPath, 'utf8'));
      
      if (!tsConfig.compilerOptions) {
        this.addError('tsconfig.json missing compilerOptions');
        return;
      }

      const requiredOptions = ['target', 'module', 'outDir', 'rootDir', 'strict'];
      requiredOptions.forEach(option => {
        if (tsConfig.compilerOptions[option] === undefined) {
          this.addWarning(`tsconfig.json missing compiler option: ${option}`);
        } else {
          this.addCheck(`TypeScript option set: ${option}`);
        }
      });

    } catch (error) {
      this.addError(`Failed to parse tsconfig.json: ${error.message}`);
    }
  }

  validateSourceStructure() {
    // Check core source files
    const coreFiles = [
      'src/types/index.ts',
      'src/core/config.ts',
      'src/core/file-operations.ts',
      'src/core/git-operations.ts',
      'src/core/github-integration.ts',
      'src/providers/anthropic.ts',
      'src/cli.ts',
      'src/github-action.ts'
    ];

    coreFiles.forEach(file => this.validateFileExists(file, true));

    // Check directories
    const coreDirectories = [
      'src',
      'src/core',
      'src/providers', 
      'src/types',
      'tests',
      'tasks',
      'examples'
    ];

    coreDirectories.forEach(dir => this.validateDirectoryExists(dir, true));
  }

  validateDocumentation() {
    const docFiles = [
      'README.md',
      'LICENSE',
      'ARCHITECTURE.md',
      'examples/basic-usage.md',
      'tasks/todo.md',
      'tasks/lessons.md'
    ];

    docFiles.forEach(file => this.validateFileExists(file, true));
  }

  validateConfiguration() {
    // Check configuration files
    this.validateFileExists('.gitignore', true);
    this.validateFileExists('.env.example', false);
    this.validateFileExists('jest.config.js', true);
    this.validateFileExists('.eslintrc.js', true);
  }

  validateGitHubActions() {
    this.validateFileExists('.github/workflows/claude-alt.yml', true);
  }

  validateBasicSyntax() {
    const tsFiles = [
      'src/types/index.ts',
      'src/core/config.ts',
      'src/core/file-operations.ts',
      'src/core/git-operations.ts',
      'src/core/github-integration.ts',
      'src/providers/anthropic.ts',
      'src/cli.ts',
      'src/github-action.ts'
    ];

    tsFiles.forEach(file => {
      const fullPath = path.join(__dirname, '..', file);
      if (fs.existsSync(fullPath)) {
        try {
          const content = fs.readFileSync(fullPath, 'utf8');
          
          // Basic syntax checks
          if (!content.includes('export')) {
            this.addWarning(`${file} might be missing exports`);
          }
          
          // Check for TypeScript imports
          if (content.includes('from ') && content.includes('.js')) {
            this.addCheck(`${file} uses proper ES module imports`);
          }
          
          // Check for proper interface definitions
          if (file.includes('types/') && !content.includes('interface')) {
            this.addWarning(`${file} in types directory should contain interface definitions`);
          }

          this.addCheck(`${file} basic syntax validation passed`);
        } catch (error) {
          this.addError(`Failed to read ${file}: ${error.message}`);
        }
      }
    });
  }

  run() {
    console.log('🔍 Running Claude Code Alternative Validation...\n');

    this.validatePackageJson();
    this.validateTsConfig();
    this.validateSourceStructure();
    this.validateDocumentation();
    this.validateConfiguration();
    this.validateGitHubActions();
    this.validateBasicSyntax();

    console.log('\n📊 Validation Summary:');
    console.log(`✅ Checks passed: ${this.checks.length}`);
    console.log(`⚠️  Warnings: ${this.warnings.length}`);
    console.log(`❌ Errors: ${this.errors.length}`);

    if (this.errors.length === 0) {
      console.log('\n🎉 All critical validations passed! The project structure is ready.');
      return 0;
    } else {
      console.log('\n💥 Validation failed. Please fix the errors above.');
      return 1;
    }
  }
}

// Run validation
const validator = new Validator();
const exitCode = validator.run();
process.exit(exitCode);