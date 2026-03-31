"""UP Bhulekh Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        khasra = inputs.get("khasraNumber", str(r.randint(1,999)))
        owners = ["Sharma R K", "Yadav S P", "Singh A", "Gupta V", "Verma P"]
        if document_type == "KHATAUNI":
            data = {"gata_no": str(r.randint(100,9999)), "khata_no": str(r.randint(1,500)), "khatedar_name": r.choice(owners),
                    "father_name": f"{r.choice(['Ram','Shiv','Hari'])} Prasad", "area_hectare": str(round(r.uniform(0.1,5),3)),
                    "area_sqm": str(r.randint(500,50000)), "remarks": r.choice(["None","Mortgage","Disputed"])}
        else:
            data = {"khasra_no": khasra, "area": f"{round(r.uniform(0.1,5),2)} hectare",
                    "crop": r.choice(["Wheat","Rice","Sugarcane","Mustard"]), "owner_name": r.choice(owners),
                    "land_use": r.choice(["Agricultural","Residential","Barren"])}
        return self.build_result(document_type, data)
