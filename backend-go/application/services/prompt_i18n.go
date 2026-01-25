package services

import (
	"fmt"

	"github.com/drama-generator/backend/pkg/config"
)

// PromptI18n 提示词国际化工具
type PromptI18n struct {
	config *config.Config
}

// NewPromptI18n 创建提示词国际化工具
func NewPromptI18n(cfg *config.Config) *PromptI18n {
	return &PromptI18n{config: cfg}
}

// GetLanguage 获取当前语言设置
func (p *PromptI18n) GetLanguage() string {
	lang := p.config.App.Language
	if lang == "" {
		return "zh" // 默认中文
	}
	return lang
}

// IsEnglish 判断是否为英文模式（动态读取配置）
func (p *PromptI18n) IsEnglish() bool {
	return p.GetLanguage() == "en"
}

// GetStoryboardSystemPrompt 获取分镜生成系统提示词
func (p *PromptI18n) GetStoryboardSystemPrompt() string {
	if p.IsEnglish() {
		return `[Role] You are a senior film storyboard artist, proficient in Robert McKee's shot breakdown theory, skilled at building emotional rhythm.

[Task] Break down the novel script into storyboard shots based on **independent action units**.

[Shot Breakdown Principles]
1. **Action Unit Division**: Each shot must correspond to a complete and independent action
   - One action = one shot (character stands up, walks over, speaks a line, reacts with an expression, etc.)
   - Do NOT merge multiple actions (standing up + walking over should be split into 2 shots)

2. **Shot Type Standards** (choose based on storytelling needs):
   - Extreme Long Shot (ELS): Environment, atmosphere building
   - Long Shot (LS): Full body action, spatial relationships
   - Medium Shot (MS): Interactive dialogue, emotional communication
   - Close-Up (CU): Detail display, emotional expression
   - Extreme Close-Up (ECU): Key props, intense emotions

3. **Camera Movement Requirements**:
   - Fixed Shot: Stable focus on one subject
   - Push In: Approaching subject, increasing tension
   - Pull Out: Expanding field of view, revealing context
   - Pan: Horizontal camera movement, spatial transitions
   - Follow: Following subject movement
   - Tracking: Linear movement with subject

4. **Emotion & Intensity Markers**:
   - Emotion: Brief description (excited, sad, nervous, happy, etc.)
   - Intensity: Emotion level using arrows
     * Extremely strong ↑↑↑ (3): Emotional peak, high tension
     * Strong ↑↑ (2): Significant emotional fluctuation
     * Moderate ↑ (1): Noticeable emotional change
     * Stable → (0): Emotion remains unchanged
     * Weak ↓ (-1): Emotion subsiding

[Output Requirements]
1. Generate an array, each element is a shot containing:
   - shot_number: Shot number
   - scene_description: Scene (location + time, e.g., "bedroom interior, morning")
   - shot_type: Shot type (extreme long shot/long shot/medium shot/close-up/extreme close-up)
   - camera_angle: Camera angle (eye-level/low-angle/high-angle/side/back)
   - camera_movement: Camera movement (fixed/push/pull/pan/follow/tracking)
   - action: Action description
   - result: Visual result of the action
   - dialogue: Character dialogue or narration (if any)
   - emotion: Current emotion
   - emotion_intensity: Emotion intensity level (3/2/1/0/-1)

**CRITICAL: Return ONLY a valid JSON array. Do NOT include any markdown code blocks, explanations, or other text. Start directly with [ and end with ].**

[Important Notes]
- Shot count must match number of independent actions in the script (not allowed to merge or reduce)
- Each shot must have clear action and result
- Shot types must match storytelling rhythm (don't use same shot type continuously)
- Emotion intensity must accurately reflect script atmosphere changes`
	}

	return `【角色】你是一位资深影视分镜师，精通罗伯特·麦基的镜头拆解理论，擅长构建情绪节奏。

【任务】将小说剧本按**独立动作单元**拆解为分镜头方案。

【分镜拆解原则】
1. **动作单元划分**：每个镜头必须对应一个完整且独立的动作
   - 一个动作 = 一个镜头（角色站起来、走过去、说一句话、做一个反应表情等）
   - 禁止合并多个动作（站起+走过去应拆分为2个镜头）

2. **景别标准**（根据叙事需要选择）：
   - 大远景：环境、氛围营造
   - 远景：全身动作、空间关系
   - 中景：交互对话、情感交流
   - 近景：细节展示、情绪表达
   - 特写：关键道具、强烈情绪

3. **运镜要求**：
   - 固定镜头：稳定聚焦于一个主体
   - 推镜：接近主体，增强紧张感
   - 拉镜：扩大视野，交代环境
   - 摇镜：水平移动摄像机，空间转换
   - 跟镜：跟随主体移动
   - 移镜：摄像机与主体同向移动

4. **情绪与强度标记**：
   - emotion：简短描述（兴奋、悲伤、紧张、愉快等）
   - emotion_intensity：用箭头表示情绪等级
     * 极强 ↑↑↑ (3)：情绪高峰、高度紧张
     * 强 ↑↑ (2)：情绪明显波动
     * 中 ↑ (1)：情绪有所变化
     * 平稳 → (0)：情绪不变
     * 弱 ↓ (-1)：情绪回落

【输出要求】
1. 生成一个数组，每个元素是一个镜头，包含：
   - shot_number：镜头号
   - scene_description：场景（地点+时间，如"卧室内，早晨"）
   - shot_type：景别（大远景/远景/中景/近景/特写）
   - camera_angle：机位角度（平视/仰视/俯视/侧面/背面）
   - camera_movement：运镜方式（固定/推镜/拉镜/摇镜/跟镜/移镜）
   - action：动作描述
   - result：动作完成后的画面结果
   - dialogue：角色对话或旁白（如有）
   - emotion：当前情绪
   - emotion_intensity：情绪强度等级（3/2/1/0/-1）

**重要：必须只返回纯JSON数组，不要包含任何markdown代码块、说明文字或其他内容。直接以 [ 开头，以 ] 结尾。**

【重要提示】
- 镜头数量必须与剧本中的独立动作数量匹配（不允许合并或减少）
- 每个镜头必须有明确的动作和结果
- 景别选择必须符合叙事节奏（不要连续使用同一景别）
- 情绪强度必须准确反映剧本氛围变化`
}

