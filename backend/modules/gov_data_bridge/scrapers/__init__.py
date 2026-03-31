"""Scraper registry - maps state keys to scraper instances"""
from modules.gov_data_bridge.config.portals_config import PORTALS


def get_scraper(state_key: str):
    """Get scraper instance for a state"""
    state_key = state_key.lower().replace(" ", "")
    portal = PORTALS.get(state_key)
    if not portal:
        return None

    cfg = {**portal, "state_key": state_key}

    scraper_map = {
        "karnataka": "modules.gov_data_bridge.scrapers.karnataka.bhoomi_scraper",
        "telangana": "modules.gov_data_bridge.scrapers.telangana.dharani_scraper",
        "tamilnadu": "modules.gov_data_bridge.scrapers.tamilnadu.tnregnet_scraper",
        "maharashtra": "modules.gov_data_bridge.scrapers.maharashtra.mahabhumi_scraper",
        "andhrapradesh": "modules.gov_data_bridge.scrapers.andhrapradesh.meebhoomi_scraper",
        "uttarpradesh": "modules.gov_data_bridge.scrapers.uttarpradesh.bhulekh_scraper",
        "rajasthan": "modules.gov_data_bridge.scrapers.rajasthan.apnakhata_scraper",
        "madhyapradesh": "modules.gov_data_bridge.scrapers.madhyapradesh.bhuabhilekh_scraper",
        "gujarat": "modules.gov_data_bridge.scrapers.gujarat.anyror_scraper",
        "haryana": "modules.gov_data_bridge.scrapers.haryana.jamabandi_scraper",
        "punjab": "modules.gov_data_bridge.scrapers.punjab.plrs_scraper",
        "westbengal": "modules.gov_data_bridge.scrapers.westbengal.banglarbhumi_scraper",
        "kerala": "modules.gov_data_bridge.scrapers.kerala.erevenue_scraper",
        "odisha": "modules.gov_data_bridge.scrapers.odisha.bhunaksha_scraper",
        "bihar": "modules.gov_data_bridge.scrapers.bihar.bhulekh_scraper",
        "jharkhand": "modules.gov_data_bridge.scrapers.jharkhand.jharbhoomi_scraper",
        "chhattisgarh": "modules.gov_data_bridge.scrapers.chhattisgarh.bhuiyan_scraper",
        "himachalpradesh": "modules.gov_data_bridge.scrapers.himachalpradesh.himbhoomi_scraper",
        "uttarakhand": "modules.gov_data_bridge.scrapers.uttarakhand.devbhoomi_scraper",
        "goa": "modules.gov_data_bridge.scrapers.goa.goa_scraper",
    }

    module_path = scraper_map.get(state_key)
    if not module_path:
        return None

    try:
        import importlib
        mod = importlib.import_module(module_path)
        scraper_class = getattr(mod, "Scraper")
        return scraper_class(cfg)
    except Exception as e:
        import logging
        logging.getLogger("govdatabridge").error(f"Failed to load scraper for {state_key}: {e}")
        return None
