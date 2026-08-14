import httpx
import base64
import json
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.pat = settings.GITHUB_PAT
        self.repo = settings.GITHUB_TARGET_REPO
        self.base_url = "https://api.github.com"
        self.file_path = "community-trial.json"

    async def push_manifest(self, manifest_data: dict) -> bool:
        if not self.pat:
            logger.warning("GITHUB_PAT is not configured. Skipping manifest push.")
            return False

        headers = {
            "Authorization": f"Bearer {self.pat}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        file_url = f"{self.base_url}/repos/{self.repo}/contents/{self.file_path}"
        
        async with httpx.AsyncClient() as client:
            # First, try to get the file to retrieve its SHA
            get_response = await client.get(file_url, headers=headers)
            sha = None
            if get_response.status_code == 200:
                sha = get_response.json().get("sha")

            # Prepare the payload
            content_str = json.dumps(manifest_data, indent=2)
            content_b64 = base64.b64encode(content_str.encode("utf-8")).decode("utf-8")

            payload = {
                "message": "chore: Update community trial manifest",
                "content": content_b64,
                "branch": "main"
            }
            if sha:
                payload["sha"] = sha

            put_response = await client.put(file_url, headers=headers, json=payload)
            if put_response.status_code in (200, 201):
                logger.info(f"Successfully pushed {self.file_path} to {self.repo}")
                return True
            else:
                logger.error(f"Failed to push {self.file_path} to GitHub: {put_response.text}")
                return False
