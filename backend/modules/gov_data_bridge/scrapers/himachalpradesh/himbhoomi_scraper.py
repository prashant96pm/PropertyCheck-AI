"""Himachal Pradesh HimBhoomi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Thakur R", "Sharma V", "Negi S", "Chauhan P", "Rana K"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Dev','Prem','Jai'])} Chand",
                    "area_bigha": str(r.randint(1,20)), "area_biswa": str(r.randint(1,19)),
                    "land_type": r.choice(["Irrigated","Unirrigated","Banjar","Gair Mumkin"])}
        else:
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2015,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners),
                    "type": r.choice(["Sale","Gift","Inheritance"]), "area": f"{r.randint(1,20)} bigha {r.randint(0,19)} biswa"}
        return self.build_result(document_type, data)
