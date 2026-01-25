package models

import (
	"time"

	"gorm.io/datatypes"
	"gorm.io/gorm"
)

type VideoMergeStatus string

const (
	VideoMergeStatusPending    VideoMergeStatus = "pending"
	VideoMergeStatusProcessing VideoMergeStatus = "processing"
	VideoMergeStatusCompleted  VideoMergeStatus = "completed"
	VideoMergeStatusFailed     VideoMergeStatus = "failed"
)

type VideoMerge struct {
	ID          uint             `gorm:"primaryKey;autoIncrement" json:"id"`
	EpisodeID   uint             `gorm:"not null;index" json:"episode_id"`
	DramaID     uint             `gorm:"not null;index" json:"drama_id"`
	Title       string           `gorm:"type:varchar(200)" json:"title"`
	Provider    string           `gorm:"type:varchar(50);not null" json:"provider"`
	Model       *string          `gorm:"type:varchar(100)" json:"model,omitempty"`
	Status      VideoMergeStatus `gorm:"type:varchar(20);not null;default:'pending'" json:"status"`
	Scenes      datatypes.JSON   `gorm:"type:json;not null" json:"scenes"`
	MergedURL   *string          `gorm:"type:varchar(500)" json:"merged_url,omitempty"`
	Duration    *int             `gorm:"type:int" json:"duration,omitempty"`
	TaskID      *string          `gorm:"type:varchar(100)" json:"task_id,omitempty"`
	ErrorMsg    *string          `gorm:"type:text" json:"error_msg,omitempty"`
	CreatedAt   time.Time        `gorm:"not null;autoCreateTime" json:"created_at"`
	CompletedAt *time.Time       `json:"completed_at,omitempty"`
	DeletedAt   gorm.DeletedAt   `gorm:"index" json:"-"`

	Episode Episode `gorm:"foreignKey:EpisodeID" json:"episode,omitempty"`
	Drama   Drama   `gorm:"foreignKey:DramaID" json:"drama,omitempty"`
}

type SceneClip struct {
	SceneID    uint                   `json:"scene_id"`
	VideoURL   string                 `json:"video_url"`
	StartTime  float64                `json:"start_time"`
	EndTime    float64                `json:"end_time"`
	Duration   float64                `json:"duration"`
	Order      int                    `json:"order"`
	Transition map[string]interface{} `json:"transition"`
}

func (v *VideoMerge) TableName() string {
	return "video_merges"
}
