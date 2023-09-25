import logging
from typing import Optional, List
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db.models import Q
from fastapi import APIRouter, HTTPException, Query

from ix.api.chains.endpoints import DeletedItem
from ix.chains.models import NodeType
from ix.api.components.types import NodeType as NodeTypePydantic, NodeTypePage

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/node_types/", response_model=NodeTypePage, tags=["Components"])
async def get_node_types(
    search: Optional[str] = None,
    types: Optional[List[str]] = Query(None, alias="types"),
    limit: int = 50,
    offset: int = 0,
):
    if search:
        query = NodeType.objects.filter(
            Q(name__icontains=search)
            | Q(description__icontains=search)
            | Q(type__icontains=search)
            | Q(class_path__icontains=search)
        )
    else:
        query = NodeType.objects.all()

    if types:
        query = query.filter(type__in=types)

    # punting on async implementation of pagination until later
    return await sync_to_async(NodeTypePage.paginate)(
        output_model=NodeTypePydantic, queryset=query, limit=limit, offset=offset
    )


class NodeTypeDetail(NodeTypePydantic):
    config_schema: Optional[dict] = None


@router.get(
    "/node_types/{node_type_id}", response_model=NodeTypeDetail, tags=["Components"]
)
async def get_node_type_detail(node_type_id: UUID):
    try:
        node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")
    return NodeTypeDetail.from_orm(node_type)


@router.post("/node_types/", response_model=NodeTypePydantic, tags=["Components"])
async def create_node_type(node_type: NodeTypePydantic):
    node_type_obj = NodeType(**node_type.dict())
    await node_type_obj.asave()
    return NodeTypePydantic.from_orm(node_type_obj)


@router.put(
    "/node_types/{node_type_id}", response_model=NodeTypePydantic, tags=["Components"]
)
async def update_node_type(node_type_id: UUID, node_type: NodeTypePydantic):
    try:
        existing_node_type = await NodeType.objects.aget(id=node_type_id)
    except NodeType.DoesNotExist:
        raise HTTPException(status_code=404, detail="Node type not found")

    for field, value in node_type.dict(exclude_unset=True).items():
        setattr(existing_node_type, field, value)

    await existing_node_type.asave()
    return NodeTypePydantic.from_orm(existing_node_type)


@router.delete(
    "/node_types/{node_type_id}", response_model=DeletedItem, tags=["Components"]
)
async def delete_node_type(node_type_id: UUID):
    query = NodeType.objects.filter(id=node_type_id)
    if not await query.aexists():
        raise HTTPException(status_code=404, detail="Node type not found")

    await query.adelete()
    return DeletedItem(id=node_type_id)
