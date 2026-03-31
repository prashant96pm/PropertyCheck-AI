"""Punjab PLRS Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Singh G", "Kaur A", "Sidhu P", "Brar M", "Gill H"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "owner_name": r.choice(owners), "father_name": f"{r.choice(['Gurbachan','Harpal','Jaswant'])} Singh",
                    "area_kanal": str(r.randint(1,20)), "area_marla": str(r.randint(1,20)), "share": f"{r.randint(1,4)}/{r.randint(4,8)}"}
        elif document_type == "MUTATION":
            data = {"mutation_no": str(r.randint(1000,9999)), "date": f"{r.randint(2015,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_party": r.choice(owners), "to_party": r.choice(owners),
                    "type": r.choice(["Intiqal","Fard","Registry"]), "area": f"{r.randint(1,20)} kanal"}
        else:
            data = {"deed_no": str(r.randint(1000,9999)), "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "parties": f"{r.choice(owners)} to {r.choice(owners)}", "property_desc": f"Khasra {khasra}",
                    "consideration": f"Rs.{r.randint(10,200)} lakhs"}
        return self.build_result(document_type, data)
