"""Odisha Bhunaksha/Bhulekh Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://bhulekh.ori.nic.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Odisha Bhulekh returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "plot": inputs.get("plotNumber","")}
            resp = await self.post_form("https://bhulekh.ori.nic.in/RoRView.aspx", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"plot_no": inputs.get("plotNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Odisha Bhulekh")
        except Exception as e:
            logger.warning(f"[Odisha] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Mohanty S", "Panda R", "Sahoo A", "Nayak P", "Das K"]
        if document_type == "ROR":
            data = {"khata_no": str(r.randint(1,500)), "plot_no": plot, "owner_name": r.choice(owners),
                    "father_name": f"{r.choice(['Biswanath','Jagannath','Pradeep'])} {r.choice(owners).split()[0]}",
                    "area_ac": str(round(r.uniform(0.1,10),2)), "area_dec": str(r.randint(1,99)),
                    "land_class": r.choice(["Abadi","Kissam-A","Kissam-B","Anabadi"])}
        else:
            data = {"plot_no": plot, "boundaries": "N-Plot 23, S-Road, E-Stream, W-Plot 45",
                    "area": f"{round(r.uniform(0.1,5),2)} acre", "coordinates": f"20.{r.randint(1,9)}N, 85.{r.randint(1,9)}E"}
        return self.build_result(document_type, data)
