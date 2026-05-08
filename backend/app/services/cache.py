import json
import redis.asyncio as redis
from typing import Dict, Any
import os

redis_client = redis.Redis.from_url(
    os.getenv("REDIS_URL", "redis://localhost:6379/0")
)


async def get_revenue_summary(property_id: str, tenant_id: str) -> Dict[str, Any]:

    cache_key = f"revenue:{tenant_id}:{property_id}"
    

    cached_result = await redis_client.get(cache_key)
    if cached_result:
        return json.loads(cached_result)
    

    from app.services.reservations import calculate_total_revenue
    

    revenue_data = await calculate_total_revenue(property_id, tenant_id)
    

    await redis_client.setex(
        cache_key,
        300,  
        json.dumps(revenue_data)
    )
    
    return revenue_data
