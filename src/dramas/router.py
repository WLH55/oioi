"""
剧目路由

定义剧目相关的 API 端点。
"""
from fastapi import APIRouter, Query

from src.core.schemas import ApiResponse, ListResponse

from .dependencies import ServiceDep
from .schemas import (
    BatchCharactersSave,
    BatchEpisodesSave,
    CharacterResponse,
    DramaCreate,
    DramaResponse,
    DramaStats,
    DramaUpdate,
    EpisodeResponse,
    OutlineSave,
    ProgressSave,
)

router = APIRouter()


# ========== 剧目接口 ==========

@router.get("/list", summary="获取剧目列表", response_model=ApiResponse[ListResponse[DramaResponse]])
async def list_dramas(
    service: ServiceDep,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
):
    """
    获取剧目列表（分页）

    返回所有剧目的分页列表，按创建时间倒序排列。
    """
    skip = (page - 1) * page_size
    items, total = await service.get_list(skip=skip, limit=page_size)

    return ApiResponse.success(data=ListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    ))


@router.get("/info", summary="获取剧目详情", response_model=ApiResponse[DramaResponse])
async def get_drama(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
):
    """
    根据 ID 获取剧目详情

    获取指定 ID 的剧目的完整信息。
    """
    drama = await service.get_by_id(drama_id)
    return ApiResponse.success(data=drama)


@router.post("/create", summary="创建剧目", response_model=ApiResponse[DramaResponse])
async def create_drama(
    data: DramaCreate,
    service: ServiceDep,
):
    """
    创建新剧目

    添加新的剧目到系统中。
    """
    drama = await service.create(data)
    return ApiResponse.success(
        data=drama,
        message="剧目创建成功"
    )


@router.post("/update", summary="更新剧目", response_model=ApiResponse[DramaResponse])
async def update_drama(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    data: DramaUpdate = None,
):
    """
    更新剧目信息

    更新指定 ID 的剧目信息。
    """
    update_data = data.model_dump(exclude_unset=True) if data else {}
    drama = await service.update(drama_id, update_data)
    return ApiResponse.success(
        data=drama,
        message="剧目更新成功"
    )


@router.post("/delete", summary="删除剧目", response_model=ApiResponse)
async def delete_drama(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
):
    """
    删除剧目

    从系统中删除指定 ID 的剧目及其关联数据。
    """
    await service.delete(drama_id)
    return ApiResponse.success(
        data={"drama_id": drama_id},
        message="剧目删除成功"
    )


@router.get("/stats", summary="获取剧目统计", response_model=ApiResponse[DramaStats])
async def get_drama_stats(
    service: ServiceDep,
):
    """
    获取剧目统计信息

    返回剧目数量、集数数量、角色数量等统计数据。
    """
    stats = await service.get_stats()
    return ApiResponse.success(data=stats)


# ========== 集数接口 ==========

@router.get("/episodes/list", summary="获取剧目集数列表", response_model=ApiResponse[list[EpisodeResponse]])
async def list_episodes(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
):
    """
    获取剧目的所有集数

    返回指定剧目的所有集数，按集数编号排序。
    """
    episodes = await service.get_episodes(drama_id)
    return ApiResponse.success(data=episodes)


@router.post("/episodes/create", summary="创建集数", response_model=ApiResponse[EpisodeResponse])
async def create_episode(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    episode_number: int = Query(..., ge=1, description="集数编号"),
    title: str = Query(..., description="标题"),
    description: str | None = Query(None, description="描述"),
    duration: int = Query(0, ge=0, description="时长（秒）"),
    script_content: str | None = Query(None, description="剧本内容"),
):
    """
    为剧目创建新集数

    为指定剧目添加新的集数。
    """
    episode_data = {
        "episode_number": episode_number,
        "title": title,
        "description": description,
        "duration": duration,
        "script_content": script_content,
    }
    episode = await service.create_episode(drama_id, episode_data)
    return ApiResponse.success(
        data=episode,
        message="集数创建成功"
    )


@router.post("/episodes/batch-save", summary="批量保存集数", response_model=ApiResponse)
async def batch_save_episodes(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    data: BatchEpisodesSave = None,
):
    """
    批量保存集数

    替换剧目的所有集数为提供的数据。
    """
    count = await service.batch_save_episodes(drama_id, data.episodes)
    return ApiResponse.success(
        data={"count": count},
        message=f"已保存 {count} 个集数"
    )


# ========== 角色接口 ==========

@router.get("/characters/list", summary="获取剧目角色列表", response_model=ApiResponse[list[CharacterResponse]])
async def list_characters(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
):
    """
    获取剧目的所有角色

    返回指定剧目的所有角色，按排序字段排列。
    """
    characters = await service.get_characters(drama_id)
    return ApiResponse.success(data=characters)


@router.post("/characters/create", summary="创建角色", response_model=ApiResponse[CharacterResponse])
async def create_character(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    name: str = Query(..., description="角色名称"),
    role: str | None = Query(None, description="角色类型"),
    description: str | None = Query(None, description="角色描述"),
    appearance: str | None = Query(None, description="外貌"),
    personality: str | None = Query(None, description="性格"),
    voice_style: str | None = Query(None, description="声音风格"),
    seed_value: str | None = Query(None, description="种子值"),
    sort_order: int = Query(0, ge=0, description="排序"),
):
    """
    为剧目创建新角色

    为指定剧目添加新的角色。
    """
    character_data = {
        "name": name,
        "role": role,
        "description": description,
        "appearance": appearance,
        "personality": personality,
        "voice_style": voice_style,
        "seed_value": seed_value,
        "sort_order": sort_order,
    }
    character = await service.create_character(drama_id, character_data)
    return ApiResponse.success(
        data=character,
        message="角色创建成功"
    )


@router.post("/characters/batch-save", summary="批量保存角色", response_model=ApiResponse)
async def batch_save_characters(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    data: BatchCharactersSave = None,
):
    """
    批量保存角色

    替换剧目的所有角色为提供的数据。
    """
    count = await service.batch_save_characters(drama_id, data.characters)
    return ApiResponse.success(
        data={"count": count},
        message=f"已保存 {count} 个角色"
    )


# ========== 其他接口 ==========

@router.post("/outline/save", summary="保存大纲", response_model=ApiResponse)
async def save_outline(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    data: OutlineSave = None,
):
    """
    保存剧目大纲

    将大纲数据保存到剧目的元数据中。
    """
    await service.save_outline(drama_id, data.outline)
    return ApiResponse.success(message="大纲保存成功")


@router.post("/progress/save", summary="保存进度", response_model=ApiResponse[DramaResponse])
async def save_progress(
    service: ServiceDep,
    drama_id: int = Query(..., description="剧目 ID"),
    data: ProgressSave = None,
):
    """
    保存剧目进度

    保存进度数据并更新剧目状态。
    """
    progress_data = data.progress
    if data.status:
        progress_data["status"] = data.status

    drama = await service.save_progress(drama_id, progress_data)
    return ApiResponse.success(
        data=drama,
        message="进度保存成功"
    )
