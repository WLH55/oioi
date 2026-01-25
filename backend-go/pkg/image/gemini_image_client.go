package image

import (
	"bytes"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type GeminiImageClient struct {
	BaseURL    string
	APIKey     string
	Model      string
	Endpoint   string
	HTTPClient *http.Client
}

type GeminiImageRequest struct {
	Contents []struct {
		Parts []GeminiPart `json:"parts"`
	} `json:"contents"`
	GenerationConfig struct {
		ResponseModalities []string `json:"responseModalities"`
	} `json:"generationConfig"`
}

type GeminiPart struct {
	Text       string            `json:"text,omitempty"`
	InlineData *GeminiInlineData `json:"inlineData,omitempty"`
}

type GeminiInlineData struct {
	MimeType string `json:"mimeType"`
	Data     string `json:"data"` // base64 编码的图片数据
}

type GeminiImageResponse struct {
	Candidates []struct {
		Content struct {
			Parts []struct {
				InlineData struct {
					MimeType string `json:"mimeType"`
					Data     string `json:"data"`
				} `json:"inlineData,omitempty"`
				Text string `json:"text,omitempty"`
			} `json:"parts"`
		} `json:"content"`
	} `json:"candidates"`
	UsageMetadata struct {
		PromptTokenCount     int `json:"promptTokenCount"`
		CandidatesTokenCount int `json:"candidatesTokenCount"`
		TotalTokenCount      int `json:"totalTokenCount"`
	} `json:"usageMetadata"`
}

// downloadImageToBase64 下载图片 URL 并转换为 base64
func downloadImageToBase64(imageURL string) (string, string, error) {
	resp, err := http.Get(imageURL)
	if err != nil {
		return "", "", fmt.Errorf("download image: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return "", "", fmt.Errorf("download image failed with status: %d", resp.StatusCode)
	}

	imageData, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", "", fmt.Errorf("read image data: %w", err)
	}

	// 根据 Content-Type 确定 mimeType
	mimeType := resp.Header.Get("Content-Type")
	if mimeType == "" {
		mimeType = "image/jpeg"
	}

	base64Data := base64.StdEncoding.EncodeToString(imageData)
	return base64Data, mimeType, nil
}

func NewGeminiImageClient(baseURL, apiKey, model, endpoint string) *GeminiImageClient {
	if baseURL == "" {
		baseURL = "https://generativelanguage.googleapis.com"
	}
	if endpoint == "" {
		endpoint = "/v1beta/models/{model}:generateContent"
	}
	if model == "" {
		model = "gemini-3-pro-image-preview"
	}
	return &GeminiImageClient{
		BaseURL:  baseURL,
		APIKey:   apiKey,
		Model:    model,
		Endpoint: endpoint,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Minute,
		},
	}
}

func (c *GeminiImageClient) GenerateImage(prompt string, opts ...ImageOption) (*ImageResult, error) {
	options := &ImageOptions{
		Size:    "1920x1920",
		Quality: "standard",
	}

	for _, opt := range opts {
		opt(options)
	}

	model := c.Model
	if options.Model != "" {
		model = options.Model
	}

	promptText := prompt
	if options.NegativePrompt != "" {
		promptText += fmt.Sprintf("\n\nNegative prompt: %s", options.NegativePrompt)
	}
	if options.Size != "" {
		promptText += fmt.Sprintf("\n\nImage size: %s", options.Size)
	}

	// 构建请求的 parts，支持参考图
	parts := []GeminiPart{}

	// 如果有参考图，先添加参考图
	if len(options.ReferenceImages) > 0 {
		for _, refImg := range options.ReferenceImages {
			var base64Data string
			var mimeType string
			var err error

			// 检查是否是 HTTP/HTTPS URL
			if strings.HasPrefix(refImg, "http://") || strings.HasPrefix(refImg, "https://") {
				// 下载图片并转换为 base64
				base64Data, mimeType, err = downloadImageToBase64(refImg)
				if err != nil {
					continue
				}
			} else if strings.HasPrefix(refImg, "data:") {
				// 如果是 data URI 格式，需要解析
				// 格式: data:image/jpeg;base64,xxxxx
				mimeType = "image/jpeg"
				parts := []byte(refImg)
				for i := 0; i < len(parts); i++ {
					if parts[i] == ',' {
						base64Data = refImg[i+1:]
						// 提取 mime type
						if i > 11 {
							mimeTypeEnd := i
							for j := 5; j < i; j++ {
								if parts[j] == ';' {
									mimeTypeEnd = j
									break
								}
							}
							mimeType = refImg[5:mimeTypeEnd]
						}
						break
					}
				}
			} else {
				// 假设已经是 base64 编码
				base64Data = refImg
				mimeType = "image/jpeg"
			}

			if base64Data != "" {
				parts = append(parts, GeminiPart{
					InlineData: &GeminiInlineData{
						MimeType: mimeType,
						Data:     base64Data,
					},
				})
			}
		}
	}

	// 添加文本提示词
	parts = append(parts, GeminiPart{
		Text: promptText,
	})

	reqBody := GeminiImageRequest{
		Contents: []struct {
			Parts []GeminiPart `json:"parts"`
		}{
			{
				Parts: parts,
			},
		},
		GenerationConfig: struct {
			ResponseModalities []string `json:"responseModalities"`
		}{
			ResponseModalities: []string{"IMAGE"},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	endpoint := c.BaseURL + c.Endpoint
	endpoint = replaceModelPlaceholder(endpoint, model)
	url := fmt.Sprintf("%s?key=%s", endpoint, c.APIKey)

	req, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		bodyStr := string(body)
		if len(bodyStr) > 1000 {
			bodyStr = fmt.Sprintf("%s ... %s", bodyStr[:500], bodyStr[len(bodyStr)-500:])
		}
		return nil, fmt.Errorf("API error (status %d): %s", resp.StatusCode, bodyStr)
	}

	var result GeminiImageResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("parse response: %w", err)
	}

	if len(result.Candidates) == 0 || len(result.Candidates[0].Content.Parts) == 0 {
		return nil, fmt.Errorf("no image generated in response")
	}

	base64Data := result.Candidates[0].Content.Parts[0].InlineData.Data
	if base64Data == "" {
		return nil, fmt.Errorf("no base64 image data in response")
	}

	dataURI := fmt.Sprintf("data:image/jpeg;base64,%s", base64Data)

	return &ImageResult{
		Status:    "completed",
		ImageURL:  dataURI,
		Completed: true,
		Width:     1024,
		Height:    1024,
	}, nil
}

func (c *GeminiImageClient) GetTaskStatus(taskID string) (*ImageResult, error) {
	return nil, fmt.Errorf("not supported for Gemini (synchronous generation)")
}

func replaceModelPlaceholder(endpoint, model string) string {
	result := endpoint
	if bytes.Contains([]byte(result), []byte("{model}")) {
		result = string(bytes.ReplaceAll([]byte(result), []byte("{model}"), []byte(model)))
	}
	return result
}
