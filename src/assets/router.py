"""
资源路由

定义资源相关的 API 端点。
"""

from fastapi import APIRouter, Query

from src.core.schemas import ApiResponse, ListResponse

from .dependencies import ServiceDep
from .schemas import (
    AssetCreate,
    AssetImportResponse,
    AssetResponse,
    AssetUpdate,
)

router = APIRouter()


@router.get("/list", summary="获取资源列表", response_model=ApiResponse[ListResponse[AssetResponse]])
async def list_assets(
    service: ServiceDep,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    drama_id: int | None = Query(None, description="剧目 ID 过滤"),
    episode_id: int | None = Query(None, description="集数 ID 过滤"),
    type: str | None = Query(None, description="资源类型过滤"),
    category: str | None = Query(None, description="分类过滤"),
):
    """
    获取资源列表（支持分页和过滤）

    支持按剧目、集数、类型和分类过滤资源。
    """
    skip = (page - 1) * page_size
    items, total = await service.get_list(
        skip=skip,
        limit=page_size,
        drama_id=drama_id,
        episode_id=episode_id,
        asset_type=type,
        category=category,
    )

    return ApiResponse.success(data=ListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/info", summary="获取资源详情", response_model=ApiResponse[AssetResponse])
async def get_asset(
    service: ServiceDep,
    asset_id: int = Query(..., description="资源 ID"),
):
    """
    根据 ID 获取资源详情

    获取指定 ID 的资源的完整信息，同时增加浏览次数。
    """
    asset = await service.get_by_id(asset_id)
    return ApiResponse.success(data=asset)


@router.post("/create", summary="创建资源", response_model=ApiResponse[AssetResponse])
async def create_asset(
    data: AssetCreate,
    service: ServiceDep,
):
    """
    创建新资源

    添加新的资源到系统中。
    """
    asset = await service.create(data)
    return ApiResponse.success(
        data=asset,
        message="资源创建成功"
    )


@router.post("/update", summary="更新资源", response_model=ApiResponse[AssetResponse])
async def update_asset(
    service: ServiceDep,
    asset_id: int = Query(..., description="资源 ID"),
    data: AssetUpdate = None,
):
    """
    更新资源信息

    更新指定 ID 的资源信息。
    """
    asset = await service.update(asset_id, data)
    return ApiResponse.success(
        data=asset,
        message="资源更新成功"
    )


@router.post("/delete", summary="删除资源", response_model=ApiResponse)
async def delete_asset(
    service: ServiceDep,
    asset_id: int = Query(..., description="资源 ID"),
):
    """
    删除资源

    从系统中删除指定 ID 的资源。
    """
    await service.delete(asset_id)
    return ApiResponse.success(
        data={"asset_id": asset_id},
        message="资源删除成功"
    )


@router.post("/import/image", summary="从图片生成导入资源", response_model=ApiResponse[AssetImportResponse])
async def import_from_image_gen(
    service: ServiceDep,
    image_gen_id: int = Query(..., description="图片生成 ID"),
    name: str = Query(..., description="资源名称"),
    description: str | None = Query(None, description="资源描述"),
    category: str | None = Query(None, description="分类"),
):
    """
    从图片生成记录导入资源

    将已生成的图片导入为资源，便于管理和复用。
    """
    asset = await service.import_from_image_gen(
        image_gen_id=image_gen_id,
        name=name,
        description=description,
        category=category,
    )

    return ApiResponse.success(
        data=AssetImportResponse(
            asset_id=asset.id,
            gen_id=image_gen_id,
            message="资源导入成功"
        ),
        message="图片资源已导入"
    )


@router.post("/import/video", summary="从视频生成导入资源", response_model=ApiResponse[AssetImportResponse])
async def import_from_video_gen(
    service: ServiceDep,
    video_gen_id: int = Query(..., description="视频生成 ID"),
    name: str = Query(..., description="资源名称"),
    description: str | None = Query(None, description="资源描述"),
    category: str | None = Query(None, description="分类"),
):
    """
    从视频生成记录导入资源

    将已生成的视频导入为资源，便于管理和复用。
    """
    asset = await service.import_from_video_gen(
        video_gen_id=video_gen_id,
        name=name,
        description=description,
        category=category,
    )

    return ApiResponse.success(
        data=AssetImportResponse(
            asset_id=asset.id,
            gen_id=video_gen_id,
            message="资源导入成功"
        ),
        message="视频资源已导入"
    )
