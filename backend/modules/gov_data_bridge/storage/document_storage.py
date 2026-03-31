"""S3 Document Storage - Upload/download PDFs with pre-signed URLs + local fallback"""
import os
import io
import logging
from datetime import datetime, timezone

logger = logging.getLogger("govdatabridge")

S3_BUCKET = os.environ.get("AWS_S3_BUCKET_GOVDOCS", "propertycheckai-govdocs")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
SIGNED_URL_EXPIRY = int(os.environ.get("GOV_SIGNED_URL_EXPIRY", "86400"))
STORAGE_PROVIDER = os.environ.get("STORAGE_PROVIDER", "auto")

LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "gov_records")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


class DocumentStorage:
    """S3 storage for government record PDFs with auto local fallback"""

    def __init__(self):
        self._s3 = None
        self._s3_available = None

    def _check_s3_credentials(self) -> bool:
        """Check if AWS credentials are configured"""
        key = os.environ.get("AWS_ACCESS_KEY_ID", "").strip()
        secret = os.environ.get("AWS_SECRET_ACCESS_KEY", "").strip()
        return bool(key and secret)

    def _get_s3_client(self):
        if self._s3:
            return self._s3
        if not self._check_s3_credentials():
            logger.info("AWS credentials not configured — using local storage")
            self._s3_available = False
            return None
        try:
            import boto3
            self._s3 = boto3.client(
                "s3",
                region_name=AWS_REGION,
                aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
            )
            self._s3_available = True
            return self._s3
        except Exception as e:
            logger.warning(f"S3 client init failed: {e}, using local storage")
            self._s3_available = False
            return None

    def _use_s3(self) -> bool:
        """Decide whether to use S3 based on STORAGE_PROVIDER and credentials"""
        if STORAGE_PROVIDER == "local":
            return False
        if STORAGE_PROVIDER == "s3":
            return self._check_s3_credentials()
        # auto: use S3 if credentials present
        return self._check_s3_credentials()

    def _s3_key(self, state: str, document_type: str, job_id: str) -> str:
        return f"gov-records/{state}/{document_type}/{job_id}.pdf"

    async def upload_pdf(self, pdf_bytes: bytes, state: str, document_type: str, job_id: str) -> dict:
        """Upload PDF to S3 or local storage with auto-fallback"""
        s3_key = self._s3_key(state, document_type, job_id)

        if self._use_s3():
            s3 = self._get_s3_client()
            if s3:
                try:
                    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=pdf_bytes, ContentType="application/pdf")
                    url = self._generate_presigned_url(s3_key)
                    logger.info(f"PDF uploaded to S3: {s3_key}")
                    return {"storage": "s3", "s3_key": s3_key, "pdf_url": url, "bucket": S3_BUCKET}
                except Exception as e:
                    logger.error(f"S3 upload failed: {e}, falling back to local")

        # Local storage fallback
        return await self._store_local(pdf_bytes, state, document_type, job_id, s3_key)

    async def _store_local(self, pdf_bytes: bytes, state: str, document_type: str, job_id: str, s3_key: str) -> dict:
        local_path = os.path.join(LOCAL_STORAGE_DIR, state, document_type)
        os.makedirs(local_path, exist_ok=True)
        filepath = os.path.join(local_path, f"{job_id}.pdf")
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)
        logger.info(f"PDF stored locally: {filepath}")
        return {
            "storage": "local",
            "local_path": filepath,
            "pdf_url": f"/api/gov/download/{state}/{document_type}/{job_id}",
            "s3_key": s3_key,
        }

    def _generate_presigned_url(self, s3_key: str) -> str:
        s3 = self._get_s3_client()
        if s3:
            try:
                return s3.generate_presigned_url(
                    "get_object",
                    Params={"Bucket": S3_BUCKET, "Key": s3_key},
                    ExpiresIn=SIGNED_URL_EXPIRY,
                )
            except Exception as e:
                logger.error(f"Pre-signed URL generation failed: {e}")
        return ""

    async def get_download_url(self, s3_key: str) -> str:
        return self._generate_presigned_url(s3_key)

    def get_storage_info(self) -> dict:
        """Return current storage configuration status"""
        return {
            "provider": STORAGE_PROVIDER,
            "s3_configured": self._check_s3_credentials(),
            "s3_bucket": S3_BUCKET if self._check_s3_credentials() else None,
            "s3_region": AWS_REGION,
            "local_dir": LOCAL_STORAGE_DIR,
            "active_backend": "s3" if self._use_s3() else "local",
        }

    async def generate_mock_pdf(self, state: str, document_type: str, data: dict) -> bytes:
        """Generate a simple mock PDF for development"""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas
            buf = io.BytesIO()
            c = canvas.Canvas(buf, pagesize=A4)
            c.drawString(72, 780, f"Government Land Record - {state.title()}")
            c.drawString(72, 760, f"Document Type: {document_type}")
            c.drawString(72, 740, f"Generated: {datetime.now(timezone.utc).isoformat()}")
            y = 700
            for k, v in data.items():
                if y < 100:
                    break
                c.drawString(72, y, f"{k}: {v}")
                y -= 20
            c.save()
            return buf.getvalue()
        except ImportError:
            content = f"Government Land Record - {state}\nDocument: {document_type}\n\n"
            for k, v in data.items():
                content += f"{k}: {v}\n"
            return content.encode()
