/**
 * API client for NexusSpace backend.
 */


const API_BASE = 'http://localhost:8001';

export const api = {
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

    // Only include analysis_prompt if provided
    if (analysisPrompt) {
      requestBody.analysis_prompt = analysisPrompt;
    }

    const response = await fetch(`${API_BASE}/api/analyze-project`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(requestBody),
    });

    if (!response.ok) {
      // Try to extract error detail from response
      let errorMessage = 'Failed to analyze project';
      try {
        const errorData = await response.json();
        if (errorData.detail) {
          errorMessage = errorData.detail;
        }
      } catch (e) {
        // If we can't parse the error, use the status text
        errorMessage = `Failed to analyze project: ${response.statusText}`;
      }
      throw new Error(errorMessage);
    }

    return response.json();
  },
};
