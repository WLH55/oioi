package services

import (
	"fmt"
	"strconv"

	"github.com/drama-generator/backend/domain/models"
	"github.com/drama-generator/backend/pkg/ai"
	"github.com/drama-generator/backend/pkg/config"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/drama-generator/backend/pkg/utils"
	"gorm.io/gorm"
)

type ScriptGenerationService struct {
	db         *gorm.DB
	aiService  *AIService
	log        *logger.Logger
	config     *config.Config
	promptI18n *PromptI18n
}

func NewScriptGenerationService(db *gorm.DB, cfg *config.Config, log *logger.Logger) *ScriptGenerationService {
	return &ScriptGenerationService{
		db:         db,
		aiService:  NewAIService(db, log),
		log:        log,
		config:     cfg,
		promptI18n: NewPromptI18n(cfg),
	}
}

type GenerateCharactersRequest struct {
	DramaID     string  `json:"drama_id" binding:"required"`
	EpisodeID   uint    `json:"episode_id"`
	Outline     string  `json:"outline"`
	Count       int     `json:"count"`
	Temperature float64 `json:"temperature"`
	Model       string  `json:"model"` // 指定使用的文本模型
}

func (s *ScriptGenerationService) GenerateCharacters(req *GenerateCharactersRequest) ([]models.Character, error) {
	var drama models.Drama
	if err := s.db.Where("id = ? ", req.DramaID).First(&drama).Error; err != nil {
		return nil, fmt.Errorf("drama not found")
	}

	count := req.Count
	if count == 0 {
		count = 5
	}

	systemPrompt := s.promptI18n.GetCharacterExtractionPrompt()

	outlineText := req.Outline
	if outlineText == "" {
		outlineText = s.promptI18n.FormatUserPrompt("drama_info_template", drama.Title, drama.Description, drama.Genre)
	}

	userPrompt := s.promptI18n.FormatUserPrompt("character_request", outlineText, count)

	temperature := req.Temperature
	if temperature == 0 {
		temperature = 0.7
	}

	// 如果指定了模型，使用指定的模型；否则使用默认配置
	var text string
	var err error
	if req.Model != "" {
		s.log.Infow("Using specified model for character generation", "model", req.Model)
		client, getErr := s.aiService.GetAIClientForModel("text", req.Model)
		if getErr != nil {
			s.log.Warnw("Failed to get client for specified model, using default", "model", req.Model, "error", getErr)
			text, err = s.aiService.GenerateText(userPrompt, systemPrompt, ai.WithTemperature(temperature))
		} else {
			text, err = client.GenerateText(userPrompt, systemPrompt, ai.WithTemperature(temperature))
		}
	} else {
		text, err = s.aiService.GenerateText(userPrompt, systemPrompt, ai.WithTemperature(temperature))
	}

	if err != nil {
		s.log.Errorw("Failed to generate characters", "error", err)
		return nil, fmt.Errorf("生成失败: %w", err)
	}

	s.log.Infow("AI response received", "length", len(text), "preview", text[:minInt(200, len(text))])

	// AI直接返回数组格式
	var result []struct {
		Name        string `json:"name"`
		Role        string `json:"role"`
		Description string `json:"description"`
		Personality string `json:"personality"`
		Appearance  string `json:"appearance"`
		VoiceStyle  string `json:"voice_style"`
	}

	if err := utils.SafeParseAIJSON(text, &result); err != nil {
		s.log.Errorw("Failed to parse characters JSON", "error", err, "raw_response", text[:minInt(500, len(text))])
		return nil, fmt.Errorf("解析 AI 返回结果失败: %w", err)
	}

	var characters []models.Character
	for _, char := range result {
		// 检查角色是否已存在
		var existingChar models.Character
		err := s.db.Where("drama_id = ? AND name = ?", req.DramaID, char.Name).First(&existingChar).Error
		if err == nil {
			// 角色已存在，直接使用已存在的角色，不覆盖
			s.log.Infow("Character already exists, skipping", "drama_id", req.DramaID, "name", char.Name)
			characters = append(characters, existingChar)
			continue
		}

		// 角色不存在，创建新角色
		dramaID, _ := strconv.ParseUint(req.DramaID, 10, 32)
		character := models.Character{
			DramaID:     uint(dramaID),
			Name:        char.Name,
			Role:        &char.Role,
			Description: &char.Description,
			Personality: &char.Personality,
			Appearance:  &char.Appearance,
			VoiceStyle:  &char.VoiceStyle,
		}

		if err := s.db.Create(&character).Error; err != nil {
			s.log.Errorw("Failed to create character", "error", err)
			continue
		}

		characters = append(characters, character)
	}

	// 如果提供了 EpisodeID，建立 episode_characters 关联关系
	if req.EpisodeID > 0 {
		var episode models.Episode
		if err := s.db.First(&episode, req.EpisodeID).Error; err == nil {
			// 使用 GORM 的 Association 建立多对多关联
			if err := s.db.Model(&episode).Association("Characters").Append(characters); err != nil {
				s.log.Errorw("Failed to associate characters with episode", "error", err, "episode_id", req.EpisodeID)
			} else {
				s.log.Infow("Characters associated with episode", "episode_id", req.EpisodeID, "character_count", len(characters))
			}
		} else {
			s.log.Errorw("Episode not found for association", "episode_id", req.EpisodeID, "error", err)
		}
	}

	s.log.Infow("Characters generated", "drama_id", req.DramaID, "total_count", len(characters), "new_count", len(characters))
	return characters, nil
}

// GenerateScenesForEpisode 已废弃，使用 StoryboardService.GenerateStoryboard 替代
// ParseScript 已废弃，使用 GenerateCharacters 替代

// minInt 返回两个整数中较小的一个
func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}
