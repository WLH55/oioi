from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class GenerateCharactersRequest(BaseModel):
    drama_id: int
    genre: Optional[str] = None
    style: Optional[str] = None
    num_characters: Optional[int] = 3


class Character(BaseModel):
    name: str
    role: str
    description: str
    appearance: str
    personality: str


@router.post("/characters")
async def generate_characters(
    request: GenerateCharactersRequest,
    background_tasks: BackgroundTasks
):
    """Generate characters using AI"""
    # In real implementation, this would call AI service to generate characters
    task_id = f"char_gen_{request.drama_id}"

    # Example response (in real implementation, this would come from AI)
    characters = [
        {
            "name": "张三",
            "role": "主角",
            "description": "一个勇敢的年轻人",
            "appearance": "英俊，身材高大",
            "personality": "勇敢，善良，正义感强"
        },
        {
            "name": "李四",
            "role": "配角",
            "description": "主角的朋友",
            "appearance": "温和，戴眼镜",
            "personality": "聪明，谨慎"
        }
    ]

    return {
        "message": "Characters generated successfully",
        "drama_id": request.drama_id,
        "task_id": task_id,
        "characters": characters
    }


@router.post("/script")
async def generate_script(
    drama_id: int,
    episode_num: int,
    plot_outline: str,
    background_tasks: BackgroundTasks
):
    """Generate script for episode"""
    task_id = f"script_gen_{drama_id}_{episode_num}"

    return {
        "message": "Script generation started",
        "drama_id": drama_id,
        "episode_num": episode_num,
        "task_id": task_id,
        "status": "pending"
    }
