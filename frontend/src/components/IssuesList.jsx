import React from 'react';
import { ExternalLink, Clock, User, Tag } from 'lucide-react';

const IssuesList = ({ issues, loading }) => {
    if (loading) {
        return (
            <div className="grid" style={{ padding: '2rem', textAlign: 'center' }}>
                <p style={{ color: 'var(--text-secondary)' }}>Loading issues...</p>
            </div>
        );
    }

    if (!issues || issues.length === 0) {
        return (
            <div className="card" style={{ padding: '3rem', textAlign: 'center', borderStyle: 'dashed' }}>
                <p style={{ color: 'var(--text-secondary)' }}>No issues found in this project.</p>
            </div>
        );
    }

    const getStatusColor = (status) => {
        const s = status.toLowerCase();
        if (s.includes('done') || s.includes('resolved')) return '#10b981';
        if (s.includes('progress')) return '#3b82f6';
        if (s.includes('todo') || s.includes('open')) return '#94a3b8';
        return '#f59e0b';
    };

    return (
        <div className="grid">
            {issues.map((issue) => (
                <div key={issue.id} className="card" style={{ transition: 'transform 0.2s' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '1rem' }}>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)', fontWeight: 'bold' }}>{issue.key}</span>
                        <div
                            style={{
                                fontSize: '0.75rem',
                                padding: '2px 8px',
                                borderRadius: '4px',
                                background: `${getStatusColor(issue.status)}20`,
                                color: getStatusColor(issue.status),
                                border: `1px solid ${getStatusColor(issue.status)}`
                            }}
                        >
                            {issue.status}
                        </div>
                    </div>

                    <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem' }}>{issue.summary}</h3>

                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '1rem', marginTop: 'auto' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                            <Tag size={14} />
                            {issue.issueType}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                            <User size={14} />
                            {issue.assignee || 'Unassigned'}
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--text-secondary)', fontSize: '0.8rem' }}>
                            <Clock size={14} />
                            {new Date(issue.createdAt).toLocaleDateString()}
                        </div>
                        <a
                            href={issue.webUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--primary)', fontSize: '0.8rem', marginLeft: 'auto', textDecoration: 'none' }}
                        >
                            <ExternalLink size={14} />
                            Jira
                        </a>
                    </div>
                </div>
            ))}
        </div>
    );
};

export default IssuesList;
