import React, { useState } from 'react';
import Nango from '@nangohq/frontend';

// Initialize Nango
const nango = new Nango({
  publicKey: 'e8b41b7f-03ad-4c06-be46-00ce9a415038', // 'dev' environment key
  host: 'https://app.nango.codemateai.dev'
});

function App() {
  const [status, setStatus] = useState('Not connected');

  const connectJira = async () => {
    try {
      setStatus('Connecting...');
      // 'jira' must match the "Unique Key" in Nango Dashboard
      await nango.auth('jira', 'user-2');
      setStatus('Connected Successfully!');
    } catch (error) {
      console.error(error);
      setStatus('Failed: ' + error.message);
    }
  };

  return (
    <div style={{ padding: 50 }}>
      <h1>Nango Integration Test</h1>
      <p>Status: {status}</p>
      <button onClick={connectJira} style={{ padding: '10px 20px', fontSize: 20 }}>
        Connect Jira
      </button>
    </div>
  );
}

export default App;