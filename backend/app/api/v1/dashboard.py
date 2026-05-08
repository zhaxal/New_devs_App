from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, Any, List
from app.services.cache import get_revenue_summary
from app.core.auth import authenticate_request as get_current_user
from app.core.redis_cache import RedisCacheService
from decimal import Decimal

router = APIRouter()
cache_service = RedisCacheService()


async def _get_tenant_properties(tenant_id: str) -> List[Dict[str, Any]]:
    cache_key = f"properties:tenant:{tenant_id}"
    cached = await cache_service.get(cache_key)
    if cached:
        return cached
    
    try:
        from app.core.database_pool import DatabasePool
        db_pool = DatabasePool()
        await db_pool.initialize()
        
        if db_pool.session_factory:
            async with db_pool.get_session() as session:
                from sqlalchemy import text
                query = text("""
                    SELECT id, name, timezone
                    FROM properties
                    WHERE tenant_id = :tenant_id
                    ORDER BY name
                """)
                result = await session.execute(query, {"tenant_id": tenant_id})
                rows = result.fetchall()
                
                if rows:
                    properties = [
                        {"id": row[0], "name": row[1], "timezone": row[2]}
                        for row in rows
                    ]
                    await cache_service.set(cache_key, properties, ttl=1800)
                    return properties
    except Exception as e:
        print(f"Database error: {e}")
    
    seed_data = {
        'tenant-a': [
            {'id': 'prop-001', 'name': 'Beach House Alpha', 'timezone': 'Europe/Paris'},
            {'id': 'prop-002', 'name': 'City Apartment Downtown', 'timezone': 'Europe/Paris'},
            {'id': 'prop-003', 'name': 'Country Villa Estate', 'timezone': 'Europe/Paris'}
        ],
        'tenant-b': [
            {'id': 'prop-001', 'name': 'Mountain Lodge Beta', 'timezone': 'America/New_York'},
            {'id': 'prop-004', 'name': 'Lakeside Cottage', 'timezone': 'America/New_York'},
            {'id': 'prop-005', 'name': 'Urban Loft Modern', 'timezone': 'America/New_York'}
        ]
    }
    
    properties = seed_data.get(tenant_id, [])
    if properties:
        await cache_service.set(cache_key, properties, ttl=1800)
    return properties


async def _is_property_owned_by_tenant(property_id: str, tenant_id: str) -> bool:
    properties = await _get_tenant_properties(tenant_id)
    return any(p['id'] == property_id for p in properties)


@router.get("/dashboard/properties")
async def get_dashboard_properties(
    current_user: dict = Depends(get_current_user)
) -> List[Dict[str, Any]]:
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    return await _get_tenant_properties(tenant_id)


@router.get("/dashboard/summary")
async def get_dashboard_summary(
    property_id: str = Query(...),
    current_user: dict = Depends(get_current_user)
) -> Dict[str, Any]:
    tenant_id = getattr(current_user, "tenant_id", "default_tenant") or "default_tenant"
    
    if not await _is_property_owned_by_tenant(property_id, tenant_id):
        raise HTTPException(
            status_code=403,
            detail=f"Property {property_id} not owned by tenant {tenant_id}"
        )
    
    revenue_data = await get_revenue_summary(property_id, tenant_id)
    total_revenue = Decimal(revenue_data['total'])
    
    return {
        "property_id": revenue_data['property_id'],
        "total_revenue": float(total_revenue),
        "currency": revenue_data['currency'],
        "reservations_count": revenue_data['count']
    }
