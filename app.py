import streamlit as st
import pandas as pd
import re
from io import BytesIO
from decimal import Decimal, InvalidOperation

st.set_page_config(page_title="MAWB筛选工具", layout="wide")

st.title("📦 MAWB 筛选工具（增强版）")

# =============================
# 核心：标准化 MAWB
# =============================
def normalize_mawb(value):
    if pd.isna(value):
        return ""

    value = str(value)

    # 去除各种空格
    value = value.replace("\xa0", "")   # NBSP
    value = value.replace("\u3000", "") # 全角空格
    value = value.strip()

    # 处理科学计数法
    if re.fullmatch(r"\d+(\.\d+)?[eE]\+?\d+", value):
        try:
            value = str(int(Decimal(value)))
        except InvalidOperation:
            pass

    # 只保留数字
    value = re.sub(r"\D", "", value)

    return value


# =============================
# 上传文件
# =============================
uploaded_file = st.file_uploader(
    "上传 Excel 或 CSV 文件",
    type=["xlsx", "xls", "csv"]
)

# =============================
# 输入 MAWB
# =============================
mawb_input = st.text_area(
    "输入需要筛选的 MAWB（每行一个）",
    placeholder="例如：\n016-56698655\n01656698655\n016 56698655"
)

# =============================
# 主逻辑
# =============================
if uploaded_file is not None:

    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file, dtype=str)
        else:
            df = pd.read_excel(uploaded_file, dtype=str)

    except Exception as e:
        st.error(f"文件读取失败: {e}")
        st.stop()

    st.subheader("📄 原始数据预览")
    st.dataframe(df.head())

    # =============================
    # 检查列
    # =============================
    if "MAWB" not in df.columns:
        st.error("❌ 文件中没有找到 'MAWB' 列")
        st.stop()

    # =============================
    # 开始处理
    # =============================
    if mawb_input.strip():

        # 输入处理
        input_list = mawb_input.splitlines()

        normalized_input = {
            normalize_mawb(x)
            for x in input_list
            if normalize_mawb(x)
        }

        # 数据处理
        df["_MAWB_NORMALIZED"] = df["MAWB"].apply(normalize_mawb)

        # =============================
        # 筛选
        # =============================
        result = df[df["_MAWB_NORMALIZED"].isin(normalized_input)].copy()

        # =============================
        # 找出没匹配到的
        # =============================
        found_set = set(result["_MAWB_NORMALIZED"])
        not_found = normalized_input - found_set

        result = result.drop(columns=["_MAWB_NORMALIZED"])

        # =============================
        # 展示结果
        # =============================
        st.subheader("✅ 筛选结果")
        st.write(f"匹配到 {len(result)} 行")
        st.dataframe(result)

        # =============================
        # 未匹配提示（重点）
        # =============================
        if not_found:
            st.warning("⚠️ 以下 MAWB 没有匹配到：")
            st.write(list(not_found))

            st.info("可能原因：\n"
                    "- Excel 已经变成科学计数法（数据丢失）\n"
                    "- 原始数据里不存在\n"
                    "- 输入错误\n")

        else:
            st.success("🎉 所有 MAWB 都匹配成功！")

        # =============================
        # 下载
        # =============================
        output = BytesIO()
        result.to_excel(output, index=False)
        output.seek(0)

        st.download_button(
            label="📥 下载筛选结果",
            data=output,
            file_name="filtered_mawb.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    else:
        st.info("请输入需要筛选的 MAWB")
