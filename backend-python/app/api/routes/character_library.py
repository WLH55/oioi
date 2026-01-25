from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from app.core.database import get_db
from app.models.character_library import CharacterLibrary
from app.models.drama import Character
from app.schemas.character_library import (
    CharacterLibraryCreate, CharacterLibraryUpdate, CharacterLibraryResponse,
    CharacterImageGenerate, BatchCharacterImageGenerate,
)

router = APIRouter()


@router.get("", response_model=List[CharacterLibraryResponse])
async def list_character_library(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    category: Optional[str] = None,
    source_type: Optional[str] = None,
    keyword: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List character library items with filters"""
    query = select(CharacterLibrary)

    # Apply filters
    if category:
        query = query.where(CharacterLibrary.category == category)
    if source_type:
        query = query.where(CharacterLibrary.source_type == source_type)
    if keyword:
        query = query.where(
            (CharacterLibrary.name.contains(keyword)) |
            (CharacterLibrary.description.contains(keyword))
        )

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated results
    query = query.offset(skip).limit(limit).order_by(CharacterLibrary.created_at.desc())
    result = await db.execute(query)
    items = result.scalars().all()

    return items


@router.post("", response_model=CharacterLibraryResponse, status_code=status.HTTP_201_CREATED)
async def create_library_item(
    item: CharacterLibraryCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create a new character library item"""
    db_item = CharacterLibrary(**item.model_dump())
    db.add(db_item)
    await db.commit()
    await db.refresh(db_item)
    return db_item


@router.get("/{item_id}", response_model=CharacterLibraryResponse)
async def get_library_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get character library item by ID"""
    result = await db.execute(select(CharacterLibrary).where(CharacterLibrary.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character library item not found"
        )

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_item(
    item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete character library item"""
    result = await db.execute(select(CharacterLibrary).where(CharacterLibrary.id == item_id))
    item = result.scalar_one_or_none()

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character library item not found"
        )

    await db.delete(item)
    await db.commit()
    return None


@router.post("/batch-generate-images")
async def batch_generate_character_images(
    request: BatchCharacterImageGenerate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Batch generate images for multiple characters"""
    # Verify characters exist
    result = await db.execute(
        select(Character).where(Character.id.in_(request.character_ids))
    )
    characters = result.scalars().all()

    if len(characters) != len(request.character_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Some characters not found"
        )

    # Create background tasks for each character
    task_ids = []
    for character in characters:
        # In real implementation, this would create actual image generation tasks
        task_id = f"char_img_gen_{character.id}_{hash(str(character.id))}"
        task_ids.append({
            "character_id": character.id,
            "task_id": task_id
        })

    return {
        "message": f"Started image generation for {len(characters)} characters",
        "tasks": task_ids
    }


@router.put("/characters/{character_id}")
async def update_character(
    character_id: int,
    name: Optional[str] = None,
    role: Optional[str] = None,
    description: Optional[str] = None,
    appearance: Optional[str] = None,
    personality: Optional[str] = None,
    voice_style: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Update character information"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    # Update fields if provided
    if name is not None:
        character.name = name
    if role is not None:
        character.role = role
    if description is not None:
        character.description = description
    if appearance is not None:
        character.appearance = appearance
    if personality is not None:
        character.personality = personality
    if voice_style is not None:
        character.voice_style = voice_style

    await db.commit()
    await db.refresh(character)

    return {
        "message": "Character updated successfully",
        "character_id": character.id
    }


@router.delete("/characters/{character_id}")
async def delete_character(
    character_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Delete a character"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    await db.delete(character)
    await db.commit()

    return {
        "message": "Character deleted successfully",
        "character_id": character_id
    }


@router.post("/characters/{character_id}/generate-image")
async def generate_character_image(
    character_id: int,
    request: CharacterImageGenerate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Generate image for a specific character"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    # In real implementation, this would trigger actual AI image generation
    task_id = f"char_img_gen_{character_id}"

    return {
        "message": "Image generation started",
        "character_id": character_id,
        "task_id": task_id,
        "status": "pending"
    }


@router.put("/characters/{character_id}/image")
async def update_character_image(
    character_id: int,
    image_url: str,
    db: AsyncSession = Depends(get_db)
):
    """Update character image"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    character.image_url = image_url
    await db.commit()
    await db.refresh(character)

    return {
        "message": "Character image updated successfully",
        "character_id": character_id,
        "image_url": image_url
    }


@router.put("/characters/{character_id}/image-from-library")
async def apply_library_item_to_character(
    character_id: int,
    library_item_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Apply character library image to character"""
    # Get character
    char_result = await db.execute(select(Character).where(Character.id == character_id))
    character = char_result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    # Get library item
    lib_result = await db.execute(
        select(CharacterLibrary).where(CharacterLibrary.id == library_item_id)
    )
    library_item = lib_result.scalar_one_or_none()

    if not library_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Library item not found"
        )

    # Apply image
    character.image_url = library_item.image_url
    await db.commit()
    await db.refresh(character)

    return {
        "message": "Library image applied successfully",
        "character_id": character_id,
        "library_item_id": library_item_id,
        "image_url": library_item.image_url
    }


@router.post("/characters/{character_id}/add-to-library")
async def add_character_to_library(
    character_id: int,
    name: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Add character to library"""
    result = await db.execute(select(Character).where(Character.id == character_id))
    character = result.scalar_one_or_none()

    if not character:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Character not found"
        )

    if not character.image_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character has no image to add to library"
        )

    # Create library item from character
    library_item = CharacterLibrary(
        name=name or character.name,
        category=category,
        image_url=character.image_url,
        description=character.description,
        source_type="character"
    )

    db.add(library_item)
    await db.commit()
    await db.refresh(library_item)

    return {
        "message": "Character added to library successfully",
        "character_id": character_id,
        "library_item_id": library_item.id
    }
