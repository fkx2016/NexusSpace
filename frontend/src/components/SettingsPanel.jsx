import React, { useState, useEffect } from 'react';
import { nexusApi } from '../api';
import './SettingsPanel.css';

const SettingsPanel = () => {
    const [provider, setProvider] = useState('');
    const [loading, setLoading] = useState(true);
    const [status, setStatus] = useState('');

    useEffect(() => {
        // Fetch current settings on component load
        fetchSettings();
    }, []);

    const fetchSettings = async () => {
        setLoading(true);
        setStatus('');
        try {
            const settings = await nexusApi.getSettings();
            setProvider(settings.llm_provider || 'openrouter'); // Default to openrouter if unset
        } catch (error) {
            console.error("Failed to fetch settings:", error);
            setStatus('Error loading settings.');
            setProvider('openrouter');
        } finally {
            setLoading(false);
        }
    };

    const handleProviderChange = (event) => {
        setProvider(event.target.value);
    };

    const handleSave = async () => {
        setLoading(true);
        setStatus('Saving...');
        try {
            await nexusApi.updateSettings({ llm_provider: provider });
            setStatus('Settings saved successfully! Backend provider switched.');
        } catch (error) {
            console.error("Failed to save settings:", error);
            setStatus(`Error saving: ${error.message}`);
        } finally {
            setLoading(false);
        }
    };

    const providerOptions = [
        { value: 'openrouter', label: 'Cloud AI (OpenRouter) - Requires API Key' },
        { value: 'ollama', label: 'Local AI (Ollama/Local Host) - Free/Private' },
    ];

    if (loading) {
        return <div className="settings-panel">Loading Settings...</div>;
    }

    return (
        <div className="settings-panel">
            <h2>⚙️ Provider Settings</h2>
            <div className="setting-row">
                <label htmlFor="llm-provider">LLM Provider:</label>
                <select
                    id="llm-provider"
                    value={provider}
                    onChange={handleProviderChange}
                >
                    {providerOptions.map(option => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                    ))}
                </select>
            </div>
            <button onClick={handleSave} disabled={loading || status.includes('Saving')}>
                Save Provider Setting
            </button>
            {status && <p className={`status-message ${status.includes('Error') ? 'error' : 'success'}`}>{status}</p>}

            <p className="note">NOTE: This requires **STORAGE_BACKEND=database** to persist settings.</p>
        </div>
    );
};

export default SettingsPanel;
