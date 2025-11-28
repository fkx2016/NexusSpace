/**
 * API client for NexusSpace backend.
 * Uses the VITE_API_BASE_URL environment variable for production readiness.
 */
const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

/**
 * Encapsulates all communication with the NexusSpace backend.
 * This class abstracts away HTTP details, allowing the rest of the
 * frontend application to use simple, clean method calls.
 */
class NexusApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl;
  }

  /**
   * Analyze a local project codebase.
   * @param {string} projectPath - Path to the project directory (default: ".")
   * @param {string|null} analysisPrompt - Optional custom analysis prompt
   * @returns {Promise<Object>} Analysis results with stage1, stage2, stage3, and metadata
   */
  async analyzeProject(projectPath = ".", analysisPrompt = null) {
    const requestBody = {
      project_path: projectPath,
    };

    if (analysisPrompt) {
      requestBody.analysis_prompt = analysisPrompt;
    }

    const response = await fetch(`${this.baseUrl}/api/analyze-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      let errorMessage = 'Failed to analyze project';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch (e) {
        errorMessage = `Failed to analyze project: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  }

  // Placeholder for future methods:
  async getConversation(conversationId) {
    // Implementation for retrieving saved analysis results
    // return this.fetch(`${this.baseUrl}/api/conversations/${conversationId}`);
  }

  async getAllConversations() {
    // Implementation for fetching the list of saved conversations
    // return this.fetch(`${this.baseUrl}/api/conversations/`);
  }

  async getSettings() {
    const response = await fetch(`${this.baseUrl}/api/settings`);
    if (!response.ok) {
      throw new Error(`Failed to fetch settings: ${response.statusText}`);
    }
    return response.json();
  }

  async updateSettings(settings) {
    const response = await fetch(`${this.baseUrl}/api/settings`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ settings }),
    });
    if (!response.ok) {
      let errorDetail = 'Unknown error during update.';
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorDetail;
      } catch {
        errorDetail = response.statusText;
      }
      throw new Error(`Failed to update settings: ${errorDetail}`);
    }
    return response.json();
  }
}

// Instantiate and export the client for the rest of the application to use
export const nexusApi = new NexusApiClient(API_BASE);
