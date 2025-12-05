# streamlit_app.py
import streamlit as st
import pandas as pd
from model import analyzer
from datetime import datetime

# ================== CẤU HÌNH ==================
st.set_page_config(page_title="Phân loại cảm xúc Tiếng Việt", layout="centered")
st.title("Phân Loại Cảm Xúc Tiếng Việt")

# Khởi tạo session_state
if "history" not in st.session_state:
    st.session_state.history = []
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False
if "delete_success" not in st.session_state:
    st.session_state.delete_success = False

# Hiện toast xóa thành công (chỉ hiện 1 lần)
if st.session_state.delete_success:
    st.toast("Đã xóa toàn bộ lịch sử thành công!")
    st.session_state.delete_success = False

# ================== NHẬP LIỆU ==================
text = st.text_area("Nhập câu cần phân tích:", height=120, placeholder="Ví dụ: Hôm nay tôi rất vui.")

col1, col2 = st.columns(2)
with col1:
    btn_predict = st.button("Phân tích cảm xúc", type="primary", use_container_width=True)
with col2:
    if st.button("Xóa lịch sử", type="secondary", use_container_width=True):
        st.session_state.confirm_clear = True

# ================== XỬ LÝ PHÂN TÍCH ==================
if btn_predict and text.strip():
    clean_text = text.strip()

    if not clean_text:
        st.toast("Vui lòng nhập nội dung trước khi phân tích!")
    elif (len(clean_text) < 5 or len(clean_text) > 50):
        st.toast("Câu quá ngắn! Vui lòng nhập vào câu có tối thiểu 5 ký tự và tối đa 50 ký tự!")
    else:
        with st.spinner("Đang phân tích cảm xúc…"):
            try:
                result = analyzer.predict(clean_text)
                sentiment = result["sentiment"]
                confidence = result["confidence"]
                conf_str = f"{confidence:.1%}"

                # Hiển thị kết quả đẹp
                if sentiment == "POSITIVE":
                    st.success(f"POSITIVE - Tích cực! (Độ tin cậy: {conf_str})")
                elif sentiment == "NEGATIVE":
                    st.error(f"NEGATIVE - Tiêu cực (Độ tin cậy: {conf_str})")
                else:
                    st.info(f"NEUTRAL - Trung tính (Độ tin cậy: {conf_str})")

                # Thêm vào lịch sử (mới nhất lên đầu)
                st.session_state.history.insert(0, {
                    "Nội dung": clean_text,
                    "Cảm xúc": "Tích cực" if sentiment == "POSITIVE" else "Tiêu cực" if sentiment == "NEGATIVE" else "Trung tính",
                    "Độ tin cậy": conf_str,
                    "Thời gian": datetime.now().strftime("%H:%M:%S %d/%m/%Y")
                })

            except Exception as e:
                st.error(f"Lỗi khi phân tích: {e}")

# ================== XÁC NHẬN XÓA LỊCH SỬ ==================
if st.session_state.confirm_clear:
    st.warning("Cảnh báo: Hành động này sẽ **xóa toàn bộ lịch sử phân tích** và không thể hoàn tác!")
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Có, xóa hết!", type="primary", use_container_width=True):
            st.session_state.history = []
            st.session_state.confirm_clear = False
            st.session_state.delete_success = True
            st.rerun()
    with col_b:
        if st.button("Hủy bỏ", type="secondary", use_container_width=True):
            st.session_state.confirm_clear = False
            st.rerun()

# ================== HIỂN THỊ LỊCH SỬ ==================
st.markdown("---")
st.subheader("Lịch sử phân tích")

if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True, hide_index=True)
else:
    st.info("Chưa có dữ liệu lịch sử nào. Hãy thử phân tích một câu ở trên!")

st.markdown("---")


