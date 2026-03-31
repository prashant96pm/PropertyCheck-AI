"""Gujarat AnyROR Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,999)))
        owners = ["Patel A B", "Shah M R", "Desai K", "Modi V P", "Joshi H"]
        if document_type == "7_12":
            data = {"survey_no": survey, "owner_name": r.choice(owners), "area": f"{round(r.uniform(0.5,10),2)} acres",
                    "land_type": r.choice(["Jirayat","Bagayat","Kyari"]), "crop": r.choice(["Cotton","Groundnut","Tobacco","Cumin"]),
                    "encumbrance": r.choice(["None","Bank Mortgage","Court Order"])}
        elif document_type == "8A":
            data = {"khata_no": str(r.randint(1,500)), "owner_name": r.choice(owners),
                    "survey_nos": f"{survey},{r.randint(1,999)}", "total_area": f"{round(r.uniform(1,20),2)} acres",
                    "assessment": f"Rs.{r.randint(500,5000)}"}
        else:
            data = {"entry_no": str(r.randint(1,500)), "date": f"{r.randint(2010,2024)}-{r.randint(1,12):02d}-{r.randint(1,28):02d}",
                    "from_owner": r.choice(owners), "to_owner": r.choice(owners),
                    "area": f"{round(r.uniform(0.1,5),2)} acres", "mutation_type": r.choice(["Sale","Gift","Inheritance"])}
        return self.build_result(document_type, data)
