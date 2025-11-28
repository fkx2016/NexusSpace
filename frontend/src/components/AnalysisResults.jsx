import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import FileMetadata from './FileMetadata';
import './AnalysisResults.css';

export default function AnalysisResults({ stage1, stage2, stage3, metadata }) {
    const [activeTab, setActiveTab] = useState('stage1');

    // Extract file metadata if available
    const fileMetadata = metadata?.file_analysis || null;

    const handlePrint = () => {
        console.log("ACTION: Printing Synthesis Report...");
        window.print();
    };

    const handleEmail = () => {
        const subject = encodeURIComponent(`NexusSpace Analysis Report: ${metadata?.source_path || 'Untitled Project'}`);
        const bodyContent = `
--- Analysis Context ---
Source: ${metadata?.source_path || 'N/A'}
Provider: ${metadata?.llm_provider || 'N/A'}
Timestamp: ${new Date().toLocaleString()}

--- Chairman's Synthesis ---
(Please view the full report in the NexusSpace application for details.)

Note: Please view the full report in the NexusSpace application for details.
`.trim();
        const body = encodeURIComponent(bodyContent);
        window.location.href = `mailto:?subject=${subject}&body=${body}`;
    };

    const handleExport = () => {
        console.log("ACTION: Exporting to Google Drive (Future Feature)...");
        alert(
            "Google Drive Export requires dedicated OAuth integration and a backend service. \n\nThis feature is planned for NexusSpace V2.0 Enterprise Tier."
        );
    };

    return (
        <div className="analysis-results">
            <div className="report-header">
                <div className="report-meta-item">
                    <span className="report-label">Source Path:</span>
                    <span className="report-value">
                        {metadata?.source_path === '.'
                            ? 'Current Project Directory (Self-Analysis)'
                            : (metadata?.source_path || 'Not Available')}
                    </span>
                </div>
            </div>

            <FileMetadata metadata={fileMetadata} />

            <div className="results-container">
                <div className="tabs-header">
                    <button
                        className={`tab-button ${activeTab === 'stage1' ? 'active' : ''}`}
                        onClick={() => setActiveTab('stage1')}
                    >
                        <span className="tab-icon">📋</span>
                        <span className="tab-label">Stage 1: Requests</span>
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'stage2' ? 'active' : ''}`}
                        onClick={() => setActiveTab('stage2')}
                    >
                        <span className="tab-icon">📊</span>
                        <span className="tab-label">Stage 2: Rankings</span>
                    </button>
                    <button
                        className={`tab-button ${activeTab === 'stage3' ? 'active' : ''}`}
                        onClick={() => setActiveTab('stage3')}
                    >
                        <span className="tab-icon">📄</span>
                        <span className="tab-label">Stage 3: Report</span>
                    </button>
                </div>

                <div className="tab-content">
                    {activeTab === 'stage1' && (
                        <div className="tab-panel">
                            <h2 className="panel-title">Stage 1: Initial Requests</h2>
                            {stage1 ? (
                                <div className="stage-content">
                                    <pre className="stage-output">{JSON.stringify(stage1, null, 2)}</pre>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-icon">📋</div>
                                    <p>No Stage 1 data available yet.</p>
                                    <p className="empty-hint">Run an analysis to see initial requests.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'stage2' && (
                        <div className="tab-panel">
                            <h2 className="panel-title">Stage 2: File Rankings</h2>
                            {stage2 ? (
                                <div className="stage-content">
                                    <pre className="stage-output">{JSON.stringify(stage2, null, 2)}</pre>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-icon">📊</div>
                                    <p>No Stage 2 data available yet.</p>
                                    <p className="empty-hint">Run an analysis to see file rankings.</p>
                                </div>
                            )}
                        </div>
                    )}

                    {activeTab === 'stage3' && (
                        <div className="tab-panel">
                            <h2 className="panel-title">Stage 3: Final Report</h2>
                            <div className="report-actions" style={{
                                display: 'flex',
                                gap: '10px',
                                marginTop: '15px',
                                padding: '10px 0',
                                borderTop: '1px solid #333'
                            }}>
                                <button className="action-button print-button" onClick={handlePrint}>
                                    Print 🖨️
                                </button>
                                <button className="action-button email-button" onClick={handleEmail}>
                                    Email ✉️
                                </button>
                                <button className="action-button export-button" onClick={handleExport}>
                                    Export to Drive ☁️
                                </button>
                            </div>
                            {stage3 ? (
                                <div className="stage-content markdown-display-container">
                                    <ReactMarkdown>{stage3.response}</ReactMarkdown>
                                </div>
                            ) : (
                                <div className="empty-state">
                                    <div className="empty-icon">📄</div>
                                    <p>No Stage 3 data available yet.</p>
                                    <p className="empty-hint">Run an analysis to see the final report.</p>
                                </div>
                            )}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
