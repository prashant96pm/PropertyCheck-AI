"""Kerala E-Revenue Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Nair K", "Menon V", "Pillai S", "Thomas J", "George M"]
        if document_type == "THANDAPER":
            data = {"survey_no": survey, "subdivision": str(r.randint(1,20)), "owner_name": r.choice(owners),
                    "extent_hectare": str(round(r.uniform(0.01,2),3)), "extent_are": str(r.randint(1,99)),
                    "classification": r.choice(["Nilam","Parambu","Purayidam","Kara"])}
        elif document_type == "POSSESSION_CERT":
            data = {"cert_no": f"PC/{r.randint(100,999)}/{r.randint(2020,2024)}", "date": f"{r.randint(2020,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "owner": r.choice(owners), "survey_no": survey, "extent": f"{round(r.uniform(0.01,2),3)} hectare",
                    "village": inputs.get("village","Kalamassery")}
        else:
            data = {"tax_receipt_no": str(r.randint(10000,99999)), "year": str(r.randint(2020,2024)),
                    "amount": f"Rs.{r.randint(100,5000)}", "owner": r.choice(owners), "survey_no": survey}
        return self.build_result(document_type, data)
