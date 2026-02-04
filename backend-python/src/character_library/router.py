"""
角色库路由

定义角色库相关的 API 端点。
"""
from typing import Optional
from fastapi import APIRouter, Query, BackgroundTasks

from src.schemas import ApiResponse, ListResponse, ResponseCode
from .schemas import (
    CharacterLibraryCreate,
    CharacterLibraryUpdate,
    CharacterLibraryResponse,
    CharacterImageGenerate,
    BatchCharacterImageGenerate,
)
from .service import CharacterLibraryService
from .dependencies import ServiceDep, LibraryItemDep, CharacterDep
from .exceptions import CharacterLibraryNotFound, CharacterNotFound, CharacterHasNoImage

router = APIRouter()


@router.get("/list", summary="获取角色库列表", response_model=ApiResponse[ListResponse[CharacterLibraryResponse]])
async def list_character_library(
    service: ServiceDep,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    category: Optional[str] = Query(None, description="分类过滤"),
    source_type: Optional[str] = Query(None, description="来源类型过滤"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
):
    """
    获取角色库列表（支持分页和过滤）

    支持按分类、来源类型和关键词过滤角色库项。
    """
    skip = (page - 1) * page_size
    items, total = await service.get_list(
        skip=skip,
        limit=page_size,
        category=category,
        source_type=source_type,
        keyword=keyword,
    )

    return ApiResponse.success(data=ListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/info", summary="获取角色库详情", response_model=ApiResponse[CharacterLibraryResponse])
async def get_library_item(
    service: ServiceDep,
    item_id: int = Query(..., description="角色库项 ID"),
):
    """
    根据 ID 获取角色库项详情

    获取指定 ID 的角色库项的完整信息。
    """
    item = await service.get_by_id(item_id)
    return ApiResponse.success(data=item)


@router.post("/create", summary="创建角色库项", response_model=ApiResponse[CharacterLibraryResponse])
async def create_library_item(
    data: CharacterLibraryCreate,
    service: ServiceDep,
):
    """
    创建新的角色库项

    添加新的角色到角色库中。
    """
    item = await service.create(data)
    return ApiResponse.success(
        data=item,
        message="角色库项创建成功"
    )


@router.post("/update", summary="更新角色库项", response_model=ApiResponse[CharacterLibraryResponse])
async def update_library_item(
    service: ServiceDep,
    item_id: int = Query(..., description="角色库项 ID"),
    data: CharacterLibraryUpdate = None,
):
    """
    更新角色库项

    更新指定 ID 的角色库项信息。
    """
    item = await service.update(item_id, data)
    return ApiResponse.success(
        data=item,
        message="角色库项更新成功"
    )


@router.post("/delete", summary="删除角色库项", response_model=ApiResponse)
async def delete_library_item(
    service: ServiceDep,
    item_id: int = Query(..., description="角色库项 ID"),
):
    """
    删除角色库项

    从角色库中删除指定 ID 的项。
    """
    await service.delete(item_id)
    return ApiResponse.success(message="角色库项删除成功")


@router.post("/batch-generate-images", summary="批量生成角色图片", response_model=ApiResponse)
async def batch_generate_character_images(
    request: BatchCharacterImageGenerate,
    background_tasks: BackgroundTasks,
    service: ServiceDep,
):
    """
    批量生成角色图片

    为多个角色批量生成图片。实际生成在后台任务中执行。
    """
    tasks = await service.batch_generate_character_images(request.character_ids)

    return ApiResponse.success(
        data={
            "tasks": tasks,
        },
        message=f"已开始为 {len(request.character_ids)} 个角色生成图片"
    )


@router.post("/characters/generate-image", summary="生成角色图片", response_model=ApiResponse)
async def generate_character_image(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
    request: CharacterImageGenerate = None,
    background_tasks: BackgroundTasks = None,
):
    """
    生成角色图片

    为指定角色生成图片。实际生成在后台任务中执行。
    """
    result = await service.generate_character_image(character_id)

    return ApiResponse.success(
        data=result,
        message="图片生成任务已开始"
    )


@router.post("/characters/update-image", summary="更新角色图片", response_model=ApiResponse)
async def update_character_image(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
    image_url: str = Query(..., description="图片 URL"),
):
    """
    更新角色图片

    更新指定角色的图片 URL。
    """
    character = await service.update_character_image(character_id, image_url)

    return ApiResponse.success(
        data={
            "character_id": character.id,
            "image_url": character.image_url,
        },
        message="角色图片更新成功"
    )


@router.post("/characters/apply-library-image", summary="应用角色库图片到角色", response_model=ApiResponse)
async def apply_library_image_to_character(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
    library_item_id: int = Query(..., description="角色库项 ID"),
):
    """
    应用角色库图片到角色

    将角色库中的图片应用到指定角色。
    """
    result = await service.apply_library_image_to_character(character_id, library_item_id)

    return ApiResponse.success(
        data=result,
        message="角色库图片已应用到角色"
    )


@router.post("/characters/add-to-library", summary="将角色添加到角色库", response_model=ApiResponse)
async def add_character_to_library(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
    name: Optional[str] = Query(None, description="自定义名称"),
    category: Optional[str] = Query(None, description="分类"),
):
    """
    将角色添加到角色库

    将指定角色添加到角色库中，角色必须已有图片。
    """
    result = await service.add_character_to_library(character_id, name, category)

    return ApiResponse.success(
        data=result,
        message="角色已添加到角色库"
    )


@router.post("/characters/update", summary="更新角色信息", response_model=ApiResponse)
async def update_character(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
    name: Optional[str] = Query(None, description="名称"),
    role: Optional[str] = Query(None, description="角色"),
    description: Optional[str] = Query(None, description="描述"),
    appearance: Optional[str] = Query(None, description="外貌"),
    personality: Optional[str] = Query(None, description="性格"),
    voice_style: Optional[str] = Query(None, description="声音风格"),
):
    """
    更新角色信息

    更新指定角色的详细信息。
    """
    character = await service.update_character(
        character_id, name, role, description, appearance, personality, voice_style
    )

    return ApiResponse.success(
        data={"character_id": character.id},
        message="角色信息更新成功"
    )


@router.post("/characters/delete", summary="删除角色", response_model=ApiResponse)
async def delete_character(
    service: ServiceDep,
    character_id: int = Query(..., description="角色 ID"),
):
    """
    删除角色

    从数据库中删除指定角色。
    """
    await service.delete_character(character_id)

    return ApiResponse.success(
        data={"character_id": character_id},
        message="角色删除成功"
    )
