package ai

// AIClient 定义文本生成客户端接口
type AIClient interface {
	GenerateText(prompt string, systemPrompt string, options ...func(*ChatCompletionRequest)) (string, error)
	TestConnection() error
}
