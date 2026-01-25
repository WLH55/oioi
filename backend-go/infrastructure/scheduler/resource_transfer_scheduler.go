package scheduler

import (
	"time"

	"github.com/drama-generator/backend/application/services"
	"github.com/drama-generator/backend/pkg/logger"
	"github.com/robfig/cron/v3"
	"gorm.io/gorm"
)

type ResourceTransferScheduler struct {
	cron            *cron.Cron
	transferService *services.ResourceTransferService
	db              *gorm.DB
	log             *logger.Logger
	running         bool
}

func NewResourceTransferScheduler(
	transferService *services.ResourceTransferService,
	db *gorm.DB,
	log *logger.Logger,
) *ResourceTransferScheduler {
	return &ResourceTransferScheduler{
		cron:            cron.New(cron.WithSeconds()),
		transferService: transferService,
		db:              db,
		log:             log,
		running:         false,
	}
}

// Start 启动定时任务
func (s *ResourceTransferScheduler) Start() error {
	if s.running {
		s.log.Warn("Resource transfer scheduler already running")
		return nil
	}

	s.log.Info("Starting resource transfer scheduler...")

	// 每小时执行一次资源转存任务
	_, err := s.cron.AddFunc("0 0 * * * *", func() {
		s.log.Info("Starting scheduled resource transfer task")
		s.transferPendingResources()
	})
	if err != nil {
		return err
	}

	// 每天凌晨2点执行完整扫描
	_, err = s.cron.AddFunc("0 0 2 * * *", func() {
		s.log.Info("Starting daily full resource scan and transfer")
		s.transferAllPendingResources()
	})
	if err != nil {
		return err
	}

	s.cron.Start()
	s.running = true
	s.log.Info("Resource transfer scheduler started successfully")

	return nil
}

// Stop 停止定时任务
func (s *ResourceTransferScheduler) Stop() {
	if !s.running {
		return
	}

	s.log.Info("Stopping resource transfer scheduler...")
	ctx := s.cron.Stop()
	<-ctx.Done()
	s.running = false
	s.log.Info("Resource transfer scheduler stopped")
}

// transferPendingResources 转存最近生成的待转存资源（最近24小时）
func (s *ResourceTransferScheduler) transferPendingResources() {
	s.log.Info("Scanning for pending resources to transfer (last 24 hours)...")

	// 查找最近24小时内完成的、还未转存的图片和视频
	type DramaCount struct {
		DramaID string
		Count   int64
	}

	// 统计每个剧本的待转存图片数量
	var imageDramas []DramaCount
	s.db.Raw(`
		SELECT drama_id, COUNT(*) as count 
		FROM image_generations 
		WHERE status = 'completed' 
		AND image_url IS NOT NULL 
		AND image_url != ''
		AND (minio_url IS NULL OR minio_url = '')
		AND completed_at >= ?
		GROUP BY drama_id
	`, time.Now().Add(-24*time.Hour)).Scan(&imageDramas)

	// 转存图片
	imageCount := 0
	for _, drama := range imageDramas {
		count, err := s.transferService.BatchTransferImagesToMinio(drama.DramaID, 50) // 每个剧本最多转50个
		if err != nil {
			s.log.Errorw("Failed to transfer images for drama",
				"drama_id", drama.DramaID,
				"error", err)
			continue
		}
		imageCount += count
		s.log.Infow("Transferred images for drama",
			"drama_id", drama.DramaID,
			"count", count)
	}

	// 统计每个剧本的待转存视频数量
	var videoDramas []DramaCount
	s.db.Raw(`
		SELECT drama_id, COUNT(*) as count 
		FROM video_generations 
		WHERE status = 'completed' 
		AND video_url IS NOT NULL 
		AND video_url != ''
		AND (minio_url IS NULL OR minio_url = '')
		AND completed_at >= ?
		GROUP BY drama_id
	`, time.Now().Add(-24*time.Hour)).Scan(&videoDramas)

	// 转存视频
	videoCount := 0
	for _, drama := range videoDramas {
		count, err := s.transferService.BatchTransferVideosToMinio(drama.DramaID, 50) // 每个剧本最多转50个
		if err != nil {
			s.log.Errorw("Failed to transfer videos for drama",
				"drama_id", drama.DramaID,
				"error", err)
			continue
		}
		videoCount += count
		s.log.Infow("Transferred videos for drama",
			"drama_id", drama.DramaID,
			"count", count)
	}

	s.log.Infow("Scheduled resource transfer task completed",
		"images", imageCount,
		"videos", videoCount)
}

// transferAllPendingResources 转存所有待转存的资源（全量扫描）
func (s *ResourceTransferScheduler) transferAllPendingResources() {
	s.log.Info("Starting full scan for all pending resources...")

	// 查找所有待转存的资源
	type DramaCount struct {
		DramaID string
		Count   int64
	}

	// 统计所有剧本的待转存图片
	var imageDramas []DramaCount
	s.db.Raw(`
		SELECT drama_id, COUNT(*) as count 
		FROM image_generations 
		WHERE status = 'completed' 
		AND image_url IS NOT NULL 
		AND image_url != ''
		AND (minio_url IS NULL OR minio_url = '')
		GROUP BY drama_id
	`).Scan(&imageDramas)

	s.log.Infow("Found dramas with pending images", "count", len(imageDramas))

	// 转存所有待转存图片
	totalImageCount := 0
	for _, drama := range imageDramas {
		count, err := s.transferService.BatchTransferImagesToMinio(drama.DramaID, 0) // 0表示全部转存
		if err != nil {
			s.log.Errorw("Failed to transfer images for drama",
				"drama_id", drama.DramaID,
				"error", err)
			continue
		}
		totalImageCount += count
		s.log.Infow("Transferred all images for drama",
			"drama_id", drama.DramaID,
			"count", count)
	}

	// 统计所有剧本的待转存视频
	var videoDramas []DramaCount
	s.db.Raw(`
		SELECT drama_id, COUNT(*) as count 
		FROM video_generations 
		WHERE status = 'completed' 
		AND video_url IS NOT NULL 
		AND video_url != ''
		AND (minio_url IS NULL OR minio_url = '')
		GROUP BY drama_id
	`).Scan(&videoDramas)

	s.log.Infow("Found dramas with pending videos", "count", len(videoDramas))

	// 转存所有待转存视频
	totalVideoCount := 0
	for _, drama := range videoDramas {
		count, err := s.transferService.BatchTransferVideosToMinio(drama.DramaID, 0) // 0表示全部转存
		if err != nil {
			s.log.Errorw("Failed to transfer videos for drama",
				"drama_id", drama.DramaID,
				"error", err)
			continue
		}
		totalVideoCount += count
		s.log.Infow("Transferred all videos for drama",
			"drama_id", drama.DramaID,
			"count", count)
	}

	s.log.Infow("Full resource scan and transfer completed",
		"total_images", totalImageCount,
		"total_videos", totalVideoCount,
		"drama_count", len(imageDramas)+len(videoDramas))
}

// RunNow 立即执行一次转存任务（用于手动触发）
func (s *ResourceTransferScheduler) RunNow() {
	s.log.Info("Manually triggering resource transfer task...")
	go s.transferPendingResources()
}

// RunFullScan 立即执行一次全量扫描（用于手动触发）
func (s *ResourceTransferScheduler) RunFullScan() {
	s.log.Info("Manually triggering full resource scan...")
	go s.transferAllPendingResources()
}
