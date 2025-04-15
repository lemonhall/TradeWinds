# tradewinds

一个简单的港口城市贸易模拟器。

## 描述

该项目模拟了一个包含多个城市和贸易船只的经济系统。每个城市都有自己的商品生产、消费和价格波动机制。船只可以在城市之间航行，根据简单的策略（低买高卖）进行贸易以赚取利润。

模拟结束后，可以绘制特定城市商品价格随时间变化的图表，以及特定船只财富变化的图表。

## 特性

*   **城市经济模拟**: 基于供需关系动态调整商品价格。
*   **船只贸易**: 船只自主进行航行和贸易决策。
*   **数据可视化**: 使用 `matplotlib` 绘制价格和财富历史图表。

## 要求

*   Python >= 3.12
*   `matplotlib`
*   `numpy`

## 安装

1.  **确保 Python 版本**: 请确保您使用的 Python 版本符合要求 (>= 3.12)。如果您使用 `pyenv` 或类似工具，可以根据 `.python-version` 文件设置环境。
2.  **安装依赖**: 推荐使用 `uv` (项目包含 `uv.lock` 文件)。
    ```bash
    uv pip install -r requirements.txt
    ```
    或者，如果您没有 `requirements.txt`，可以直接根据 `pyproject.toml` 安装：
    ```bash
    uv pip install matplotlib numpy
    ```
    如果您使用 `pip`：
    ```bash
    pip install matplotlib numpy
    ```

## 使用

直接运行主脚本即可启动模拟：

```bash
python main.py
```

模拟将运行预设的天数，并在结束后显示示例城市（例如 "Lisbon"）的价格图和示例船只（例如 "The Serpent"）的财富图。您可以修改 `main.py` 文件末尾的 `if __name__ == "__main__":` 部分来自定义模拟参数、城市、船只和绘图选项。

## 贡献

欢迎提出改进建议或贡献代码。

## 许可证

该项目目前未指定许可证。
