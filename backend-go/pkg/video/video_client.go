package video

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

type VideoClient interface {
	GenerateVideo(imageURL, prompt string, opts ...VideoOption) (*VideoResult, error)
	GetTaskStatus(taskID string) (*VideoResult, error)
}

type VideoResult struct {
	TaskID       string
	Status       string
	VideoURL     string
	ThumbnailURL string
	Duration     int
	Width        int
	Height       int
	Error        string
	Completed    bool
}

type VideoOptions struct {
	Model              string
	Duration           int
	FPS                int
	Resolution         string
	AspectRatio        string
	Style              string
	MotionLevel        int
	CameraMotion       string
	Seed               int64
	FirstFrameURL      string
	LastFrameURL       string
	ReferenceImageURLs []string
}

type VideoOption func(*VideoOptions)

func WithModel(model string) VideoOption {
	return func(o *VideoOptions) {
		o.Model = model
	}
}

func WithDuration(duration int) VideoOption {
	return func(o *VideoOptions) {
		o.Duration = duration
	}
}

func WithFPS(fps int) VideoOption {
	return func(o *VideoOptions) {
		o.FPS = fps
	}
}

func WithResolution(resolution string) VideoOption {
	return func(o *VideoOptions) {
		o.Resolution = resolution
	}
}

func WithAspectRatio(ratio string) VideoOption {
	return func(o *VideoOptions) {
		o.AspectRatio = ratio
	}
}

func WithStyle(style string) VideoOption {
	return func(o *VideoOptions) {
		o.Style = style
	}
}

func WithMotionLevel(level int) VideoOption {
	return func(o *VideoOptions) {
		o.MotionLevel = level
	}
}

func WithCameraMotion(motion string) VideoOption {
	return func(o *VideoOptions) {
		o.CameraMotion = motion
	}
}

func WithSeed(seed int64) VideoOption {
	return func(o *VideoOptions) {
		o.Seed = seed
	}
}

func WithFirstFrame(url string) VideoOption {
	return func(o *VideoOptions) {
		o.FirstFrameURL = url
	}
}

func WithLastFrame(url string) VideoOption {
	return func(o *VideoOptions) {
		o.LastFrameURL = url
	}
}

func WithReferenceImages(urls []string) VideoOption {
	return func(o *VideoOptions) {
		o.ReferenceImageURLs = urls
	}
}

type RunwayClient struct {
	BaseURL    string
	APIKey     string
	Model      string
	HTTPClient *http.Client
}

type RunwayRequest struct {
	Model       string `json:"model"`
	PromptImage string `json:"prompt_image"`
	PromptText  string `json:"prompt_text"`
	Duration    int    `json:"duration,omitempty"`
	AspectRatio string `json:"aspect_ratio,omitempty"`
	Seed        int64  `json:"seed,omitempty"`
}

type RunwayResponse struct {
	ID     string `json:"id"`
	Status string `json:"status"`
	Output struct {
		URL string `json:"url"`
	} `json:"output"`
	Error string `json:"error,omitempty"`
}

func NewRunwayClient(baseURL, apiKey, model string) *RunwayClient {
	return &RunwayClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
		Model:   model,
		HTTPClient: &http.Client{
			Timeout: 180 * time.Second,
		},
	}
}

func (c *RunwayClient) GenerateVideo(imageURL, prompt string, opts ...VideoOption) (*VideoResult, error) {
	options := &VideoOptions{
		Duration:    5,
		AspectRatio: "16:9",
	}

	for _, opt := range opts {
		opt(options)
	}

	model := c.Model
	if options.Model != "" {
		model = options.Model
	}

	reqBody := RunwayRequest{
		Model:       model,
		PromptImage: imageURL,
		PromptText:  prompt,
		Duration:    options.Duration,
		AspectRatio: options.AspectRatio,
		Seed:        options.Seed,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	endpoint := c.BaseURL + "/v1/video/generate"
	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return nil, fmt.Errorf("API error (status %d): %s", resp.StatusCode, string(body))
	}

	var result RunwayResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("parse response: %w", err)
	}

	if result.Error != "" {
		return nil, fmt.Errorf("runway error: %s", result.Error)
	}

	videoResult := &VideoResult{
		TaskID:    result.ID,
		Status:    result.Status,
		Completed: result.Status == "succeeded",
	}

	if result.Output.URL != "" {
		videoResult.VideoURL = result.Output.URL
	}

	return videoResult, nil
}

