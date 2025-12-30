
import asyncio
import httpx
from services.nango_service import nango_service

async def test_jira():
    connection_id = "user-2"
    cloud_id = await nango_service.get_cloud_id(connection_id)
    
    print(f"Testing with Cloud ID: {cloud_id}")
    
    endpoints = [
        f"/ex/jira/{cloud_id}/rest/api/3/myself",
        f"/ex/jira/{cloud_id}/rest/api/3/project/search",
        f"/ex/jira/{cloud_id}/rest/api/3/search/jql?jql=created is not null&maxResults=1"
    ]
    
    for endpoint in endpoints:
        print(f"\nTesting endpoint: {endpoint}")
        try:
            res = await nango_service.proxy_get(connection_id, endpoint)
            print(f"SUCCESS: {str(res)[:100]}...")
        except httpx.HTTPStatusError as e:
            print(f"FAILED (HTTP {e.response.status_code}): {e.response.text}")
        except Exception as e:
            print(f"ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_jira())
