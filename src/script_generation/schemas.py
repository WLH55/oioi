"""
Script Generation 模块的 Pydantic 模型
"""
from pydantic import BaseModel, Field


class GenerateCharactersRequest(BaseModel):
    """生成角色请求模型"""
    drama_id: int = Field(..., description="剧目ID")
    genre: str | None = Field(None, description="类型")
    style: str | None = Field(None, description="风格")
    num_characters: int = Field(3, description="角色数量", ge=1, le=10)
    custom_prompt: str | None = Field(None, description="自定义提示词")


class CharacterData(BaseModel):
    """角色数据模型"""
    name: str = Field(..., description="角色名称")
    role: str = Field(..., description="角色定位")
    description: str = Field(..., description="角色描述")
    appearance: str = Field(..., description="外貌")
    personality: str = Field(..., description="性格")
    voice_style: str | None = Field(None, description="声音风格")


class GenerateCharactersResponse(BaseModel):
    """生成角色响应模型"""
    message: str
    drama_id: int
    task_id: str
    characters: list[CharacterData]
    count: int


class GenerateScriptRequest(BaseModel):
    """生成剧本请求模型"""
    drama_id: int = Field(..., description="剧目ID")
    episode_num: int = Field(..., description="集数编号", ge=1)
    plot_outline: str = Field(..., description="剧情大纲")
    style: str | None = Field(None, description="风格")
    duration: int | None = Field(None, description="目标时长(分钟)", ge=1)


class GenerateScriptResponse(BaseModel):
    """生成剧本响应模型"""
    message: str
    drama_id: int
    episode_id: int
    episode_num: int
    title: str
    script_length: int
    duration: int
    task_id: str
    status: str


class GenerateScenesRequest(BaseModel):
    """生成场景请求模型"""
    episode_id: int = Field(..., description="集数ID")


class SceneData(BaseModel):
    """场景数据模型"""
    scene_number: int
    location: str
    time: str
    description: str


class GenerateScenesResponse(BaseModel):
    """生成场景响应模型"""
    message: str
    episode_id: int
    scenes_count: int
    scenes: list[SceneData]
    task_id: str
    status: str
