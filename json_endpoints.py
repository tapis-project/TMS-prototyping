from fastapi import APIRouter, Security
from pydantic import BaseModel
from fastapi import Depends
from fastapi.security import APIKeyHeader

router = APIRouter(
    tags=["JSON Endpoints"], dependencies=[Security(APIKeyHeader(name="x-tms-token"))]
)


class ProviderResponse(BaseModel):
    id: str
    name: str
    institution: str | None = None
    description: str | None = None
    location: str | None = None
    is_linked: bool = False


class SystemResponse(BaseModel):
    id: str
    name: str
    resource_type: str = "compute"
    description: str | None = None
    is_linked: bool = False


provider_response_fixture = [
    {
        "id": "rp_tacc",
        "name": "TACC",
        "institution": "UT Austin",
        "description": "TACC provides large-scale computing resources for open science research.",
        "location": "Austin, TX, USA",
        "is_linked": True,
    },
    {
        "id": "rp_sdsc",
        "name": "San Diego Supercomputer Center (SDSC)",
        "institution": "UC San Diego",
        "description": "SDSC operates HPC systems designed for science gateways.",
        "location": "San Diego, CA, USA",
        "is_linked": False,
    },
]

system_response_fixture = [
    {
        "id": "expanse",
        "name": "Expanse",
        "resource_type": "compute",
        "is_linked": False,
        "description": "Expanse supports SDSC's vision of “Computing without Boundaries” by increasing the capacity and performance for thousands of users of batch-oriented and science gateway computing.",
    },
    {
        "id": "voyager",
        "name": "Voyager",
        "resource_type": "compute",
        "is_linked": True,
        "description": "Voyager is an innovative AI system designed specifically for science and engineering research at scale.",
    },
]


@router.get("/providers", response_model=list[ProviderResponse])
def get_providers_for_user():
    return [ProviderResponse(**f) for f in provider_response_fixture]


@router.put("/providers/{provider_id}", response_model=list[ProviderResponse])
def link_provider_identity_to_user_identity():
    return [ProviderResponse(**f) for f in provider_response_fixture]


@router.delete(
    "/providers/{provider_id}/{provider_user_id}", response_model=list[ProviderResponse]
)
def unlink_provider_identity_from_user_identity():
    return [ProviderResponse(**f) for f in provider_response_fixture]


@router.get(
    "/systems/{provider_id}/{provider_user_id}", response_model=list[SystemResponse]
)
def get_systems_for_provider():
    return [SystemResponse(**s) for s in system_response_fixture]


@router.put("/systems/{provider_id}/{system_id}", response_model=list[SystemResponse])
def link_system():
    return [SystemResponse(**s) for s in system_response_fixture]


@router.delete(
    "/systems/{provider_id}/{provider_user_id}/{system_id}",
    response_model=list[SystemResponse],
)
def unlink_system():
    return [SystemResponse(**s) for s in system_response_fixture]