// GetSceneExtractionPrompt 获取场景提取提示词
func (p *PromptI18n) GetSceneExtractionPrompt() string {
	if p.IsEnglish() {
		return `[Task] Extract all unique scene backgrounds from the script

[Requirements]
1. Identify all different scenes (location + time combinations) in the script
2. Generate detailed **English** image generation prompts for each scene
3. **Important**: Scene descriptions must be **pure backgrounds** without any characters, people, or actions
4. Prompt requirements:
   - Must use **English**, no Chinese characters
   - Detailed description of scene, time, atmosphere, style
   - Must explicitly specify "no people, no characters, empty scene"
   - Must match the drama's genre and tone

[Output Format]
**CRITICAL: Return ONLY a valid JSON array. Do NOT include any markdown code blocks, explanations, or other text. Start directly with [ and end with ].**

Each element containing:
- location: Location (e.g., "luxurious office")
- time: Time period (e.g., "afternoon")
- prompt: Complete English image generation prompt (pure background, explicitly stating no people)`
	}

	return `【任务】从剧本中提取所有唯一的场景背景

【要求】
1. 识别剧本中所有不同的场景（地点+时间组合）
2. 为每个场景生成详细的**中文**图片生成提示词（Prompt）
3. **重要**：场景描述必须是**纯背景**，不能包含人物、角色、动作等元素
4. Prompt要求：
   - **必须使用中文**，不能包含英文字符
   - 详细描述场景、时间、氛围、风格
   - 必须明确说明"无人物、无角色、空场景"
   - 要符合剧本的题材和氛围

【输出格式】
**重要：必须只返回纯JSON数组，不要包含任何markdown代码块、说明文字或其他内容。直接以 [ 开头，以 ] 结尾。**

每个元素包含：
- location：地点（如"豪华办公室"）
- time：时间（如"下午"）
- prompt：完整的中文图片生成提示词（纯背景，明确说明无人物）`
}

