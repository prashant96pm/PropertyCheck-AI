"""Chhattisgarh Bhuiyan Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Sahu R", "Verma P", "Yadav S", "Patel K", "Thakur V"]
        if document_type == "B1_KHASRA":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Ram','Gopal','Deen'])} Dayal",
                    "area": f"{round(r.uniform(0.1,10),2)} hectare", "land_type": r.choice(["Agricultural","Residential","Forest"]),
                    "crop": r.choice(["Paddy","Wheat","Lentil","Maize"])}
        else:
            data = {"khasra_no": khasra, "boundaries": "N-Khasra 12, S-Road, E-Stream, W-Khasra 14",
                    "area": f"{round(r.uniform(0.1,5),2)} hectare", "dimensions": f"{r.randint(20,200)}m x {r.randint(20,200)}m"}
        return self.build_result(document_type, data)
