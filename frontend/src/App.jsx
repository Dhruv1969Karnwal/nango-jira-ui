import React, { useState, useEffect, useCallback } from 'react';
import { RefreshCw, Plus, Search, Filter, LogOut } from 'lucide-react';
import Header from './components/Header';
import AuthScreen from './components/AuthScreen';
import IssuesList from './components/IssuesList';
import CreateIssueModal from './components/CreateIssueModal';
import { jiraApi } from './services/api';

function App() {
    const [connectionId, setConnectionId] = useState(localStorage.getItem('nango_connection_id'));
    const [connectionStatus, setConnectionStatus] = useState(null);
    const [projects, setProjects] = useState([]);
    const [issues, setIssues] = useState([]);
    const [loading, setLoading] = useState(true);
    const [issuesLoading, setIssuesLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [selectedProject, setSelectedProject] = useState('');
    const [searchQuery, setSearchQuery] = useState('');

    const handleLogin = (id) => {
        localStorage.setItem('nango_connection_id', id);
        setConnectionId(id);
    };

    const handleLogout = useCallback(() => {
        localStorage.removeItem('nango_connection_id');
        setConnectionId(null);
        setConnectionStatus(null);
        setProjects([]);
        setIssues([]);
    }, []);

    const fetchConnectionStatus = useCallback(async () => {
        if (!connectionId) return null;
        try {
            const { data } = await jiraApi.getConnectionStatus(connectionId);
            setConnectionStatus(data);
            if (!data.connected) {
                handleLogout();
            }
            return data;
        } catch (error) {
            console.error('Failed to fetch status:', error);
            handleLogout();
            return null;
        }
    }, [connectionId, handleLogout]);

    const fetchProjects = useCallback(async () => {
        if (!connectionId) return;
        try {
            const { data } = await jiraApi.getProjects(connectionId);
            setProjects(data);
            if (data.length > 0 && !selectedProject) {
                setSelectedProject(data[0].key);
            }
        } catch (error) {
            console.error('Failed to fetch projects:', error);
        }
    }, [connectionId, selectedProject]);

    const fetchIssues = useCallback(async () => {
        if (!connectionId || !connectionStatus?.connected) return;

        setIssuesLoading(true);
        try {
            const params = {};
            if (selectedProject) params.project_key = selectedProject;
            if (searchQuery) params.jql = `summary ~ "${searchQuery}"`;

            const { data } = await jiraApi.getIssues(connectionId, params);
            setIssues(data);
        } catch (error) {
            console.error('Failed to fetch issues:', error);
        } finally {
            setIssuesLoading(false);
        }
    }, [connectionId, connectionStatus, selectedProject, searchQuery]);

    const init = useCallback(async () => {
        if (!connectionId) {
            setLoading(false);
            return;
        }

        setLoading(true);
        const status = await fetchConnectionStatus();
        if (status?.connected) {
            await fetchProjects();
        }
        setLoading(false);
    }, [connectionId, fetchConnectionStatus, fetchProjects]);

    useEffect(() => {
        init();
    }, [init]);

    useEffect(() => {
        if (connectionId && connectionStatus?.connected) {
            fetchIssues();
        }
    }, [connectionId, connectionStatus, selectedProject, fetchIssues]);

    if (loading && connectionId) {
        return (
            <div style={{ height: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                <RefreshCw className="animate-spin" size={32} />
                <span style={{ marginLeft: '1rem' }}>Restoring your session...</span>
            </div>
        );
    }

    return (
        <div className="app-container">
            <Header connectionStatus={connectionStatus} />

            {!connectionId || !connectionStatus?.connected ? (
                <AuthScreen onLogin={handleLogin} />
            ) : (
                <main>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                        <div>
                            <h2 style={{ fontSize: '1.5rem' }}>Dashboard</h2>
                            <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Connection ID: <code style={{ background: 'rgba(255,255,255,0.1)', padding: '2px 4px', borderRadius: '4px' }}>{connectionId}</code></p>
                        </div>
                        <button className="button button-outline" onClick={handleLogout} style={{ color: 'var(--error)', borderColor: 'rgba(239, 68, 68, 0.2)' }}>
                            <LogOut size={18} />
                            Disconnect
                        </button>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
                        <div style={{ display: 'flex', gap: '1rem', flex: 1 }}>
                            <div style={{ position: 'relative', flex: 1, maxWidth: '400px' }}>
                                <Search size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                                <input
                                    className="input-field"
                                    placeholder="Search issues..."
                                    style={{ paddingLeft: '40px' }}
                                    value={searchQuery}
                                    onChange={(e) => setSearchQuery(e.target.value)}
                                    onKeyDown={(e) => e.key === 'Enter' && fetchIssues()}
                                />
                            </div>
                            <div style={{ position: 'relative', width: '200px' }}>
                                <Filter size={18} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} />
                                <select
                                    className="input-field"
                                    style={{ paddingLeft: '40px' }}
                                    value={selectedProject}
                                    onChange={(e) => setSelectedProject(e.target.value)}
                                >
                                    <option value="">All Projects</option>
                                    {projects.map(p => <option key={p.id} value={p.key}>{p.name}</option>)}
                                </select>
                            </div>
                        </div>

                        <button className="button button-primary" onClick={() => setIsModalOpen(true)}>
                            <Plus size={20} />
                            Create Issue
                        </button>
                    </div>

                    <div style={{ marginBottom: '1rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <h2 style={{ fontSize: '1.25rem' }}>
                            {selectedProject ? `Issues for ${projects.find(p => p.key === selectedProject)?.name}` : 'Recent Issues'}
                        </h2>
                        <button
                            className="button button-outline"
                            style={{ padding: '8px' }}
                            onClick={fetchIssues}
                            disabled={issuesLoading}
                        >
                            <RefreshCw size={18} className={issuesLoading ? 'animate-spin' : ''} />
                        </button>
                    </div>

                    <IssuesList issues={issues} loading={issuesLoading} />
                </main>
            )}

            {connectionId && (
                <CreateIssueModal
                    isOpen={isModalOpen}
                    onClose={() => setIsModalOpen(false)}
                    connectionId={connectionId}
                    projects={projects}
                    onIssueCreated={fetchIssues}
                />
            )}

            <footer style={{ marginTop: '4rem', textAlign: 'center', padding: '2rem', color: 'var(--text-secondary)', borderTop: '1px solid var(--border)', fontSize: '0.875rem' }}>
                Built with Nango & FastAPI • {new Date().getFullYear()}
            </footer>

            <style>
                {`
          .animate-spin {
            animation: spin 1s linear infinite;
          }
          @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
          }
        `}
            </style>
        </div>
    );
}

export default App;