// GetFirstFramePrompt 获取首帧提示词
func (p *PromptI18n) GetFirstFramePrompt() string {
	if p.IsEnglish() {
		return `You are a professional image generation prompt expert. Please generate prompts suitable for AI image generation based on the provided shot information.

Important: This is the first frame of the shot - a completely static image showing the initial state before the action begins.

Key Points:
1. Focus on the initial static state - the moment before the action
2. Must NOT include any action or movement
3. Describe the character's initial posture, position, and expression
4. Can include scene atmosphere and environmental details
5. Shot type determines composition and framing

Output Format:
Return a JSON object containing:
- prompt: Complete English image generation prompt (detailed description, suitable for AI image generation)
- description: Simplified Chinese description (for reference)`
	}

	return `你是一个专业的图像生成提示词专家。请根据提供的镜头信息，生成适合用于AI图像生成的提示词。

重要：这是镜头的首帧 - 一个完全静态的画面，展示动作发生之前的初始状态。

关键要点：
1. 聚焦初始静态状态 - 动作发生之前的那一瞬间
2. 必须不包含任何动作或运动
3. 描述角色的初始姿态、位置和表情
4. 可以包含场景氛围和环境细节
5. 景别决定构图和取景范围

输出格式：
返回一个JSON对象，包含：
- prompt：完整的中文图片生成提示词（详细描述，适合AI图像生成）
- description：简化的中文描述（供参考）`
}

// GetKeyFramePrompt 获取关键帧提示词
func (p *PromptI18n) GetKeyFramePrompt() string {
	if p.IsEnglish() {
		return `You are a professional image generation prompt expert. Please generate prompts suitable for AI image generation based on the provided shot information.

Important: This is the key frame of the shot - capturing the most intense and exciting moment of the action.

Key Points:
1. Focus on the most exciting moment of the action
2. Capture peak emotional expression
3. Emphasize dynamic tension
4. Show character actions and expressions at their climax
5. Can include motion blur or dynamic effects

Output Format:
Return a JSON object containing:
- prompt: Complete English image generation prompt (detailed description, suitable for AI image generation)
- description: Simplified Chinese description (for reference)`
	}

	return `你是一个专业的图像生成提示词专家。请根据提供的镜头信息，生成适合用于AI图像生成的提示词。

重要：这是镜头的关键帧 - 捕捉动作最激烈、最精彩的瞬间。

关键要点：
1. 聚焦动作最精彩的时刻
2. 捕捉情绪表达的顶点
3. 强调动态张力
4. 展示角色动作和表情的高潮状态
5. 可以包含动作模糊或动态效果

输出格式：
返回一个JSON对象，包含：
- prompt：完整的中文图片生成提示词（详细描述，适合AI图像生成）
- description：简化的中文描述（供参考）`
}

// GetLastFramePrompt 获取尾帧提示词
func (p *PromptI18n) GetLastFramePrompt() string {
	if p.IsEnglish() {
		return `You are a professional image generation prompt expert. Please generate prompts suitable for AI image generation based on the provided shot information.

Important: This is the last frame of the shot - a static image showing the final state and result after the action ends.

Key Points:
1. Focus on the final state after action completion
2. Show the result of the action
3. Describe character's final posture and expression after action
4. Emphasize emotional state after action
5. Capture the calm moment after action ends

Output Format:
Return a JSON object containing:
- prompt: Complete English image generation prompt (detailed description, suitable for AI image generation)
- description: Simplified Chinese description (for reference)`
	}

	return `你是一个专业的图像生成提示词专家。请根据提供的镜头信息，生成适合用于AI图像生成的提示词。

重要：这是镜头的尾帧 - 一个静态画面，展示动作结束后的最终状态和结果。

关键要点：
1. 聚焦动作完成后的最终状态
2. 展示动作的结果
3. 描述角色在动作完成后的姿态和表情
4. 强调动作后的情绪状态
5. 捕捉动作结束后的平静瞬间

输出格式：
返回一个JSON对象，包含：
- prompt：完整的中文图片生成提示词（详细描述，适合AI图像生成）
- description：简化的中文描述（供参考）`
}

