# GitHub Actions 工作流

本项目使用优化的 GitHub Actions 工作流，确保高效的构建、测试和发布流程。

## 目录结构

```
.github/
└── workflows/            # GitHub Actions 工作流
    ├── release.yml       # 发布工作流（标签触发）
    ├── bumpversion.yml   # 版本更新工作流
    ├── codecov.yml       # 代码覆盖率工作流
    ├── docs.yml          # 文档构建工作流
    └── issue-translator.yml # 问题翻译工作流
```

## 工作流说明

### 主工作流 (`release.yml`)

主工作流在代码推送到主分支、创建 Pull Request 或发布新标签时自动运行。它执行以下任务：

- **构建任务**: 在所有支持的平台（Ubuntu、macOS、Windows）和 Python 版本（3.8-3.12）上构建包
- **测试任务**: 在所有支持的平台和 Python 版本上运行测试
- **发布任务**: 在标签推送时发布包到 PyPI

### 版本更新工作流 (`bumpversion.yml`)

当代码推送到主分支时自动运行，执行以下任务：

- 使用 commitizen 自动更新版本号
- 根据提交消息生成 changelog
- 提交版本更新和 changelog 到仓库

### 代码覆盖率工作流 (`codecov.yml`)

在代码推送和 Pull Request 时自动运行，执行以下任务：

- 运行测试并收集代码覆盖率信息
- 将代码覆盖率报告上传到 Codecov

### 文档构建工作流 (`docs.yml`)

在文档或源代码更改时自动运行，执行以下任务：

- 构建项目文档
- 将文档部署到 GitHub Pages

## 优化特点

1. **资源优化**: 代码检查和文档构建任务只在单一环境中执行一次，避免重复执行
2. **Python 版本支持**: 支持 Python 3.8 到 3.12 版本
3. **平台覆盖**: 在 Ubuntu、macOS 和 Windows 上进行测试
4. **自动发布**: 标签推送时自动构建并发布到 PyPI

## 使用方法

- **自动构建和测试**: 创建 Pull Request 或推送到主分支
- **发布新版本**: 创建以数字开头的新标签（如 0.1.0）

## 故障排除

### 404 错误

如果在访问文档时遇到 404 错误：

1. 确保 GitHub Pages 在仓库设置中已启用
2. 检查源是否设置为 `gh-pages` 分支
3. 等待几分钟，让 GitHub Pages 在工作流完成后部署
4. 验证 `gh-pages` 分支是否包含预期内容

### 工作流运行失败

如果工作流运行失败：

1. 检查工作流日志中的错误消息
2. 确保所有依赖项都正确指定
3. 验证仓库设置中是否配置了所需的 secrets
4. 尝试在本地运行失败的步骤进行调试

## 环境变量

- `PERSONAL_ACCESS_TOKEN`: 具有所需权限的 GitHub 令牌，用于版本更新和发布
- `CODECOV_TOKEN`: Codecov 令牌，用于上传代码覆盖率报告
