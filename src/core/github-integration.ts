import { Octokit } from '@octokit/rest';
import { GitHubContext, TaskResult } from '../types/index.js';

export class GitHubIntegrationManager {
  private octokit: Octokit;
  private context: GitHubContext;

  constructor(context: GitHubContext) {
    this.context = context;
    this.octokit = new Octokit({
      auth: context.token,
    });
  }

  async createComment(body: string, issueNumber?: number): Promise<void> {
    const targetIssue = issueNumber || this.context.issueNumber || this.context.prNumber;
    
    if (!targetIssue) {
      throw new Error('No issue or PR number provided');
    }

    try {
      await this.octokit.rest.issues.createComment({
        owner: this.context.owner,
        repo: this.context.repo,
        issue_number: targetIssue,
        body,
      });
    } catch (error) {
      throw new Error(`Failed to create comment: ${error}`);
    }
  }

  async updateComment(commentId: number, body: string): Promise<void> {
    try {
      await this.octokit.rest.issues.updateComment({
        owner: this.context.owner,
        repo: this.context.repo,
        comment_id: commentId,
        body,
      });
    } catch (error) {
      throw new Error(`Failed to update comment: ${error}`);
    }
  }

  async getIssue(issueNumber: number): Promise<any> {
    try {
      const response = await this.octokit.rest.issues.get({
        owner: this.context.owner,
        repo: this.context.repo,
        issue_number: issueNumber,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get issue: ${error}`);
    }
  }

  async getPullRequest(prNumber: number): Promise<any> {
    try {
      const response = await this.octokit.rest.pulls.get({
        owner: this.context.owner,
        repo: this.context.repo,
        pull_number: prNumber,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get pull request: ${error}`);
    }
  }

  async createPullRequest(
    title: string,
    body: string,
    head: string,
    base: string = 'main'
  ): Promise<any> {
    try {
      const response = await this.octokit.rest.pulls.create({
        owner: this.context.owner,
        repo: this.context.repo,
        title,
        body,
        head,
        base,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to create pull request: ${error}`);
    }
  }

  async getFileContents(path: string, ref?: string): Promise<string> {
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.context.owner,
        repo: this.context.repo,
        path,
        ref,
      });

      if ('content' in response.data) {
        return Buffer.from(response.data.content, 'base64').toString('utf-8');
      }

      throw new Error('File content not available');
    } catch (error) {
      throw new Error(`Failed to get file contents: ${error}`);
    }
  }

  async updateFile(
    path: string,
    content: string,
    message: string,
    sha?: string,
    branch?: string
  ): Promise<void> {
    try {
      const params: any = {
        owner: this.context.owner,
        repo: this.context.repo,
        path,
        message,
        content: Buffer.from(content).toString('base64'),
      };

      if (sha) {
        params.sha = sha;
      }

      if (branch) {
        params.branch = branch;
      }

      await this.octokit.rest.repos.createOrUpdateFileContents(params);
    } catch (error) {
      throw new Error(`Failed to update file: ${error}`);
    }
  }

  async getCommitDiff(commitSha: string): Promise<any> {
    try {
      const response = await this.octokit.rest.repos.getCommit({
        owner: this.context.owner,
        repo: this.context.repo,
        ref: commitSha,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get commit diff: ${error}`);
    }
  }

  async listPullRequestFiles(prNumber: number): Promise<any[]> {
    try {
      const response = await this.octokit.rest.pulls.listFiles({
        owner: this.context.owner,
        repo: this.context.repo,
        pull_number: prNumber,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to list PR files: ${error}`);
    }
  }

  async createReviewComment(
    prNumber: number,
    body: string,
    path: string,
    line: number,
    commitSha: string
  ): Promise<void> {
    try {
      await this.octokit.rest.pulls.createReviewComment({
        owner: this.context.owner,
        repo: this.context.repo,
        pull_number: prNumber,
        body,
        path,
        line,
        commit_id: commitSha,
      });
    } catch (error) {
      throw new Error(`Failed to create review comment: ${error}`);
    }
  }

  async getRepository(): Promise<any> {
    try {
      const response = await this.octokit.rest.repos.get({
        owner: this.context.owner,
        repo: this.context.repo,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to get repository info: ${error}`);
    }
  }

  async listBranches(): Promise<any[]> {
    try {
      const response = await this.octokit.rest.repos.listBranches({
        owner: this.context.owner,
        repo: this.context.repo,
      });
      return response.data;
    } catch (error) {
      throw new Error(`Failed to list branches: ${error}`);
    }
  }

  async createBranch(branchName: string, fromSha: string): Promise<void> {
    try {
      await this.octokit.rest.git.createRef({
        owner: this.context.owner,
        repo: this.context.repo,
        ref: `refs/heads/${branchName}`,
        sha: fromSha,
      });
    } catch (error) {
      throw new Error(`Failed to create branch: ${error}`);
    }
  }
}