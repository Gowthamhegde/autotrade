from app.core.config import settings
from app.brokers.mock import MockBroker

def get_broker():
    """Factory to return appropriate broker based on config"""
    # print(f"DEBUG: BROKER_MODE is {settings.BROKER_MODE}")
    if settings.BROKER_MODE == "mock":
        return MockBroker()
    elif settings.BROKER_MODE == "paper":
        from app.brokers.paper import PaperBroker
        return PaperBroker()
    elif settings.BROKER_MODE == "zerodha":
        # from app.brokers.zerodha import ZerodhaBroker
        # return ZerodhaBroker()
        raise NotImplementedError("Zerodha broker not yet implemented")
    else:
        raise ValueError(f"Unknown broker mode: {settings.BROKER_MODE}")
