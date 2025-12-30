import React from 'react';
import { Share2 } from 'lucide-react';
import nango from '../services/nango';

const ConnectButton = ({ onConnect, loading }) => {
    const handleConnect = async () => {
        try {
            // 'jira' must match the "Unique Key" in Nango Dashboard
            await nango.auth('jira', 'user-2');
            if (onConnect) onConnect();
        } catch (error) {
            console.error('Nango Auth Error:', error);
            alert('Failed to connect to Jira: ' + error.message);
        }
    };

    return (
        <button
            onClick={handleConnect}
            className="button button-primary"
            disabled={loading}
            style={{ width: '100%', maxWidth: '300px' }}
        >
            <Share2 size={20} />
            {loading ? 'Processing...' : 'Connect Jira Account'}
        </button>
    );
};

export default ConnectButton;
