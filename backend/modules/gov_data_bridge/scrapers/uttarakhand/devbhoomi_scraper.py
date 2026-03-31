"""Uttarakhand DevBhoomi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Rawat S", "Bisht P", "Negi V", "Panwar R", "Chauhan A"]
        data = {"khata_no": str(r.randint(1,500)), "khasra_no": khasra, "owner_name": r.choice(owners),
                "father_name": f"{r.choice(['Narayan','Govind','Mohan'])} Singh",
                "area": f"{round(r.uniform(0.1,10),2)} nali", "land_type": r.choice(["Irrigated","Unirrigated","Orchard","Forest"])}
        return self.build_result(document_type, data)
