"""Uttarakhand DevBhoomi Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://devbhoomi.uk.gov.in/")
            if resp.status_code >= 400: raise ConnectionError(f"DevBhoomi returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "khasra": inputs.get("khasraNumber","")}
            resp = await self.post_form("https://devbhoomi.uk.gov.in/LORC/Home", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"khasra_no": inputs.get("khasraNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from DevBhoomi")
        except Exception as e:
            logger.warning(f"[DevBhoomi] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Rawat S", "Negi R", "Bisht A", "Panwar V", "Joshi K"]
        data = {"khata_no": str(r.randint(1,500)), "khasra_no": khasra, "owner_name": r.choice(owners),
                "father_name": f"{r.choice(['Mohan','Kishan','Pratap'])} Singh", "area": f"{round(r.uniform(0.1,10),2)} nali",
                "land_type": r.choice(["Irrigated","Unirrigated","Forest","Barren"])}
        return self.build_result(document_type, data)
