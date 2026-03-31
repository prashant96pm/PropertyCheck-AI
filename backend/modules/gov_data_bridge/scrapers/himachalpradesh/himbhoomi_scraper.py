"""Himachal Pradesh HimBhoomi Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://himbhoomi.nic.in/")
            if resp.status_code >= 400: raise ConnectionError(f"HimBhoomi returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "tehsil": inputs.get("tehsil",""), "village": inputs.get("village",""), "khasra": inputs.get("khasraNumber","")}
            resp = await self.post_form("https://himbhoomi.nic.in/Nakal/Nakal.aspx", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"khasra_no": inputs.get("khasraNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from HimBhoomi")
        except Exception as e:
            logger.warning(f"[HimBhoomi] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Thakur R", "Sharma V", "Chauhan A", "Negi S", "Verma P"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Mohan','Kishan','Devi'])} {r.choice(owners).split()[0]}",
                    "area_bigha": str(r.randint(1,20)), "area_biswa": str(r.randint(1,20)),
                    "land_type": r.choice(["Irrigated","Unirrigated","Barani","Orchards"])}
        else:
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners), "type": r.choice(["Sale","Gift","Inheritance"]),
                    "area": f"{r.randint(1,20)} bigha"}
        return self.build_result(document_type, data)
