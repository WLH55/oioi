package models

import (
	"time"

	"gorm.io/gorm"
)

// AsyncTask 异步任务模型
type AsyncTask struct {
	ID          string         `gorm:"primaryKey;size:36" json:"id"`
	Type        string         `gorm:"size:50;not null;index" json:"type"`   // 任务类型：storyboard_generation
	Status      string         `gorm:"size:20;not null;index" json:"status"` // pending, processing, completed, failed
	Progress    int            `gorm:"default:0" json:"progress"`            // 0-100
	Message     string         `gorm:"size:500" json:"message,omitempty"`    // 当前状态消息
	Error       string         `gorm:"type:text" json:"error,omitempty"`     // 错误信息
	Result      string         `gorm:"type:text" json:"result,omitempty"`    // JSON格式的结果数据
	ResourceID  string         `gorm:"size:36;index" json:"resource_id"`     // 关联资源ID（如episode_id）
	CreatedAt   time.Time      `gorm:"autoCreateTime" json:"created_at"`
	UpdatedAt   time.Time      `gorm:"autoUpdateTime" json:"updated_at"`
	CompletedAt *time.Time     `json:"completed_at,omitempty"`
	DeletedAt   gorm.DeletedAt `gorm:"index" json:"-"`
}