func (c *RunwayClient) GetTaskStatus(taskID string) (*VideoResult, error) {
	endpoint := c.BaseURL + "/v1/video/status/" + taskID
	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	var result RunwayResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("parse response: %w", err)
	}

	videoResult := &VideoResult{
		TaskID:    result.ID,
		Status:    result.Status,
		Completed: result.Status == "succeeded",
	}

	if result.Error != "" {
		videoResult.Error = result.Error
	}

	if result.Output.URL != "" {
		videoResult.VideoURL = result.Output.URL
	}

	return videoResult, nil
}

type PikaClient struct {
	BaseURL    string
	APIKey     string
	Model      string
	HTTPClient *http.Client
}

type PikaRequest struct {
	Model        string `json:"model"`
	Image        string `json:"image"`
	Prompt       string `json:"prompt"`
	Duration     int    `json:"duration,omitempty"`
	AspectRatio  string `json:"aspect_ratio,omitempty"`
	Motion       int    `json:"motion,omitempty"`
	CameraMotion string `json:"camera_motion,omitempty"`
	Seed         int64  `json:"seed,omitempty"`
}

type PikaResponse struct {
	JobID  string `json:"job_id"`
	Status string `json:"status"`
	Result struct {
		VideoURL string `json:"video_url"`
	} `json:"result"`
	Error string `json:"error,omitempty"`
}

func NewPikaClient(baseURL, apiKey, model string) *PikaClient {
	return &PikaClient{
		BaseURL: baseURL,
		APIKey:  apiKey,
		Model:   model,
		HTTPClient: &http.Client{
			Timeout: 180 * time.Second,
		},
	}
}

func (c *PikaClient) GenerateVideo(imageURL, prompt string, opts ...VideoOption) (*VideoResult, error) {
	options := &VideoOptions{
		Duration:    3,
		AspectRatio: "16:9",
		MotionLevel: 50,
	}

	for _, opt := range opts {
		opt(options)
	}

	model := c.Model
	if options.Model != "" {
		model = options.Model
	}

	reqBody := PikaRequest{
		Model:        model,
		Image:        imageURL,
		Prompt:       prompt,
		Duration:     options.Duration,
		AspectRatio:  options.AspectRatio,
		Motion:       options.MotionLevel,
		CameraMotion: options.CameraMotion,
		Seed:         options.Seed,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("marshal request: %w", err)
	}

	endpoint := c.BaseURL + "/v1/video/generate"
	req, err := http.NewRequest("POST", endpoint, bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK && resp.StatusCode != http.StatusCreated {
		return nil, fmt.Errorf("API error (status %d): %s", resp.StatusCode, string(body))
	}

	var result PikaResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("parse response: %w", err)
	}

	if result.Error != "" {
		return nil, fmt.Errorf("pika error: %s", result.Error)
	}

	videoResult := &VideoResult{
		TaskID:    result.JobID,
		Status:    result.Status,
		Completed: result.Status == "completed",
	}

	if result.Result.VideoURL != "" {
		videoResult.VideoURL = result.Result.VideoURL
	}

	return videoResult, nil
}

func (c *PikaClient) GetTaskStatus(taskID string) (*VideoResult, error) {
	endpoint := c.BaseURL + "/v1/video/status/" + taskID
	req, err := http.NewRequest("GET", endpoint, nil)
	if err != nil {
		return nil, fmt.Errorf("create request: %w", err)
	}

	req.Header.Set("Authorization", "Bearer "+c.APIKey)

	resp, err := c.HTTPClient.Do(req)
	if err != nil {
		return nil, fmt.Errorf("send request: %w", err)
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, fmt.Errorf("read response: %w", err)
	}

	var result PikaResponse
	if err := json.Unmarshal(body, &result); err != nil {
		return nil, fmt.Errorf("parse response: %w", err)
	}

	videoResult := &VideoResult{
		TaskID:    result.JobID,
		Status:    result.Status,
		Completed: result.Status == "completed",
	}

	if result.Error != "" {
		videoResult.Error = result.Error
	}

	if result.Result.VideoURL != "" {
		videoResult.VideoURL = result.Result.VideoURL
	}

	return videoResult, nil
}
