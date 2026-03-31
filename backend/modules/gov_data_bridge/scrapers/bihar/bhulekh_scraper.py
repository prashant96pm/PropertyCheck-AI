"""Bihar Bhu-Lekh Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        mauza = inputs.get("mauzaNumber", str(r.randint(1,999)))
        owners = ["Kumar R", "Prasad S", "Yadav V", "Mishra A", "Singh P"]
        if document_type == "JAMABANDI_NAKAL":
            data = {"khata_no": str(r.randint(1,500)), "khesra_no": mauza, "raiyat_name": r.choice(owners),
                    "father_name": f"{r.choice(['Ram','Shiv','Hari'])} Nandan", "area_ac": str(round(r.uniform(0.1,5),2)),
                    "area_dec": str(r.randint(1,99))}
        else:
            data = {"khatiyan_no": str(r.randint(1,999)), "raiyat_name": r.choice(owners),
                    "plot_nos": f"{mauza},{r.randint(1,999)}", "total_area": f"{round(r.uniform(0.5,10),2)} acre",
                    "land_type": r.choice(["Bhita","Dhanhar","Bahal","Tanr"])}
        return self.build_result(document_type, data)
