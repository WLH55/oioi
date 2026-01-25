package handlers

import (
	"strconv"
	"strings"

	"github.com/drama-generator/backend/application/services"
	"github.com/drama-generator/backend/domain/models"
	"github.com/drama-generator/backend/pkg/config"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/drama-generator/backend/pkg/response"
	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type AssetHandler struct {
	assetService *services.AssetService
	log          *logger.Logger
}

func NewAssetHandler(db *gorm.DB, cfg *config.Config, log *logger.Logger) *AssetHandler {
	return &AssetHandler{
		assetService: services.NewAssetService(db, log),
		log:          log,
	}
}

func (h *AssetHandler) CreateAsset(c *gin.Context) {

	var req services.CreateAssetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	asset, err := h.assetService.CreateAsset(&req)
	if err != nil {
		h.log.Errorw("Failed to create asset", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, asset)
}

func (h *AssetHandler) UpdateAsset(c *gin.Context) {

	assetID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	var req services.UpdateAssetRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		response.BadRequest(c, err.Error())
		return
	}

	asset, err := h.assetService.UpdateAsset(uint(assetID), &req)
	if err != nil {
		h.log.Errorw("Failed to update asset", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, asset)
}

func (h *AssetHandler) GetAsset(c *gin.Context) {

	assetID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	asset, err := h.assetService.GetAsset(uint(assetID))
	if err != nil {
		response.NotFound(c, "素材不存在")
		return
	}

	response.Success(c, asset)
}

func (h *AssetHandler) ListAssets(c *gin.Context) {

	var dramaID *string
	if dramaIDStr := c.Query("drama_id"); dramaIDStr != "" {
		dramaID = &dramaIDStr
	}

	var episodeID *uint
	if episodeIDStr := c.Query("episode_id"); episodeIDStr != "" {
		if id, err := strconv.ParseUint(episodeIDStr, 10, 32); err == nil {
			uid := uint(id)
			episodeID = &uid
		}
	}

	var storyboardID *uint
	if storyboardIDStr := c.Query("storyboard_id"); storyboardIDStr != "" {
		if id, err := strconv.ParseUint(storyboardIDStr, 10, 32); err == nil {
			uid := uint(id)
			storyboardID = &uid
		}
	}

	var assetType *models.AssetType
	if typeStr := c.Query("type"); typeStr != "" {
		t := models.AssetType(typeStr)
		assetType = &t
	}

	var isFavorite *bool
	if favoriteStr := c.Query("is_favorite"); favoriteStr != "" {
		if favoriteStr == "true" {
			fav := true
			isFavorite = &fav
		} else if favoriteStr == "false" {
			fav := false
			isFavorite = &fav
		}
	}

	var tagIDs []uint
	if tagIDsStr := c.Query("tag_ids"); tagIDsStr != "" {
		for _, idStr := range strings.Split(tagIDsStr, ",") {
			if id, err := strconv.ParseUint(strings.TrimSpace(idStr), 10, 32); err == nil {
				tagIDs = append(tagIDs, uint(id))
			}
		}
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "20"))

	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 20
	}

	req := &services.ListAssetsRequest{
		DramaID:      dramaID,
		EpisodeID:    episodeID,
		StoryboardID: storyboardID,
		Type:         assetType,
		Category:     c.Query("category"),
		TagIDs:       tagIDs,
		IsFavorite:   isFavorite,
		Search:       c.Query("search"),
		Page:         page,
		PageSize:     pageSize,
	}

	assets, total, err := h.assetService.ListAssets(req)
	if err != nil {
		h.log.Errorw("Failed to list assets", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.SuccessWithPagination(c, assets, total, page, pageSize)
}

func (h *AssetHandler) DeleteAsset(c *gin.Context) {

	assetID, err := strconv.ParseUint(c.Param("id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	if err := h.assetService.DeleteAsset(uint(assetID)); err != nil {
		h.log.Errorw("Failed to delete asset", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, nil)
}

func (h *AssetHandler) ImportFromImageGen(c *gin.Context) {

	imageGenID, err := strconv.ParseUint(c.Param("image_gen_id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	asset, err := h.assetService.ImportFromImageGen(uint(imageGenID))
	if err != nil {
		h.log.Errorw("Failed to import from image gen", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, asset)
}

func (h *AssetHandler) ImportFromVideoGen(c *gin.Context) {

	videoGenID, err := strconv.ParseUint(c.Param("video_gen_id"), 10, 32)
	if err != nil {
		response.BadRequest(c, "无效的ID")
		return
	}

	asset, err := h.assetService.ImportFromVideoGen(uint(videoGenID))
	if err != nil {
		h.log.Errorw("Failed to import from video gen", "error", err)
		response.InternalError(c, err.Error())
		return
	}

	response.Success(c, asset)
}
