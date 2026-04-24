import streamlit as st
import pandas as pd
import re
from io import BytesIO

st.set_page_config(page_title="MAWB筛选工具", layout="wide")

st.title("MAWB 筛选工具")

def normalize_mawb(value):
    """
    标准化 MAWB：
    - 转成字符串
    - 去掉所有非数字字符
    """
    if pd.isna(value):
        return ""
    value = str(value)
    value = re.sub(r"\D", "", value)
    return value

uploaded_file = st.file_uploader(
    "上传文件",
    type=["xlsx", "xls", "csv"]
)

mawb_input = st.text_area(
    "输入需要保留的 MAWB",
    placeholder="示例：\n016-56698655\n01656698655\n016 56698655"
)

if uploaded_file is not None:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file, dtype=str)
    else:
        df = pd.read_excel(uploaded_file, dtype=str)

    st.subheader("原始数据预览")
    st.dataframe(df.head())

    if "MAWB" not in df.columns:
        st.error("文件中没有找到名为 MAWB 的列")
    else:
        if mawb_input.strip():
            input_mawbs = mawb_input.splitlines()

            normalized_input = {
                normalize_mawb(x)
                for x in input_mawbs
                if normalize_mawb(x)
            }

            df["_MAWB_NORMALIZED"] = df["MAWB"].apply(normalize_mawb)

            result = df[df["_MAWB_NORMALIZED"].isin(normalized_input)].copy()
            result = result.drop(columns=["_MAWB_NORMALIZED"])

            st.subheader("筛选结果")
            st.write(f"共筛选出 {len(result)} 行")
            st.dataframe(result)

            output = BytesIO()
            result.to_excel(output, index=False)
            output.seek(0)

            st.download_button(
                label="下载筛选结果 Excel",
                data=output,
                file_name="filtered_mawb.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.info("请输入需要保留的 MAWB")
