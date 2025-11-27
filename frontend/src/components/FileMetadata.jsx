import './FileMetadata.css';

export default function FileMetadata({ metadata }) {
    // Use placeholder data if metadata is null
    const data = metadata || {
        files_read: 0,
        total_size_mb: '0.00',
        files_skipped: 0,
    };

    return (
        <div className="file-metadata">
            <h3 className="metadata-title">📊 Project Analysis Summary</h3>
            <div className="metadata-grid">
                <div className="metadata-card">
                    <div className="metadata-icon">📁</div>
                    <div className="metadata-content">
                        <div className="metadata-label">Files Analyzed</div>
                        <div className="metadata-value">{data.files_read}</div>
                    </div>
                </div>

                <div className="metadata-card">
                    <div className="metadata-icon">💾</div>
                    <div className="metadata-content">
                        <div className="metadata-label">Total Size</div>
                        <div className="metadata-value">{data.total_size_mb} MB</div>
                    </div>
                </div>

                <div className="metadata-card">
                    <div className="metadata-icon">⏭️</div>
                    <div className="metadata-content">
                        <div className="metadata-label">Files Skipped</div>
                        <div className="metadata-value">{data.files_skipped}</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
