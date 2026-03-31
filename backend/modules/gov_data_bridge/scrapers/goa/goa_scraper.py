"""Goa Land Records Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Fernandes A", "D'Souza M", "Naik P", "Kamat R", "Prabhu V"]
        if document_type == "FORM_I_XIV":
            data = {"survey_no": survey, "owner_name": r.choice(owners), "area_sq_mt": str(r.randint(100,5000)),
                    "land_type": r.choice(["Residential","Agricultural","Orchard","Khazan"]),
                    "assessment": f"Rs.{r.randint(500,10000)}"}
        else:
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2015,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners),
                    "type": r.choice(["Sale","Gift","Inheritance"]), "area": f"{r.randint(100,5000)} sq.mt"}
        return self.build_result(document_type, data)
