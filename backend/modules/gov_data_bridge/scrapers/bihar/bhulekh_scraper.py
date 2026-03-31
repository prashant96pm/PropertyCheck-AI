"""Bihar Bhu-Lekh Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://lrc.bih.nic.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Bihar LRC returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "zone": inputs.get("zone",""), "circle": inputs.get("circle",""), "mauza": inputs.get("mauzaNumber","")}
            resp = await self.post_form("https://lrc.bih.nic.in/RoR.aspx", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"mauza": inputs.get("mauzaNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Bihar LRC")
        except Exception as e:
            logger.warning(f"[Bihar] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        owners = ["Prasad R", "Kumar S", "Yadav A", "Singh V", "Thakur M"]
        if document_type == "JAMABANDI_NAKAL":
            data = {"khata_no": str(r.randint(1,500)), "khesra_no": str(r.randint(1,999)), "raiyat_name": r.choice(owners),
                    "father_name": f"{r.choice(['Ram','Shiv','Hari'])} {r.choice(owners).split()[0]}", "area_ac": str(round(r.uniform(0.1,10),2)),
                    "area_dec": str(r.randint(1,99))}
        else:
            data = {"khatiyan_no": str(r.randint(1,500)), "raiyat_name": r.choice(owners),
                    "plot_nos": f"{r.randint(1,999)}, {r.randint(1,999)}", "total_area": f"{round(r.uniform(0.5,20),2)} acre",
                    "land_type": r.choice(["Bhita","Dhanhar","Bari","Orchard"])}
        return self.build_result(document_type, data)
