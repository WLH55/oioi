"""
Resource Transfer Service

Handles transferring resources (characters, scenes, assets) between dramas.
"""

from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.drama import Drama, Episode, Character, Scene
from app.models.asset import Asset
from app.models.image_generation import ImageGeneration
from app.models.video_generation import VideoGeneration
from app.utils.logger import log


class ResourceTransferService:
    """Service for transferring resources between dramas"""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def transfer_character(
        self,
        source_drama_id: int,
        target_drama_id: int,
        character_name: str,
        new_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transfer a character from source drama to target drama

        Args:
            source_drama_id: Source drama ID
            target_drama_id: Target drama ID
            character_name: Name of character to transfer
            new_name: New name for character in target drama (optional)

        Returns:
            Transferred character info
        """
        try:
            # Verify both dramas exist
            source_result = await self.db.execute(
                select(Drama).where(Drama.id == source_drama_id)
            )
            source_drama = source_result.scalar_one_or_none()

            if not source_drama:
                raise ValueError(f"Source drama {source_drama_id} not found")

            target_result = await self.db.execute(
                select(Drama).where(Drama.id == target_drama_id)
            )
            target_drama = target_result.scalar_one_or_none()

            if not target_drama:
                raise ValueError(f"Target drama {target_drama_id} not found")

            # Get character from source drama
            char_result = await self.db.execute(
                select(Character).where(
                    Character.drama_id == source_drama_id,
                    Character.name == character_name
                )
            )
            source_character = char_result.scalar_one_or_none()

            if not source_character:
                raise ValueError(f"Character '{character_name}' not found in source drama")

            # Check if character already exists in target drama
            target_name = new_name or character_name
            existing_result = await self.db.execute(
                select(Character).where(
                    Character.drama_id == target_drama_id,
                    Character.name == target_name
                )
            )
            existing = existing_result.scalar_one_or_none()

            if existing:
                log.info(f"Character '{target_name}' already exists in target drama")
                return {
                    "character_id": existing.id,
                    "name": existing.name,
                    "already_exists": True
                }

            # Create new character in target drama
            new_character = Character(
                drama_id=target_drama_id,
                name=target_name,
                role=source_character.role,
                description=source_character.description,
                appearance=source_character.appearance,
                personality=source_character.personality,
                voice_style=source_character.voice_style,
                reference_images=source_character.reference_images,
                seed_value=source_character.seed_value,
                sort_order=source_character.sort_order
            )

            self.db.add(new_character)
            await self.db.commit()
            await self.db.refresh(new_character)

            log.info(f"Transferred character '{character_name}' from drama {source_drama_id} to {target_drama_id}")

            return {
                "character_id": new_character.id,
                "name": new_character.name,
                "source_drama_id": source_drama_id,
                "target_drama_id": target_drama_id,
                "already_exists": False
            }

        except Exception as e:
            log.error(f"Error transferring character: {str(e)}")
            await self.db.rollback()
            raise

    async def transfer_scene(
        self,
        source_scene_id: int,
        target_episode_id: int,
        new_scene_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Transfer a scene to a different episode

        Args:
            source_scene_id: Source scene ID
            target_episode_id: Target episode ID
            new_scene_number: New scene number (optional)

        Returns:
            Transferred scene info
        """
        try:
            # Get source scene
            source_result = await self.db.execute(
                select(Scene).where(Scene.id == source_scene_id)
            )
            source_scene = source_result.scalar_one_or_none()

            if not source_scene:
                raise ValueError(f"Source scene {source_scene_id} not found")

            # Get target episode
            episode_result = await self.db.execute(
                select(Episode).where(Episode.id == target_episode_id)
            )
            target_episode = episode_result.scalar_one_or_none()

            if not target_episode:
                raise ValueError(f"Target episode {target_episode_id} not found")

            # Determine new scene number
            if new_scene_number is None:
                # Get max scene number in target episode
                max_result = await self.db.execute(
                    select(Scene)
                    .where(Scene.episode_id == target_episode_id)
                    .order_by(Scene.scene_number.desc())
                )
                max_scene = max_result.scalar_one_or_none()
                new_scene_number = (max_scene.scene_number + 1) if max_scene else 1

            # Create new scene
            new_scene = Scene(
                drama_id=target_episode.drama_id,
                episode_id=target_episode_id,
                scene_number=new_scene_number,
                location=source_scene.location,
                time=source_scene.time,
                description=source_scene.description,
                prompt=source_scene.prompt,
                duration=source_scene.duration,
                status="pending"
            )

            self.db.add(new_scene)
            await self.db.commit()
            await self.db.refresh(new_scene)

            log.info(f"Transferred scene {source_scene_id} to episode {target_episode_id}")

            return {
                "scene_id": new_scene.id,
                "scene_number": new_scene.scene_number,
                "source_scene_id": source_scene_id,
                "target_episode_id": target_episode_id
            }

        except Exception as e:
            log.error(f"Error transferring scene: {str(e)}")
            await self.db.rollback()
            raise

    async def transfer_assets(
        self,
        source_drama_id: int,
        target_drama_id: int,
        asset_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Transfer assets from source drama to target drama

        Args:
            source_drama_id: Source drama ID
            target_drama_id: Target drama ID
            asset_types: Types of assets to transfer (image, video, all)

        Returns:
            Transfer results
        """
        try:
            # Verify dramas exist
            source_result = await self.db.execute(
                select(Drama).where(Drama.id == source_drama_id)
            )
            source_drama = source_result.scalar_one_or_none()

            if not source_drama:
                raise ValueError(f"Source drama {source_drama_id} not found")

            target_result = await self.db.execute(
                select(Drama).where(Drama.id == target_drama_id)
            )
            target_drama = target_result.scalar_one_or_none()

            if not target_drama:
                raise ValueError(f"Target drama {target_drama_id} not found")

            transferred_images = []
            transferred_videos = []

            # Transfer images
            if asset_types is None or "image" in asset_types or "all" in asset_types:
                image_result = await self.db.execute(
                    select(ImageGeneration).where(
                        ImageGeneration.drama_id == source_drama_id
                    )
                )
                images = image_result.scalars().all()

                for image in images:
                    # Create new asset record
                    new_asset = Asset(
                        drama_id=target_drama_id,
                        asset_type="image",
                        name=f"Transferred from {source_drama.title}",
                        url=image.image_url,
                        local_path=image.local_path,
                        metadata={
                            "source_drama_id": source_drama_id,
                            "source_image_id": image.id,
                            "image_type": image.image_type,
                            "prompt": image.prompt
                        }
                    )
                    self.db.add(new_asset)
                    transferred_images.append({
                        "source_id": image.id,
                        "url": image.image_url
                    })

            # Transfer videos
            if asset_types is None or "video" in asset_types or "all" in asset_types:
                video_result = await self.db.execute(
                    select(VideoGeneration).where(
                        VideoGeneration.drama_id == source_drama_id
                    )
                )
                videos = video_result.scalars().all()

                for video in videos:
                    # Create new asset record
                    new_asset = Asset(
                        drama_id=target_drama_id,
                        asset_type="video",
                        name=f"Transferred from {source_drama.title}",
                        url=video.video_url,
                        local_path=video.local_path,
                        metadata={
                            "source_drama_id": source_drama_id,
                            "source_video_id": video.id,
                            "provider": video.provider,
                            "prompt": video.prompt
                        }
                    )
                    self.db.add(new_asset)
                    transferred_videos.append({
                        "source_id": video.id,
                        "url": video.video_url
                    })

            await self.db.commit()

            log.info(f"Transferred {len(transferred_images)} images and {len(transferred_videos)} videos")

            return {
                "source_drama_id": source_drama_id,
                "target_drama_id": target_drama_id,
                "transferred_images": len(transferred_images),
                "transferred_videos": len(transferred_videos),
                "images": transferred_images,
                "videos": transferred_videos
            }

        except Exception as e:
            log.error(f"Error transferring assets: {str(e)}")
            await self.db.rollback()
            raise

    async def clone_episode_structure(
        self,
        source_episode_id: int,
        target_drama_id: int,
        new_episode_number: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Clone episode structure (scenes, storyboards) to a new drama

        Args:
            source_episode_id: Source episode ID
            target_drama_id: Target drama ID
            new_episode_number: New episode number (optional)

        Returns:
            Clone results
        """
        try:
            # Get source episode
            source_result = await self.db.execute(
                select(Episode).where(Episode.id == source_episode_id)
            )
            source_episode = source_result.scalar_one_or_none()

            if not source_episode:
                raise ValueError(f"Source episode {source_episode_id} not found")

            # Get target drama
            target_result = await self.db.execute(
                select(Drama).where(Drama.id == target_drama_id)
            )
            target_drama = target_result.scalar_one_or_none()

            if not target_drama:
                raise ValueError(f"Target drama {target_drama_id} not found")

            # Determine new episode number
            if new_episode_number is None:
                max_result = await self.db.execute(
                    select(Episode)
                    .where(Episode.drama_id == target_drama_id)
                    .order_by(Episode.episode_number.desc())
                )
                max_episode = max_result.scalar_one_or_none()
                new_episode_number = (max_episode.episode_number + 1) if max_episode else 1

            # Create new episode
            new_episode = Episode(
                drama_id=target_drama_id,
                episode_number=new_episode_number,
                title=f"{source_episode.title} (Copy)",
                script_content=source_episode.script_content,
                description=source_episode.description,
                duration=source_episode.duration,
                status="draft"
            )

            self.db.add(new_episode)
            await self.db.flush()  # Get the ID without committing

            # Clone scenes
            scenes_result = await self.db.execute(
                select(Scene).where(Scene.episode_id == source_episode_id)
            )
            source_scenes = scenes_result.scalars().all()

            cloned_scenes = []
            for source_scene in source_scenes:
                new_scene = Scene(
                    drama_id=target_drama_id,
                    episode_id=new_episode.id,
                    scene_number=source_scene.scene_number,
                    location=source_scene.location,
                    time=source_scene.time,
                    description=source_scene.description,
                    prompt=source_scene.prompt,
                    duration=source_scene.duration,
                    status="pending"
                )
                self.db.add(new_scene)
                cloned_scenes.append({
                    "source_scene_id": source_scene.id,
                    "scene_number": new_scene.scene_number
                })

            await self.db.commit()
            await self.db.refresh(new_episode)

            log.info(f"Cloned episode {source_episode_id} structure to drama {target_drama_id}")

            return {
                "source_episode_id": source_episode_id,
                "new_episode_id": new_episode.id,
                "new_episode_number": new_episode_number,
                "scenes_cloned": len(cloned_scenes),
                "scenes": cloned_scenes
            }

        except Exception as e:
            log.error(f"Error cloning episode structure: {str(e)}")
            await self.db.rollback()
            raise

    async def batch_transfer_resources(
        self,
        source_drama_id: int,
        target_drama_id: int,
        resources: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Batch transfer multiple resources

        Args:
            source_drama_id: Source drama ID
            target_drama_id: Target drama ID
            resources: Dict specifying what to transfer
                {
                    "characters": bool or list of names,
                    "assets": bool or list of types,
                    "episodes": list of episode IDs
                }

        Returns:
            Batch transfer results
        """
        try:
            results = {
                "source_drama_id": source_drama_id,
                "target_drama_id": target_drama_id,
                "characters": {"transferred": [], "already_exists": []},
                "assets": {"images": 0, "videos": 0},
                "episodes": {"cloned": []}
            }

            # Transfer characters
            if resources.get("characters"):
                char_result = await self.db.execute(
                    select(Character).where(Character.drama_id == source_drama_id)
                )
                characters = char_result.scalars().all()

                char_names = resources["characters"]
                if isinstance(char_names, list):
                    characters = [c for c in characters if c.name in char_names]

                for character in characters:
                    try:
                        result = await self.transfer_character(
                            source_drama_id,
                            target_drama_id,
                            character.name
                        )
                        if result.get("already_exists"):
                            results["characters"]["already_exists"].append(character.name)
                        else:
                            results["characters"]["transferred"].append(character.name)
                    except Exception as e:
                        log.warning(f"Failed to transfer character '{character.name}': {e}")

            # Transfer assets
            if resources.get("assets"):
                asset_types = resources["assets"]
                if asset_types is True:
                    asset_types = None  # Transfer all

                asset_result = await self.transfer_assets(
                    source_drama_id,
                    target_drama_id,
                    asset_types
                )
                results["assets"]["images"] = asset_result["transferred_images"]
                results["assets"]["videos"] = asset_result["transferred_videos"]

            # Clone episodes
            if resources.get("episodes"):
                for episode_id in resources["episodes"]:
                    try:
                        result = await self.clone_episode_structure(
                            episode_id,
                            target_drama_id
                        )
                        results["episodes"]["cloned"].append({
                            "source_episode_id": episode_id,
                            "new_episode_id": result["new_episode_id"]
                        })
                    except Exception as e:
                        log.warning(f"Failed to clone episode {episode_id}: {e}")

            log.info(f"Batch transfer completed from drama {source_drama_id} to {target_drama_id}")

            return results

        except Exception as e:
            log.error(f"Error in batch transfer: {str(e)}")
            raise
