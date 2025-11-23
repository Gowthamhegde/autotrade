"""Payment service for Razorpay integration"""
import razorpay
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class PaymentService:
    """Handle payment operations with Razorpay"""
    
    def __init__(self):
        if settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET:
            self.client = razorpay.Client(
                auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
            )
        else:
            self.client = None
            logger.warning("Razorpay credentials not configured")
    
    def create_order(self, amount: float, currency: str = "INR", receipt: str = None):
        """Create a Razorpay order for payment"""
        if not self.client:
            raise Exception("Razorpay not configured")
        
        # Amount in paise (smallest currency unit)
        amount_paise = int(amount * 100)
        
        order_data = {
            'amount': amount_paise,
            'currency': currency,
            'receipt': receipt or f'order_{int(amount)}',
            'payment_capture': 1  # Auto capture
        }
        
        order = self.client.order.create(data=order_data)
        return order
    
    def verify_payment(self, razorpay_order_id: str, razorpay_payment_id: str, razorpay_signature: str):
        """Verify payment signature"""
        if not self.client:
            raise Exception("Razorpay not configured")
        
        try:
            self.client.utility.verify_payment_signature({
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            })
            return True
        except razorpay.errors.SignatureVerificationError:
            return False
    
    def get_payment_details(self, payment_id: str):
        """Get payment details"""
        if not self.client:
            raise Exception("Razorpay not configured")
        
        return self.client.payment.fetch(payment_id)
    
    def initiate_refund(self, payment_id: str, amount: float = None):
        """Initiate refund"""
        if not self.client:
            raise Exception("Razorpay not configured")
        
        refund_data = {}
        if amount:
            refund_data['amount'] = int(amount * 100)
        
        return self.client.payment.refund(payment_id, refund_data)

# Singleton instance
payment_service = PaymentService()
