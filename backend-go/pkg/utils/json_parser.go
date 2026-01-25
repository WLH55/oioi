package utils

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"
)

// SafeParseAIJSON 安全地解析AI返回的JSON，处理常见的格式问题
// 包括：
// 1. 移除Markdown代码块标记
// 2. 提取JSON对象
// 3. 清理多余的空白和换行
// 4. 尝试修复截断的JSON
// 5. 提供详细的错误信息
func SafeParseAIJSON(aiResponse string, v interface{}) error {
	if aiResponse == "" {
		return fmt.Errorf("AI返回内容为空")
	}

	// 1. 移除可能的Markdown代码块标记
	cleaned := strings.TrimSpace(aiResponse)
	// 移除开头的 ```json 或 ```
	cleaned = regexp.MustCompile("(?m)^```json\\s*").ReplaceAllString(cleaned, "")
	cleaned = regexp.MustCompile("(?m)^```\\s*").ReplaceAllString(cleaned, "")
	// 移除结尾的 ```
	cleaned = regexp.MustCompile("(?m)```\\s*$").ReplaceAllString(cleaned, "")
	cleaned = strings.TrimSpace(cleaned)

	// 2. 提取JSON (支持对象 {} 和数组 [])
	var jsonMatch string

	// 优先尝试提取完整的JSON（对象或数组）
	// 先尝试对象格式
	if strings.HasPrefix(cleaned, "{") {
		jsonRegex := regexp.MustCompile(`(?s)\{.*\}`)
		jsonMatch = jsonRegex.FindString(cleaned)
	}

	// 如果没找到对象，尝试数组格式
	if jsonMatch == "" && strings.HasPrefix(cleaned, "[") {
		jsonRegex := regexp.MustCompile(`(?s)\[.*\]`)
		jsonMatch = jsonRegex.FindString(cleaned)
	}

	// 如果还是没找到，尝试从中间提取
	if jsonMatch == "" {
		// 尝试对象
		objRegex := regexp.MustCompile(`(?s)\{.*\}`)
		jsonMatch = objRegex.FindString(cleaned)

		// 如果对象没找到，尝试数组
		if jsonMatch == "" {
			arrRegex := regexp.MustCompile(`(?s)\[.*\]`)
			jsonMatch = arrRegex.FindString(cleaned)
		}
	}

	if jsonMatch == "" {
		return fmt.Errorf("响应中未找到有效的JSON对象或数组，原始响应: %s", truncateString(aiResponse, 200))
	}

	// 3. 尝试解析JSON
	err := json.Unmarshal([]byte(jsonMatch), v)
	if err == nil {
		return nil // 解析成功
	}

	// 4. 如果解析失败，尝试修复截断的JSON
	fixedJSON := attemptJSONRepair(jsonMatch)
	if fixedJSON != jsonMatch {
		if err := json.Unmarshal([]byte(fixedJSON), v); err == nil {
			return nil // 修复后解析成功
		}
	}

	// 5. 检测是否是响应被截断导致的问题
	if isTruncated(jsonMatch) {
		return fmt.Errorf(
			"AI响应可能被截断，导致JSON不完整。\n请尝试：\n1. 增加maxTokens参数\n2. 简化输入内容\n3. 使用更强大的模型\n\n原始错误: %s\n响应长度: %d\n响应末尾: %s",
			err.Error(),
			len(jsonMatch),
			truncateString(jsonMatch[maxInt(0, len(jsonMatch)-200):], 200),
		)
	}

	// 6. 提供详细的错误上下文
	if jsonErr, ok := err.(*json.SyntaxError); ok {
		errorPos := int(jsonErr.Offset)
		start := maxInt(0, errorPos-100)
		end := minInt(len(jsonMatch), errorPos+100)

		context := jsonMatch[start:end]
		marker := strings.Repeat(" ", errorPos-start) + "^"

		return fmt.Errorf(
			"JSON解析失败: %s\n错误位置附近:\n%s\n%s",
			jsonErr.Error(),
			context,
			marker,
		)
	}

	return fmt.Errorf("JSON解析失败: %w\n原始响应: %s", err, truncateString(jsonMatch, 300))
}

// attemptJSONRepair 尝试修复常见的JSON问题
func attemptJSONRepair(jsonStr string) string {
	// 1. 处理未闭合的字符串
	// 如果最后一个字符不是 }，尝试补全
	trimmed := strings.TrimSpace(jsonStr)

	// 2. 检查是否有未闭合的引号
	if strings.Count(trimmed, `"`)%2 != 0 {
		// 有奇数个引号，尝试补全最后一个引号
		trimmed += `"`
	}

	// 3. 统计括号
	openBraces := strings.Count(trimmed, "{")
	closeBraces := strings.Count(trimmed, "}")
	openBrackets := strings.Count(trimmed, "[")
	closeBrackets := strings.Count(trimmed, "]")

	// 4. 补全未闭合的数组
	for i := 0; i < openBrackets-closeBrackets; i++ {
		trimmed += "]"
	}

	// 5. 补全未闭合的对象
	for i := 0; i < openBraces-closeBraces; i++ {
		trimmed += "}"
	}

	return trimmed
}

// ExtractJSONFromText 从文本中提取JSON对象或数组
func ExtractJSONFromText(text string) string {
	text = strings.TrimSpace(text)

	// 移除Markdown代码块
	text = regexp.MustCompile("(?m)^```json\\s*").ReplaceAllString(text, "")
	text = regexp.MustCompile("(?m)^```\\s*").ReplaceAllString(text, "")
	text = strings.TrimSpace(text)

	// 查找JSON对象
	if idx := strings.Index(text, "{"); idx != -1 {
		if lastIdx := strings.LastIndex(text, "}"); lastIdx != -1 && lastIdx > idx {
			return text[idx : lastIdx+1]
		}
	}

	// 查找JSON数组
	if idx := strings.Index(text, "["); idx != -1 {
		if lastIdx := strings.LastIndex(text, "]"); lastIdx != -1 && lastIdx > idx {
			return text[idx : lastIdx+1]
		}
	}

	return text
}

// ValidateJSON 验证JSON字符串是否有效
func ValidateJSON(jsonStr string) error {
	var js json.RawMessage
	return json.Unmarshal([]byte(jsonStr), &js)
}

// isTruncated 检测JSON字符串是否可能被截断
func isTruncated(jsonStr string) bool {
	trimmed := strings.TrimSpace(jsonStr)
	if len(trimmed) == 0 {
		return false
	}

	// 检查是否以不完整的字符串结尾（引号未闭合）
	lastChar := trimmed[len(trimmed)-1]
	if lastChar != '}' && lastChar != ']' {
		return true
	}

	// 检查括号是否匹配
	openBraces := strings.Count(trimmed, "{")
	closeBraces := strings.Count(trimmed, "}")
	openBrackets := strings.Count(trimmed, "[")
	closeBrackets := strings.Count(trimmed, "]")

	if openBraces != closeBraces || openBrackets != closeBrackets {
		return true
	}

	// 检查引号是否匹配（简化检查，不考虑转义）
	quoteCount := strings.Count(trimmed, `"`)
	if quoteCount%2 != 0 {
		return true
	}

	return false
}

// Helper functions
func truncateString(s string, maxLen int) string {
	if len(s) <= maxLen {
		return s
	}
	return s[:maxLen] + "..."
}

func maxInt(a, b int) int {
	if a > b {
		return a
	}
	return b
}

func minInt(a, b int) int {
	if a < b {
		return a
	}
	return b
}
