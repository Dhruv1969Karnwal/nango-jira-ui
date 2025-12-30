import React from 'react';
import { Layout, CheckCircle2, XCircle } from 'lucide-react';

const Header = ({ connectionStatus }) => {
    return (
        <header className="card" style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{ background: 'var(--primary)', padding: '8px', borderRadius: '8px' }}>
                    <Layout color="white" size={24} />
                </div>
                <div>
                    <h1 style={{ fontSize: '1.25rem' }}>Nango Jira Manager</h1>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>Production-grade Jira Integration</p>
                </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                {connectionStatus && (
                    <div className={`status-badge ${connectionStatus.connected ? 'status-connected' : 'status-disconnected'}`} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        {connectionStatus.connected ? <CheckCircle2 size={12} /> : <XCircle size={12} />}
                        {connectionStatus.connected ? 'Jira Connected' : 'Not Connected'}
                    </div>
                )}
                {connectionStatus?.connected && connectionStatus?.userName && (
                    <div style={{ textAlign: 'right' }}>
                        <p style={{ fontSize: '0.875rem', fontWeight: '600' }}>{connectionStatus.userName}</p>
                        <p style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>{connectionStatus.userEmail}</p>
                    </div>
                )}
            </div>
        </header>
    );
};

export default Header;
