import { useState, useEffect } from 'react';
import './AnalysisProgress.css';

export default function AnalysisProgress() {
    const [currentStage, setCurrentStage] = useState(0);
    const [progress, setProgress] = useState(0);

    const stages = [
        { id: 1, name: 'Stage 1: Collecting', description: 'Reading project files and structure...', duration: 12000 },
        { id: 2, name: 'Stage 2: Ranking', description: 'Analyzing and prioritizing files...', duration: 12000 },
        { id: 3, name: 'Stage 3: Generating', description: 'Creating comprehensive report...', duration: 12000 },
    ];

    useEffect(() => {
        let stageTimer;
        let progressTimer;
        let progressValue = 0;

        const startStage = (stageIndex) => {
            if (stageIndex >= stages.length) {
                // Loop back to the beginning
                setCurrentStage(0);
                setProgress(0);
                startStage(0);
                return;
            }

            setCurrentStage(stageIndex);
            progressValue = 0;
            setProgress(0);

            const stageDuration = stages[stageIndex].duration;
            const progressIncrement = 100 / (stageDuration / 100); // Update every 100ms

            progressTimer = setInterval(() => {
                progressValue += progressIncrement;
                if (progressValue >= 100) {
                    progressValue = 100;
                    clearInterval(progressTimer);
                }
                setProgress(Math.min(progressValue, 100));
            }, 100);

            stageTimer = setTimeout(() => {
                clearInterval(progressTimer);
                startStage(stageIndex + 1);
            }, stageDuration);
        };

        startStage(0);

        return () => {
            clearTimeout(stageTimer);
            clearInterval(progressTimer);
        };
    }, []);

    const currentStageData = stages[currentStage];

    return (
        <div className="analysis-progress">
            <div className="progress-header">
                <div className="progress-icon">⚙️</div>
                <h2 className="progress-title">Analysis in Progress</h2>
            </div>

            <div className="stage-info">
                <div className="stage-name">{currentStageData.name}</div>
                <div className="stage-description">{currentStageData.description}</div>
            </div>

            <div className="progress-bar-container">
                <div className="progress-bar" style={{ width: `${progress}%` }}>
                    <div className="progress-shimmer"></div>
                </div>
            </div>

            <div className="progress-percentage">{Math.round(progress)}%</div>

            <div className="stage-indicators">
                {stages.map((stage, index) => (
                    <div
                        key={stage.id}
                        className={`stage-indicator ${index === currentStage ? 'active' : ''} ${index < currentStage ? 'completed' : ''
                            }`}
                    >
                        <div className="indicator-dot"></div>
                        <div className="indicator-label">Stage {stage.id}</div>
                    </div>
                ))}
            </div>
        </div>
    );
}
