# streamlit_app.py - PHIÊN BẢN HOÀN HẢO CHO STREAMLIT CLOUD
import streamlit as st
import pandas as pd
from model import analyzer
from datetime import datetime

st.set_page_config(page_title="Phân loại cảm xúc Tiếng Việt", layout="centered")
st.title("Phân Loại Cảm Xúc Tiếng Việt")
st.markdown("**Dùng AI Transformer (PhoBERT) – Chính xác > 92%**")

text = st.text_area("Nhập câu cần phân tích:", height=120, placeholder="Ví dụ: Hôm nay tôi rất vui!")

col1, col2 = st.columns(2)
with col1:
    btn_predict = st.button("Phân tích cảm xúc", type="primary", use_container_width=True)
with col2:
    btn_clear = st.button("Xóa lịch sử", type="secondary", use_container_width=True)

# Khởi tạo lịch sử trong session_state
if "history" not in st.session_state:
    st.session_state.history = []

# Xử lý xóa lịch sử
if btn_clear:
    st.session_state.history = []
    st.success("Đã xóa toàn bộ lịch sử!")
    st.rerun()

# Xử lý phân tích
if btn_predict and text.strip():
    with st.spinner("Đang phân tích cảm xúc…"):
        try:
            result = analyzer.predict(text.strip())
            sentiment = result["sentiment"]
            confidence = result["confidence"]
            conf_str = f"{confidence:.1%}"

            if sentiment == "POSITIVE":
                st.success(f"POSITIVE - Tích cực! (độ tin cậy: {conf_str})")
            elif sentiment == "NEGATIVE":
                st.error(f"NEGATIVE - Tiêu cực (độ tin cậy: {conf_str})")
            else:
                st.info(f"NEUTRAL - Trung tính (độ tin cậy: {conf_str})")

            # Thêm vào lịch sử
            st.session_state.history.insert(0, {
                "Câu": text.strip(),
                "Cảm xúc": "Tích cực" if sentiment == "POSITIVE" else "Tiêu cực" if sentiment == "NEGATIVE" else "Trung tính",
                "Độ tin cậy": conf_str,
                "Thời gian": datetime.now().strftime("%H:%M:%S %d/%m")
            })

        except Exception as e:
            st.error(f"Lỗi khi phân tích: {e}")

# Hiển thị lịch sử
st.markdown("---")
st.subheader("Lịch sử phân tích")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có lịch sử phân tích nào. Hãy thử một câu ở trên nhé!")
