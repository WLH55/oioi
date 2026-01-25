package ai

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)

type OpenAIClient struct {
	BaseURL    string
	APIKey     string
	Model      string
	Endpoint   string
	HTTPClient *http.Client
}

type ChatMessage struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatCompletionRequest struct {
	Model               string        `json:"model"`
	Messages            []ChatMessage `json:"messages"`
	Temperature         float64       `json:"temperature,omitempty"`
	MaxTokens           *int          `json:"max_tokens,omitempty"`
	MaxCompletionTokens *int          `json:"max_completion_tokens,omitempty"`
	TopP                float64       `json:"top_p,omitempty"`
	Stream              bool          `json:"stream,omitempty"`
}

type ChatCompletionResponse struct {
	ID      string `json:"id"`
	Object  string `json:"object"`
	Created int64  `json:"created"`
	Model   string `json:"model"`
	Choices []struct {
		Index   int `json:"index"`
		Message struct {
			Role    string `json:"role"`
			Content string `json:"content"`
		} `json:"message"`
		FinishReason string `json:"finish_reason"`
	} `json:"choices"`
	Usage struct {
		PromptTokens     int `json:"prompt_tokens"`
		CompletionTokens int `json:"completion_tokens"`
		TotalTokens      int `json:"total_tokens"`
	} `json:"usage"`
}

type ErrorResponse struct {
	Error struct {
		Message string `json:"message"`
		Type    string `json:"type"`
		Code    string `json:"code"`
	} `json:"error"`
}

func NewOpenAIClient(baseURL, apiKey, model, endpoint string) *OpenAIClient {
	if endpoint == "" {
		endpoint = "/v1/chat/completions"
	}

	return &OpenAIClient{
		BaseURL:  baseURL,
		APIKey:   apiKey,
		Model:    model,
		Endpoint: endpoint,
		HTTPClient: &http.Client{
			Timeout: 10 * time.Minute,
		},
	}
}

func (c *OpenAIClient) ChatCompletion(messages []ChatMessage, options ...func(*ChatCompletionRequest)) (*ChatCompletionResponse, error) {
	req := &ChatCompletionRequest{
		Model:    c.Model,
		Messages: messages,
	}

	for _, option := range options {
		option(req)
	}

	return c.sendChatRequest(req)
}

func (c *OpenAIClient) sendChatRequest(req *ChatCompletionRequest) (*ChatCompletionResponse, error) {
	resp, err := c.doChatRequest(req)
	if err == nil {
		return resp, nil
	}

	if shouldRetryWithMaxCompletionTokens(err, req) {
		tokens := *req.MaxTokens
		retryReq := *req
		retryReq.MaxTokens = nil
		retryReq.MaxCompletionTokens = &tokens
		fmt.Printf("OpenAI: retrying with max_completion_tokens=%d\n", tokens)
		return c.doChatRequest(&retryReq)
	}

	return nil, err
}

