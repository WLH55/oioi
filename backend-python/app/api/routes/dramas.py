from fastapi import APIRouter, Depends, HTTPException, status, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.core.response import APIResponse
from app.core.exceptions import NotFoundException, BadRequestException
from app.models.drama import Drama, Episode, Character

router = APIRouter()


@router.get("")
async def list_dramas(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    drama_id: Optional[str] = Query(None),  # For compatibility with Go backend
    db: AsyncSession = Depends(get_db)
):
    """List all dramas with pagination"""
    # Calculate offset
    skip = (page - 1) * page_size

    # Get total count
    count_result = await db.execute(select(func.count(Drama.id)))
    total = count_result.scalar() or 0

    # Get dramas with pagination
    result = await db.execute(
        select(Drama)
        .offset(skip)
        .limit(page_size)
        .order_by(Drama.created_at.desc())
    )
    dramas = result.scalars().all()

    # Convert to dict for response
    dramas_data = []
    for drama in dramas:
        dramas_data.append({
            "id": drama.id,
            "title": drama.title,
            "description": drama.description,
            "author": drama.author,
            "genre": drama.genre,
            "status": drama.status,
            "metadata": drama.meta_data,
            "created_at": drama.created_at.isoformat() if drama.created_at else None,
            "updated_at": drama.updated_at.isoformat() if drama.updated_at else None
        })

    return APIResponse.success_with_pagination(
        items=dramas_data,
        total=total,
        page=page,
        page_size=page_size
    )


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_drama(
    drama: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Create a new drama"""
    db_drama = Drama(
        title=drama.get("title", ""),
        description=drama.get("description"),
        author=drama.get("author"),
        genre=drama.get("genre"),
        status=drama.get("status", "draft")
    )
    db.add(db_drama)
    await db.commit()
    await db.refresh(db_drama)

    return APIResponse.created({
        "id": db_drama.id,
        "title": db_drama.title,
        "description": db_drama.description,
        "author": db_drama.author,
        "genre": db_drama.genre,
        "status": db_drama.status,
        "created_at": db_drama.created_at.isoformat() if db_drama.created_at else None
    })


@router.get("/{drama_id}")
async def get_drama(
    drama_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get drama by ID - supports both string UUID and integer ID"""
    # Try to parse as integer first
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        # If not an integer, try as string (for future UUID support)
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    return APIResponse.success({
        "id": drama.id,
        "title": drama.title,
        "description": drama.description,
        "author": drama.author,
        "genre": drama.genre,
        "status": drama.status,
        "metadata": drama.metadata,
        "created_at": drama.created_at.isoformat() if drama.created_at else None,
        "updated_at": drama.updated_at.isoformat() if drama.updated_at else None
    })


@router.put("/{drama_id}")
async def update_drama(
    drama_id: str,
    drama: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Update drama"""
    # Try to parse as integer first
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    db_drama = result.scalar_one_or_none()

    if not db_drama:
        raise NotFoundException("剧本不存在")

    # Update fields
    if "title" in drama:
        db_drama.title = drama["title"]
    if "description" in drama:
        db_drama.description = drama["description"]
    if "author" in drama:
        db_drama.author = drama["author"]
    if "genre" in drama:
        db_drama.genre = drama["genre"]
    if "status" in drama:
        db_drama.status = drama["status"]

    await db.commit()
    await db.refresh(db_drama)

    return APIResponse.success({
        "id": db_drama.id,
        "title": db_drama.title,
        "description": db_drama.description,
        "author": db_drama.author,
        "genre": db_drama.genre,
        "status": db_drama.status,
        "updated_at": db_drama.updated_at.isoformat() if db_drama.updated_at else None
    })


@router.delete("/{drama_id}")
async def delete_drama(
    drama_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Delete drama"""
    # Try to parse as integer first
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    await db.delete(drama)
    await db.commit()

    return APIResponse.success({"message": "删除成功"})


@router.get("/{drama_id}/episodes")
async def list_episodes(
    drama_id: str,
    db: AsyncSession = Depends(get_db)
):
    """List all episodes for a drama"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # Get episodes
    result = await db.execute(
        select(Episode)
        .where(Episode.drama_id == drama_id_int)
        .order_by(Episode.episode_number)
    )
    episodes = result.scalars().all()

    episodes_data = []
    for ep in episodes:
        episodes_data.append({
            "id": ep.id,
            "drama_id": ep.drama_id,
            "episode_number": ep.episode_number,
            "title": ep.title,
            "description": ep.description,
            "script_content": ep.script_content,
            "duration": ep.duration,
            "status": ep.status,
            "video_url": ep.video_url,
            "created_at": ep.created_at.isoformat() if ep.created_at else None,
            "updated_at": ep.updated_at.isoformat() if ep.updated_at else None
        })

    return APIResponse.success(episodes_data)


@router.post("/{drama_id}/episodes", status_code=status.HTTP_201_CREATED)
async def create_episode(
    drama_id: str,
    episode: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Create a new episode for a drama"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    db_episode = Episode(
        drama_id=drama_id_int,
        episode_number=episode.get("episode_number", 1),
        title=episode.get("title", ""),
        script_content=episode.get("script_content"),
        description=episode.get("description"),
        duration=episode.get("duration", 0),
        status=episode.get("status", "draft")
    )
    db.add(db_episode)
    await db.commit()
    await db.refresh(db_episode)

    return APIResponse.created({
        "id": db_episode.id,
        "drama_id": db_episode.drama_id,
        "episode_number": db_episode.episode_number,
        "title": db_episode.title,
        "status": db_episode.status,
        "created_at": db_episode.created_at.isoformat() if db_episode.created_at else None
    })


@router.get("/{drama_id}/characters")
async def list_characters(
    drama_id: str,
    episode_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
):
    """List all characters for a drama, optionally filtered by episode"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # If episode_id provided, verify episode exists
    if episode_id:
        try:
            episode_id_int = int(episode_id)
            ep_result = await db.execute(
                select(Episode).where(Episode.id == episode_id_int)
            )
            episode = ep_result.scalar_one_or_none()
            if not episode:
                raise NotFoundException("章节不存在")
        except ValueError:
            raise NotFoundException("章节不存在")

    # Get characters
    result = await db.execute(
        select(Character)
        .where(Character.drama_id == drama_id_int)
        .order_by(Character.sort_order)
    )
    characters = result.scalars().all()

    characters_data = []
    for char in characters:
        characters_data.append({
            "id": char.id,
            "drama_id": char.drama_id,
            "name": char.name,
            "role": char.role,
            "description": char.description,
            "appearance": char.appearance,
            "personality": char.personality,
            "voice_style": char.voice_style,
            "image_url": char.image_url,
            "reference_images": char.reference_images,
            "seed_value": char.seed_value,
            "sort_order": char.sort_order,
            "created_at": char.created_at.isoformat() if char.created_at else None
        })

    return APIResponse.success(characters_data)


@router.post("/{drama_id}/characters", status_code=status.HTTP_201_CREATED)
async def create_character(
    drama_id: str,
    character: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Create a new character for a drama"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    db_character = Character(
        drama_id=drama_id_int,
        name=character.get("name", ""),
        role=character.get("role"),
        description=character.get("description"),
        appearance=character.get("appearance"),
        personality=character.get("personality"),
        voice_style=character.get("voice_style"),
        image_url=character.get("image_url"),
        reference_images=character.get("reference_images"),
        seed_value=character.get("seed_value"),
        sort_order=character.get("sort_order", 0)
    )
    db.add(db_character)
    await db.commit()
    await db.refresh(db_character)

    return APIResponse.created({
        "id": db_character.id,
        "drama_id": db_character.drama_id,
        "name": db_character.name,
        "role": db_character.role,
        "created_at": db_character.created_at.isoformat() if db_character.created_at else None
    })


@router.get("/stats")
async def get_drama_stats(
    db: AsyncSession = Depends(get_db)
):
    """Get drama statistics"""
    # Count total dramas
    total_dramas_result = await db.execute(select(func.count(Drama.id)))
    total_dramas = total_dramas_result.scalar() or 0

    # Count dramas by status
    status_stats_result = await db.execute(
        select(Drama.status, func.count(Drama.id))
        .group_by(Drama.status)
    )
    status_stats = {row[0]: row[1] for row in status_stats_result.all()}

    # Count total episodes
    total_episodes_result = await db.execute(select(func.count(Episode.id)))
    total_episodes = total_episodes_result.scalar() or 0

    # Count total characters
    total_characters_result = await db.execute(select(func.count(Character.id)))
    total_characters = total_characters_result.scalar() or 0

    stats = {
        "total_dramas": total_dramas,
        "total_episodes": total_episodes,
        "total_characters": total_characters,
        "status_breakdown": status_stats,
        "completed_dramas": status_stats.get("completed", 0),
        "in_progress": status_stats.get("producing", 0) + status_stats.get("draft", 0)
    }

    return APIResponse.success(stats)


@router.put("/{drama_id}/characters")
async def save_characters(
    drama_id: str,
    characters: List[Dict[str, Any]] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Batch save characters for a drama"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # Delete existing characters
    await db.execute(
        select(Character).where(Character.drama_id == drama_id_int)
    )

    # Create new characters
    saved_characters = []
    for char_data in characters:
        db_character = Character(
            drama_id=drama_id_int,
            name=char_data.get("name", ""),
            role=char_data.get("role"),
            description=char_data.get("description"),
            appearance=char_data.get("appearance"),
            personality=char_data.get("personality"),
            voice_style=char_data.get("voice_style"),
            image_url=char_data.get("image_url"),
            reference_images=char_data.get("reference_images"),
            seed_value=char_data.get("seed_value"),
            sort_order=char_data.get("sort_order", 0)
        )
        db.add(db_character)
        saved_characters.append(db_character)

    await db.commit()

    return APIResponse.success({
        "message": f"保存了 {len(saved_characters)} 个角色",
        "count": len(saved_characters)
    })


@router.put("/{drama_id}/outline")
async def save_outline(
    drama_id: str,
    outline: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Save drama outline"""
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # Update metadata with outline
    if drama.meta_data is None:
        drama.meta_data = {}

    drama.meta_data["outline"] = outline
    await db.commit()

    return APIResponse.success({"message": "保存成功"})


@router.put("/{drama_id}/episodes")
async def save_episodes(
    drama_id: str,
    episodes: List[Dict[str, Any]] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Batch save episodes for a drama"""
    # Verify drama exists
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # Delete existing episodes
    await db.execute(
        select(Episode).where(Episode.drama_id == drama_id_int)
    )

    # Create new episodes
    saved_episodes = []
    for ep_data in episodes:
        db_episode = Episode(
            drama_id=drama_id_int,
            episode_number=ep_data.get("episode_number", 1),
            title=ep_data.get("title", ""),
            script_content=ep_data.get("script_content"),
            description=ep_data.get("description"),
            duration=ep_data.get("duration", 0),
            status=ep_data.get("status", "draft")
        )
        db.add(db_episode)
        saved_episodes.append(db_episode)

    await db.commit()

    return APIResponse.success({
        "message": f"保存了 {len(saved_episodes)} 个章节",
        "count": len(saved_episodes)
    })


@router.put("/{drama_id}/progress")
async def save_progress(
    drama_id: str,
    progress: Dict[str, Any] = Body(...),
    db: AsyncSession = Depends(get_db)
):
    """Save drama progress"""
    try:
        drama_id_int = int(drama_id)
        result = await db.execute(select(Drama).where(Drama.id == drama_id_int))
    except ValueError:
        result = await db.execute(select(Drama).where(Drama.id == drama_id))

    drama = result.scalar_one_or_none()

    if not drama:
        raise NotFoundException("剧本不存在")

    # Update metadata with progress
    if drama.meta_data is None:
        drama.meta_data = {}

    drama.meta_data["progress"] = progress

    # Update status if provided
    if "status" in progress:
        drama.status = progress["status"]

    await db.commit()

    return APIResponse.success({
        "message": "保存成功",
        "drama_id": drama_id_int,
        "progress": progress
    })
