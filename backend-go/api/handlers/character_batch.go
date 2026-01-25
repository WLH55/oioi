package handlers

import (
	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
)

// BatchGenerateCharacterImages 批量生成角色图片
func (h *CharacterLibraryHandler) BatchGenerateCharacterImages(c *gin.Context) {

	var req struct {
		CharacterIDs []string `json:"character_ids" binding:"required,min=1"`
		Model        string   `json:"model"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	// 限制批量生成数量
	if len(req.CharacterIDs) > 10 {
		response.BadRequest(c, "单次最多生成10个角色")
		return
	}

	// 异步批量生成
	go h.libraryService.BatchGenerateCharacterImages(req.CharacterIDs, h.imageService, req.Model)

	response.Success(c, gin.H{
		"message": "批量生成任务已提交",
		"count":   len(req.CharacterIDs),
	})
}
