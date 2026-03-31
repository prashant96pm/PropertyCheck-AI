"""Telangana Dharani Scraper - Live httpx API + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """Live: Dharani has partial API support — attempt httpx fetch"""
        district = inputs.get("district", "Hyderabad")
        mandal = inputs.get("mandal", "Secunderabad")
        village = inputs.get("village", "Bowenpally")
        survey = inputs.get("surveyNumber", "")

        try:
            await self.init()
            # Try the Dharani search API
            api_url = "https://dharani.telangana.gov.in/homePage"
            resp = await self.navigate_to(api_url)
            if resp.status_code >= 400:
                raise ConnectionError(f"Dharani portal returned {resp.status_code}")

            # Try form-based lookup
            search_url = "https://dharani.telangana.gov.in/landDetails"
            form_data = {
                "districtId": district, "mandalId": mandal,
                "villageId": village, "surveyNo": survey,
            }
            resp = await self.post_form(search_url, form_data)

            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    data = self._parse_dharani(tables, inputs, document_type)
                    if data:
                        return self.build_result(document_type, data)

            raise ConnectionError("Could not extract data from Dharani portal")

        except Exception as e:
            logger.warning(f"[Dharani] Live scraping failed: {e}")
            raise

    def _parse_dharani(self, tables, inputs, document_type):
        try:
            cells = []
            for table in tables[:2]:
                for row in table.find_all("tr"):
                    for cell in row.find_all(["td", "th"]):
                        cells.append(cell.get_text(strip=True))
            if len(cells) > 3:
                return {
                    "survey_no": inputs.get("surveyNumber", ""),
                    "pattadar_name": cells[1] if len(cells) > 1 else "N/A",
                    "extent": cells[3] if len(cells) > 3 else "N/A",
                    "district": inputs.get("district", ""),
                    "source": "live_parsed",
                }
        except Exception:
            pass
        return None

    async def fetch_mock(self, inputs: dict, document_type: str) -> dict:
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,500)))
        district = inputs.get("district", "Hyderabad")
        owners = ["Srinivas Rao", "Padma Devi", "Rajesh Kumar", "Lakshmi Bai", "Venkat Reddy"]

        if document_type == "PATTADAR_PASSBOOK":
            data = {"pattadar_name": r.choice(owners), "father_name": f"{r.choice(['Krishna','Ram','Shiva'])} Rao",
                    "survey_no": survey, "extent": f"{round(r.uniform(0.5,10),2)} acres",
                    "classification": r.choice(["Wet","Dry","Garden","Jareebu"]),
                    "market_value": f"Rs.{r.randint(50,500)} lakhs", "district": district,
                    "mandal": inputs.get("mandal","Secunderabad"), "village": inputs.get("village","Bowenpally")}
        elif document_type == "EC":
            data = {"doc_no": str(r.randint(1000,9999)), "reg_date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "parties": f"{r.choice(owners)} → {r.choice(owners)}", "property_desc": f"Survey {survey}, {district}",
                    "consideration": f"Rs.{r.randint(10,200)} lakhs", "sub_registrar": f"SRO {district}"}
        else:
            data = {"survey_no": survey, "classification": r.choice(["Residential","Commercial","Agricultural"]),
                    "rate_per_sq_yard": f"Rs.{r.randint(5000,50000)}", "rate_per_acre": f"Rs.{r.randint(50,500)} lakhs",
                    "zone": f"Zone-{r.randint(1,10)}"}
        return self.build_result(document_type, data)
