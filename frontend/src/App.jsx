import { useState } from 'react';
import AnalysisSidebar from './components/AnalysisSidebar';
import AnalysisProgress from './components/AnalysisProgress';
import AnalysisResults from './components/AnalysisResults';
import { api } from './api';
import './App.css';

function App() {
  // Analysis state
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);

  const handleAnalyzeClick = async () => {
    setIsAnalyzing(true);
    setAnalysisError(null);
    setAnalysisResult(null);

    try {
      // Call the analyze-project endpoint
      const result = await api.analyzeProject(".");

      // Store the results
      setAnalysisResult(result);
    } catch (error) {
      console.error('Failed to analyze project:', error);
      setAnalysisError(error.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Extract file metadata for sidebar if available
  const fileMetadata = analysisResult?.metadata?.file_analysis || null;

  return (
    <div className="app">
      <AnalysisSidebar
        onAnalyzeProject={handleAnalyzeClick}
        isLoading={isAnalyzing}
        fileMetadata={fileMetadata}
      />

      <main className="main-content">
        {isAnalyzing && <AnalysisProgress />}

        {!isAnalyzing && analysisError && (
          <div className="error-container">
            <div className="error-icon">⚠️</div>
            <h2 className="error-title">Analysis Failed</h2>
            <p className="error-message">{analysisError}</p>
            <button className="retry-button" onClick={handleAnalyzeClick}>
              Try Again
            </button>
          </div>
        )}

        {!isAnalyzing && !analysisError && analysisResult && (
          <AnalysisResults
            stage1={analysisResult.stage1}
            stage2={analysisResult.stage2}
            stage3={analysisResult.stage3}
            metadata={analysisResult.metadata}
          />
        )}

        {!isAnalyzing && !analysisError && !analysisResult && (
          <div className="welcome-container">
            <div className="welcome-icon">🚀</div>
            <h1 className="welcome-title">Welcome to NexusSpace</h1>
            <p className="welcome-subtitle">Code Analysis Dashboard</p>
            <p className="welcome-description">
              Click the <strong>"Analyze Project"</strong> button in the sidebar to begin
              analyzing your codebase. NexusSpace will read your project files,
              rank them by importance, and generate a comprehensive analysis report.
            </p>
            <div className="welcome-features">
              <div className="feature-item">
                <span className="feature-icon">📁</span>
                <span className="feature-text">Automatic file discovery</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span className="feature-text">Intelligent ranking</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📄</span>
                <span className="feature-text">Detailed reports</span>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}

export default App;
