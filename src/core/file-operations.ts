import { readFile, writeFile, unlink, mkdir, stat, readdir } from 'fs/promises';
import { existsSync } from 'fs';
import { dirname, resolve, extname } from 'path';
import { FileOperation, CommandContext } from '../types/index.js';

export class FileOperationsManager {
  private context: CommandContext;

  constructor(context: CommandContext) {
    this.context = context;
  }

  async readFile(filePath: string, encoding: BufferEncoding = 'utf-8'): Promise<string> {
    const fullPath = resolve(this.context.workingDirectory, filePath);
    
    if (!existsSync(fullPath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    try {
      return await readFile(fullPath, encoding);
    } catch (error) {
      throw new Error(`Failed to read file ${filePath}: ${error}`);
    }
  }

  async writeFile(filePath: string, content: string, encoding: BufferEncoding = 'utf-8'): Promise<void> {
    const fullPath = resolve(this.context.workingDirectory, filePath);
    const directory = dirname(fullPath);

    if (!existsSync(directory)) {
      await mkdir(directory, { recursive: true });
    }

    try {
      await writeFile(fullPath, content, encoding);
    } catch (error) {
      throw new Error(`Failed to write file ${filePath}: ${error}`);
    }
  }

  async deleteFile(filePath: string): Promise<void> {
    const fullPath = resolve(this.context.workingDirectory, filePath);
    
    if (!existsSync(fullPath)) {
      throw new Error(`File not found: ${filePath}`);
    }

    try {
      await unlink(fullPath);
    } catch (error) {
      throw new Error(`Failed to delete file ${filePath}: ${error}`);
    }
  }

  async fileExists(filePath: string): Promise<boolean> {
    const fullPath = resolve(this.context.workingDirectory, filePath);
    return existsSync(fullPath);
  }

  async listFiles(directoryPath: string = '.'): Promise<string[]> {
    const fullPath = resolve(this.context.workingDirectory, directoryPath);
    
    try {
      return await readdir(fullPath);
    } catch (error) {
      throw new Error(`Failed to list files in ${directoryPath}: ${error}`);
    }
  }

  async getFileInfo(filePath: string): Promise<{
    size: number;
    modified: Date;
    isDirectory: boolean;
    extension: string;
  }> {
    const fullPath = resolve(this.context.workingDirectory, filePath);
    
    try {
      const stats = await stat(fullPath);
      return {
        size: stats.size,
        modified: stats.mtime,
        isDirectory: stats.isDirectory(),
        extension: extname(filePath),
      };
    } catch (error) {
      throw new Error(`Failed to get file info for ${filePath}: ${error}`);
    }
  }

  async executeOperations(operations: FileOperation[]): Promise<void> {
    for (const operation of operations) {
      switch (operation.type) {
        case 'read':
          await this.readFile(operation.path, operation.encoding as BufferEncoding);
          break;
        case 'write':
        case 'create':
          if (!operation.content) {
            throw new Error(`Content required for ${operation.type} operation`);
          }
          await this.writeFile(operation.path, operation.content, operation.encoding as BufferEncoding);
          break;
        case 'delete':
          await this.deleteFile(operation.path);
          break;
        default:
          throw new Error(`Unknown operation type: ${operation.type}`);
      }
    }
  }

  async findFiles(pattern: string, directory: string = '.'): Promise<string[]> {
    const fullPath = resolve(this.context.workingDirectory, directory);
    const files = await this.listFiles(directory);
    
    const regex = new RegExp(pattern.replace(/\*/g, '.*').replace(/\?/g, '.'));
    return files.filter(file => regex.test(file));
  }

  getFileMimeType(filePath: string): string {
    const ext = extname(filePath).toLowerCase();
    const mimeTypes: Record<string, string> = {
      '.js': 'application/javascript',
      '.ts': 'application/typescript',
      '.json': 'application/json',
      '.html': 'text/html',
      '.css': 'text/css',
      '.md': 'text/markdown',
      '.txt': 'text/plain',
      '.py': 'text/x-python',
      '.java': 'text/x-java-source',
      '.cpp': 'text/x-c++src',
      '.c': 'text/x-csrc',
      '.go': 'text/x-go',
      '.rs': 'text/x-rust',
      '.php': 'text/x-php',
      '.rb': 'text/x-ruby',
    };
    
    return mimeTypes[ext] || 'text/plain';
  }
}