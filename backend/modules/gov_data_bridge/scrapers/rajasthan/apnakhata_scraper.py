"""Rajasthan Apna Khata Scraper - Live httpx + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://apnakhata.raj.nic.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"Apna Khata portal returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "khasra": inputs.get("khasraNumber","")}
            resp = await self.post_form("https://apnakhata.raj.nic.in/LRCOpen.aspx", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells:
                        return self.build_result(document_type, {"khasra_no": inputs.get("khasraNumber",""), "district": inputs.get("district",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract data from Apna Khata")
        except Exception as e:
            logger.warning(f"[Apna Khata] Live scraping failed: {e}")
            raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Meena R", "Sharma P", "Jat S K", "Gurjar V", "Rajput H S"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "area": f"{round(r.uniform(0.5,20),2)} bigha", "owner_name": r.choice(owners),
                    "father_name": f"{r.choice(['Mohan','Kishan','Bhagwan'])} Lal", "land_type": r.choice(["Irrigated","Unirrigated","Culturable Waste"]),
                    "irrigation": r.choice(["Well","Canal","Tube Well","None"])}
        elif document_type == "NAKAL":
            data = {"doc_no": str(r.randint(1000,9999)), "year": str(r.randint(2010,2024)),
                    "parties": f"{r.choice(owners)} to {r.choice(owners)}", "property_desc": f"Khasra {khasra}",
                    "consideration": f"Rs.{r.randint(5,100)} lakhs"}
        else:
            data = {"plot_no": khasra, "area": f"{round(r.uniform(0.5,20),2)} bigha",
                    "crop": r.choice(["Wheat","Bajra","Mustard","Gram"]), "irrigation_source": r.choice(["Well","Canal","None"]),
                    "soil_type": r.choice(["Sandy","Loamy","Clay"])}
        return self.build_result(document_type, data)
