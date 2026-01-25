package models

import (
	"time"

	"gorm.io/datatypes"
)

type ImageGeneration struct {
	ID              uint                  `gorm:"primarykey" json:"id"`
	StoryboardID    *uint                 `gorm:"index" json:"storyboard_id,omitempty"`
	DramaID         uint                  `gorm:"not null;index" json:"drama_id"`
	SceneID         *uint                 `gorm:"index" json:"scene_id,omitempty"`
	CharacterID     *uint                 `gorm:"index" json:"character_id,omitempty"`
	ImageType       string                `gorm:"size:20;index;default:'storyboard'" json:"image_type"`
	FrameType       *string               `gorm:"size:20" json:"frame_type,omitempty"`
	Provider        string                `gorm:"size:50;not null" json:"provider"`
	Prompt          string                `gorm:"type:text;not null" json:"prompt"`
	NegPrompt       *string               `gorm:"column:negative_prompt;type:text" json:"negative_prompt,omitempty"`
	Model           string                `gorm:"size:100" json:"model"`
	Size            string                `gorm:"size:20" json:"size"`
	Quality         string                `gorm:"size:20" json:"quality"`
	Style           *string               `gorm:"size:50" json:"style,omitempty"`
	Steps           *int                  `json:"steps,omitempty"`
	CfgScale        *float64              `json:"cfg_scale,omitempty"`
	Seed            *int64                `json:"seed,omitempty"`
	ImageURL        *string               `gorm:"type:text" json:"image_url,omitempty"`
	MinioURL        *string               `gorm:"type:text" json:"minio_url,omitempty"`
	LocalPath       *string               `gorm:"type:text" json:"local_path,omitempty"`
	Status          ImageGenerationStatus `gorm:"size:20;not null;default:'pending'" json:"status"`
	TaskID          *string               `gorm:"size:200" json:"task_id,omitempty"`
	ErrorMsg        *string               `gorm:"type:text" json:"error_msg,omitempty"`
	Width           *int                  `json:"width,omitempty"`
	Height          *int                  `json:"height,omitempty"`
	ReferenceImages datatypes.JSON        `gorm:"type:json" json:"reference_images,omitempty"`
	CreatedAt       time.Time             `json:"created_at"`
	UpdatedAt       time.Time             `json:"updated_at"`
	CompletedAt     *time.Time            `json:"completed_at,omitempty"`

	Storyboard *Storyboard `gorm:"foreignKey:StoryboardID" json:"storyboard,omitempty"`
	Drama      Drama       `gorm:"foreignKey:DramaID" json:"drama,omitempty"`
	Scene      *Scene      `gorm:"foreignKey:SceneID" json:"scene,omitempty"`
	Character  *Character  `gorm:"foreignKey:CharacterID" json:"character,omitempty"`
}

func (ImageGeneration) TableName() string {
	return "image_generations"
}

type ImageGenerationStatus string

const (
	ImageStatusPending    ImageGenerationStatus = "pending"
	ImageStatusProcessing ImageGenerationStatus = "processing"
	ImageStatusCompleted  ImageGenerationStatus = "completed"
	ImageStatusFailed     ImageGenerationStatus = "failed"
)

type ImageProvider string

const (
	ProviderOpenAI          ImageProvider = "openai"
	ProviderMidjourney      ImageProvider = "midjourney"
	ProviderStableDiffusion ImageProvider = "stable_diffusion"
	ProviderDALLE           ImageProvider = "dalle"
)

// ImageType 图片类型
type ImageType string

const (
	ImageTypeCharacter  ImageType = "character"  // 角色图片
	ImageTypeScene      ImageType = "scene"      // 场景图片
	ImageTypeStoryboard ImageType = "storyboard" // 分镜图片
)
