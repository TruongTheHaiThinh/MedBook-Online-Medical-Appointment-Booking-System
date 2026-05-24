import asyncio
import traceback
from app.core.email import send_reset_password_email

async def test():
    try:
        print("Sending test email to thinhtruongclone1@gmail.com...")
        await send_reset_password_email("thinhtruongclone1@gmail.com", "Thinh Truong Clone", "test-token-123456")
        print("TEST RUN COMPLETED SUCCESS")
    except Exception as e:
        print("TEST FAILED WITH EXCEPTION:")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test())
