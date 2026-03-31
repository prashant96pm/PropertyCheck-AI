"""Maharashtra MahaBhumi Scraper - Live httpx + Mock fallback"""
import random
import logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

logger = logging.getLogger("govdatabridge")


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        """Live scraping from MahaBhumi / Bhulekh portal"""
        district = inputs.get("district", "Pune")
        taluka = inputs.get("taluka", "Haveli")
        village = inputs.get("village", "Kothrud")
        gut_no = inputs.get("gutNumber", "")

        try:
            await self.init()
            resp = await self.navigate_to("https://bhulekh.mahabhumi.gov.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"MahaBhumi portal returned {resp.status_code}")

            # Try Satbara/7-12 lookup
            if document_type in ("SATBARA", "PROPERTY_CARD"):
                search_url = "https://bhulekh.mahabhumi.gov.in/Satbara/SatbaraReport"
                form_data = {
                    "districtId": district, "talukaId": taluka,
                    "villageId": village, "gutNo": gut_no,
                }
                resp = await self.post_form(search_url, form_data)

                if resp.status_code == 200 and len(resp.text) > 300:
                    from bs4 import BeautifulSoup
                    soup = BeautifulSoup(resp.text, "html.parser")
                    tables = soup.find_all("table")
                    if tables:
                        data = self._parse_maha_table(tables, inputs, document_type)
                        if data:
                            return self.build_result(document_type, data)

            raise ConnectionError("Could not extract data from MahaBhumi portal")
        except Exception as e:
            logger.warning(f"[MahaBhumi] Live scraping failed: {e}")
            raise

    def _parse_maha_table(self, tables, inputs, document_type):
        try:
            cells = []
            for table in tables[:3]:
                for row in table.find_all("tr"):
                    for cell in row.find_all(["td", "th"]):
                        cells.append(cell.get_text(strip=True))
            if cells:
                return {
                    "gut_no": inputs.get("gutNumber", ""),
                    "district": inputs.get("district", ""),
                    "taluka": inputs.get("taluka", ""),
                    "village": inputs.get("village", ""),
                    "data": cells[:10],
                    "source": "live_parsed",
                }
        except Exception:
            pass
        return None

    async def fetch_mock(self, inputs: dict, document_type: str) -> dict:
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        gut = inputs.get("gutNumber", str(r.randint(1,999)))
        district = inputs.get("district", "Pune")
        owners = ["Patil S R", "Deshmukh V M", "Jadhav A K", "Shinde P L", "Kulkarni R G"]

        if document_type == "SATBARA":
            data = {"gut_no": gut, "owner_name": r.choice(owners),
                    "area_hectare": str(round(r.uniform(0.1,5),3)), "area_are": str(r.randint(1,99)),
                    "crop": r.choice(["Sugarcane","Jowar","Cotton","Grapes","Onion"]),
                    "water_source": r.choice(["Well","Canal","Rain-fed","Borewell"]),
                    "land_type": r.choice(["Jirayat","Bagayat","Paddy"]),
                    "taluka": inputs.get("taluka","Haveli"), "village": inputs.get("village","Kothrud")}
        elif document_type == "PROPERTY_CARD":
            data = {"cts_no": f"{r.randint(100,9999)}/{r.choice(['A','B','C'])}",
                    "owner_name": r.choice(owners), "area_sq_mt": str(r.randint(50,2000)),
                    "built_up": f"{r.randint(30,500)} sq.mt", "open_land": f"{r.randint(10,200)} sq.mt",
                    "floor": r.choice(["Ground","First","Second","Third"]),
                    "usage": r.choice(["Residential","Commercial","Mixed"])}
        else:
            data = {"mutation_no": str(r.randint(1000,9999)),
                    "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners),
                    "type": r.choice(["Sale","Gift","Inheritance","Partition"]),
                    "area": f"{round(r.uniform(0.1,5),2)} hectare",
                    "order": f"Tahsildar Order No. {r.randint(100,999)}/{r.randint(2020,2024)}"}
        return self.build_result(document_type, data)
