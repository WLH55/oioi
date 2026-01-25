package models

import (
	"time"

	"gorm.io/gorm"
)

type Asset struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	DramaID *uint  `gorm:"index" json:"drama_id,omitempty"`
	Drama   *Drama `gorm:"foreignKey:DramaID" json:"drama,omitempty"`

	EpisodeID     *uint `gorm:"index" json:"episode_id,omitempty"`
	StoryboardID  *uint `gorm:"index" json:"storyboard_id,omitempty"`
	StoryboardNum *int  `json:"storyboard_num,omitempty"`

	Name         string    `gorm:"type:varchar(200);not null" json:"name"`
	Description  *string   `gorm:"type:text" json:"description,omitempty"`
	Type         AssetType `gorm:"type:varchar(20);not null;index" json:"type"`
	Category     *string   `gorm:"type:varchar(50);index" json:"category,omitempty"`
	URL          string    `gorm:"type:varchar(1000);not null" json:"url"`
	ThumbnailURL *string   `gorm:"type:varchar(1000)" json:"thumbnail_url,omitempty"`
	LocalPath    *string   `gorm:"type:varchar(500)" json:"local_path,omitempty"`

	FileSize *int64  `json:"file_size,omitempty"`
	MimeType *string `gorm:"type:varchar(100)" json:"mime_type,omitempty"`
	Width    *int    `json:"width,omitempty"`
	Height   *int    `json:"height,omitempty"`
	Duration *int    `json:"duration,omitempty"`
	Format   *string `gorm:"type:varchar(50)" json:"format,omitempty"`

	ImageGenID *uint           `gorm:"index" json:"image_gen_id,omitempty"`
	ImageGen   ImageGeneration `gorm:"foreignKey:ImageGenID" json:"image_gen,omitempty"`

	VideoGenID *uint           `gorm:"index" json:"video_gen_id,omitempty"`
	VideoGen   VideoGeneration `gorm:"foreignKey:VideoGenID" json:"video_gen,omitempty"`

	IsFavorite bool `gorm:"default:false" json:"is_favorite"`
	ViewCount  int  `gorm:"default:0" json:"view_count"`
}

type AssetType string

const (
	AssetTypeImage AssetType = "image"
	AssetTypeVideo AssetType = "video"
	AssetTypeAudio AssetType = "audio"
)

func (Asset) TableName() string {
	return "assets"
}
