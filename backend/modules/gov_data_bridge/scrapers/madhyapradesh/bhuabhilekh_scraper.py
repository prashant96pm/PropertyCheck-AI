"""MP Bhu-Abhilekh Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Thakur R", "Patel S", "Chouhan V", "Malviya A", "Dwivedi P"]
        if document_type == "KHASRA":
            data = {"plot_no": plot, "area": f"{round(r.uniform(0.1,10),2)} hectare",
                    "crop": r.choice(["Soybean","Wheat","Gram","Cotton"]), "owner_name": r.choice(owners),
                    "land_type": r.choice(["Agricultural","Residential","Forest"])}
        elif document_type == "KHATAUNI":
            data = {"khata_no": str(r.randint(1,500)), "owner_name": r.choice(owners),
                    "father_name": f"{r.choice(['Hari','Ram','Shiv'])} Shankar", "plot_nos": f"{plot},{r.randint(1,999)}",
                    "total_area": f"{round(r.uniform(0.5,15),2)} hectare"}
        else:
            data = {"plot_no": plot, "boundaries": "N-Road, S-Nala, E-Plot 45, W-Plot 43",
                    "dimensions": f"{r.randint(20,100)}m x {r.randint(20,100)}m", "area": f"{round(r.uniform(0.1,5),2)} hectare"}
        return self.build_result(document_type, data)
