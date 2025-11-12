"""
Organizations Service client for external API communication.
Handles communication with the Organizations Service to update employee data.
"""
import logging
from uuid import UUID
from typing import Optional
import httpx
from app.config import get_settings

# Configure logging
logger = logging.getLogger(__name__)


async def update_employee_has_account(
    organization_id: UUID,
    employee_id: UUID,
    has_account: bool,
    auth_token: str
) -> bool:
    """
    Update the hasAccount attribute for an employee in the Organizations Service.
    
    Args:
        organization_id: UUID of the organization
        employee_id: UUID of the employee (entity_id)
        has_account: Boolean value to set for hasAccount
        auth_token: JWT Bearer token for authentication
        
    Returns:
        bool: True if update was successful, False otherwise
        
    Raises:
        httpx.HTTPStatusError: If the request fails with an HTTP error
        httpx.RequestError: If there's a network-related error
    """
    settings = get_settings()
    url = f"{settings.organizations_service_url}/organizations/{organization_id}/employees/{employee_id}"
    
    headers = {
        "Content-Type": "application/merge-patch+json",
        "Authorization": f"Bearer {auth_token}"
    }
    
    payload = {
        "hasAccount": has_account
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            logger.info(
                f"Updating employee {employee_id} in organization {organization_id} - hasAccount={has_account}"
            )
            
            response = await client.patch(url, json=payload, headers=headers)
            response.raise_for_status()
            
            logger.info(
                f"Successfully updated employee {employee_id} - hasAccount={has_account}"
            )
            return True
            
    except httpx.HTTPStatusError as e:
        logger.error(
            f"HTTP error updating employee {employee_id}: {e.response.status_code} - {e.response.text}"
        )
        raise
        
    except httpx.RequestError as e:
        logger.error(
            f"Network error updating employee {employee_id}: {str(e)}"
        )
        raise
        
    except Exception as e:
        logger.error(
            f"Unexpected error updating employee {employee_id}: {str(e)}"
        )
        raise
