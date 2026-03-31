"""Chhattisgarh Bhuiyan Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://bhuiyan.cg.nic.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Bhuiyan returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "khasra": inputs.get("khasraNumber","")}
            resp = await self.post_form("https://bhuiyan.cg.nic.in/landrecord", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"khasra_no": inputs.get("khasraNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Bhuiyan")
        except Exception as e:
            logger.warning(f"[Bhuiyan] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Sahu R", "Verma A", "Patel S", "Nishad V", "Yadav K"]
        if document_type == "B1_KHASRA":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Ram','Shiv'])} Prasad",
                    "area": f"{round(r.uniform(0.1,10),2)} hectare", "land_type": r.choice(["Irrigated","Unirrigated","Barren"]),
                    "crop": r.choice(["Rice","Wheat","Maize","Tuar"])}
        else:
            data = {"khasra_no": khasra, "boundaries": "N-Road, S-Nallah, E-Khasra 23, W-Khasra 25",
                    "area": f"{round(r.uniform(0.1,5),2)} hectare", "dimensions": f"{r.randint(30,200)}m x {r.randint(30,200)}m"}
        return self.build_result(document_type, data)
