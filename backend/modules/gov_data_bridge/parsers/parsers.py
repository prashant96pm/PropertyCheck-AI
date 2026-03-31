"""Parsers - HTML table/form parsing, PDF parsing, data normalization"""
import re
import logging

logger = logging.getLogger("govdatabridge")


class HtmlParser:
    """Parse HTML tables and forms from government portals"""

    @staticmethod
    def parse_table(html: str, table_index: int = 0) -> list:
        """Extract data from HTML tables"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            tables = soup.find_all("table")
            if not tables or table_index >= len(tables):
                return []

            table = tables[table_index]
            headers = []
            rows = []

            for th in table.find_all("th"):
                headers.append(th.get_text(strip=True))

            for tr in table.find_all("tr"):
                cells = [td.get_text(strip=True) for td in tr.find_all("td")]
                if cells:
                    if headers:
                        rows.append(dict(zip(headers, cells)))
                    else:
                        rows.append(cells)
            return rows
        except Exception as e:
            logger.error(f"HTML parse error: {e}")
            return []

    @staticmethod
    def extract_form_fields(html: str) -> dict:
        """Extract hidden form fields (CSRF tokens, etc.)"""
        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, "lxml")
            fields = {}
            for inp in soup.find_all("input", {"type": "hidden"}):
                name = inp.get("name")
                if name:
                    fields[name] = inp.get("value", "")
            return fields
        except Exception as e:
            logger.error(f"Form field extraction error: {e}")
            return {}


class Normalizer:
    """Normalize data across different state formats"""

    @staticmethod
    def normalize_area(value: str, unit: str = "acres") -> dict:
        """Normalize area to standard units"""
        try:
            num = float(re.sub(r"[^\d.]", "", value))
            conversions = {
                "acres": num,
                "hectares": num * 0.404686,
                "sq_meters": num * 4046.86,
                "sq_feet": num * 43560,
                "guntas": num * 40,
                "cents": num * 100,
            }
            if unit == "hectares":
                conversions = {
                    "acres": num * 2.47105,
                    "hectares": num,
                    "sq_meters": num * 10000,
                    "sq_feet": num * 107639,
                }
            return conversions
        except (ValueError, TypeError):
            return {"raw": value, "unit": unit}

    @staticmethod
    def normalize_name(name: str) -> str:
        """Standardize owner names"""
        if not name:
            return ""
        name = re.sub(r"\s+", " ", name.strip())
        name = re.sub(r"\b(S/O|D/O|W/O|C/O)\b", "", name, flags=re.IGNORECASE).strip()
        return name.title()

    @staticmethod
    def normalize_date(date_str: str) -> str:
        """Try to normalize date to YYYY-MM-DD"""
        if not date_str:
            return ""
        for fmt in ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d", "%d.%m.%Y", "%m/%d/%Y"]:
            try:
                from datetime import datetime
                dt = datetime.strptime(date_str.strip(), fmt)
                return dt.strftime("%Y-%m-%d")
            except ValueError:
                continue
        return date_str.strip()


class PdfParser:
    """Extract structured data from PDFs"""

    @staticmethod
    def extract_text(pdf_bytes: bytes) -> str:
        """Extract text from PDF bytes"""
        try:
            import pdfplumber
            import io
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                return text
        except Exception as e:
            logger.error(f"PDF text extraction error: {e}")
            return ""

    @staticmethod
    def extract_tables(pdf_bytes: bytes) -> list:
        """Extract tables from PDF"""
        try:
            import pdfplumber
            import io
            tables = []
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            return tables
        except Exception as e:
            logger.error(f"PDF table extraction error: {e}")
            return []
