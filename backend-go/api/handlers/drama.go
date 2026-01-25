package handlers

import (
	"github.com/drama-generator/backend/application/services"
	"github.com/drama-generator/backend/domain/models"
	"github.com/drama-generator/backend/pkg/config"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type DramaHandler struct {
	db                *gorm.DB
	dramaService      *services.DramaService
	videoMergeService *services.VideoMergeService
	log               *logger.Logger
}

func NewDramaHandler(db *gorm.DB, cfg *config.Config, log *logger.Logger, transferService *services.ResourceTransferService) *DramaHandler {
	return &DramaHandler{
		db:                db,
		dramaService:      services.NewDramaService(db, log),
		videoMergeService: services.NewVideoMergeService(db, transferService, cfg.Storage.LocalPath, cfg.Storage.BaseURL, log),
		log:               log,
	}
}

func (h *DramaHandler) CreateDrama(c *gin.Context) {

	var req services.CreateDramaRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	drama, err := h.dramaService.CreateDrama(&req)
	if err != nil {
		response.InternalError(c, "创建失败")
		return
	}

	response.Created(c, drama)
}

func (h *DramaHandler) GetDrama(c *gin.Context) {

	dramaID := c.Param("id")

	drama, err := h.dramaService.GetDrama(dramaID)
	if err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "获取失败")
		return
	}

	response.Success(c, drama)
}

func (h *DramaHandler) ListDramas(c *gin.Context) {

	var query services.DramaListQuery
	if err := c.ShouldBindQuery(&query); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	if query.Page < 1 {
		query.Page = 1
	}
	if query.PageSize < 1 || query.PageSize > 100 {
		query.PageSize = 20
	}

	dramas, total, err := h.dramaService.ListDramas(&query)
	if err != nil {
		response.InternalError(c, "获取列表失败")
		return
	}

	response.SuccessWithPagination(c, dramas, total, query.Page, query.PageSize)
}

func (h *DramaHandler) UpdateDrama(c *gin.Context) {

	dramaID := c.Param("id")

	var req services.UpdateDramaRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	drama, err := h.dramaService.UpdateDrama(dramaID, &req)
	if err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "更新失败")
		return
	}

	response.Success(c, drama)
}

func (h *DramaHandler) DeleteDrama(c *gin.Context) {

	dramaID := c.Param("id")

	if err := h.dramaService.DeleteDrama(dramaID); err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "删除失败")
		return
	}

	response.Success(c, gin.H{"message": "删除成功"})
}

func (h *DramaHandler) GetDramaStats(c *gin.Context) {

	stats, err := h.dramaService.GetDramaStats()
	if err != nil {
		response.InternalError(c, "获取统计失败")
		return
	}

	response.Success(c, stats)
}

func (h *DramaHandler) SaveOutline(c *gin.Context) {

	dramaID := c.Param("id")

	var req services.SaveOutlineRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	if err := h.dramaService.SaveOutline(dramaID, &req); err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "保存失败")
		return
	}

	response.Success(c, gin.H{"message": "保存成功"})
}

func (h *DramaHandler) GetCharacters(c *gin.Context) {

	dramaID := c.Param("id")
	episodeID := c.Query("episode_id") // 可选：如果提供则只返回该章节的角色

	var episodeIDPtr *string
	if episodeID != "" {
		episodeIDPtr = &episodeID
	}

	characters, err := h.dramaService.GetCharacters(dramaID, episodeIDPtr)
	if err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		if err.Error() == "episode not found" {
			response.NotFound(c, "章节不存在")
			return
		}
		response.InternalError(c, "获取角色失败")
		return
	}

	response.Success(c, characters)
}

func (h *DramaHandler) SaveCharacters(c *gin.Context) {

	dramaID := c.Param("id")

	var req services.SaveCharactersRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	if err := h.dramaService.SaveCharacters(dramaID, &req); err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "保存失败")
		return
	}

	response.Success(c, gin.H{"message": "保存成功"})
}

func (h *DramaHandler) SaveEpisodes(c *gin.Context) {

	dramaID := c.Param("id")

	var req services.SaveEpisodesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	if err := h.dramaService.SaveEpisodes(dramaID, &req); err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "保存失败")
		return
	}

	response.Success(c, gin.H{"message": "保存成功"})
}

func (h *DramaHandler) SaveProgress(c *gin.Context) {

	dramaID := c.Param("id")

	var req services.SaveProgressRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	if err := h.dramaService.SaveProgress(dramaID, &req); err != nil {
		if err.Error() == "drama not found" {
			response.NotFound(c, "剧本不存在")
			return
		}
		response.InternalError(c, "保存失败")
		return
	}

	response.Success(c, gin.H{"message": "保存成功"})
}

// FinalizeEpisode 完成集数制作（触发视频合成）
func (h *DramaHandler) FinalizeEpisode(c *gin.Context) {

	episodeID := c.Param("episode_id")
	if episodeID == "" {
		response.BadRequest(c, "episode_id不能为空")
		return
	}

	// 尝试读取时间线数据（可选）
	var timelineData *services.FinalizeEpisodeRequest
	if err := c.ShouldBindJSON(&timelineData); err != nil {
		// 如果没有请求体或解析失败，使用nil（将使用默认场景顺序）
		h.log.Warnw("No timeline data provided, will use default scene order", "error", err)
		timelineData = nil
	} else if timelineData != nil {
		h.log.Infow("Received timeline data", "clips_count", len(timelineData.Clips), "episode_id", episodeID)
	}

	// 触发视频合成任务
	result, err := h.videoMergeService.FinalizeEpisode(episodeID, timelineData)
	if err != nil {
		h.log.Errorw("Failed to finalize episode", "error", err, "episode_id", episodeID)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, result)
}

// DownloadEpisodeVideo 下载剧集视频
func (h *DramaHandler) DownloadEpisodeVideo(c *gin.Context) {

	episodeID := c.Param("episode_id")
	if episodeID == "" {
		response.BadRequest(c, "episode_id不能为空")
		return
	}

	// 查询episode
	var episode models.Episode
	if err := h.db.Preload("Drama").Where("id = ?", episodeID).First(&episode).Error; err != nil {
		response.NotFound(c, "剧集不存在")
		return
	}

	// 检查是否有视频
	if episode.VideoURL == nil || *episode.VideoURL == "" {
		response.BadRequest(c, "该剧集还没有生成视频")
		return
	}

	// 返回视频URL，让前端重定向下载
	c.JSON(200, gin.H{
		"video_url":      *episode.VideoURL,
		"title":          episode.Title,
		"episode_number": episode.EpisodeNum,
	})
}
