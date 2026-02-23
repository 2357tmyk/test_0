import { simpleGit, SimpleGit, StatusResult, DiffResult } from 'simple-git';
import { CommandContext } from '../types/index.js';

export class GitOperationsManager {
  private git: SimpleGit;
  private context: CommandContext;

  constructor(context: CommandContext) {
    this.context = context;
    this.git = simpleGit(context.workingDirectory);
  }

  async isRepository(): Promise<boolean> {
    try {
      await this.git.status();
      return true;
    } catch {
      return false;
    }
  }

  async getStatus(): Promise<StatusResult> {
    try {
      return await this.git.status();
    } catch (error) {
      throw new Error(`Failed to get git status: ${error}`);
    }
  }

  async getCurrentBranch(): Promise<string> {
    try {
      const status = await this.git.status();
      return status.current || 'main';
    } catch (error) {
      throw new Error(`Failed to get current branch: ${error}`);
    }
  }

  async createBranch(branchName: string, checkout: boolean = true): Promise<void> {
    try {
      if (checkout) {
        await this.git.checkoutLocalBranch(branchName);
      } else {
        await this.git.branch([branchName]);
      }
    } catch (error) {
      throw new Error(`Failed to create branch ${branchName}: ${error}`);
    }
  }

  async switchBranch(branchName: string): Promise<void> {
    try {
      await this.git.checkout(branchName);
    } catch (error) {
      throw new Error(`Failed to switch to branch ${branchName}: ${error}`);
    }
  }

  async addFiles(files: string[]): Promise<void> {
    try {
      await this.git.add(files);
    } catch (error) {
      throw new Error(`Failed to add files: ${error}`);
    }
  }

  async commit(message: string, author?: { name: string; email: string }): Promise<void> {
    try {
      const options: any = {};
      if (author) {
        options['--author'] = `"${author.name} <${author.email}>"`;
      }
      
      await this.git.commit(message, undefined, options);
    } catch (error) {
      throw new Error(`Failed to commit: ${error}`);
    }
  }

  async push(remote: string = 'origin', branch?: string): Promise<void> {
    try {
      const currentBranch = branch || await this.getCurrentBranch();
      await this.git.push(remote, currentBranch);
    } catch (error) {
      throw new Error(`Failed to push to ${remote}: ${error}`);
    }
  }

  async pull(remote: string = 'origin', branch?: string): Promise<void> {
    try {
      const currentBranch = branch || await this.getCurrentBranch();
      await this.git.pull(remote, currentBranch);
    } catch (error) {
      throw new Error(`Failed to pull from ${remote}: ${error}`);
    }
  }

  async getDiff(options?: { staged?: boolean; file?: string }): Promise<string> {
    try {
      const diffOptions: string[] = [];
      
      if (options?.staged) {
        diffOptions.push('--staged');
      }
      
      if (options?.file) {
        diffOptions.push(options.file);
      }

      return await this.git.diff(diffOptions);
    } catch (error) {
      throw new Error(`Failed to get diff: ${error}`);
    }
  }

  async getCommitHistory(limit: number = 10): Promise<any[]> {
    try {
      const log = await this.git.log({ maxCount: limit });
      return log.all;
    } catch (error) {
      throw new Error(`Failed to get commit history: ${error}`);
    }
  }

  async getChangedFiles(): Promise<string[]> {
    try {
      const status = await this.git.status();
      return [
        ...status.modified,
        ...status.created,
        ...status.deleted,
        ...status.renamed.map(r => r.to),
      ];
    } catch (error) {
      throw new Error(`Failed to get changed files: ${error}`);
    }
  }

  async stashChanges(message?: string): Promise<void> {
    try {
      await this.git.stash(['push', ...(message ? ['-m', message] : [])]);
    } catch (error) {
      throw new Error(`Failed to stash changes: ${error}`);
    }
  }

  async applyStash(stashIndex: number = 0): Promise<void> {
    try {
      await this.git.stash(['apply', `stash@{${stashIndex}}`]);
    } catch (error) {
      throw new Error(`Failed to apply stash: ${error}`);
    }
  }

  async getRemoteUrl(remote: string = 'origin'): Promise<string> {
    try {
      const remotes = await this.git.getRemotes(true);
      const originRemote = remotes.find(r => r.name === remote);
      return originRemote?.refs?.fetch || '';
    } catch (error) {
      throw new Error(`Failed to get remote URL: ${error}`);
    }
  }

  async isClean(): Promise<boolean> {
    try {
      const status = await this.git.status();
      return status.isClean();
    } catch (error) {
      return false;
    }
  }

  async resetHard(commit: string = 'HEAD'): Promise<void> {
    try {
      await this.git.reset(['--hard', commit]);
    } catch (error) {
      throw new Error(`Failed to reset to ${commit}: ${error}`);
    }
  }
}