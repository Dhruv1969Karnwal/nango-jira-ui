import { Nango } from '@nangohq/node';

const nango = new Nango({
    secretKey: "8a4e4167-e0ba-4a3e-ab15-3d43139478d1",  // UUID format
    host: "https://app.nango.codemateai.dev"
});

// Use the cloudId from your connection configuration
const cloudId = '6966bf3a-8a8d-48a2-b832-86246698e317';

const res = await nango.get({
    providerConfigKey: 'jira',
    connectionId: 'user-2',
    endpoint: `/ex/jira/${cloudId}/rest/api/3/myself`
});

console.log(res.data);   