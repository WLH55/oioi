"""
Script Generation 模块路由

提供剧本生成相关的 API 端点
"""
from fastapi import APIRouter, BackgroundTasks, Depends, Query

from src.core.schemas import ApiResponse

from .dependencies import get_script_generation_service
from .schemas import (
    GenerateCharactersRequest,
    GenerateCharactersResponse,
    GenerateScenesResponse,
    GenerateScriptRequest,
    GenerateScriptResponse,
)
from .service import ScriptGenerationService

router = APIRouter()


# ============================================================================
# 角色生成端点
# ============================================================================

@router.post(
    "/characters",
    summary="生成角色",
    description="使用 AI 为指定剧目生成角色",
    response_model=ApiResponse[GenerateCharactersResponse]
)
async def generate_characters(
    request: GenerateCharactersRequest,
    background_tasks: BackgroundTasks = None,
    service: ScriptGenerationService = Depends(get_script_generation_service)
) -> ApiResponse[GenerateCharactersResponse]:
    """
    生成角色

    使用 AI 为剧目生成角色，包括姓名、定位、描述、外貌、性格等信息

    - **drama_id**: 剧目ID
    - **genre**: 可选，类型
    - **style**: 可选，风格
    - **num_characters**: 角色数量，默认3
    - **custom_prompt**: 可选，自定义提示词
    """
    import uuid
    task_id = f"char_gen_{request.drama_id}_{uuid.uuid4().hex[:8]}"

    result = await service.generate_characters(
        drama_id=request.drama_id,
        genre=request.genre,
        style=request.style,
        num_characters=request.num_characters,
        custom_prompt=request.custom_prompt
    )

    return ApiResponse.success(data=GenerateCharactersResponse(
        message="角色生成成功",
        drama_id=result["drama_id"],
        task_id=task_id,
        characters=result["characters"],
        count=result["count"]
    ))


# ============================================================================
# 剧本生成端点
# ============================================================================

@router.post(
    "/script",
    summary="生成剧本",
    description="使用 AI 为指定集数生成剧本",
    response_model=ApiResponse[GenerateScriptResponse]
)
async def generate_script(
    request: GenerateScriptRequest,
    background_tasks: BackgroundTasks = None,
    service: ScriptGenerationService = Depends(get_script_generation_service)
) -> ApiResponse[GenerateScriptResponse]:
    """
    生成剧本

    使用 AI 为集数生成剧本内容

    - **drama_id**: 剧目ID
    - **episode_num**: 集数编号
    - **plot_outline**: 剧情大纲
    - **style**: 可选，风格
    - **duration**: 可选，目标时长
    """
    import uuid
    task_id = f"script_gen_{request.drama_id}_{request.episode_num}_{uuid.uuid4().hex[:8]}"

    result = await service.generate_script(
        drama_id=request.drama_id,
        episode_num=request.episode_num,
        plot_outline=request.plot_outline,
        style=request.style,
        duration=request.duration
    )

    return ApiResponse.success(data=GenerateScriptResponse(
        message="剧本生成成功",
        drama_id=result["drama_id"],
        episode_id=result["episode_id"],
        episode_num=result["episode_num"],
        title=result["title"],
        script_length=result["script_length"],
        duration=result["duration"],
        task_id=task_id,
        status="completed"
    ))


# ============================================================================
# 场景生成端点
# ============================================================================

@router.post(
    "/scenes",
    summary="从剧本生成场景",
    description="根据剧本内容自动拆分场景",
    response_model=ApiResponse[GenerateScenesResponse]
)
async def generate_scenes(
    episode_id: int = Query(..., description="集数ID"),
    background_tasks: BackgroundTasks = None,
    service: ScriptGenerationService = Depends(get_script_generation_service)
) -> ApiResponse[GenerateScenesResponse]:
    """
    从剧本生成场景

    分析剧本内容并自动拆分为场景

    - **episode_id**: 集数ID
    """
    import uuid
    task_id = f"scene_gen_{episode_id}_{uuid.uuid4().hex[:8]}"

    result = await service.generate_scenes_from_script(episode_id)

    return ApiResponse.success(data=GenerateScenesResponse(
        message="场景生成成功",
        episode_id=result["episode_id"],
        scenes_count=result["scenes_count"],
        scenes=result["scenes"],
        task_id=task_id,
        status="completed"
    ))
