import Anthropic from '@anthropic-ai/sdk';
import { AIProvider, CodeAnalysis, Issue, Suggestion } from '../types/index.js';

export class AnthropicProvider implements AIProvider {
  public readonly name = 'anthropic';
  private client: Anthropic;

  constructor(apiKey: string, endpoint?: string) {
    this.client = new Anthropic({
      apiKey,
      baseURL: endpoint,
    });
  }

  async generateResponse(prompt: string, context?: string): Promise<string> {
    const systemPrompt = context 
      ? `Context: ${context}\n\nPlease provide a helpful response to the following request.`
      : 'Please provide a helpful response to the following request.';

    try {
      const response = await this.client.messages.create({
        model: 'claude-3-5-sonnet-20241022',
        max_tokens: 4096,
        system: systemPrompt,
        messages: [
          {
            role: 'user',
            content: prompt,
          },
        ],
      });

      return response.content[0]?.type === 'text' 
        ? response.content[0].text 
        : 'No response generated';
    } catch (error) {
      throw new Error(`Anthropic API error: ${error}`);
    }
  }

  async analyzeCode(code: string, filePath?: string): Promise<CodeAnalysis> {
    const analysisPrompt = `Please analyze the following code and provide:
1. Any issues (errors, warnings, or potential problems)
2. Suggestions for improvement
3. A brief summary of the code

${filePath ? `File: ${filePath}` : ''}

Code:
\`\`\`
${code}
\`\`\`

Please format your response as JSON with the structure:
{
  "issues": [{"severity": "error|warning|info", "message": "description", "line": number}],
  "suggestions": [{"type": "refactor|optimization|style|security", "message": "description", "line": number}],
  "summary": "brief summary of the code"
}`;

    try {
      const response = await this.generateResponse(analysisPrompt);
      
      try {
        const parsed = JSON.parse(response);
        return {
          issues: parsed.issues?.map((issue: any) => ({
            severity: issue.severity || 'info',
            message: issue.message,
            line: issue.line,
            file: filePath,
          })) || [],
          suggestions: parsed.suggestions?.map((suggestion: any) => ({
            type: suggestion.type || 'refactor',
            message: suggestion.message,
            line: suggestion.line,
            file: filePath,
          })) || [],
          summary: parsed.summary || 'Code analysis completed',
        };
      } catch (parseError) {
        return {
          issues: [],
          suggestions: [],
          summary: response,
        };
      }
    } catch (error) {
      throw new Error(`Code analysis failed: ${error}`);
    }
  }
}