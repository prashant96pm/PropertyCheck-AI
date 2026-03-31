"""West Bengal Banglarbhumi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Chatterjee S", "Banerjee A", "Das P", "Ghosh R", "Mukherjee K"]
        if document_type == "RS_LR_PLOT":
            data = {"plot_no": plot, "rs_no": str(r.randint(1,200)), "lr_no": str(r.randint(1,200)),
                    "area": f"{round(r.uniform(0.01,2),3)} acre", "classification": r.choice(["Shali","Non-Shali","Homestead","Orchard"])}
        elif document_type == "KHATIAN":
            data = {"khatian_no": str(r.randint(1,999)), "owner_name": r.choice(owners), "father_name": f"{r.choice(['Anil','Sunil','Ratan'])} Kumar",
                    "plot_nos": f"{plot},{r.randint(1,999)}", "total_area": f"{round(r.uniform(0.1,5),2)} acre"}
        else:
            data = {"mouza": inputs.get("mouza","Dum Dum"), "jl_no": str(r.randint(1,50)), "plot_no": plot,
                    "dag_no": str(r.randint(1,500)), "owner": r.choice(owners), "area": f"{round(r.uniform(0.01,2),3)} acre"}
        return self.build_result(document_type, data)
