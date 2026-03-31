"""UP Bhulekh Scraper - Live httpx + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://upbhulekh.gov.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"UP Bhulekh portal returned {resp.status_code}")
            search_url = "https://upbhulekh.gov.in/public/public_ror/Public_ROR.jsp"
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "khasra": inputs.get("khasraNumber","")}
            resp = await self.post_form(search_url, form_data)
            if resp.status_code == 200 and len(resp.text) > 300:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells:
                        return self.build_result(document_type, {"khasra_no": inputs.get("khasraNumber",""), "district": inputs.get("district",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract data from UP Bhulekh")
        except Exception as e:
            logger.warning(f"[UP Bhulekh] Live scraping failed: {e}")
            raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Sharma R K", "Yadav S P", "Singh A", "Gupta V", "Verma P"]
        if document_type == "KHATAUNI":
            data = {"gata_no": str(r.randint(100,9999)), "khata_no": str(r.randint(1,500)), "khatedar_name": r.choice(owners),
                    "father_name": f"{r.choice(['Ram','Shiv','Hari'])} Prasad", "area_hectare": str(round(r.uniform(0.1,5),3)),
                    "area_sqm": str(r.randint(500,50000)), "remarks": r.choice(["None","Mortgage","Disputed"])}
        else:
            data = {"khasra_no": khasra, "area": f"{round(r.uniform(0.1,5),2)} hectare",
                    "crop": r.choice(["Wheat","Rice","Sugarcane","Mustard"]), "owner_name": r.choice(owners),
                    "land_use": r.choice(["Agricultural","Residential","Barren"])}
        return self.build_result(document_type, data)