func (c *OpenAIClient) doChatRequest(req *ChatCompletionRequest) (*ChatCompletionResponse, error) {
	jsonData, err := json.Marshal(req)
	if err != nil {
		fmt.Printf("OpenAI: Failed to marshal request: %v\n", err)
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	url := c.BaseURL + c.Endpoint

	// 打印请求信息
	fmt.Printf("OpenAI: Sending request to: %s\n", url)
	fmt.Printf("OpenAI: BaseURL=%s, Endpoint=%s, Model=%s\n", c.BaseURL, c.Endpoint, c.Model)
	requestPreview := string(jsonData)
	if len(jsonData) > 300 {
		requestPreview = string(jsonData[:300]) + "..."
	}
	fmt.Printf("OpenAI: Request body: %s\n", requestPreview)

	httpReq, err := http.NewRequest("POST", url, bytes.NewBuffer(jsonData))
	if err != nil {
		fmt.Printf("OpenAI: Failed to create request: %v\n", err)
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	httpReq.Header.Set("Content-Type", "application/json")
	httpReq.Header.Set("Authorization", "Bearer "+c.APIKey)

	fmt.Printf("OpenAI: Executing HTTP request...\n")
	resp, err := c.HTTPClient.Do(httpReq)
	if err != nil {
		fmt.Printf("OpenAI: HTTP request failed: %v\n", err)
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	fmt.Printf("OpenAI: Received response with status: %d\n", resp.StatusCode)

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		fmt.Printf("OpenAI: Failed to read response body: %v\n", err)
		return nil, fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		fmt.Printf("OpenAI: API error (status %d): %s\n", resp.StatusCode, string(body))
		var errResp ErrorResponse
		if err := json.Unmarshal(body, &errResp); err != nil {
			return nil, fmt.Errorf("API error (status %d): %s", resp.StatusCode, string(body))
		}
		return nil, fmt.Errorf("API error: %s", errResp.Error.Message)
	}

	// 打印响应体用于调试
	bodyPreview := string(body)
	if len(body) > 500 {
		bodyPreview = string(body[:500]) + "..."
	}
	fmt.Printf("OpenAI: Response body: %s\n", bodyPreview)

	var chatResp ChatCompletionResponse
	if err := json.Unmarshal(body, &chatResp); err != nil {
		errorPreview := string(body)
		if len(body) > 200 {
			errorPreview = string(body[:200])
		}
		fmt.Printf("OpenAI: Failed to parse response: %v\n", err)
		return nil, fmt.Errorf("failed to unmarshal response: %w, body preview: %s", err, errorPreview)
	}

	fmt.Printf("OpenAI: Successfully parsed response, choices count: %d\n", len(chatResp.Choices))

	if len(chatResp.Choices) == 0 {
		fmt.Printf("OpenAI: No choices in response\n")
		return nil, fmt.Errorf("no choices in response")
	}

	// 检查 finish_reason，处理内容过滤的情况
	if len(chatResp.Choices) > 0 {
		finishReason := chatResp.Choices[0].FinishReason
		content := chatResp.Choices[0].Message.Content
		usage := chatResp.Usage

		fmt.Printf("OpenAI: finish_reason=%s, content_length=%d\n", finishReason, len(content))

		if finishReason == "content_filter" {
			return nil, fmt.Errorf("AI内容被安全过滤器拦截，可能因为：\n1. 请求内容触发了安全策略\n2. 生成的内容包含敏感信息\n3. 建议：调整输入内容或联系API提供商调整过滤策略")
		}

		if usage.TotalTokens == 0 && finishReason != "stop" {
			return nil, fmt.Errorf("AI返回内容为空 (finish_reason: %s)，可能的原因：\n1. 内容被过滤\n2. Token限制\n3. API异常", finishReason)
		}
	}

	return &chatResp, nil
}

func WithTemperature(temp float64) func(*ChatCompletionRequest) {
	return func(req *ChatCompletionRequest) {
		req.Temperature = temp
	}
}

func WithMaxTokens(tokens int) func(*ChatCompletionRequest) {
	return func(req *ChatCompletionRequest) {
		req.MaxTokens = &tokens
	}
}

func WithTopP(topP float64) func(*ChatCompletionRequest) {
	return func(req *ChatCompletionRequest) {
		req.TopP = topP
	}
}

func (c *OpenAIClient) GenerateText(prompt string, systemPrompt string, options ...func(*ChatCompletionRequest)) (string, error) {
	messages := []ChatMessage{}

	if systemPrompt != "" {
		messages = append(messages, ChatMessage{
			Role:    "system",
			Content: systemPrompt,
		})
	}

	messages = append(messages, ChatMessage{
		Role:    "user",
		Content: prompt,
	})

	resp, err := c.ChatCompletion(messages, options...)
	if err != nil {
		return "", err
	}

	if len(resp.Choices) == 0 {
		return "", fmt.Errorf("no response from API")
	}

	return resp.Choices[0].Message.Content, nil
}

func (c *OpenAIClient) TestConnection() error {
	fmt.Printf("OpenAI: TestConnection called with BaseURL=%s, Endpoint=%s, Model=%s\n", c.BaseURL, c.Endpoint, c.Model)

	messages := []ChatMessage{
		{
			Role:    "user",
			Content: "Hello",
		},
	}

	_, err := c.ChatCompletion(messages, WithMaxTokens(50))
	if err != nil {
		fmt.Printf("OpenAI: TestConnection failed: %v\n", err)
	} else {
		fmt.Printf("OpenAI: TestConnection succeeded\n")
	}
	return err
}

func shouldRetryWithMaxCompletionTokens(err error, req *ChatCompletionRequest) bool {
	if err == nil || req == nil || req.MaxTokens == nil || req.MaxCompletionTokens != nil {
		return false
	}

	msg := err.Error()
	if strings.Contains(msg, "Unsupported parameter: 'max_tokens'") {
		return true
	}
	if strings.Contains(msg, "max_tokens is not supported") {
		return true
	}
	if strings.Contains(msg, "max_completion_tokens") {
		return true
	}
	return false
}
