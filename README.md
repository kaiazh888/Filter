# MAWB Filter App

一个基于 Streamlit 的工具，用于根据 MAWB 列筛选数据。

## 功能

- 上传 Excel 或 CSV 文件
- 根据 MAWB 列筛选数据
- 自动识别不同格式：
  - 016-56698655
  - 01656698655
  - 016 56698655
- 支持多个 MAWB 批量筛选
- 下载筛选结果

## 使用方法

### 本地运行

```bash
pip install -r requirements.txt
streamlit run app.py
