package models

import (
	"time"

	"gorm.io/gorm"
)

type Timeline struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	DramaID uint  `gorm:"not null;index" json:"drama_id"`
	Drama   Drama `gorm:"foreignKey:DramaID" json:"drama,omitempty"`

	EpisodeID *uint    `gorm:"index" json:"episode_id,omitempty"`
	Episode   *Episode `gorm:"foreignKey:EpisodeID" json:"episode,omitempty"`

	Name        string  `gorm:"type:varchar(200);not null" json:"name"`
	Description *string `gorm:"type:text" json:"description,omitempty"`

	Duration   int     `gorm:"default:0" json:"duration"`
	FPS        int     `gorm:"default:30" json:"fps"`
	Resolution *string `gorm:"type:varchar(50)" json:"resolution,omitempty"`

	Status TimelineStatus `gorm:"type:varchar(20);not null;default:'draft';index" json:"status"`

	Tracks []TimelineTrack `gorm:"foreignKey:TimelineID" json:"tracks,omitempty"`
}

type TimelineStatus string

const (
	TimelineStatusDraft     TimelineStatus = "draft"
	TimelineStatusEditing   TimelineStatus = "editing"
	TimelineStatusCompleted TimelineStatus = "completed"
	TimelineStatusExporting TimelineStatus = "exporting"
)

func (Timeline) TableName() string {
	return "timelines"
}

type TimelineTrack struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	TimelineID uint     `gorm:"not null;index" json:"timeline_id"`
	Timeline   Timeline `gorm:"foreignKey:TimelineID" json:"-"`

	Name     string    `gorm:"type:varchar(100);not null" json:"name"`
	Type     TrackType `gorm:"type:varchar(20);not null" json:"type"`
	Order    int       `gorm:"not null;default:0" json:"order"`
	IsLocked bool      `gorm:"default:false" json:"is_locked"`
	IsMuted  bool      `gorm:"default:false" json:"is_muted"`
	Volume   *int      `gorm:"default:100" json:"volume,omitempty"`

	Clips []TimelineClip `gorm:"foreignKey:TrackID" json:"clips,omitempty"`
}

type TrackType string

const (
	TrackTypeVideo TrackType = "video"
	TrackTypeAudio TrackType = "audio"
	TrackTypeText  TrackType = "text"
)

func (TimelineTrack) TableName() string {
	return "timeline_tracks"
}

type TimelineClip struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	TrackID uint          `gorm:"not null;index" json:"track_id"`
	Track   TimelineTrack `gorm:"foreignKey:TrackID" json:"-"`

	AssetID *uint `gorm:"index" json:"asset_id,omitempty"`
	Asset   Asset `gorm:"foreignKey:AssetID" json:"asset,omitempty"`

	StoryboardID *uint       `gorm:"index" json:"storyboard_id,omitempty"`
	Storyboard   *Storyboard `gorm:"foreignKey:StoryboardID" json:"storyboard,omitempty"`

	Name string `gorm:"type:varchar(200)" json:"name"`

	StartTime int `gorm:"not null" json:"start_time"`
	EndTime   int `gorm:"not null" json:"end_time"`
	Duration  int `gorm:"not null" json:"duration"`

	TrimStart *int `json:"trim_start,omitempty"`
	TrimEnd   *int `json:"trim_end,omitempty"`

	Speed *float64 `gorm:"default:1.0" json:"speed,omitempty"`

	Volume  *int `json:"volume,omitempty"`
	IsMuted bool `gorm:"default:false" json:"is_muted"`
	FadeIn  *int `json:"fade_in,omitempty"`
	FadeOut *int `json:"fade_out,omitempty"`

	TransitionIn  *uint          `gorm:"index" json:"transition_in_id,omitempty"`
	TransitionOut *uint          `gorm:"index" json:"transition_out_id,omitempty"`
	InTransition  ClipTransition `gorm:"foreignKey:TransitionIn" json:"in_transition,omitempty"`
	OutTransition ClipTransition `gorm:"foreignKey:TransitionOut" json:"out_transition,omitempty"`

	Effects []ClipEffect `gorm:"foreignKey:ClipID" json:"effects,omitempty"`
}

func (TimelineClip) TableName() string {
	return "timeline_clips"
}

type ClipTransition struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	Type     TransitionType `gorm:"type:varchar(50);not null" json:"type"`
	Duration int            `gorm:"not null;default:500" json:"duration"`
	Easing   *string        `gorm:"type:varchar(50)" json:"easing,omitempty"`

	Config map[string]interface{} `gorm:"serializer:json" json:"config,omitempty"`
}

type TransitionType string

const (
	TransitionTypeFade      TransitionType = "fade"
	TransitionTypeCrossFade TransitionType = "crossfade"
	TransitionTypeSlide     TransitionType = "slide"
	TransitionTypeWipe      TransitionType = "wipe"
	TransitionTypeZoom      TransitionType = "zoom"
	TransitionTypeDissolve  TransitionType = "dissolve"
)

func (ClipTransition) TableName() string {
	return "clip_transitions"
}

type ClipEffect struct {
	ID        uint           `gorm:"primarykey" json:"id"`
	CreatedAt time.Time      `json:"created_at"`
	UpdatedAt time.Time      `json:"updated_at"`
	DeletedAt gorm.DeletedAt `gorm:"index" json:"-"`

	ClipID uint         `gorm:"not null;index" json:"clip_id"`
	Clip   TimelineClip `gorm:"foreignKey:ClipID" json:"-"`

	Type      EffectType `gorm:"type:varchar(50);not null" json:"type"`
	Name      string     `gorm:"type:varchar(100)" json:"name"`
	IsEnabled bool       `gorm:"default:true" json:"is_enabled"`
	Order     int        `gorm:"default:0" json:"order"`

	Config map[string]interface{} `gorm:"serializer:json" json:"config,omitempty"`
}

type EffectType string

const (
	EffectTypeFilter     EffectType = "filter"
	EffectTypeColor      EffectType = "color"
	EffectTypeBlur       EffectType = "blur"
	EffectTypeBrightness EffectType = "brightness"
	EffectTypeContrast   EffectType = "contrast"
	EffectTypeSaturation EffectType = "saturation"
)

func (ClipEffect) TableName() string {
	return "clip_effects"
}
