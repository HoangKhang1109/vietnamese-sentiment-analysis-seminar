# streamlit_app.py - Phiên bản ĐỘC LẬP (không cần FastAPI)
import streamlit as st
import pandas as pd
from model import analyzer  # Import trực tiếp từ model.py
import sqlite3
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="Phân loại cảm xúc Tiếng Việt", layout="centered")
st.title(" Phân Loại Cảm Xúc Tiếng Việt")
st.markdown("**Dùng AI Transformer (PhoBERT) - Chính xác >92%**")

# Input
text = st.text_area("Nhập câu cần phân tích:", height=100, placeholder="Ví dụ: Hôm nay tôi rất vui!")

col1, col2 = st.columns(2)
with col1:
    btn_predict = st.button(" Phân tích cảm xúc", type="primary", use_container_width=True)
with col2:
    btn_clear = st.button(" Xóa lịch sử", type="secondary", use_container_width=True)

# Khởi tạo session_state cho xác nhận xóa
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

# XỬ LÝ NÚT XÓA LỊCH SỬ (có xác nhận)
if btn_clear:
    if st.session_state.confirm_clear:
        with st.spinner("Đang xóa lịch sử..."):
            try:
                conn = sqlite3.connect('history.db')
                c = conn.cursor()
                c.execute("DELETE FROM predictions")
                c.execute("DELETE FROM sqlite_sequence WHERE name='predictions'")
                conn.commit()
                conn.close()
                st.success("Đã xóa toàn bộ lịch sử thành công!")
                st.session_state.confirm_clear = False
                st.rerun()
            except Exception:
                st.error("Lỗi khi xóa lịch sử!")
        st.stop()
    else:
        st.warning(" Bạn có chắc chắn muốn xóa toàn bộ lịch sử không? Hành động này không thể hoàn tác!")
        col_confirm, col_cancel = st.columns(2)
        with col_confirm:
            if st.button("Có, xóa hết!", type="primary", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()
        with col_cancel:
            if st.button(" Hủy", type="secondary", use_container_width=True):
                st.rerun()
        st.stop()

# XỬ LÝ NÚT PHÂN TÍCH (gọi trực tiếp analyzer, không cần API)
if btn_predict and text.strip():
    with st.spinner("Đang phân tích..."):
        try:
            result = analyzer.predict(text)
            sentiment = result['sentiment']
            confidence = f"{result['confidence']:.1%}"

            # Hiệu ứng màu
            if sentiment == "POSITIVE":
                st.success(f" POSITIVE - Tích cực! (độ tin cậy: {confidence})")
            elif sentiment == "NEGATIVE":
                st.error(f" NEGATIVE - Tiêu cực (độ tin cậy: {confidence})")
            else:
                st.info(f" NEUTRAL - Trung tính (độ tin cậy: {confidence})")

            # Lưu vào DB ngay lập tức (như backend cũ)
            conn = sqlite3.connect('history.db')
            c = conn.cursor()
            c.execute("CREATE TABLE IF NOT EXISTS predictions (id INTEGER PRIMARY KEY AUTOINCREMENT, text TEXT, sentiment TEXT, confidence REAL, timestamp TEXT)")
            c.execute("INSERT INTO predictions (text, sentiment, confidence, timestamp) VALUES (?, ?, ?, ?)",
                      (text, sentiment, result['confidence'], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()

        except Exception as e:
            st.error(f"Lỗi phân tích: {str(e)}")

# HIỂN THỊ LỊCH SỬ
st.markdown("---")
st.subheader(" Lịch sử phân tích")

@st.cache_data(ttl=300)  # Cache 5 phút để nhanh hơn
def load_history():
    try:
        conn = sqlite3.connect('history.db')
        df = pd.read_sql_query("SELECT text, sentiment, confidence, timestamp as time FROM predictions ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

history_df = load_history()
if not history_df.empty:
    # Đổi tên cột và format
    history_df = history_df.rename(columns={
        "text": "Câu tiếng Việt",
        "sentiment": "Cảm xúc",
        "confidence": "Độ tin cậy",
        "time": "Thời gian"
    })
    history_df["Độ tin cậy"] = history_df["Độ tin cậy"].apply(lambda x: f"{x:.1%}")
    history_df["Cảm xúc"] = history_df["Cảm xúc"].map({
        "POSITIVE": " Tích cực",
        "NEGATIVE": " Tiêu cực",
        "NEUTRAL": " Trung tính"
    })
    st.dataframe(history_df, use_container_width=True, hide_index=True)
else:
    st.info(" Chưa có lịch sử phân tích nào. Hãy thử phân tích một câu!")

