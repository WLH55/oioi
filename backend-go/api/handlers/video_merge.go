package handlers

import (
	"strconv"

	services2 "github.com/drama-generator/backend/application/services"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type VideoMergeHandler struct {
	mergeService *services2.VideoMergeService
	log          *logger.Logger
}

func NewVideoMergeHandler(db *gorm.DB, transferService *services2.ResourceTransferService, storagePath, baseURL string, log *logger.Logger) *VideoMergeHandler {
	return &VideoMergeHandler{
		mergeService: services2.NewVideoMergeService(db, transferService, storagePath, baseURL, log),
		log:          log,
	}
}

func (h *VideoMergeHandler) MergeVideos(c *gin.Context) {
	var req services2.MergeVideoRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, "Invalid request")
		return
	}

	merge, err := h.mergeService.MergeVideos(&req)
	if err != nil {
		h.log.Errorw("Failed to merge videos", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, gin.H{
		"message": "Video merge task created",
		"merge":   merge,
	})
}

func (h *VideoMergeHandler) GetMerge(c *gin.Context) {
	mergeIDStr := c.Param("merge_id")
	mergeID, err := strconv.ParseUint(mergeIDStr, 10, 32)
	if err != nil {
		response.BadRequest(c, "Invalid merge ID")
		return
	}

	merge, err := h.mergeService.GetMerge(uint(mergeID))
	if err != nil {
		h.log.Errorw("Failed to get merge", "error", err)
		response.NotFound(c, "Merge not found")
		return
	}

	response.Success(c, gin.H{"merge": merge})
}

func (h *VideoMergeHandler) ListMerges(c *gin.Context) {
	episodeID := c.Query("episode_id")
	status := c.Query("status")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	var episodeIDPtr *string
	if episodeID != "" {
		episodeIDPtr = &episodeID
	}

	merges, total, err := h.mergeService.ListMerges(episodeIDPtr, status, page, pageSize)
	if err != nil {
		h.log.Errorw("Failed to list merges", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, gin.H{
		"merges":    merges,
		"total":     total,
		"page":      page,
		"page_size": pageSize,
	})
}

func (h *VideoMergeHandler) DeleteMerge(c *gin.Context) {
	mergeIDStr := c.Param("merge_id")
	mergeID, err := strconv.ParseUint(mergeIDStr, 10, 32)
	if err != nil {
		response.BadRequest(c, "Invalid merge ID")
		return
	}

	if err := h.mergeService.DeleteMerge(uint(mergeID)); err != nil {
		h.log.Errorw("Failed to delete merge", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, gin.H{"message": "Merge deleted successfully"})
}
