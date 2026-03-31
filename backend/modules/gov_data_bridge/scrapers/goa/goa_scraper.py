"""Goa Land Records Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://goaonline.gov.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Goa portal returned {resp.status_code}")
            form_data = {"taluka": inputs.get("taluka",""), "village": inputs.get("village",""), "survey": inputs.get("surveyNumber","")}
            resp = await self.post_form("https://goaonline.gov.in/landrecords", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"survey_no": inputs.get("surveyNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Goa portal")
        except Exception as e:
            logger.warning(f"[Goa] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Fernandes A", "D'Souza M", "Naik R", "Shetty V", "Dessai P"]
        if document_type == "FORM_I_XIV":
            data = {"survey_no": survey, "owner_name": r.choice(owners), "area_sq_mt": str(r.randint(100,10000)),
                    "land_type": r.choice(["Agriculture","Settlement","Communidade","Government"]),
                    "assessment": f"Rs.{r.randint(500,10000)}"}
        else:
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners), "type": r.choice(["Sale","Gift","Inheritance"]),
                    "area": f"{r.randint(100,5000)} sq.mt"}
        return self.build_result(document_type, data)
