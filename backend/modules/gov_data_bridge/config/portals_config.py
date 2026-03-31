"""Portal configurations for all 20 Indian state land record portals"""

PORTALS = {
    "karnataka": {
        "name": "Bhoomi",
        "url": "https://bhoomi.karnataka.gov.in",
        "documents": ["RTC", "MR", "PT"],
        "inputs": ["district", "taluk", "hobli", "village", "surveyNumber"],
        "captcha_type": "image",
        "dropdown_cascade": True,
        "scraper_type": "playwright",
        "record_format": {
            "RTC": {"fields": ["survey_no", "surnoc", "hissa", "owner_name", "father_name", "extent_acres", "extent_guntas", "land_type", "crop_info", "mutation_date", "taluk", "hobli", "village"]},
            "MR": {"fields": ["mutation_no", "date", "from_owner", "to_owner", "type", "extent", "order_date"]},
            "PT": {"fields": ["khata_no", "property_id", "owner_name", "total_extent", "assessment"]},
        },
    },
    "telangana": {
        "name": "Dharani",
        "url": "https://dharani.telangana.gov.in",
        "documents": ["PATTADAR_PASSBOOK", "EC", "MARKET_VALUE"],
        "inputs": ["district", "mandal", "village", "surveyNumber"],
        "captcha_type": "none",
        "has_api": True,
        "api_endpoint": "https://dharani.telangana.gov.in/api/landrecords",
        "scraper_type": "httpx",
        "record_format": {
            "PATTADAR_PASSBOOK": {"fields": ["pattadar_name", "father_name", "survey_no", "extent", "classification", "market_value", "district", "mandal", "village"]},
            "EC": {"fields": ["doc_no", "reg_date", "parties", "property_desc", "consideration", "sub_registrar"]},
            "MARKET_VALUE": {"fields": ["survey_no", "classification", "rate_per_sq_yard", "rate_per_acre", "zone"]},
        },
    },
    "tamilnadu": {
        "name": "TNREGINET",
        "url": "https://tnreginet.gov.in",
        "documents": ["EC", "GUIDELINE_VALUE", "DOCUMENT_SEARCH"],
        "inputs": ["zone", "district", "subRegistrarOffice", "surveyNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "EC": {"fields": ["doc_no", "year", "parties", "property_schedule", "nature", "consideration"]},
            "GUIDELINE_VALUE": {"fields": ["zone", "street", "classification", "rate_per_sq_ft", "rate_per_cent"]},
            "DOCUMENT_SEARCH": {"fields": ["doc_no", "year", "book_type", "parties", "village", "survey_no"]},
        },
    },
    "maharashtra": {
        "name": "MahaBhumi",
        "url": "https://mahabhumi.gov.in",
        "documents": ["SATBARA", "PROPERTY_CARD", "MUTATION"],
        "inputs": ["district", "taluka", "village", "gutNumber"],
        "captcha_type": "image",
        "dropdown_cascade": True,
        "scraper_type": "playwright",
        "record_format": {
            "SATBARA": {"fields": ["gut_no", "owner_name", "area_hectare", "area_are", "crop", "water_source", "land_type", "taluka", "village"]},
            "PROPERTY_CARD": {"fields": ["cts_no", "owner_name", "area_sq_mt", "built_up", "open_land", "floor", "usage"]},
            "MUTATION": {"fields": ["mutation_no", "date", "from_party", "to_party", "type", "area", "order"]},
        },
    },
    "andhrapradesh": {
        "name": "Meebhoomi",
        "url": "https://meebhoomi.ap.gov.in",
        "documents": ["ADANGAL", "1B_RECORD", "PAHANI"],
        "inputs": ["district", "zone", "mandal", "village", "surveyNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "ADANGAL": {"fields": ["survey_no", "pattadar_name", "father_name", "extent", "classification", "tax_details", "water_source"]},
            "1B_RECORD": {"fields": ["survey_no", "subdivision", "pattadar", "extent", "nature_of_land", "assessment"]},
            "PAHANI": {"fields": ["survey_no", "owner", "extent_ac", "extent_cents", "soil_type", "irrigation"]},
        },
    },
    "uttarpradesh": {
        "name": "Bhulekh UP",
        "url": "https://upbhulekh.gov.in",
        "documents": ["KHATAUNI", "KHASRA_CODE"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "KHATAUNI": {"fields": ["gata_no", "khata_no", "khatedar_name", "father_name", "area_hectare", "area_sqm", "remarks"]},
            "KHASRA_CODE": {"fields": ["khasra_no", "area", "crop", "owner_name", "land_use"]},
        },
    },
    "rajasthan": {
        "name": "Apna Khata",
        "url": "https://apnakhata.raj.nic.in",
        "documents": ["JAMABANDI", "NAKAL", "KHASRA"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "JAMABANDI": {"fields": ["khasra_no", "area", "owner_name", "father_name", "land_type", "irrigation"]},
            "NAKAL": {"fields": ["doc_no", "year", "parties", "property_desc", "consideration"]},
            "KHASRA": {"fields": ["plot_no", "area", "crop", "irrigation_source", "soil_type"]},
        },
    },
    "madhyapradesh": {
        "name": "Bhu-Abhilekh",
        "url": "https://mpbhulekh.gov.in",
        "documents": ["KHASRA", "KHATAUNI", "NAKSHA"],
        "inputs": ["district", "tehsil", "village", "plotNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "KHASRA": {"fields": ["plot_no", "area", "crop", "owner_name", "land_type"]},
            "KHATAUNI": {"fields": ["khata_no", "owner_name", "father_name", "plot_nos", "total_area"]},
            "NAKSHA": {"fields": ["plot_no", "boundaries", "dimensions", "area"]},
        },
    },
    "gujarat": {
        "name": "AnyROR",
        "url": "https://anyror.gujarat.gov.in",
        "documents": ["7_12", "8A", "VF6"],
        "inputs": ["district", "taluka", "village", "surveyNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "7_12": {"fields": ["survey_no", "owner_name", "area", "land_type", "crop", "encumbrance"]},
            "8A": {"fields": ["khata_no", "owner_name", "survey_nos", "total_area", "assessment"]},
            "VF6": {"fields": ["entry_no", "date", "from_owner", "to_owner", "area", "mutation_type"]},
        },
    },
    "haryana": {
        "name": "Jamabandi",
        "url": "https://jamabandi.nic.in",
        "documents": ["JAMABANDI", "MUTATION", "CADASTRAL_MAP"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "JAMABANDI": {"fields": ["khasra_no", "owner_name", "father_name", "area_kanal", "area_marla", "khewat_no"]},
            "MUTATION": {"fields": ["mutation_no", "date", "from_party", "to_party", "type", "area"]},
            "CADASTRAL_MAP": {"fields": ["khasra_no", "boundaries", "area", "neighbors"]},
        },
    },
    "punjab": {
        "name": "PLRS",
        "url": "https://jamabandi.punjab.gov.in",
        "documents": ["JAMABANDI", "MUTATION", "REGISTRY_DEED"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "JAMABANDI": {"fields": ["khasra_no", "owner_name", "father_name", "area_kanal", "area_marla", "share"]},
            "MUTATION": {"fields": ["mutation_no", "date", "from_party", "to_party", "type", "area"]},
            "REGISTRY_DEED": {"fields": ["deed_no", "date", "parties", "property_desc", "consideration"]},
        },
    },
    "westbengal": {
        "name": "Banglarbhumi",
        "url": "https://banglarbhumi.gov.in",
        "documents": ["RS_LR_PLOT", "KHATIAN", "PARCHA"],
        "inputs": ["district", "block", "mouza", "plotNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "RS_LR_PLOT": {"fields": ["plot_no", "rs_no", "lr_no", "area", "classification"]},
            "KHATIAN": {"fields": ["khatian_no", "owner_name", "father_name", "plot_nos", "total_area"]},
            "PARCHA": {"fields": ["mouza", "jl_no", "plot_no", "dag_no", "owner", "area"]},
        },
    },
    "kerala": {
        "name": "E-Revenue",
        "url": "https://erevenue.kerala.gov.in",
        "documents": ["THANDAPER", "POSSESSION_CERT", "LAND_TAX"],
        "inputs": ["district", "taluk", "village", "surveyNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "THANDAPER": {"fields": ["survey_no", "subdivision", "owner_name", "extent_hectare", "extent_are", "classification"]},
            "POSSESSION_CERT": {"fields": ["cert_no", "date", "owner", "survey_no", "extent", "village"]},
            "LAND_TAX": {"fields": ["tax_receipt_no", "year", "amount", "owner", "survey_no"]},
        },
    },
    "odisha": {
        "name": "Bhunaksha / Bhulekh",
        "url": "https://bhulekh.ori.nic.in",
        "documents": ["ROR", "MAP"],
        "inputs": ["district", "tehsil", "village", "plotNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "ROR": {"fields": ["khata_no", "plot_no", "owner_name", "father_name", "area_ac", "area_dec", "land_class"]},
            "MAP": {"fields": ["plot_no", "boundaries", "area", "coordinates"]},
        },
    },
    "bihar": {
        "name": "Bhu-Lekh Bihar",
        "url": "https://lrc.bih.nic.in",
        "documents": ["JAMABANDI_NAKAL", "KHATIYAN"],
        "inputs": ["district", "zone", "circle", "mauzaNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "JAMABANDI_NAKAL": {"fields": ["khata_no", "khesra_no", "raiyat_name", "father_name", "area_ac", "area_dec"]},
            "KHATIYAN": {"fields": ["khatiyan_no", "raiyat_name", "plot_nos", "total_area", "land_type"]},
        },
    },
    "jharkhand": {
        "name": "JharBhoomi",
        "url": "https://jharbhoomi.nic.in",
        "documents": ["REGISTER_2", "KHATIYAN"],
        "inputs": ["district", "block", "halka", "mauzaNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "REGISTER_2": {"fields": ["khata_no", "plot_no", "raiyat_name", "area", "land_class", "remarks"]},
            "KHATIYAN": {"fields": ["khatiyan_no", "raiyat_name", "plot_nos", "total_area"]},
        },
    },
    "chhattisgarh": {
        "name": "Bhuiyan",
        "url": "https://bhuiyan.cg.nic.in",
        "documents": ["B1_KHASRA", "PARIVAR_NAKSHA"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "B1_KHASRA": {"fields": ["khasra_no", "owner_name", "father_name", "area", "land_type", "crop"]},
            "PARIVAR_NAKSHA": {"fields": ["khasra_no", "boundaries", "area", "dimensions"]},
        },
    },
    "himachalpradesh": {
        "name": "HimBhoomi",
        "url": "https://himbhoomi.nic.in",
        "documents": ["JAMABANDI", "MUTATION"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "JAMABANDI": {"fields": ["khasra_no", "owner_name", "father_name", "area_bigha", "area_biswa", "land_type"]},
            "MUTATION": {"fields": ["mutation_no", "date", "from_party", "to_party", "type", "area"]},
        },
    },
    "uttarakhand": {
        "name": "DevBhoomi",
        "url": "https://devbhoomi.uk.gov.in",
        "documents": ["KHATAUNI"],
        "inputs": ["district", "tehsil", "village", "khasraNumber"],
        "captcha_type": "image",
        "scraper_type": "playwright",
        "record_format": {
            "KHATAUNI": {"fields": ["khata_no", "khasra_no", "owner_name", "father_name", "area", "land_type"]},
        },
    },
    "goa": {
        "name": "Goa Land Records",
        "url": "https://goaonline.gov.in",
        "documents": ["FORM_I_XIV", "MUTATION"],
        "inputs": ["taluka", "village", "surveyNumber"],
        "captcha_type": "none",
        "scraper_type": "httpx",
        "record_format": {
            "FORM_I_XIV": {"fields": ["survey_no", "owner_name", "area_sq_mt", "land_type", "assessment"]},
            "MUTATION": {"fields": ["mutation_no", "date", "from_party", "to_party", "type", "area"]},
        },
    },
}


def get_portal(state: str) -> dict:
    return PORTALS.get(state.lower().replace(" ", ""))


def get_all_states() -> list:
    return [
        {"state_key": k, "name": v["name"], "url": v["url"], "documents": v["documents"],
         "inputs": v["inputs"], "captcha_type": v["captcha_type"], "scraper_type": v.get("scraper_type", "httpx")}
        for k, v in PORTALS.items()
    ]


def get_supported_documents(state: str) -> list:
    portal = get_portal(state)
    return portal["documents"] if portal else []
