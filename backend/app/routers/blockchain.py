from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from loguru import logger

from app.dependencies import get_current_user
from app.services.blockchain_service import blockchain_service
from app.database import supabase

router = APIRouter(prefix="/blockchain", tags=["Blockchain"])


class MintRequest(BaseModel):
    credential_id: str


@router.post("/mint", summary="Mint credential NFT on Solana blockchain")
async def mint_credential(
    request: MintRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Mint a credential as an NFT on Solana devnet.
    
    Args:
        request: Credential ID to mint
        current_user: Authenticated user
    Returns:
        Transaction hash and explorer URL
    """
    # Get credential from database
    result = supabase.table("credentials")\
        .select("*")\
        .eq("id", request.credential_id)\
        .eq("user_id", current_user["id"])\
        .execute()
    
    if not result.data:
        raise HTTPException(status_code=404, detail="Credential not found.")
    
    credential = result.data[0]
    
    if credential.get("blockchain_tx_hash"):
        raise HTTPException(status_code=400, detail="Credential already minted on blockchain.")
    
    try:
        tx_hash, explorer_url = await blockchain_service.mint_credential(
            user_id=current_user["id"],
            certificate_id=credential["certificate_id"],
            skills=credential.get("skills", []),
            level=credential.get("level", "Beginner")
        )
        
        # Update credential with transaction hash
        supabase.table("credentials")\
            .update({
                "blockchain_tx_hash": tx_hash,
                "verified": True
            })\
            .eq("id", request.credential_id)\
            .execute()
        
        logger.info(f"Credential {credential['certificate_id']} minted on Solana: {tx_hash}")
        
        return {
            "success": True,
            "transaction_hash": tx_hash,
            "explorer_url": explorer_url,
            "credential_id": credential["certificate_id"]
        }
    except Exception as e:
        logger.error(f"Blockchain mint error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to mint credential: {str(e)}")


@router.get("/status/{tx_hash}", summary="Check blockchain transaction status")
async def get_transaction_status(
    tx_hash: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Check the status of a Solana transaction.
    
    Args:
        tx_hash: Transaction hash to check
        current_user: Authenticated user
    Returns:
        Transaction status with confirmations
    """
    try:
        status = await blockchain_service.check_transaction_status(tx_hash)
        return {"success": True, "status": status}
    except Exception as e:
        logger.error(f"Transaction status check error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check transaction status: {str(e)}")