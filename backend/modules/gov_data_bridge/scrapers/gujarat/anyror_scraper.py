"""Gujarat AnyROR Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://anyror.gujarat.gov.in/")
            if resp.status_code >= 400:
                raise ConnectionError(f"AnyROR returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "taluka": inputs.get("taluka",""), "village": inputs.get("village",""), "survey": inputs.get("surveyNumber","")}
            resp = await self.post_form("https://anyror.gujarat.gov.in/7aborrecord.aspx", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells:
                        return self.build_result(document_type, {"survey_no": inputs.get("surveyNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract data from AnyROR")
        except Exception as e:
            logger.warning(f"[AnyROR] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Patel A B", "Shah M K", "Desai R P", "Mehta V S", "Joshi H D"]
        if document_type == "7_12":
            data = {"survey_no": survey, "owner_name": r.choice(owners), "area": f"{round(r.uniform(0.1,10),2)} hectare",
                    "land_type": r.choice(["Jirayat","Bagayat","Paddy"]), "crop": r.choice(["Cotton","Groundnut","Wheat","Castor"]),
                    "encumbrance": r.choice(["None","Bank Mortgage","Pending Litigation"])}
        elif document_type == "8A":
            data = {"khata_no": str(r.randint(1,500)), "owner_name": r.choice(owners), "survey_nos": f"{survey}, {r.randint(1,999)}",
                    "total_area": f"{round(r.uniform(1,20),2)} hectare", "assessment": f"Rs.{r.randint(500,5000)}"}
        else:
            data = {"entry_no": str(r.randint(1,500)), "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_owner": r.choice(owners), "to_owner": r.choice(owners), "area": f"{round(r.uniform(0.1,5),2)} hectare",
                    "mutation_type": r.choice(["Sale","Gift","Inheritance","Partition"])}
        return self.build_result(document_type, data)
