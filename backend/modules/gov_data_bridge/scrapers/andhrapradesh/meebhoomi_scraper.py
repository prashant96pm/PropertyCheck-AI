"""Andhra Pradesh Meebhoomi Scraper"""
import random
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        raise NotImplementedError("Live scraping not yet implemented for Meebhoomi")
    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs)
        r = random.Random(s)
        survey = inputs.get("surveyNumber", str(r.randint(1,500)))
        owners = ["Naidu V", "Reddy K", "Rao P", "Devi L", "Kumar S"]
        if document_type == "ADANGAL":
            data = {"survey_no": survey, "pattadar_name": r.choice(owners), "father_name": f"{r.choice(['Venkat','Krishna','Siva'])} Rao",
                    "extent": f"{round(r.uniform(0.5,10),2)} acres", "classification": r.choice(["Wet","Dry","Garden"]),
                    "tax_details": f"Rs.{r.randint(100,2000)}", "water_source": r.choice(["Canal","Well","Rain-fed"])}
        elif document_type == "1B_RECORD":
            data = {"survey_no": survey, "subdivision": str(r.randint(1,20)), "pattadar": r.choice(owners),
                    "extent": f"{round(r.uniform(0.5,10),2)} acres", "nature_of_land": r.choice(["Ryotwari","Inam","Government"]),
                    "assessment": f"Rs.{r.randint(200,3000)}"}
        else:
            data = {"survey_no": survey, "owner": r.choice(owners), "extent_ac": str(round(r.uniform(0.5,10),2)),
                    "extent_cents": str(r.randint(1,99)), "soil_type": r.choice(["Black","Red","Sandy","Loamy"]),
                    "irrigation": r.choice(["Canal","Well","Drip","None"])}
        return self.build_result(document_type, data)
