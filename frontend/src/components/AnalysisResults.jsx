import { useState } from 'react';
import FileMetadata from './FileMetadata';
import './AnalysisResults.css';

export default function AnalysisResults({ stage1, stage2, stage3, metadata }) {
    const [activeTab, setActiveTab] = useState('stage1');

    // Extract file metadata if available
    const fileMetadata = metadata?.file_analysis || null;

    return (
        <div className="analysis-results">
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
                            {stage3 ? (
                                <div className="stage-content">
                                    <pre className="stage-output">{JSON.stringify(stage3, null, 2)}</pre>
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
