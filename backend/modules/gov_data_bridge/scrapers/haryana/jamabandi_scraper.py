"""Haryana Jamabandi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Hooda J", "Malik S", "Dahiya R", "Yadav P K", "Sangwan V"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Raj','Balwan','Omprakash'])} Singh",
                    "area_kanal": str(r.randint(1,20)), "area_marla": str(r.randint(1,20)),
                    "khewat_no": str(r.randint(1,500))}
        elif document_type == "MUTATION":
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2015,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners),
                    "type": r.choice(["Sale","Gift","Inheritance","Partition"]), "area": f"{r.randint(1,20)} kanal {r.randint(0,19)} marla"}
        else:
            data = {"khasra_no": khasra, "boundaries": "N-Road, S-Khasra 45, E-Nala, W-Khasra 43",
                    "area": f"{r.randint(1,20)} kanal", "neighbors": "Hooda, Malik, Dahiya"}
        return self.build_result(document_type, data)