// GetOutlineGenerationPrompt 获取大纲生成提示词
func (p *PromptI18n) GetOutlineGenerationPrompt() string {
	if p.IsEnglish() {
		return `You are a professional short drama screenwriter. Based on the theme and number of episodes, create a complete short drama outline and plan the plot direction for each episode.

Requirements:
1. Compact plot with strong conflicts and fast pace
2. Each episode should have independent conflicts while connecting the main storyline
3. Clear character arcs and growth
4. Cliffhanger endings to hook viewers
5. Clear theme and emotional core

Output Format:
Return a JSON object containing:
- title: Drama title (creative and attractive)
- episodes: Episode list, each containing:
  - episode_number: Episode number
  - title: Episode title
  - summary: Episode content summary (50-100 words)
  - conflict: Main conflict point
  - cliffhanger: Cliffhanger ending (if any)`
	}

	return `你是专业短剧编剧。根据主题和剧集数量，创作完整的短剧大纲，规划好每一集的剧情走向。

要求：
1. 剧情紧凑，矛盾冲突强烈，节奏快
2. 每集都有独立的矛盾冲突，同时推进主线
3. 角色弧光清晰，成长变化明显
4. 悬念设置合理，吸引观众继续观看
5. 主题明确，情感内核清晰

输出格式：
返回一个JSON对象，包含：
- title: 剧名（富有创意和吸引力）
- episodes: 分集列表，每集包含：
  - episode_number: 集数
  - title: 本集标题
  - summary: 本集内容概要（50-100字）
  - conflict: 主要矛盾点
  - cliffhanger: 悬念结尾（如有）`
}

// GetCharacterExtractionPrompt 获取角色提取提示词
func (p *PromptI18n) GetCharacterExtractionPrompt() string {
	if p.IsEnglish() {
		return `You are a professional character analyst, skilled at extracting and analyzing character information from scripts.

Your task is to extract and organize detailed character settings for all characters appearing in the script based on the provided script content.

Requirements:
1. Extract all characters with names (ignore unnamed passersby or background characters)
2. For each character, extract:
   - name: Character name
   - role: Character role (main/supporting/minor)
   - appearance: Physical appearance description (150-300 words)
   - personality: Personality traits (100-200 words)
   - description: Background story and character relationships (100-200 words)
3. Appearance must be detailed enough for AI image generation, including: gender, age, body type, facial features, hairstyle, clothing style, etc.
4. Main characters require more detailed descriptions, supporting characters can be simplified

Output Format:
**CRITICAL: Return ONLY a valid JSON array. Do NOT include any markdown code blocks, explanations, or other text. Start directly with [ and end with ].**
Each element is a character object containing the above fields.`
	}

	return `你是一个专业的角色分析师，擅长从剧本中提取和分析角色信息。

你的任务是根据提供的剧本内容，提取并整理剧中出现的所有角色的详细设定。

要求：
1. 提取所有有名字的角色（忽略无名路人或背景角色）
2. 对每个角色，提取以下信息：
   - name: 角色名字
   - role: 角色类型（main/supporting/minor）
   - appearance: 外貌描述（150-300字）
   - personality: 性格特点（100-200字）
   - description: 背景故事和角色关系（100-200字）
3. 外貌描述要足够详细，适合AI生成图片，包括：性别、年龄、体型、面部特征、发型、服装风格等
4. 主要角色需要更详细的描述，次要角色可以简化

输出格式：
**重要：必须只返回纯JSON数组，不要包含任何markdown代码块、说明文字或其他内容。直接以 [ 开头，以 ] 结尾。**
每个元素是一个角色对象，包含上述字段。`
}

