import './AnalysisSidebar.css';

export default function AnalysisSidebar({
    onAnalyzeProject,
    isLoading,
    fileMetadata,
}) {
    return (
        <div className="sidebar">
            <div className="sidebar-header">
                <h1>NexusSpace</h1>
                <p className="subtitle">Code Analysis Dashboard</p>
                <button
                    className="new-conversation-btn analyze-btn"
                    onClick={onAnalyzeProject}
                    disabled={isLoading}
                >
                    {isLoading ? '⏳ Analyzing...' : '🔍 Analyze Project'}
                </button>
            </div>

            {fileMetadata && (
                <div className="project-info">
                    <h3>Project Info</h3>
                    <div className="info-item">
                        <span className="info-label">📁 Files Analyzed:</span>
                        <span className="info-value">{fileMetadata.files_read}</span>
                    </div>
                    <div className="info-item">
                        <span className="info-label">📊 Total Size:</span>
                        <span className="info-value">{fileMetadata.total_size_mb} MB</span>
                    </div>
                    {fileMetadata.files_skipped > 0 && (
                        <div className="info-item">
                            <span className="info-label">⏭️ Files Skipped:</span>
                            <span className="info-value">{fileMetadata.files_skipped}</span>
                        </div>
                    )}
                    <div className="info-item">
                        <span className="info-label">✅ Status:</span>
                        <span className="info-value">Complete</span>
                    </div>
                </div>
            )}
        </div>
    );
}
