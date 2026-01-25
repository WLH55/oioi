package models

import (
	"time"

	"gorm.io/gorm"
)

type VideoGeneration struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	StoryboardID *uint       `gorm:"index" json:"storyboard_id,omitempty"`
	Storyboard   *Storyboard `gorm:"foreignKey:StoryboardID" json:"storyboard,omitempty"`

	DramaID uint  `gorm:"not null;index" json:"drama_id"`
	Drama   Drama `gorm:"foreignKey:DramaID" json:"drama,omitempty"`

	Provider string `gorm:"type:varchar(50);not null;index" json:"provider"`
	Prompt   string `gorm:"type:text;not null" json:"prompt"`
	Model    string `gorm:"type:varchar(100)" json:"model,omitempty"`

	ImageGenID *uint           `gorm:"index" json:"image_gen_id,omitempty"`
	ImageGen   ImageGeneration `gorm:"foreignKey:ImageGenID" json:"image_gen,omitempty"`

	// 参考图模式：single(单图), first_last(首尾帧), multiple(多图), none(无)
	ReferenceMode *string `gorm:"type:varchar(20)" json:"reference_mode,omitempty"`

	ImageURL           *string `gorm:"type:varchar(1000)" json:"image_url,omitempty"`
	FirstFrameURL      *string `gorm:"type:varchar(1000)" json:"first_frame_url,omitempty"`
	LastFrameURL       *string `gorm:"type:varchar(1000)" json:"last_frame_url,omitempty"`
	ReferenceImageURLs *string `gorm:"type:text" json:"reference_image_urls,omitempty"` // JSON数组存储多张参考图

	Duration     *int    `json:"duration,omitempty"`
	FPS          *int    `json:"fps,omitempty"`
	Resolution   *string `gorm:"type:varchar(50)" json:"resolution,omitempty"`
	AspectRatio  *string `gorm:"type:varchar(20)" json:"aspect_ratio,omitempty"`
	Style        *string `gorm:"type:varchar(100)" json:"style,omitempty"`
	MotionLevel  *int    `json:"motion_level,omitempty"`
	CameraMotion *string `gorm:"type:varchar(100)" json:"camera_motion,omitempty"`
	Seed         *int64  `json:"seed,omitempty"`

	VideoURL  *string `gorm:"type:varchar(1000)" json:"video_url,omitempty"`
	MinioURL  *string `gorm:"type:varchar(1000)" json:"minio_url,omitempty"`
	LocalPath *string `gorm:"type:varchar(500)" json:"local_path,omitempty"`

	Status VideoStatus `gorm:"type:varchar(20);not null;default:'pending';index" json:"status"`
	TaskID *string     `gorm:"type:varchar(200);index" json:"task_id,omitempty"`

	ErrorMsg    *string    `gorm:"type:text" json:"error_msg,omitempty"`
	CompletedAt *time.Time `json:"completed_at,omitempty"`

	Width  *int `json:"width,omitempty"`
	Height *int `json:"height,omitempty"`
}

type VideoStatus string

const (
	VideoStatusPending    VideoStatus = "pending"
	VideoStatusProcessing VideoStatus = "processing"
	VideoStatusCompleted  VideoStatus = "completed"
	VideoStatusFailed     VideoStatus = "failed"
)

type VideoProvider string

const (
	VideoProviderRunway VideoProvider = "runway"
	VideoProviderPika   VideoProvider = "pika"
	VideoProviderDoubao VideoProvider = "doubao"
	VideoProviderOpenAI VideoProvider = "openai"
)

func (VideoGeneration) TableName() string {
	return "video_generations"
}
