package database

import (
	"context"
	"strings"
	"time"

	"gorm.io/gorm/logger"
)

// CustomLogger 自定义 GORM logger，截断过长的 SQL 参数（如 base64 数据）
type CustomLogger struct {
	logger.Interface
}

// NewCustomLogger 创建自定义 logger
func NewCustomLogger() logger.Interface {
	return &CustomLogger{
		Interface: logger.Default.LogMode(logger.Silent),
	}
}

// Trace 重写 Trace 方法，禁用 SQL 日志输出
func (l *CustomLogger) Trace(ctx context.Context, begin time.Time, fc func() (sql string, rowsAffected int64), err error) {
	// 不输出任何 SQL 日志
	// 如果需要调试，可以临时取消注释下面的代码
	/*
		sql, rows := fc()
		sql = truncateLongValues(sql)
		elapsed := time.Since(begin)
		if err != nil {
			l.Interface.Error(ctx, "SQL error: %v [%v] %s", err, elapsed, sql)
		} else {
			l.Interface.Info(ctx, "[%.3fms] [rows:%d] %s", float64(elapsed.Nanoseconds())/1e6, rows, sql)
		}
	*/
}

// truncateLongValues 截断 SQL 中的长字符串值
func truncateLongValues(sql string) string {
	// 查找 base64 格式的数据 (data:image/...;base64,...)
	if strings.Contains(sql, "data:image/") && strings.Contains(sql, ";base64,") {
		parts := strings.Split(sql, "\"")
		for i, part := range parts {
			if strings.HasPrefix(part, "data:image/") && strings.Contains(part, ";base64,") {
				if len(part) > 100 {
					// 保留前50字符，添加截断标记
					parts[i] = part[:50] + "...[base64 data truncated]"
				}
			}
		}
		sql = strings.Join(parts, "\"")
	}

	// 截断其他过长的值
	if len(sql) > 5000 {
		// 查找 VALUES 或 SET 后的内容
		if idx := strings.Index(sql, " VALUES "); idx > 0 && len(sql) > idx+5000 {
			sql = sql[:idx+5000] + "...[truncated]"
		} else if idx := strings.Index(sql, " SET "); idx > 0 && len(sql) > idx+3000 {
			sql = sql[:idx+3000] + "...[truncated]"
		} else if len(sql) > 5000 {
			sql = sql[:5000] + "...[truncated]"
		}
	}

	return sql
}

// Info 实现 Info 方法
func (l *CustomLogger) Info(ctx context.Context, msg string, data ...interface{}) {
	l.Interface.Info(ctx, msg, data...)
}

// Warn 实现 Warn 方法
func (l *CustomLogger) Warn(ctx context.Context, msg string, data ...interface{}) {
	l.Interface.Warn(ctx, msg, data...)
}

// Error 实现 Error 方法
func (l *CustomLogger) Error(ctx context.Context, msg string, data ...interface{}) {
	// 检查并截断 data 中的长字符串
	truncatedData := make([]interface{}, len(data))
	for i, d := range data {
		if str, ok := d.(string); ok && len(str) > 200 {
			if strings.HasPrefix(str, "data:image/") {
				truncatedData[i] = str[:50] + "...[base64 data]"
			} else {
				truncatedData[i] = str[:200] + "..."
			}
		} else {
			truncatedData[i] = d
		}
	}
	l.Interface.Error(ctx, msg, truncatedData...)
}

// LogMode 实现 LogMode 方法
func (l *CustomLogger) LogMode(level logger.LogLevel) logger.Interface {
	newLogger := *l
	newLogger.Interface = l.Interface.LogMode(level)
	return &newLogger
}
