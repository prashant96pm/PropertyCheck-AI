"""Karnataka Bhoomi Scraper - Live Playwright + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """Live scraping from Bhoomi portal using httpx (Playwright fallback)"""
        district = inputs.get("district", "Bengaluru Urban")
        taluk = inputs.get("taluk", "Bengaluru North")
        village = inputs.get("village", "Hebbal")
        survey = inputs.get("surveyNumber", "")

        try:
            # Attempt httpx-based scraping of Bhoomi portal
            await self.init()
            resp = await self.navigate_to(self.url)
            if resp.status_code >= 400:
                raise ConnectionError(f"Bhoomi portal returned {resp.status_code}")

            # Try the RTC lookup API endpoint
            rtc_url = f"https://landrecords.karnataka.gov.in/service2/RTC_V2.aspx"
            form_data = {
                "dist": district, "taluk": taluk, "hobli": f"{village} Hobli",
                "village": village, "srnoc": survey, "hession": "",
            }
            resp = await self.post_form(rtc_url, form_data)

            if resp.status_code == 200 and len(resp.text) > 500:
                # Parse HTML response
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(resp.text, "html.parser")
                tables = soup.find_all("table")
                if tables:
                    data = self._parse_rtc_table(tables, inputs, document_type)
                    if data:
                        return self.build_result(document_type, data)

            raise ConnectionError("Could not extract data from Bhoomi portal response")

        except Exception as e:
            logger.warning(f"[Bhoomi] Live scraping failed: {e}")
            raise

    def _parse_rtc_table(self, tables, inputs, document_type):
        """Parse Bhoomi RTC HTML tables"""
        try:
            cells = []
            for table in tables[:3]:
                for row in table.find_all("tr"):
                    for cell in row.find_all(["td", "th"]):
                        cells.append(cell.get_text(strip=True))

            if len(cells) > 5:
                return {
                    "survey_no": inputs.get("surveyNumber", ""),
                    "owner_name": cells[2] if len(cells) > 2 else "N/A",
                    "extent_acres": cells[4] if len(cells) > 4 else "N/A",
                    "land_type": cells[6] if len(cells) > 6 else "N/A",
                    "district": inputs.get("district", ""),
                    "taluk": inputs.get("taluk", ""),
                    "village": inputs.get("village", ""),
                    "source": "live_parsed",
                }
        except Exception:
            pass
        return None

    async def fetch_mock(self, inputs: dict, document_type: str) -> dict:
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", f"{r.randint(1,999)}/{r.randint(1,99)}")
        district = inputs.get("district", "Bengaluru Urban")
        taluk = inputs.get("taluk", "Bengaluru North")
        village = inputs.get("village", "Hebbal")
        owners = ["Ramesh Kumar", "Suresh Reddy", "Lakshmi Devi", "Manjunath G", "Venkatesh B R"]
        crops = ["Paddy", "Ragi", "Coconut", "Arecanut", "Sugarcane", "Mango"]

        if document_type == "RTC":
            data = {
                "survey_no": survey, "surnoc": str(r.randint(1,50)),
                "hissa": str(r.randint(1,10)), "owner_name": r.choice(owners),
                "father_name": f"{r.choice(owners).split()[0]} {r.choice(['Gowda','Reddy','Shetty'])}",
                "extent_acres": str(round(r.uniform(0.5, 15.0), 2)),
                "extent_guntas": str(r.randint(1,39)),
                "land_type": r.choice(["Agricultural", "Non-Agricultural", "Commercial", "Residential"]),
                "crop_info": ", ".join(r.sample(crops, r.randint(1,3))),
                "mutation_date": f"{r.randint(2005,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                "taluk": taluk, "hobli": f"{village} Hobli", "village": village,
                "district": district, "state": "Karnataka",
            }
        elif document_type == "MR":
            data = {
                "mutation_no": str(r.randint(1000,9999)),
                "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                "from_owner": r.choice(owners), "to_owner": r.choice(owners),
                "type": r.choice(["Sale", "Gift", "Inheritance", "Partition"]),
                "extent": f"{round(r.uniform(0.5,10),2)} acres",
                "order_date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                "district": district,
            }
        else:
            data = {
                "khata_no": str(r.randint(100,999)), "property_id": f"KA-{district[:3].upper()}-{r.randint(10000,99999)}",
                "owner_name": r.choice(owners), "total_extent": f"{round(r.uniform(0.1,5),2)} acres",
                "assessment": f"Rs.{r.randint(500,5000)}", "district": district,
            }
        return self.build_result(document_type, data)
