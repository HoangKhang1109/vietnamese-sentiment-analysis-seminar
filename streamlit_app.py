# streamlit_app.py
import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

# Khởi tạo session_state nếu chưa có
if "confirm_clear" not in st.session_state:
    st.session_state.confirm_clear = False

st.set_page_config(page_title="Phân loại cảm xúc Tiếng Việt", layout="centered")
st.title("Phân Loại Cảm Xúc Tiếng Việt")

if "delete_success" not in st.session_state:
    st.session_state.delete_success = False

if st.session_state.delete_success:
    st.toast("Đã xóa toàn bộ lịch sử thành công!")
    st.session_state.delete_success = False  # Reset trạng thái để không hiện mãi

# --- PHẦN NHẬP LIỆU ---
text = st.text_area("Nhập câu cần phân tích:", height=100)

col1, col2 = st.columns([1, 1])
with col1:
    btn_predict = st.button("Phân tích cảm xúc", type="primary", use_container_width=True)
with col2:
    if st.button("Xóa lịch sử", use_container_width=True):
        st.session_state.confirm_clear = True

# --- XỬ LÝ SỰ KIỆN PHÂN TÍCH
if btn_predict:
    clean_text = text.strip()
    # Kiểm tra rỗng
    if not clean_text:
        st.toast("Vui lòng nhập nội dung trước khi phân tích!")  
    # Kiểm tra độ dài câu nhập vào
    elif len(clean_text) < 5:
        st.toast("Câu quá ngắn! Vui lòng nhập vào câu có tối thiểu 5 ký tự")
    else:
        with st.spinner("Đang phân tích..."):
            try:
                response = requests.post(f"{API_URL}/predict", json={"text": clean_text})
                if response.status_code == 200:
                    result = response.json()
                    sentiment = result['sentiment']
                    confidence = result['confidence']
                    
                    if sentiment == "POSITIVE":
                        st.success(f"POSITIVE - Tích cực! (Độ tin cậy: {confidence})")
                    elif sentiment == "NEGATIVE":
                        st.error(f"NEGATIVE - Tiêu cực (Độ tin cậy: {confidence})")
                    else:
                        st.info(f"NEUTRAL - Trung tính (Độ tin cậy: {confidence})")
                else:
                    st.error(f"Lỗi API: {response.status_code}")
            except Exception as e:
                st.error(f"Lỗi kết nối: {e}")
                
# --- XỬ LÝ SỰ KIỆN XÓA
if st.session_state.confirm_clear:
    # Tạo một container để chứa giao diện cảnh báo
    with st.container():
        st.warning("Cảnh báo: Hành động này sẽ xóa toàn bộ lịch sử!")
        col_confirm_1, col_confirm_2 = st.columns(2)       
        with col_confirm_1:
            # Nút xác nhận xóa
            if st.button("Có, xóa hết!", type="primary", use_container_width=True):
                with st.spinner("Đang xóa..."):
                    try:
                        # Gọi API xóa
                        response = requests.delete(f"{API_URL}/history")
                        if response.status_code == 200:
                            st.session_state.confirm_clear = False
                            st.session_state.delete_success = True
                            st.rerun()
                        else:
                            st.error(f"Lỗi Server: {response.status_code}")             
                    except requests.exceptions.ConnectionError:
                        st.error("Không kết nối được với API ")
                    except Exception as e:
                        st.error(f"Lỗi không xác định: {e}")
        
        with col_confirm_2:
            # Nút hủy
            if st.button("Hủy bỏ", use_container_width=True):
                st.session_state.confirm_clear = False
                st.rerun()

# --- HIỂN THỊ LỊCH SỬ ---
st.markdown("---")
st.subheader("Lịch sử phân tích")

try:
    response = requests.get(f"{API_URL}/history")
    if response.status_code == 200:
        history = response.json()
        if history:
            df = pd.DataFrame(history)
            df.columns = ["Nội dung", "Cảm xúc", "Độ tin cậy", "Thời gian"]
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có dữ liệu lịch sử nào.")
    else:
        st.error("Lỗi khi tải lịch sử.")
except:
    st.error("Không kết nối được với Server để lấy lịch sử.")