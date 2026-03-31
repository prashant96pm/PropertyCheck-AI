"""West Bengal Banglarbhumi Scraper - Live httpx + Mock fallback"""
import random, logging
from modules.gov_data_bridge.scrapers.base.base_scraper import BaseScraper
logger = logging.getLogger("govdatabridge")

class Scraper(BaseScraper):
    async def extract_data(self, inputs, document_type):
        try:
            await self.init()
            resp = await self.navigate_to("https://banglarbhumi.gov.in/")
            if resp.status_code >= 400: raise ConnectionError(f"Banglarbhumi returned {resp.status_code}")
            form_data = {"district": inputs.get("district",""), "block": inputs.get("block",""), "mouza": inputs.get("mouza",""), "plot": inputs.get("plotNumber","")}
            resp = await self.post_form("https://banglarbhumi.gov.in/BanglarBhumi/Home", form_data)
            if resp.status_code == 200 and len(resp.text) > 200:
                from bs4 import BeautifulSoup
                tables = BeautifulSoup(resp.text, "html.parser").find_all("table")
                if tables:
                    cells = [c.get_text(strip=True) for t in tables[:2] for r in t.find_all("tr") for c in r.find_all(["td","th"])]
                    if cells: return self.build_result(document_type, {"plot_no": inputs.get("plotNumber",""), "parsed_data": cells[:10], "source": "live_parsed"})
            raise ConnectionError("Could not extract from Banglarbhumi")
        except Exception as e:
            logger.warning(f"[Banglarbhumi] Live failed: {e}"); raise

    async def fetch_mock(self, inputs, document_type):
        s = self.generate_deterministic_seed(inputs); r = random.Random(s)
        plot = inputs.get("plotNumber", str(r.randint(1,999)))
        owners = ["Das A", "Banerjee S", "Roy P", "Ghosh R", "Mondal K"]
        if document_type == "RS_LR_PLOT":
            data = {"plot_no": plot, "rs_no": str(r.randint(1,999)), "lr_no": str(r.randint(1,999)),
                    "area": f"{round(r.uniform(0.01,2),3)} acre", "classification": r.choice(["Agricultural","Homestead","Tank","Orchard"])}
        elif document_type == "KHATIAN":
            data = {"khatian_no": str(r.randint(1,999)), "owner_name": r.choice(owners), "father_name": f"{r.choice(['Sujit','Ashok','Ranjit'])} {r.choice(owners).split()[0]}",
                    "plot_nos": f"{plot}, {r.randint(1,999)}", "total_area": f"{round(r.uniform(0.1,5),2)} acre"}
        else:
            data = {"mouza": inputs.get("mouza",""), "jl_no": str(r.randint(1,100)), "plot_no": plot,
                    "dag_no": str(r.randint(1,500)), "owner": r.choice(owners), "area": f"{round(r.uniform(0.01,2),3)} acre"}
        return self.build_result(document_type, data)
