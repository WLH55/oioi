package image

type ImageClient interface {
	GenerateImage(prompt string, opts ...ImageOption) (*ImageResult, error)
	GetTaskStatus(taskID string) (*ImageResult, error)
}

type ImageResult struct {
	TaskID    string
	Status    string
	ImageURL  string
	Width     int
	Height    int
	Error     string
	Completed bool
}

type ImageOptions struct {
	NegativePrompt  string
	Size            string
	Quality         string
	Style           string
	Steps           int
	CfgScale        float64
	Seed            int64
	Model           string
	Width           int
	Height          int
	ReferenceImages []string // 参考图片URL列表
}

type ImageOption func(*ImageOptions)

func WithNegativePrompt(prompt string) ImageOption {
	return func(o *ImageOptions) {
		o.NegativePrompt = prompt
	}
}

func WithSize(size string) ImageOption {
	return func(o *ImageOptions) {
		o.Size = size
	}
}

func WithQuality(quality string) ImageOption {
	return func(o *ImageOptions) {
		o.Quality = quality
	}
}

func WithStyle(style string) ImageOption {
	return func(o *ImageOptions) {
		o.Style = style
	}
}

func WithSteps(steps int) ImageOption {
	return func(o *ImageOptions) {
		o.Steps = steps
	}
}

func WithCfgScale(scale float64) ImageOption {
	return func(o *ImageOptions) {
		o.CfgScale = scale
	}
}

func WithSeed(seed int64) ImageOption {
	return func(o *ImageOptions) {
		o.Seed = seed
	}
}

func WithModel(model string) ImageOption {
	return func(o *ImageOptions) {
		o.Model = model
	}
}

func WithDimensions(width, height int) ImageOption {
	return func(o *ImageOptions) {
		o.Width = width
		o.Height = height
	}
}

func WithReferenceImages(images []string) ImageOption {
	return func(o *ImageOptions) {
		o.ReferenceImages = images
	}
}
