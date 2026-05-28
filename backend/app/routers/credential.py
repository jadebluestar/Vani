import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from loguru import logger
import qrcode
import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER

from app.dependencies import get_current_user
from app.database import supabase
from app.services.progress_service import progress_service
from app.utils.formatters import generate_certificate_id

router = APIRouter(prefix="/credential", tags=["Credentials"])


class GenerateCredentialRequest(BaseModel):
    level: Optional[str] = "Beginner"


def generate_qr_code(data: str) -> str:
    """Generate QR code as base64 string."""
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return base64.b64encode(buffered.getvalue()).decode()


@router.post("/generate", summary="Generate a new credential certificate")
async def generate_credential(
    request: GenerateCredentialRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a new credential based on user's progress.
    
    Args:
        request: Level of credential
        current_user: Authenticated user
    Returns:
        Generated credential details
    """
    # Get user's skill scores
    skill_data = await progress_service.get_skill_breakdown(current_user["id"])
    skills = skill_data.get("skills", {})
    
    # Calculate overall score
    scores = [v["score"] for v in skills.values() if v["score"] > 0]
    overall_score = sum(scores) / len(scores) if scores else 0
    
    # Determine level based on score if not specified
    level = request.level
    if not level or level == "Auto":
        if overall_score >= 80:
            level = "Advanced"
        elif overall_score >= 60:
            level = "Intermediate"
        elif overall_score >= 40:
            level = "Beginner"
        else:
            level = "Starter"
    
    certificate_id = generate_certificate_id()
    
    # Get skill names with scores > 50
    earned_skills = [k.capitalize() for k, v in skills.items() if v["score"] > 50]
    if not earned_skills:
        earned_skills = ["Communication Skills"]
    
    credential_data = {
        "user_id": current_user["id"],
        "certificate_id": certificate_id,
        "level": level,
        "skills": earned_skills,
        "overall_score": overall_score,
        "issued_at": datetime.utcnow().isoformat(),
        "verified": False
    }
    
    result = supabase.table("credentials").insert(credential_data).execute()
    credential = result.data[0]
    
    logger.info(f"Credential generated: {certificate_id} for user {current_user['id'][:8]}")
    
    return {
        "success": True,
        "credential": {
            "id": credential["id"],
            "certificate_id": certificate_id,
            "level": level,
            "skills": earned_skills,
            "overall_score": overall_score,
            "issued_at": credential["issued_at"]
        }
    }


@router.get("/list", summary="Get all credentials for current user")
async def list_credentials(
    current_user: dict = Depends(get_current_user)
):
    """
    Return all credentials for the authenticated user.
    
    Args:
        current_user: Authenticated user
    Returns:
        List of credentials
    """
    result = supabase.table("credentials")\
        .select("*")\
        .eq("user_id", current_user["id"])\
        .order("issued_at", desc=True)\
        .execute()
    
    return {
        "success": True,
        "credentials": result.data or [],
        "count": len(result.data or [])
    }


@router.get("/{certificate_id}/verify", summary="Verify a credential publicly")
async def verify_credential(
    certificate_id: str
):
    """
    Public endpoint to verify a credential's authenticity.
    No authentication required.
    
    Args:
        certificate_id: Unique certificate identifier
    Returns:
        Verification result with credential details
    """
    result = supabase.table("credentials")\
        .select("*, users(name, phone)")\
        .eq("certificate_id", certificate_id)\
        .execute()
    
    if not result.data:
        return {
            "success": True,
            "verified": False,
            "message": "Certificate not found or invalid."
        }
    
    credential = result.data[0]
    user_info = credential.get("users", {})
    
    return {
        "success": True,
        "verified": True,
        "certificate_id": credential["certificate_id"],
        "user_name": user_info.get("name", "Anonymous"),
        "level": credential["level"],
        "skills": credential["skills"],
        "issued_at": credential["issued_at"],
        "blockchain_tx_hash": credential.get("blockchain_tx_hash"),
        "verification_url": f"/credential/{certificate_id}/verify"
    }


@router.get("/share/{credential_id}", summary="Get shareable link for credential")
async def get_share_link(
    credential_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate a shareable link and QR code for a credential.
    
    Args:
        credential_id: Credential UUID
        current_user: Authenticated user
    Returns:
        Shareable URL and QR code
    """
    result = supabase.table("credentials")\
        .select("*")\
        .eq("id", credential_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Credential not found.")
    
    credential = result.data[0]
    base_url = "https://vani.app"
    verify_url = f"{base_url}/verify/{credential['certificate_id']}"
    qr_code = generate_qr_code(verify_url)
    
    return {
        "success": True,
        "share_url": verify_url,
        "qr_code": qr_code,
        "certificate_id": credential["certificate_id"]
    }


@router.get("/download/{credential_id}", summary="Download credential as PDF")
async def download_credential(
    credential_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Generate and download credential as PDF.
    
    Args:
        credential_id: Credential UUID
        current_user: Authenticated user
    Returns:
        PDF file
    """
    from fastapi.responses import StreamingResponse
    
    result = supabase.table("credentials")\
        .select("*, users(name)")\
        .eq("id", credential_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Credential not found.")
    
    credential = result.data[0]
    user_info = credential.get("users", {})
    
    # Create PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=24,
        alignment=TA_CENTER,
        spaceAfter=30
    )
    
    content = []
    
    # Title
    content.append(Paragraph("Certificate of Achievement", title_style))
    content.append(Spacer(1, 20))
    
    # Body
    content.append(Paragraph(f"This certificate is awarded to", styles['Normal']))
    content.append(Spacer(1, 10))
    content.append(Paragraph(f"<b>{user_info.get('name', 'Learner')}</b>", styles['Heading2']))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"for demonstrating proficiency in:", styles['Normal']))
    content.append(Spacer(1, 10))
    
    skills_text = ", ".join(credential.get("skills", ["Communication Skills"]))
    content.append(Paragraph(f"<b>{skills_text}</b>", styles['Normal']))
    content.append(Spacer(1, 20))
    content.append(Paragraph(f"Level: <b>{credential.get('level', 'Beginner')}</b>", styles['Normal']))
    content.append(Spacer(1, 30))
    
    # Footer
    content.append(Paragraph(f"Issued on: {credential['issued_at'][:10]}", styles['Normal']))
    content.append(Paragraph(f"Certificate ID: {credential['certificate_id']}", styles['Normal']))
    
    if credential.get("blockchain_tx_hash"):
        content.append(Paragraph(f"Blockchain Verified: Yes", styles['Normal']))
    
    doc.build(content)
    buffer.seek(0)
    
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=certificate_{credential['certificate_id']}.pdf"}
    )