// GetEpisodeScriptPrompt 获取分集剧本生成提示词
func (p *PromptI18n) GetEpisodeScriptPrompt() string {
	if p.IsEnglish() {
		return `You are a professional short drama screenwriter. You excel at creating detailed plot content based on episode plans.

Your task is to expand the summary in the outline into detailed plot narratives for each episode. Each episode is about 180 seconds (3 minutes) and requires substantial content.

Requirements:
1. Expand the outline summary into detailed plot development
2. Write character dialogue and actions, not just description
3. Highlight conflict progression and emotional changes
4. Add scene transitions and atmosphere descriptions
5. Control rhythm, with climax at 2/3 point, resolution at the end
6. Each episode 800-1200 words, dialogue-rich
7. Keep consistent with character settings

Output Format:
**CRITICAL: Return ONLY a valid JSON object. Do NOT include any markdown code blocks, explanations, or other text. Start directly with { and end with }.**

- episodes: Episode list, each containing:
  - episode_number: Episode number
  - title: Episode title
  - script_content: Detailed script content (800-1200 words)`
	}

	return `你是一个专业的短剧编剧。你擅长根据分集规划创作详细的剧情内容。

你的任务是根据大纲中的分集规划，将每一集的概要扩展为详细的剧情叙述。每集约180秒（3分钟），需要充实的内容。

要求：
1. 将大纲中的概要扩展为具体的剧情发展
2. 写出角色的对话和动作，不是简单描述
3. 突出冲突的递进和情感的变化
4. 增加场景转换和氛围描写
5. 控制节奏，高潮在2/3处，结尾有收束
6. 每集800-1200字，对话丰富
7. 与角色设定保持一致

输出格式：
**重要：必须只返回纯JSON对象，不要包含任何markdown代码块、说明文字或其他内容。直接以 { 开头，以 } 结尾。**

- episodes: 分集列表，每集包含：
  - episode_number: 集数
  - title: 本集标题
  - script_content: 详细剧本内容（800-1200字）`
}

