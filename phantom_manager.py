"""Phantom wallet integration and management"""
import logging
import asyncio
from typing import Dict, Optional, Any
from playwright.async_api import Page

class PhantomTransaction:
    """Represents a Phantom wallet transaction"""
    def __init__(self, type: str, params: Dict[str, Any]):
        self.type = type
        self.params = params
        self.signature: Optional[str] = None
        self.status: str = "pending"
        self.error: Optional[str] = None

class PhantomPopupHandler:
    """Handles Phantom wallet popup interactions"""
    def __init__(self, page: Page):
        self.page = page
        self.logger = logging.getLogger(__name__)
        
    async def wait_for_popup(self, timeout: int = 30000) -> bool:
        """Wait for and detect Phantom popup"""
        try:
            # Wait for Phantom popup iframe
            await self.page.wait_for_selector(
                'iframe[name*="phantom"]',
                timeout=timeout
            )
            return True
        except Exception as e:
            self.logger.error(f"Failed to detect Phantom popup: {e}")
            return False
            
    async def approve_connection(self) -> bool:
        """Approve wallet connection request"""
        try:
            # Wait for and click connect button
            await self.page.frame_locator('iframe[name*="phantom"]').locator(
                'button:has-text("Connect")'
            ).click(timeout=5000)
            return True
        except Exception as e:
            self.logger.error(f"Failed to approve connection: {e}")
            return False
            
    async def approve_transaction(self) -> bool:
        """Approve transaction request"""
        try:
            # Wait for and click approve button
            await self.page.frame_locator('iframe[name*="phantom"]').locator(
                'button:has-text("Approve")'
            ).click(timeout=5000)
            return True
        except Exception as e:
            self.logger.error(f"Failed to approve transaction: {e}")
            return False

class PhantomManager:
    """Manages Phantom wallet interactions"""
    def __init__(self, page: Page):
        self.page = page
        self.popup_handler = PhantomPopupHandler(page)
        self.logger = logging.getLogger(__name__)
        self.connected = False
        self.network = "mainnet-beta"
        
    async def detect_wallet(self) -> bool:
        """Detect if Phantom wallet is installed"""
        try:
            has_phantom = await self.page.evaluate("""
                () => window.solana && window.solana.isPhantom
            """)
            return bool(has_phantom)
        except Exception as e:
            self.logger.error(f"Failed to detect Phantom wallet: {e}")
            return False
            
    async def connect(self) -> bool:
        """Connect to Phantom wallet"""
        if self.connected:
            return True
            
        try:
            # Request connection
            await self.page.evaluate("""
                () => window.solana.connect()
            """)
            
            # Wait for and handle popup
            if await self.popup_handler.wait_for_popup():
                if await self.popup_handler.approve_connection():
                    self.connected = True
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Phantom: {e}")
            return False
            
    async def send_transaction(self, transaction: PhantomTransaction) -> bool:
        """Send transaction to Phantom wallet"""
        if not self.connected:
            self.logger.error("Not connected to wallet")
            return False
            
        try:
            # Format transaction based on type
            tx_data = self._format_transaction(transaction)
            
            # Send transaction
            signature = await self.page.evaluate(f"""
                async () => {{
                    const tx = {tx_data};
                    const signature = await window.solana.signAndSendTransaction(tx);
                    return signature;
                }}
            """)
            
            # Wait for and handle approval popup
            if await self.popup_handler.wait_for_popup():
                if await self.popup_handler.approve_transaction():
                    transaction.signature = signature
                    return True
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to send transaction: {e}")
            transaction.error = str(e)
            return False
            
    def _format_transaction(self, transaction: PhantomTransaction) -> str:
        """Format transaction data for Phantom wallet"""
        # Format based on transaction type
        if transaction.type == "transfer":
            return self._format_transfer(transaction.params)
        elif transaction.type == "token":
            return self._format_token_transfer(transaction.params)
        else:
            raise ValueError(f"Unsupported transaction type: {transaction.type}")
            
    def _format_transfer(self, params: Dict) -> str:
        """Format SOL transfer transaction"""
        return f"""{{
            to: "{params['to']}",
            amount: {params['amount']},
            network: "{self.network}"
        }}"""
        
    def _format_token_transfer(self, params: Dict) -> str:
        """Format SPL token transfer transaction"""
        return f"""{{
            to: "{params['to']}",
            amount: {params['amount']},
            token: "{params['token']}",
            network: "{self.network}"
        }}"""
