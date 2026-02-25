"""
Wallet management using Magic + unju credits system
"""
import os
import json
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from eth_account import Account

# TODO: Import actual Magic SDK and unju-python SDK
# from magic_admin import Magic
# from unju import CreditsClient


class WalletManager:
    """
    Manages user wallets using Magic server wallets.
    Charges unju credits for wallet creation and rent.
    """
    
    def __init__(self):
        # Initialize Magic (TODO: use actual Magic SDK)
        self.magic_api_key = os.getenv("MAGIC_API_KEY")
        # self.magic = Magic(api_secret_key=self.magic_api_key)
        
        # Initialize unju credits client (TODO: use actual SDK)
        # self.credits = CreditsClient()
        
        # For now, store wallet info in memory (TODO: use database)
        self.wallets: Dict[str, Dict[str, Any]] = {}
    
    def create_wallet(self, email: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Create a new Magic wallet for user and charge 1 credit.
        
        Args:
            email: User email
            user_id: Optional user ID
        
        Returns:
            Wallet info including address and rent due date
        
        Raises:
            Exception: If insufficient credits or wallet creation fails
        """
        # TODO: Check user has at least 1 credit
        # if not self.credits.check_balance(user_id, amount=1):
        #     raise Exception("Insufficient credits. Need 1 credit to create wallet.")
        
        # TODO: Create Magic wallet
        # wallet = self.magic.wallet.create(email=email)
        # address = wallet.public_address
        
        # For now, create a test wallet
        account = Account.create()
        address = account.address
        private_key = account.key.hex()
        
        # Calculate next rent due (1 year from now)
        next_rent_due = datetime.utcnow() + timedelta(days=365)
        
        # Store wallet info
        self.wallets[address] = {
            "email": email,
            "user_id": user_id,
            "address": address,
            "private_key": private_key,  # TODO: Store securely in Magic
            "created_at": datetime.utcnow().isoformat(),
            "next_rent_due": next_rent_due.isoformat(),
            "credits_remaining": 10,  # Annual rent credits
            "active": True
        }
        
        # TODO: Charge 1 credit for wallet creation
        # self.credits.charge(user_id, amount=1, reason="Wallet creation")
        
        return {
            "address": address,
            "next_rent_due": next_rent_due.isoformat(),
            "credits_charged": 1
        }
    
    def get_wallet_info(self, address: str) -> Dict[str, Any]:
        """Get wallet information."""
        wallet_info = self.wallets.get(address, {})
        
        if not wallet_info:
            # Check if wallet exists from env var
            if address == os.getenv("HYPERLIQUID_ADDRESS"):
                return {
                    "address": address,
                    "active": True,
                    "credits_remaining": 999,
                    "next_rent_due": (datetime.utcnow() + timedelta(days=365)).isoformat(),
                    "source": "environment"
                }
        
        return wallet_info
    
    def check_rent_due(self, address: str) -> bool:
        """Check if wallet rent is due."""
        wallet_info = self.wallets.get(address)
        if not wallet_info:
            return False
        
        next_rent_due = datetime.fromisoformat(wallet_info["next_rent_due"])
        return datetime.utcnow() >= next_rent_due
    
    def charge_rent(self, address: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Charge annual rent (10 credits) for wallet.
        
        Args:
            address: Wallet address
            user_id: User ID
        
        Returns:
            Updated wallet info
        
        Raises:
            Exception: If insufficient credits
        """
        wallet_info = self.wallets.get(address)
        if not wallet_info:
            raise Exception("Wallet not found")
        
        # TODO: Check user has at least 10 credits
        # if not self.credits.check_balance(user_id, amount=10):
        #     raise Exception("Insufficient credits. Need 10 credits for annual rent.")
        
        # TODO: Charge 10 credits
        # self.credits.charge(user_id, amount=10, reason="Wallet annual rent")
        
        # Update next rent due
        next_rent_due = datetime.utcnow() + timedelta(days=365)
        wallet_info["next_rent_due"] = next_rent_due.isoformat()
        wallet_info["credits_remaining"] = 10
        
        return wallet_info
    
    def get_or_create_wallet(
        self,
        email: str,
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get existing wallet or create new one."""
        # Check if user already has a wallet
        for address, info in self.wallets.items():
            if info.get("email") == email or info.get("user_id") == user_id:
                return info
        
        # Create new wallet
        return self.create_wallet(email, user_id)
