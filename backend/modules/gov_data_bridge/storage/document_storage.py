"""S3 Document Storage - Upload/download PDFs with pre-signed URLs"""
import os
import io
import logging
from datetime import datetime, timezone

logger = logging.getLogger("govdatabridge")

GOV_MOCK_MODE = os.environ.get("GOV_MOCK_MODE", "true").lower() == "true"
S3_BUCKET = os.environ.get("AWS_S3_BUCKET_GOVDOCS", "propertycheckai-govdocs")
AWS_REGION = os.environ.get("AWS_REGION", "ap-south-1")
SIGNED_URL_EXPIRY = int(os.environ.get("GOV_SIGNED_URL_EXPIRY", "86400"))

# Local storage fallback
LOCAL_STORAGE_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "..", "uploads", "gov_records")
os.makedirs(LOCAL_STORAGE_DIR, exist_ok=True)


class DocumentStorage:
    """S3 storage for government record PDFs with local fallback"""

    def __init__(self):
        self.mock_mode = GOV_MOCK_MODE
        self._s3 = None

    def _get_s3_client(self):
        if not self._s3:
            try:
                import boto3
                self._s3 = boto3.client(
                    "s3",
                    region_name=AWS_REGION,
                    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
                    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
                )
            except Exception as e:
                logger.warning(f"S3 client init failed: {e}, using local storage")
                self._s3 = None
        return self._s3

    def _s3_key(self, state: str, document_type: str, job_id: str) -> str:
        return f"gov-records/{state}/{document_type}/{job_id}.pdf"

    async def upload_pdf(self, pdf_bytes: bytes, state: str, document_type: str, job_id: str) -> dict:
        """Upload PDF to S3 or local storage"""
        s3_key = self._s3_key(state, document_type, job_id)

        if not self.mock_mode:
            s3 = self._get_s3_client()
            if s3:
                try:
                    s3.put_object(Bucket=S3_BUCKET, Key=s3_key, Body=pdf_bytes, ContentType="application/pdf")
                    url = self._generate_presigned_url(s3_key)
                    return {"storage": "s3", "s3_key": s3_key, "pdf_url": url, "bucket": S3_BUCKET}
                except Exception as e:
                    logger.error(f"S3 upload failed: {e}, falling back to local")

        # Local storage fallback
        local_path = os.path.join(LOCAL_STORAGE_DIR, state, document_type)
        os.makedirs(local_path, exist_ok=True)
        filepath = os.path.join(local_path, f"{job_id}.pdf")
        with open(filepath, "wb") as f:
            f.write(pdf_bytes)

        return {
            "storage": "local",
            "local_path": filepath,
            "pdf_url": f"/api/gov/download/{state}/{document_type}/{job_id}",
            "s3_key": s3_key,
        }

    def _generate_presigned_url(self, s3_key: str) -> str:
        """Generate pre-signed URL for secure download"""
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
        """Get download URL for existing document"""
        return self._generate_presigned_url(s3_key)

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
            # Simple text-based "PDF" if reportlab not available
            content = f"Government Land Record - {state}\nDocument: {document_type}\n\n"
            for k, v in data.items():
                content += f"{k}: {v}\n"
            return content.encode()
