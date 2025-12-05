# streamlit_app.py - Phiên bản HOÀN CHỈNH chạy ngon trên Streamlit Cloud
import streamlit as st
import pandas as pd
from model import analyzer          # ← quan trọng: phải có đúng file model.py trong repo
import sqlite3
from datetime import datetime

# ================== CẤU HÌNH TRANG ==================
st.set_page_config(page_title="Phân loại cảm xúc Tiếng Việt", layout="centered")
st.title("Phân Loại Cảm Xúc Tiếng Việt")
st.markdown("**Dùng AI Transformer (PhoBERT) – Chính xác > 92%**")

# ================== INPUT ==================
text = st.text_area("Nhập câu cần phân tích:", height=120, placeholder="Ví dụ: Hôm nay tôi rất vui!")

col1, col2 = st.columns(2)
with col1:
    btn_predict = st.button("Phân tích cảm xúc", type="primary", use_container_width=True)
with col2:
    btn_clear = st.button("Xóa lịch sử", type="secondary", use_container_width=True)

# ================== XÁC NHẬN XÓA ==================
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

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
            except:
                st.error("Lỗi khi xóa lịch sử!")
        st.stop()

    else:
        st.warning("Bạn có chắc chắn muốn xóa toàn bộ lịch sử không? Hành động này không thể hoàn tác!")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Có, xóa hết!", type="primary", use_container_width=True):
                st.session_state.confirm_clear = True
                st.rerun()
        with c2:
            if st.button("Hủy", type="secondary", use_container_width=True):
                st.rerun()
        st.stop()

# ================== PHÂN TÍCH CẢM XÚC ==================
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

            # Lưu vào SQLite
            conn = sqlite3.connect('history.db')
            c = conn.cursor()
            c.execute("""CREATE TABLE IF NOT EXISTS predictions
                         (id INTEGER PRIMARY KEY AUTOINCREMENT,
                          text TEXT, sentiment TEXT, confidence REAL, timestamp TEXT)""")
            c.execute("INSERT INTO predictions (text, sentiment, confidence, timestamp) VALUES (?, ?, ?, ?)",
                      (text.strip(), sentiment, confidence, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            conn.commit()
            conn.close()

        except Exception as e:
            st.error(f"Lỗi khi phân tích: {e}")

# ================== LỊCH SỬ ==================
st.markdown("---")
st.subheader("Lịch sử phân tích")

@st.cache_data(ttl=60)  # cache 60 giây cho nhanh
def load_history():
    try:
        conn = sqlite3.connect('history.db')
        df = pd.read_sql_query(
            "SELECT text, sentiment, confidence, timestamp as time FROM predictions ORDER BY id DESC LIMIT 100",
            conn
        )
        conn.close()
        return df
    except:
        return pd.DataFrame(columns=["text", "sentiment", "confidence", "time"])

df_history = load_history()

if not df_history.empty:
    df_display = df_history.copy()
    df_display = df_display.rename(columns={
        "text": "Câu",
        "sentiment": "Cảm xúc",
        "confidence": "Độ tin cậy",
        "time": "Thời gian"
    })
    df_display["Độ tin cậy"] = df_display["Độ tin cậy"].apply(lambda x: f"{x:.1%}")
    df_display["Cảm xúc"] = df_display["Cảm xúc"].map({
        "POSITIVE": "Tích cực",
        "NEGATIVE": "Tiêu cực",
        "NEUTRAL": "Trung tính"
    })
    st.dataframe(df_display, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có lịch sử phân tích nào. Hãy thử một câu ở trên nhé!")
