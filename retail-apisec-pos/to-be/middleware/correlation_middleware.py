import uuid
import time
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

logger = logging.getLogger("APISec_Observability")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('%(message)s'))
logger.addHandler(handler)

class CorrelationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        start_time = time.time()
        response = await call_next(request)
        elapsed_ms = round((time.time() - start_time) * 1000, 2)
        
        telemetry_record = {
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "correlation_id": correlation_id,
            "client_ip": request.client.host if request.client else "unknown",
            "http_method": request.method,
            "endpoint": request.url.path,
            "status_code": response.status_code,
            "duration_ms": elapsed_ms,
            "service": "retail-pos-api"
        }
        logger.info(json.dumps(telemetry_record))
        response.headers["X-Correlation-ID"] = correlation_id
        return response