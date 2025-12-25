import httpx
from bs4 import BeautifulSoup
from langchain_core.documents import Document

class ScraperService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    async def scrape_url(self, url: str) -> str:
        """
        Fetches the content of a URL and returns the clean text. 
        Uses httpx for async fetching and BeautifulSoup for parsing.
        """
        try:
            async with httpx.AsyncClient(follow_redirects=True) as client:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                response.raise_for_status()
                
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Extract clean text with separators
            text = soup.get_text(separator="\n", strip=True)
            return text
            
        except httpx.HTTPError as e:
            return f"Error scraping {url}: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
