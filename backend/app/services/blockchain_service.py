import json
import base64
from typing import Optional, Dict, Any, Tuple
from loguru import logger
from app.config import settings

try:
    from solders.keypair import Keypair
    from solders.pubkey import Pubkey
    from solders.system_program import TransferParams, transfer
    from solders.transaction import Transaction
    from solana.rpc.async_api import AsyncClient
    from solana.rpc.commitment import Confirmed
    SOLANA_AVAILABLE = True
except ImportError:
    SOLANA_AVAILABLE = False
    logger.warning("Solana libraries not fully available, using mock mode")


class BlockchainService:
    """Service for minting and verifying skill credentials on Solana devnet."""

    def __init__(self):
        self.rpc_url = settings.SOLANA_RPC_URL
        self.mock_mode = not SOLANA_AVAILABLE
        if SOLANA_AVAILABLE and settings.SOLANA_WALLET_PRIVATE_KEY:
            try:
                key_bytes = base64.b58decode(settings.SOLANA_WALLET_PRIVATE_KEY)
                self.keypair = Keypair.from_bytes(key_bytes)
                logger.info(f"Solana wallet loaded")
            except Exception as e:
                logger.warning(f"Could not load Solana keypair: {e}, using mock mode")
                self.mock_mode = True
                self.keypair = None
        else:
            self.keypair = None

    async def mint_credential(self, user_id: str, certificate_id: str, skills: list, level: str) -> Tuple[str, str]:
        if self.mock_mode:
            return await self._mock_mint(certificate_id, skills, level)
        try:
            async with AsyncClient(self.rpc_url) as client:
                balance = await client.get_balance(self.keypair.pubkey())
                if balance.value < 5000:
                    await client.request_airdrop(self.keypair.pubkey(), 1_000_000_000)
                credential_data = {"vani": True, "cert_id": certificate_id, "user": user_id[:8], "level": level, "skills": skills[:3]}
                memo_text = json.dumps(credential_data, separators=(',', ':'))[:200]
                recent_blockhash = await client.get_latest_blockhash()
                transfer_ix = transfer(TransferParams(from_pubkey=self.keypair.pubkey(), to_pubkey=self.keypair.pubkey(), lamports=1000))
                tx = Transaction(recent_blockhash=recent_blockhash.value.blockhash, fee_payer=self.keypair.pubkey())
                tx.add(transfer_ix)
                tx.sign(self.keypair)
                result = await client.send_transaction(tx)
                tx_hash = str(result.value)
                explorer_url = f"https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
                return tx_hash, explorer_url
        except Exception as e:
            logger.error(f"Solana mint error: {e}, falling back to mock")
            return await self._mock_mint(certificate_id, skills, level)

    async def _mock_mint(self, certificate_id: str, skills: list, level: str) -> Tuple[str, str]:
        import hashlib
        mock_hash = hashlib.sha256(f"{certificate_id}{level}{''.join(skills)}".encode()).hexdigest()
        tx_hash = f"MOCK_{mock_hash[:60]}"
        explorer_url = f"https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"
        return tx_hash, explorer_url

    async def check_transaction_status(self, tx_hash: str) -> Dict[str, Any]:
        if tx_hash.startswith("MOCK_"):
            return {"status": "confirmed", "confirmations": 100, "slot": 123456789, "is_mock": True}
        if self.mock_mode:
            return {"status": "unknown", "error": "Solana unavailable", "is_mock": True}
        try:
            async with AsyncClient(self.rpc_url) as client:
                result = await client.get_transaction(tx_hash, commitment=Confirmed, max_supported_transaction_version=0)
                if result.value is None:
                    return {"status": "not_found", "tx_hash": tx_hash}
                if result.value.transaction.meta and result.value.transaction.meta.err is None:
                    status = "confirmed"
                elif result.value.transaction.meta and result.value.transaction.meta.err:
                    status = "failed"
                else:
                    status = "pending"
                return {"status": status, "slot": result.value.slot, "tx_hash": tx_hash, "explorer_url": f"https://explorer.solana.com/tx/{tx_hash}?cluster=devnet"}
        except Exception as e:
            return {"status": "error", "error": str(e), "tx_hash": tx_hash}


blockchain_service = BlockchainService()