"""
Character Library Service

Manages character library operations including extraction, storage, and retrieval.
"""

import json
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.drama import Drama, Character
from app.models.character_library import CharacterLibrary
from app.models.image_generation import ImageGeneration
from app.services.ai_factory import get_ai_provider
from app.utils.logger import log


class CharacterLibraryService:
    """Service for managing character library"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def extract_character_from_drama(
        self,
        drama_id: int,
        character_name: str
    ) -> Dict[str, Any]:
        """
        Extract a character from a drama and add to library

        Args:
            drama_id: Drama ID
            character_name: Name of character to extract

        Returns:
            Extracted character library entry
        """
        try:
            # Get character from drama
            result = await self.db.execute(
                select(Character).where(
                    and_(
                        Character.drama_id == drama_id,
                        Character.name == character_name
                    )
                )
            )
            character = result.scalar_one_or_none()

            if not character:
                raise ValueError(f"Character '{character_name}' not found in drama {drama_id}")

            # Get drama
            drama_result = await self.db.execute(select(Drama).where(Drama.id == drama_id))
            drama = drama_result.scalar_one_or_none()

            # Check if character already exists in library
            existing_result = await self.db.execute(
                select(CharacterLibrary).where(
                    and_(
                        CharacterLibrary.source_drama_id == drama_id,
                        CharacterLibrary.character_name == character_name
                    )
                )
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                log.info(f"Character '{character_name}' already in library")
                return {
                    "id": existing.id,
                    "character_name": existing.character_name,
                    "source_drama": existing.source_drama_id,
                    "already_exists": True
                }

            # Create character library entry
            library_entry = CharacterLibrary(
                source_drama_id=drama_id,
                character_name=character_name,
                role=character.role,
                description=character.description,
                appearance=character.appearance,
                personality=character.personality,
                voice_style=character.voice_style,
                reference_images=character.reference_images,
                metadata={
                    "source_drama_title": drama.title if drama else "",
                    "genre": drama.genre if drama else "",
                    "tags": self._extract_character_tags(character)
                }
            )

            self.db.add(library_entry)
            await self.db.commit()
            await self.db.refresh(library_entry)

            log.info(f"Extracted character '{character_name}' to library")

            return {
                "id": library_entry.id,
                "character_name": library_entry.character_name,
                "role": library_entry.role,
                "source_drama_id": drama_id,
                "already_exists": False
            }

        except Exception as e:
            log.error(f"Error extracting character: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_extract_characters(
        self,
        drama_id: int
    ) -> Dict[str, Any]:
        """
        Extract all characters from a drama to library

        Args:
            drama_id: Drama ID

        Returns:
            Batch extraction results
        """
        try:
            # Get all characters from drama
            result = await self.db.execute(
                select(Character).where(Character.drama_id == drama_id)
            )
            characters = result.scalars().all()

            if not characters:
                raise ValueError(f"No characters found in drama {drama_id}")

            extracted = []
            already_exists = []

            for character in characters:
                try:
                    result = await self.extract_character_from_drama(
                        drama_id=drama_id,
                        character_name=character.name
                    )

                    if result.get("already_exists"):
                        already_exists.append(character.name)
                    else:
                        extracted.append(character.name)

                except Exception as e:
                    log.warning(f"Failed to extract character '{character.name}': {e}")

            log.info(f"Extracted {len(extracted)} characters, {len(already_exists)} already existed")

            return {
                "drama_id": drama_id,
                "extracted_count": len(extracted),
                "already_exists_count": len(already_exists),
                "extracted": extracted,
                "already_exists": already_exists
            }

        except Exception as e:
            log.error(f"Error in batch extraction: {str(e)}")
            raise

    async def search_library(
        self,
        query: Optional[str] = None,
        role: Optional[str] = None,
        genre: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Search character library

        Args:
            query: Search query string
            role: Filter by role
            genre: Filter by genre
            tags: Filter by tags
            limit: Max results

        Returns:
            Search results
        """
        try:
            # Build query
            db_query = select(CharacterLibrary)

            # Apply filters
            if query:
                db_query = db_query.where(
                    CharacterLibrary.character_name.ilike(f"%{query}%")
                )

            if role:
                db_query = db_query.where(CharacterLibrary.role == role)

            # Genre filter (from metadata)
            if genre:
                db_query = db_query.where(
                    CharacterLibrary.metadata["genre"].astext == genre
                )

            db_query = db_query.limit(limit)

            # Execute query
            result = await self.db.execute(db_query)
            characters = result.scalars().all()

            # Filter by tags if provided
            if tags:
                characters = [
                    c for c in characters
                    if any(tag in c.metadata.get("tags", []) for tag in tags)
                ]

            return {
                "count": len(characters),
                "characters": [
                    {
                        "id": c.id,
                        "character_name": c.character_name,
                        "role": c.role,
                        "description": c.description,
                        "appearance": c.appearance,
                        "genre": c.metadata.get("genre", ""),
                        "tags": c.metadata.get("tags", []),
                        "source_drama_id": c.source_drama_id
                    }
                    for c in characters
                ]
            }

        except Exception as e:
            log.error(f"Error searching library: {str(e)}")
            raise

    async def get_character_detail(
        self,
        library_id: int
    ) -> Dict[str, Any]:
        """
        Get detailed information about a library character

        Args:
            library_id: Character library ID

        Returns:
            Character details
        """
        try:
            result = await self.db.execute(
                select(CharacterLibrary).where(CharacterLibrary.id == library_id)
            )
            character = result.scalar_one_or_none()

            if not character:
                raise ValueError(f"Character library entry {library_id} not found")

            # Get source drama info
            drama_result = await self.db.execute(
                select(Drama).where(Drama.id == character.source_drama_id)
            )
            drama = drama_result.scalar_one_or_none()

            return {
                "id": character.id,
                "character_name": character.character_name,
                "role": character.role,
                "description": character.description,
                "appearance": character.appearance,
                "personality": character.personality,
                "voice_style": character.voice_style,
                "reference_images": character.reference_images,
                "source_drama": {
                    "id": character.source_drama_id,
                    "title": drama.title if drama else "",
                    "genre": drama.genre if drama else ""
                },
                "metadata": character.metadata,
                "usage_count": character.usage_count,
                "created_at": character.created_at.isoformat()
            }

        except Exception as e:
            log.error(f"Error getting character detail: {str(e)}")
            raise

    async def update_character_usage(
        self,
        library_id: int
    ) -> Dict[str, Any]:
        """
        Increment usage count for a library character

        Args:
            library_id: Character library ID

        Returns:
            Updated character info
        """
        try:
            result = await self.db.execute(
                select(CharacterLibrary).where(CharacterLibrary.id == library_id)
            )
            character = result.scalar_one_or_none()

            if not character:
                raise ValueError(f"Character library entry {library_id} not found")

            character.usage_count = (character.usage_count or 0) + 1

            await self.db.commit()
            await self.db.refresh(character)

            log.info(f"Updated usage count for character {library_id}: {character.usage_count}")

            return {
                "id": character.id,
                "character_name": character.character_name,
                "usage_count": character.usage_count
            }

        except Exception as e:
            log.error(f"Error updating usage count: {str(e)}")
            await self.db.rollback()
            raise

    async def delete_from_library(
        self,
        library_id: int
    ) -> Dict[str, Any]:
        """
        Delete character from library

        Args:
            library_id: Character library ID

        Returns:
            Deletion result
        """
        try:
            result = await self.db.execute(
                select(CharacterLibrary).where(CharacterLibrary.id == library_id)
            )
            character = result.scalar_one_or_none()

            if not character:
                raise ValueError(f"Character library entry {library_id} not found")

            character_name = character.character_name

            await self.db.delete(character)
            await self.db.commit()

            log.info(f"Deleted character '{character_name}' from library")

            return {
                "id": library_id,
                "character_name": character_name,
                "deleted": True
            }

        except Exception as e:
            log.error(f"Error deleting from library: {str(e)}")
            await self.db.rollback()
            raise

    async def get_popular_characters(
        self,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get most used characters from library

        Args:
            limit: Max results

        Returns:
            Popular characters
        """
        try:
            result = await self.db.execute(
                select(CharacterLibrary)
                .order_by(CharacterLibrary.usage_count.desc())
                .limit(limit)
            )
            characters = result.scalars().all()

            return {
                "count": len(characters),
                "characters": [
                    {
                        "id": c.id,
                        "character_name": c.character_name,
                        "role": c.role,
                        "usage_count": c.usage_count or 0,
                        "source_drama_id": c.source_drama_id
                    }
                    for c in characters
                ]
            }

        except Exception as e:
            log.error(f"Error getting popular characters: {str(e)}")
            raise

    def _extract_character_tags(
        self,
        character: Character
    ) -> List[str]:
        """Extract tags from character data"""
        tags = []

        # Add role as tag
        if character.role:
            tags.append(character.role)

        # Extract tags from description
        if character.description:
            desc_lower = character.description.lower()
            # Common character traits
            traits = [
                "brave", "smart", "kind", "cunning", "strong",
                "gentle", "mysterious", "cheerful", "serious",
                "ambitious", "loyal", "rebellious"
            ]
            for trait in traits:
                if trait in desc_lower:
                    tags.append(trait)

        # Extract tags from personality
        if character.personality:
            personality_lower = character.personality.lower()
            # Personality keywords
            keywords = [
                "introverted", "extroverted", "optimistic", "pessimistic",
                "leader", "follower", "creative", "analytical"
            ]
            for keyword in keywords:
                if keyword in personality_lower:
                    tags.append(keyword)

        return list(set(tags))  # Remove duplicates
