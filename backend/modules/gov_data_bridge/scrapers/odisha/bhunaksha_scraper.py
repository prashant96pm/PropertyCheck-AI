"""Odisha Bhunaksha/Bhulekh Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Mohanty S", "Panda R", "Sahoo A", "Nayak P", "Mishra K"]
        if document_type == "ROR":
            data = {"khata_no": str(r.randint(1,500)), "plot_no": plot, "owner_name": r.choice(owners),
                    "father_name": f"{r.choice(['Gopi','Hari','Jagannath'])} Nath", "area_ac": str(round(r.uniform(0.1,5),2)),
                    "area_dec": str(r.randint(1,99)), "land_class": r.choice(["Abad","Abada Jogya","Rakhit","Kisam"])}
        else:
            data = {"plot_no": plot, "boundaries": "N-Plot 12, S-Road, E-Nala, W-Plot 14",
                    "area": f"{round(r.uniform(0.1,5),2)} acre", "coordinates": f"{r.uniform(20,22):.4f}N, {r.uniform(83,87):.4f}E"}
        return self.build_result(document_type, data)
