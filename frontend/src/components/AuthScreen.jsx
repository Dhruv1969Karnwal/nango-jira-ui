import React, { useState } from 'react';
import { LogIn, PlusCircle, AlertCircle, Share2, Key } from 'lucide-react';
import nango from '../services/nango';
import { jiraApi } from '../services/api';

const AuthScreen = ({ onLogin }) => {
    const [existingId, setExistingId] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleExistingConnect = async (e) => {
        e.preventDefault();
        if (!existingId.trim()) return;

        setLoading(true);
        setError(null);
        try {
            const { data } = await jiraApi.getConnectionStatus(existingId.trim());
            if (data.connected) {
                onLogin(existingId.trim());
            } else {
                setError('Connection ID not found or inactive. Please connect a new account.');
            }
        } catch (err) {
            setError('Invalid Connection ID. Please check and try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleNewConnect = async () => {
        setLoading(true);
        setError(null);
        try {
            // Generate a unique ID for this new connection
            const newConnId = `user-${Math.random().toString(36).substr(2, 9)}`;

            // Trigger Nango Auth
            await nango.auth('jira', newConnId);

            // Save to MongoDB via our backend
            await jiraApi.saveConnection(newConnId);

            onLogin(newConnId);
        } catch (err) {
            console.error('Auth Error:', err);
            setError('Failed to connect to Jira. ' + (err.response?.data?.detail || err.message));
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{ minHeight: '80vh', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <div className="card" style={{ width: '100%', maxWidth: '450px', padding: '2.5rem' }}>
                <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
                    <div style={{ background: 'var(--primary)', width: '64px', height: '64px', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1.5rem' }}>
                        <Key color="white" size={32} />
                    </div>
                    <h2 style={{ fontSize: '1.75rem', marginBottom: '0.5rem' }}>Jira Integration</h2>
                    <p style={{ color: 'var(--text-secondary)' }}>Connect your Jira workspace to continue</p>
                </div>

                {error && (
                    <div style={{ background: 'rgba(239, 68, 68, 0.1)', color: 'var(--error)', padding: '1rem', borderRadius: '8px', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem', fontSize: '0.875rem' }}>
                        <AlertCircle size={16} />
                        {error}
                    </div>
                )}

                <div className="grid">
                    <form onSubmit={handleExistingConnect}>
                        <label style={{ display: 'block', fontSize: '0.875rem', marginBottom: '0.5rem', color: 'var(--text-secondary)' }}>Returning User?</label>
                        <div style={{ display: 'flex', gap: '0.5rem' }}>
                            <input
                                className="input-field"
                                placeholder="Enter Connection ID"
                                value={existingId}
                                onChange={(e) => setExistingId(e.target.value)}
                                disabled={loading}
                            />
                            <button type="submit" className="button button-outline" style={{ padding: '0.75rem' }} disabled={loading || !existingId}>
                                <LogIn size={20} />
                            </button>
                        </div>
                    </form>

                    <div style={{ display: 'flex', alignItems: 'center', margin: '1rem 0' }}>
                        <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
                        <span style={{ padding: '0 1rem', fontSize: '0.75rem', color: 'var(--text-secondary)', textTransform: 'uppercase' }}>OR</span>
                        <div style={{ flex: 1, height: '1px', background: 'var(--border)' }}></div>
                    </div>

                    <button
                        onClick={handleNewConnect}
                        className="button button-primary"
                        style={{ width: '100%' }}
                        disabled={loading}
                    >
                        <Share2 size={20} />
                        {loading ? 'Connecting...' : 'Connect New Jira Account'}
                    </button>
                </div>

                <p style={{ marginTop: '2rem', fontSize: '0.75rem', color: 'var(--text-secondary)', textAlign: 'center' }}>
                    By connecting, you agree to allow this app to access your Jira projects and issues via Nango.
                </p>
            </div>
        </div>
    );
};

export default AuthScreen;
