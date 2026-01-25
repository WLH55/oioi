package handlers

import (
	"strconv"

	"github.com/drama-generator/backend/application/services"
	"github.com/drama-generator/backend/infrastructure/storage"
	"github.com/drama-generator/backend/pkg/config"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type ImageGenerationHandler struct {
	imageService *services.ImageGenerationService
	taskService  *services.TaskService
	log          *logger.Logger
}

func NewImageGenerationHandler(db *gorm.DB, cfg *config.Config, log *logger.Logger, transferService *services.ResourceTransferService, localStorage *storage.LocalStorage) *ImageGenerationHandler {
	return &ImageGenerationHandler{
		imageService: services.NewImageGenerationService(db, cfg, transferService, localStorage, log),
		taskService:  services.NewTaskService(db, log),
		log:          log,
	}
}

func (h *ImageGenerationHandler) GenerateImage(c *gin.Context) {

	var req services.GenerateImageRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	imageGen, err := h.imageService.GenerateImage(&req)
	if err != nil {
		h.log.Errorw("Failed to generate image", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, imageGen)
}

func (h *ImageGenerationHandler) GenerateImagesForScene(c *gin.Context) {

	sceneID := c.Param("scene_id")

	images, err := h.imageService.GenerateImagesForScene(sceneID)
	if err != nil {
		h.log.Errorw("Failed to generate images for scene", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, images)
}

func (h *ImageGenerationHandler) GetBackgroundsForEpisode(c *gin.Context) {

	episodeID := c.Param("episode_id")

	backgrounds, err := h.imageService.GetScencesForEpisode(episodeID)
	if err != nil {
		h.log.Errorw("Failed to get backgrounds", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, backgrounds)
}

func (h *ImageGenerationHandler) ExtractBackgroundsForEpisode(c *gin.Context) {
	episodeID := c.Param("episode_id")

	// 接收可选的 model 参数
	var req struct {
		Model string `json:"model"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		// 如果没有提供body或者解析失败，使用空字符串（使用默认模型）
		req.Model = ""
	}

	// 创建异步任务
	task, err := h.taskService.CreateTask("background_extraction", episodeID)
	if err != nil {
		h.log.Errorw("Failed to create task", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	// 启动后台goroutine处理
	go h.processBackgroundExtraction(task.ID, episodeID, req.Model)

	// 立即返回任务ID
	response.Success(c, gin.H{
		"task_id": task.ID,
		"status":  "pending",
		"message": "场景提取任务已创建，正在后台处理...",
	})
}

// processBackgroundExtraction 后台处理场景提取
func (h *ImageGenerationHandler) processBackgroundExtraction(taskID, episodeID, model string) {
	h.log.Infow("Starting background extraction", "task_id", taskID, "episode_id", episodeID, "model", model)

	// 更新任务状态为处理中
	if err := h.taskService.UpdateTaskStatus(taskID, "processing", 10, "开始提取场景..."); err != nil {
		h.log.Errorw("Failed to update task status", "error", err)
	}

	// 调用实际的提取逻辑
	backgrounds, err := h.imageService.ExtractBackgroundsForEpisode(episodeID, model)
	if err != nil {
		h.log.Errorw("Failed to extract backgrounds", "error", err, "task_id", taskID)
		if updateErr := h.taskService.UpdateTaskError(taskID, err); updateErr != nil {
			h.log.Errorw("Failed to update task error", "error", updateErr)
		}
		return
	}

	// 更新任务结果
	result := gin.H{
		"backgrounds": backgrounds,
		"total":       len(backgrounds),
	}
	if err := h.taskService.UpdateTaskResult(taskID, result); err != nil {
		h.log.Errorw("Failed to update task result", "error", err)
		return
	}

	h.log.Infow("Background extraction completed", "task_id", taskID, "total", len(backgrounds))
}

func (h *ImageGenerationHandler) BatchGenerateForEpisode(c *gin.Context) {

	episodeID := c.Param("episode_id")

	images, err := h.imageService.BatchGenerateImagesForEpisode(episodeID)
	if err != nil {
		h.log.Errorw("Failed to batch generate images", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, images)
}

func (h *ImageGenerationHandler) GetImageGeneration(c *gin.Context) {

	imageGenID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	imageGen, err := h.imageService.GetImageGeneration(uint(imageGenID))
	if err != nil {
		response.NotFound(c, "图片生成记录不存在")
		return
	}

	response.Success(c, imageGen)
}

func (h *ImageGenerationHandler) ListImageGenerations(c *gin.Context) {
	var sceneID *uint
	if sceneIDStr := c.Query("scene_id"); sceneIDStr != "" {
		id, err := strconv.ParseUint(sceneIDStr, 10, 32)
		if err == nil {
			uid := uint(id)
			sceneID = &uid
		}
	}

	var storyboardID *uint
	if storyboardIDStr := c.Query("storyboard_id"); storyboardIDStr != "" {
		id, err := strconv.ParseUint(storyboardIDStr, 10, 32)
		if err == nil {
			uid := uint(id)
			storyboardID = &uid
		}
	}

	frameType := c.Query("frame_type")
	status := c.Query("status")
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	var dramaIDUint *uint
	if dramaIDStr := c.Query("drama_id"); dramaIDStr != "" {
		did, _ := strconv.ParseUint(dramaIDStr, 10, 32)
		didUint := uint(did)
		dramaIDUint = &didUint
	}

	images, total, err := h.imageService.ListImageGenerations(dramaIDUint, sceneID, storyboardID, frameType, status, page, pageSize)

	if err != nil {
		h.log.Errorw("Failed to list images", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.SuccessWithPagination(c, images, total, page, pageSize)
}

func (h *ImageGenerationHandler) DeleteImageGeneration(c *gin.Context) {

	imageGenID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	if err := h.imageService.DeleteImageGeneration(uint(imageGenID)); err != nil {
		h.log.Errorw("Failed to delete image", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, nil)
}
