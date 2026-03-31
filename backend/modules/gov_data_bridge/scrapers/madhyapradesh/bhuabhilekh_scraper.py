"""Madhya Pradesh Bhu-Abhilekh Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://mpbhulekh.gov.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"MP Bhulekh returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "plot": inputs.get("plotNumber","")}
            resp = await self.post_form("https://mpbhulekh.gov.in/viewFreeROR.do", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells:
                        return self.build_result(document_type, {"plot_no": inputs.get("plotNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract data from MP Bhulekh")
        except Exception as e:
            logger.warning(f"[MP Bhulekh] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Thakur A", "Patel R", "Joshi V", "Sharma S", "Yadav K"]
        if document_type == "KHASRA":
            data = {"plot_no": plot, "area": f"{round(r.uniform(0.1,10),2)} hectare", "crop": r.choice(["Wheat","Soybean","Rice","Cotton"]),
                    "owner_name": r.choice(owners), "land_type": r.choice(["Irrigated","Unirrigated","Barren"])}
        elif document_type == "KHATAUNI":
            data = {"khata_no": str(r.randint(1,500)), "owner_name": r.choice(owners), "father_name": f"{r.choice(['Ram','Shiv'])} Prasad",
                    "plot_nos": f"{plot}, {r.randint(1,999)}", "total_area": f"{round(r.uniform(1,20),2)} hectare"}
        else:
            data = {"plot_no": plot, "boundaries": "N-Road, S-Stream, E-Plot 23, W-Plot 25", "dimensions": f"{r.randint(30,200)}m x {r.randint(30,200)}m", "area": f"{round(r.uniform(0.1,5),2)} hectare"}
        return self.build_result(document_type, data)
