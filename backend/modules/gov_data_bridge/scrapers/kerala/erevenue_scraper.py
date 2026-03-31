"""Kerala E-Revenue Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://erekha.kerala.gov.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Kerala E-Revenue returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "taluk": inputs.get("taluk",""), "village": inputs.get("village",""), "survey": inputs.get("surveyNumber","")}
            resp = await self.post_form("https://erekha.kerala.gov.in/Search", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"survey_no": inputs.get("surveyNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Kerala E-Revenue")
        except Exception as e:
            logger.warning(f"[Kerala] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Nair K", "Menon S", "Thomas P", "Pillai R", "Varma A"]
        if document_type == "THANDAPER":
            data = {"survey_no": survey, "subdivision": str(r.randint(1,20)), "owner_name": r.choice(owners),
                    "extent_hectare": str(round(r.uniform(0.01,2),3)), "extent_are": str(r.randint(1,99)),
                    "classification": r.choice(["Nilam","Purayidam","Parambu","Thotam"])}
        elif document_type == "POSSESSION_CERT":
            data = {"cert_no": f"PC/{r.randint(1000,9999)}/{r.randint(2020,2025)}", "date": f"{r.randint(2020,2025)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "owner": r.choice(owners), "survey_no": survey, "extent": f"{round(r.uniform(0.01,2),3)} hectare", "village": inputs.get("village","")}
        else:
            data = {"tax_receipt_no": str(r.randint(10000,99999)), "year": f"{r.randint(2022,2025)}-{r.randint(2023,2026)}",
                    "amount": f"Rs.{r.randint(100,5000)}", "owner": r.choice(owners), "survey_no": survey}
        return self.build_result(document_type, data)
