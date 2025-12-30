import React, { useState, useEffect } from 'react';
import { X, PlusCircle, AlertCircle } from 'lucide-react';
import { jiraApi } from '../services/api';

const CreateIssueModal = ({ isOpen, onClose, connectionId, projects, onIssueCreated }) => {
    const [formData, setFormData] = useState({
        projectKey: '',
        summary: '',
        description: '',
        issueType: 'Task'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    useEffect(() => {
        if (projects && projects.length > 0 && !formData.projectKey) {
            setFormData(prev => ({ ...prev, projectKey: projects[0].key }));
        }
    }, [projects]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            await jiraApi.createIssue(connectionId, formData);
            onIssueCreated();
            onClose();
            setFormData({
                projectKey: projects[0].key,
                summary: '',
                description: '',
                issueType: 'Task'
            });
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to create issue');
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <div className="modal-overlay">
            <div className="card modal-content">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ fontSize: '1.25rem' }}>Create New Issue</h2>
                    <button onClick={onClose} className="button button-outline" style={{ padding: '4px' }}>
                        <X size={20} />
                    </button>
                </div>

                {error && (
                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)', padding: '1rem', borderRadius: '8px', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                        <AlertCircle size={16} />
                        {error}
                    </div>
                )}

                <form onSubmit={handleSubmit} className="grid">
                    <div>
                        <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Project</label>
                        <select
                            className="input-field"
                            value={formData.projectKey}
                            onChange={(e) => setFormData(prev => ({ ...prev, projectKey: e.target.value }))}
                            required
                        >
                            {projects.map(p => <option key={p.id} value={p.key}>{p.name} ({p.key})</option>)}
                        </select>
                    </div>

                    <div>
                        <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Summary</label>
                        <input
                            className="input-field"
                            value={formData.summary}
                            onChange={(e) => setFormData(prev => ({ ...prev, summary: e.target.value }))}
                            placeholder="What needs to be done?"
                            required
                        />
                    </div>

                    <div>
                        <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Description</label>
                        <textarea
                            className="input-field"
                            value={formData.description}
                            onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
                            placeholder="Add more details..."
                            rows={4}
                        />
                    </div>

                    <div style={{ marginTop: '1rem', display: 'flex', gap: '1rem' }}>
                        <button type="button" onClick={onClose} className="button button-outline" style={{ flex: 1 }}>Cancel</button>
                        <button type="submit" className="button button-primary" style={{ flex: 2 }} disabled={loading}>
                            <PlusCircle size={20} />
                            {loading ? 'Creating...' : 'Create Issue'}
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
};

export default CreateIssueModal;
