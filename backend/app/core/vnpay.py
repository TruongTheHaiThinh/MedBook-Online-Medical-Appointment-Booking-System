import hmac
import hashlib
import urllib.parse
from datetime import datetime

class VNPay:
    def __init__(self, tmn_code, hash_secret, payment_url):
        self.tmn_code = tmn_code
        self.hash_secret = hash_secret
        self.payment_url = payment_url
        self.request_data = {}
        self.response_data = {}

    def get_payment_url(self, vnp_TxnRef, vnp_Amount, vnp_OrderInfo, vnp_OrderType, vnp_ReturnUrl, vnp_IpAddr, vnp_BankCode=None):
        self.request_data = {
            "vnp_Version": "2.1.0",
            "vnp_Command": "pay",
            "vnp_TmnCode": self.tmn_code,
            "vnp_Amount": str(int(vnp_Amount) * 100),
            "vnp_CurrCode": "VND",
            "vnp_TxnRef": str(vnp_TxnRef),
            "vnp_OrderInfo": str(vnp_OrderInfo),
            "vnp_OrderType": str(vnp_OrderType),
            "vnp_Locale": "vn",
            "vnp_ReturnUrl": vnp_ReturnUrl,
            "vnp_IpAddr": vnp_IpAddr,
            "vnp_CreateDate": datetime.now().strftime("%Y%m%d%H%M%S"),
        }
        if vnp_BankCode:
            self.request_data["vnp_BankCode"] = str(vnp_BankCode)
        
        # Sort data
        input_data = sorted(self.request_data.items())
        
        # Build query string manually with quote_plus exactly like the official Python demo
        query_parts = []
        for key, val in input_data:
            query_parts.append(f"{key}={urllib.parse.quote_plus(str(val))}")
        query_string = "&".join(query_parts)
        
        # Generate hash
        secure_hash = self.__hmacsha512(self.hash_secret, query_string)
        
        return f"{self.payment_url}?{query_string}&vnp_SecureHash={secure_hash}"

    def validate_response(self, secret_key):
        vnp_SecureHash = self.response_data.get("vnp_SecureHash")
        # Remove hash from data to verify
        if "vnp_SecureHash" in self.response_data:
            self.response_data.pop("vnp_SecureHash")
        if "vnp_SecureHashType" in self.response_data:
            self.response_data.pop("vnp_SecureHashType")

        # Sort and build query with vnp_ prefixed parameters only, using quote_plus like demo
        input_data = sorted(self.response_data.items())
        
        query_parts = []
        for key, val in input_data:
            if str(key).startswith("vnp_"):
                # Handle cases where value is a list (FastAPI MultiDict can have list values)
                val_str = val[0] if isinstance(val, list) else val
                query_parts.append(f"{key}={urllib.parse.quote_plus(str(val_str))}")
        
        query_string = "&".join(query_parts)
        
        # Calculate expected hash
        check_hash = self.__hmacsha512(secret_key, query_string)
        
        print(f"[VNPAY VALIDATION DEBUG] QueryString: {query_string} | ExpectedHash: {check_hash} | ReceivedHash: {vnp_SecureHash}")
        
        return vnp_SecureHash == check_hash

    def __hmacsha512(self, key, data):
        byte_key = key.encode("utf-8")
        byte_data = data.encode("utf-8")
        return hmac.new(byte_key, byte_data, hashlib.sha512).hexdigest()

