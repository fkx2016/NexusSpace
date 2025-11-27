import { useState } from 'react';
import AnalysisSidebar from './components/AnalysisSidebar';
import ChatInterface from './components/ChatInterface';
import { api } from './api';
import './App.css';

function App() {
  // Analysis state
  const [analysisResult, setAnalysisResult] = useState(null);
  const [fileMetadata, setFileMetadata] = useState(null);
  const [analysisError, setAnalysisError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleAnalyzeProject = async () => {
    setIsLoading(true);
    setAnalysisError(null);
    setAnalysisResult(null);
    setFileMetadata(null);

    try {
      // Call the new analyze-project endpoint
      // Hardcoded to analyze current directory for Phase 1
      const result = await api.analyzeProject(".", null);

      // Store the results
      setAnalysisResult({
        stage1: result.stage1,
        stage2: result.stage2,
        stage3: result.stage3,
        metadata: result.metadata,
      });

      // Store file metadata separately for easy access
      if (result.metadata && result.metadata.file_analysis) {
        setFileMetadata(result.metadata.file_analysis);
      }
    } catch (error) {
      console.error('Failed to analyze project:', error);
      setAnalysisError(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <AnalysisSidebar
        onAnalyzeProject={handleAnalyzeProject}
        isLoading={isLoading}
        fileMetadata={fileMetadata}
      />
      <ChatInterface
        analysisResult={analysisResult}
        analysisError={analysisError}
        isLoading={isLoading}
      />
    </div>
  );
}

export default App;
