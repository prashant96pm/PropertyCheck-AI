"""Andhra Pradesh Meebhoomi Scraper - Live httpx + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """Live scraping from Meebhoomi portal"""
        district = inputs.get("district", "Guntur")
        survey = inputs.get("surveyNumber", "")

        try:
            await self.init()
            resp = await self.navigate_to("https://meebhoomi.ap.gov.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"Meebhoomi portal returned {resp.status_code}")

            # Try Adangal lookup
            adangal_url = "https://meebhoomi.ap.gov.in/SearchROR.aspx"
            form_data = {
                "distId": district, "mandalId": inputs.get("mandal", ""),
                "villageId": inputs.get("village", ""), "surveyNo": survey,
            }
            resp = await self.post_form(adangal_url, form_data)

            if resp.status_code == 200 and len(resp.text) > 300:
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    data = self._parse_ap_table(tables, inputs, document_type)
                    if data:
                        return self.build_result(document_type, data)

            raise ConnectionError("Could not extract data from Meebhoomi portal")
        except Exception as e:
            logger.warning(f"[Meebhoomi] Live scraping failed: {e}")
            raise

    def _parse_ap_table(self, tables, inputs, document_type):
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

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,500)))
        owners = ["Naidu V", "Reddy K", "Rao P", "Devi L", "Kumar S"]
        if document_type == "ADANGAL":
            data = {"survey_no": survey, "pattadar_name": r.choice(owners), "father_name": f"{r.choice(['Venkat','Krishna','Siva'])} Rao",
                    "extent": f"{round(r.uniform(0.5,10),2)} acres", "classification": r.choice(["Wet","Dry","Garden"]),
                    "tax_details": f"Rs.{r.randint(100,2000)}", "water_source": r.choice(["Canal","Well","Rain-fed"])}
        elif document_type == "1B_RECORD":
            data = {"survey_no": survey, "subdivision": str(r.randint(1,20)), "pattadar": r.choice(owners),
                    "extent": f"{round(r.uniform(0.5,10),2)} acres", "nature_of_land": r.choice(["Ryotwari","Inam","Government"]),
                    "assessment": f"Rs.{r.randint(200,3000)}"}
        else:
            data = {"survey_no": survey, "owner": r.choice(owners), "extent_ac": str(round(r.uniform(0.5,10),2)),
                    "extent_cents": str(r.randint(1,99)), "soil_type": r.choice(["Black","Red","Sandy","Loamy"]),
                    "irrigation": r.choice(["Canal","Well","Drip","None"])}
        return self.build_result(document_type, data)
