"""Tamil Nadu TNREGINET Scraper - EC, GUIDELINE_VALUE, DOCUMENT_SEARCH"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper


class Scraper(BaseScraper):
    async def extract_data(self, inputs: dict, document_type: str) -> dict:
        raise NotImplementedError("Live scraping not yet implemented for TNREGINET")

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
