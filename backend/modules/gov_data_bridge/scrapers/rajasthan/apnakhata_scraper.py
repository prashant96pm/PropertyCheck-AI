"""Rajasthan Apna Khata Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Meena R", "Sharma P", "Jat S K", "Gurjar V", "Rajput H S"]
        if document_type == "JAMABANDI":
            data = {"khasra_no": khasra, "area": f"{round(r.uniform(0.5,20),2)} bigha", "owner_name": r.choice(owners),
                    "father_name": f"{r.choice(['Mohan','Kishan','Bhagwan'])} Lal", "land_type": r.choice(["Irrigated","Unirrigated","Culturable Waste"]),
                    "irrigation": r.choice(["Well","Canal","Tube Well","None"])}
        elif document_type == "NAKAL":
            data = {"doc_no": str(r.randint(1000,9999)), "year": str(r.randint(2010,2024)),
                    "parties": f"{r.choice(owners)} to {r.choice(owners)}", "property_desc": f"Khasra {khasra}",
                    "consideration": f"Rs.{r.randint(5,100)} lakhs"}
        else:
            data = {"plot_no": khasra, "area": f"{round(r.uniform(0.5,20),2)} bigha",
                    "crop": r.choice(["Wheat","Bajra","Mustard","Gram"]), "irrigation_source": r.choice(["Well","Canal","None"]),
                    "soil_type": r.choice(["Sandy","Loamy","Clay"])}
        return self.build_result(document_type, data)
