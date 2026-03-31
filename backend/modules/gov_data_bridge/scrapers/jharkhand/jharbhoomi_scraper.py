"""Jharkhand JharBhoomi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        mauza = inputs.get("mauzaNumber", str(r.randint(1,999)))
        owners = ["Mahto S", "Oraon R", "Munda P", "Soren A", "Tirkey V"]
        if document_type == "REGISTER_2":
            data = {"khata_no": str(r.randint(1,500)), "plot_no": mauza, "raiyat_name": r.choice(owners),
                    "area": f"{round(r.uniform(0.1,5),2)} acre", "land_class": r.choice(["Residential","Agricultural","Forest"]),
                    "remarks": r.choice(["None","SC/ST Land","Govt Land"])}
        else:
            data = {"khatiyan_no": str(r.randint(1,999)), "raiyat_name": r.choice(owners),
                    "plot_nos": f"{mauza},{r.randint(1,999)}", "total_area": f"{round(r.uniform(0.5,10),2)} acre"}
        return self.build_result(document_type, data)
