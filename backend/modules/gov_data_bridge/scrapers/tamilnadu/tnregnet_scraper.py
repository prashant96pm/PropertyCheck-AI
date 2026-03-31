"""Tamil Nadu TNREGINET Scraper - Live httpx + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """Live scraping from TNREGINET portal"""
        district = inputs.get("district", "Chennai")
        survey = inputs.get("surveyNumber", "")

        try:
            await self.init()
            resp = await self.navigate_to("https://tnreginet.gov.in/portal/")
            if resp.status_code >= 400:
                raise ConnectionError(f"TNREGINET portal returned {resp.status_code}")

            # Attempt EC search
            if document_type in ("EC", "GUIDELINE_VALUE"):
                ec_url = "https://tnreginet.gov.in/portal/webDTO/ecSearchRequest"
                form_data = {"districtCode": district, "surveyNo": survey}
                resp = await self.post_form(ec_url, form_data)

                if resp.status_code == 200 and len(resp.text) > 200:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "html.parser")
                    tables = soup.find_all("table")
                    if tables:
                        data = self._parse_tn_table(tables, inputs, document_type)
                        if data:
                            return self.build_result(document_type, data)

            raise ConnectionError("Could not extract data from TNREGINET portal")
        except Exception as e:
            logger.warning(f"[TNREGINET] Live scraping failed: {e}")
            raise

    def _parse_tn_table(self, tables, inputs, document_type):
        try:
            cells = []
            for table in tables[:2]:
                for row in table.find_all("tr"):
                    for cell in row.find_all(["td", "th"]):
                        cells.append(cell.get_text(strip=True))
            if cells:
                return {
                    "survey_no": inputs.get("surveyNumber", ""),
                    "district": inputs.get("district", ""),
                    "data": cells[:10],
                    "source": "live_parsed",
                }
        except Exception:
            pass
        return None

    async def fetch_mock(self, inputs: dict, document_type: str) -> dict:
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,500)))
        district = inputs.get("district", "Chennai")
        owners = ["Murugan S", "Lakshmi K", "Selvam R", "Priya M", "Karthik V"]

        if document_type == "EC":
            data = {"doc_no": str(r.randint(1000,9999)), "year": str(r.randint(2010,2024)),
                    "parties": f"{r.choice(owners)} to {r.choice(owners)}",
                    "property_schedule": f"Survey {survey}, {district}",
                    "nature": r.choice(["Sale Deed","Gift Deed","Mortgage","Release Deed"]),
                    "consideration": f"Rs.{r.randint(10,300)} lakhs"}
        elif document_type == "GUIDELINE_VALUE":
            data = {"zone": f"Zone-{r.choice(['A','B','C','D'])}", "street": f"Street {r.randint(1,50)}",
                    "classification": r.choice(["Residential","Commercial","Industrial"]),
                    "rate_per_sq_ft": f"Rs.{r.randint(3000,25000)}",
                    "rate_per_cent": f"Rs.{r.randint(5,100)} lakhs"}
        else:
            data = {"doc_no": str(r.randint(1000,9999)), "year": str(r.randint(2005,2024)),
                    "book_type": r.choice(["Book-1","Book-3","Book-4"]),
                    "parties": f"{r.choice(owners)}", "village": inputs.get("village","Mylapore"), "survey_no": survey}
        return self.build_result(document_type, data)
