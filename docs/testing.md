# 测试指南

本文档提供了关于如何运行和扩展py-eacopy项目测试的详细信息。

## 测试框架

py-eacopy使用以下工具进行测试：

- **pytest**: 用于运行单元测试
- **pytest-cov**: 用于生成测试覆盖率报告
- **nox**: 用于自动化测试和构建流程

## 运行测试

### 使用便捷脚本

项目提供了便捷脚本来运行测试：

#### Windows

```bash
run_tests.bat [--build] [--no-tests]
```

#### Linux/macOS

```bash
./run_tests.sh [--build] [--no-tests]
```

选项：
- `--build`: 在运行测试前构建项目
- `--no-tests`: 仅构建项目，不运行测试

### 使用nox命令

项目提供了多种nox命令来运行测试：

#### 1. 基本测试

```bash
nox -s pytest
```

这个命令会运行所有测试，但不会生成覆盖率报告。

#### 2. 覆盖率测试

```bash
nox -s coverage
```

这个命令会运行所有测试并生成覆盖率报告。报告将以HTML格式保存在`htmlcov`目录中。

#### 3. 构建并测试

```bash
nox -s build-test
```

这个命令会构建项目并运行测试，但不会生成覆盖率报告。

#### 4. 构建、安装并测试覆盖率（推荐）

```bash
nox -s build-test-coverage
```

这个命令会执行以下步骤：

1. 构建项目并创建wheel文件
2. 安装生成的wheel文件
3. 运行测试并生成覆盖率报告

这是最全面的测试命令，推荐用于验证项目的完整性。

### 直接使用pytest

如果你已经安装了项目，也可以直接使用pytest运行测试：

```bash
pytest tests/
```

要生成覆盖率报告，可以使用：

```bash
pytest tests/ --cov=py_eacopy --cov-report=html
```

## 测试文件结构

测试文件组织如下：

- **test_basic.py**: 基本文件复制功能测试
- **test_async.py**: 异步复制功能测试
- **test_config.py**: 配置选项测试
- **test_cli.py**: 命令行界面测试
- **test_version.py**: 版本信息测试
- **test_error_handling.py**: 错误处理和恢复策略测试
- **test_callbacks.py**: 进度回调功能测试
- **test_unicode.py**: Unicode/非ASCII路径处理测试
- **test_performance.py**: 性能测试

## 编写新测试

编写新测试时，请遵循以下准则：

1. 使用pytest的fixture机制管理测试依赖和资源
2. 使用参数化测试(parametrize)减少重复代码
3. 使用pytest的mark装饰器对测试进行分类
4. 使用pytest的断言机制获得更详细的失败信息

示例：

```python
import pytest
import os
import py_eacopy

@pytest.mark.parametrize("thread_count", [1, 4, 8])
def test_thread_count(test_file, dest_dir, thread_count):
    """Test thread_count configuration with different values."""
    # Set thread count
    py_eacopy.config.thread_count = thread_count

    # Copy the file
    py_eacopy.copy(test_file, dest_dir)

    # Check if the file was copied
    dest_file = os.path.join(dest_dir, "test.txt")
    assert os.path.exists(dest_file)
```

## 测试覆盖率

测试覆盖率报告会显示代码的哪些部分被测试覆盖，哪些部分没有被覆盖。

要查看覆盖率报告，请在运行`nox -s coverage`或`nox -s build-test-coverage`后，打开`htmlcov/index.html`文件。

### 提高测试覆盖率

要提高测试覆盖率，请关注覆盖率报告中标记为未覆盖的代码行，并为这些代码添加测试。

常见的未覆盖区域包括：

- 错误处理代码
- 边缘情况
- 配置选项
- 回调函数

## 持续集成

项目使用GitHub Actions进行持续集成。每次提交或创建Pull Request时，都会自动运行测试。

CI配置文件位于`.github/workflows/`目录中。

## 故障排除

如果测试失败，请检查以下几点：

1. 确保已安装所有依赖项
2. 检查测试环境（操作系统、Python版本等）
3. 查看测试日志以获取详细错误信息
4. 在本地重现失败的测试

如果遇到与Windows特定功能相关的测试失败，请确保在Windows环境中运行测试。