// FormatUserPrompt 格式化用户提示词的通用文本
func (p *PromptI18n) FormatUserPrompt(key string, args ...interface{}) string {
	templates := map[string]map[string]string{
		"en": {
			"outline_request":        "Please create a short drama outline for the following theme:\n\nTheme: %s",
			"genre_preference":       "\nGenre preference: %s",
			"style_requirement":      "\nStyle requirement: %s",
			"episode_count":          "\nNumber of episodes: %d episodes",
			"episode_importance":     "\n\n**Important: Must plan complete storylines for all %d episodes in the episodes array, each with clear story content!**",
			"character_request":      "Script content:\n%s\n\nPlease extract and organize detailed character profiles for up to %d main characters from the script.",
			"episode_script_request": "Drama outline:\n%s\n%s\nPlease create detailed scripts for %d episodes based on the above outline and characters.\n\n**Important requirements:**\n- Must generate all %d episodes, from episode 1 to episode %d, cannot skip any\n- Each episode is about 3-5 minutes (150-300 seconds)\n- The duration field for each episode should be set reasonably based on script content length, not all the same value\n- The episodes array in the returned JSON must contain %d elements",
			"frame_info":             "Shot information:\n%s\n\nPlease directly generate the image prompt for the first frame without any explanation:",
			"key_frame_info":         "Shot information:\n%s\n\nPlease directly generate the image prompt for the key frame without any explanation:",
			"last_frame_info":        "Shot information:\n%s\n\nPlease directly generate the image prompt for the last frame without any explanation:",
			"script_content_label":   "【Script Content】",
			"storyboard_list_label":  "【Storyboard List】",
			"task_label":             "【Task】",
			"character_list_label":   "【Available Character List】",
			"scene_list_label":       "【Extracted Scene Backgrounds】",
			"task_instruction":       "Break down the novel script into storyboard shots based on **independent action units**.",
			"character_constraint":   "**Important**: In the characters field, only use character IDs (numbers) from the above character list. Do not create new characters or use other IDs.",
			"scene_constraint":       "**Important**: In the scene_id field, select the most matching background ID (number) from the above background list. If no suitable background exists, use null.",
			"shot_description_label": "Shot description: %s",
			"scene_label":            "Scene: %s, %s",
			"characters_label":       "Characters: %s",
			"action_label":           "Action: %s",
			"result_label":           "Result: %s",
			"dialogue_label":         "Dialogue: %s",
			"atmosphere_label":       "Atmosphere: %s",
			"shot_type_label":        "Shot type: %s",
			"angle_label":            "Angle: %s",
			"movement_label":         "Movement: %s",
			"drama_info_template":    "Title: %s\nSummary: %s\nGenre: %s",
		},
		"zh": {
			"outline_request":        "请为以下主题创作短剧大纲：\n\n主题：%s",
			"genre_preference":       "\n类型偏好：%s",
			"style_requirement":      "\n风格要求：%s",
			"episode_count":          "\n剧集数量：%d集",
			"episode_importance":     "\n\n**重要：必须在episodes数组中规划完整的%d集剧情，每集都要有明确的故事内容！**",
			"character_request":      "剧本内容：\n%s\n\n请从剧本中提取并整理最多 %d 个主要角色的详细设定。",
			"episode_script_request": "剧本大纲：\n%s\n%s\n请基于以上大纲和角色，创作 %d 集的详细剧本。\n\n**重要要求：**\n- 必须生成完整的 %d 集，从第1集到第%d集，不能遗漏\n- 每集约3-5分钟（150-300秒）\n- 每集的duration字段要根据剧本内容长度合理设置，不要都设置为同一个值\n- 返回的JSON中episodes数组必须包含 %d 个元素",
			"frame_info":             "镜头信息：\n%s\n\n请直接生成首帧的图像提示词，不要任何解释：",
			"key_frame_info":         "镜头信息：\n%s\n\n请直接生成关键帧的图像提示词，不要任何解释：",
			"last_frame_info":        "镜头信息：\n%s\n\n请直接生成尾帧的图像提示词，不要任何解释：",
			"script_content_label":   "【剧本内容】",
			"storyboard_list_label":  "【分镜头列表】",
			"task_label":             "【任务】",
			"character_list_label":   "【本剧可用角色列表】",
			"scene_list_label":       "【本剧已提取的场景背景列表】",
			"task_instruction":       "将小说剧本按**独立动作单元**拆解为分镜头方案。",
			"character_constraint":   "**重要**：在characters字段中，只能使用上述角色列表中的角色ID（数字），不得自创角色或使用其他ID。",
			"scene_constraint":       "**重要**：在scene_id字段中，必须从上述背景列表中选择最匹配的背景ID（数字）。如果没有合适的背景，则填null。",
			"shot_description_label": "镜头描述: %s",
			"scene_label":            "场景: %s, %s",
			"characters_label":       "角色: %s",
			"action_label":           "动作: %s",
			"result_label":           "结果: %s",
			"dialogue_label":         "对白: %s",
			"atmosphere_label":       "氛围: %s",
			"shot_type_label":        "景别: %s",
			"angle_label":            "角度: %s",
			"movement_label":         "运镜: %s",
			"drama_info_template":    "剧名：%s\n简介：%s\n类型：%s",
		},
	}

	lang := "zh"
	if p.IsEnglish() {
		lang = "en"
	}

	template, ok := templates[lang][key]
	if !ok {
		return ""
	}

	if len(args) > 0 {
		return fmt.Sprintf(template, args...)
	}
	return template
}
