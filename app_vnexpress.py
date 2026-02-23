import streamlit as st
import pandas as pd
import plotly.express as px
import os
from io import BytesIO
from datetime import datetime

# --- CẤU HÌNH ---
# Đọc file CSV bạn vừa gửi (Streamlit sẽ nhận diện file này)
DATA_FILE = 'Danh sach 200 UVTW Khoa XIV.xlsx'
DEFAULT_IMAGE = "https://thuvienphapluat.vn/images/no-image.png"

def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Làm sạch dữ liệu: Đảm bảo cột Năm sinh là số
        df['Năm sinh'] = pd.to_numeric(df['Năm sinh'], errors='coerce')
        # Tính tuổi dựa trên năm hiện tại (2026)
        df['Tuổi'] = 2026 - df['Năm sinh']
        return df
    return pd.DataFrame()

# --- GIAO DIỆN ---
st.set_page_config(page_title="Hồ sơ 200 Ủy viên Trung ương Khóa XIV", layout="wide")
df = load_data()

# --- SIDEBAR: ĐĂNG NHẬP & BỘ LỌC ---
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a1/Logo_VnExpress.svg/1200px-Logo_VnExpress.svg.png", width=150)
    st.title("Quản trị Hệ thống")
    
    if "admin" not in st.session_state:
        st.session_state.admin = False
    
    if not st.session_state.admin:
        pwd = st.text_input("Mật khẩu", type="password")
        if st.button("Xác nhận"):
            if pwd == "admin123":
                st.session_state.admin = True
                st.rerun()
    else:
        st.success("Chế độ: Quản trị viên")
        if st.button("Đăng xuất"):
            st.session_state.admin = False
            st.rerun()

# --- THỐNG KÊ TỔNG QUAN ---
st.title("🏛️ Hồ sơ 200 Ủy viên Trung ương Khóa XIV")
st.markdown("---")

if not df.empty:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tổng số Ủy viên", f"{len(df)} nhân sự")
    with c2:
        st.metric("Độ tuổi trung bình", f"{int(df['Tuổi'].mean())} tuổi")
    with c3:
        # Xuất file báo cáo dựa trên kết quả tìm kiếm
        output = BytesIO()
        df.to_csv(output, index=False)
        st.download_button("📥 Tải danh sách (CSV)", data=output.getvalue(), file_name="danh_sach_uvtw.csv")

    # Biểu đồ thống kê
    exp = st.expander("📊 Phân tích dữ liệu (Độ tuổi & Địa phương)", expanded=True)
    with exp:
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_age = px.histogram(df, x="Tuổi", nbins=10, title="Phân bố độ tuổi", color_discrete_sequence=['#9b2321'])
            st.plotly_chart(fig_age, use_container_width=True)
        with col_chart2:
            top_que = df['Quê quán'].value_counts().head(10)
            fig_que = px.bar(top_que, orientation='h', title="Top 10 địa phương có nhiều Ủy viên nhất")
            st.plotly_chart(fig_que, use_container_width=True)

# --- TRA CỨU & HIỂN THỊ THẺ ---
search = st.text_input("🔍 Tìm kiếm theo tên hoặc quê quán (Ví dụ: Hà Nội, Nghệ An...)", placeholder="Nhập từ khóa...")

filtered_df = df.copy()
if search:
    filtered_df = df[df.astype(str).apply(lambda x: x.str.contains(search, case=False)).any(axis=1)]

st.subheader(f"Kết quả tìm kiếm: {len(filtered_df)}")

# Hiển thị dạng Grid Card 


cols = st.columns(4)
for i, (idx, row) in enumerate(filtered_df.iterrows()):
    with cols[i % 4]:
        with st.container(border=True):
            st.markdown(f"### {row['Họ và tên']}")
            st.write(f"🎂 **Năm sinh:** {int(row['Năm sinh']) if not pd.isna(row['Năm sinh']) else 'N/A'}")
            st.write(f"📍 **Quê quán:** {row['Quê quán']}")
            st.info(f"**Chức vụ:** {row['Chức vụ hiện nay']}")
            
            if st.button("Xem chi tiết", key=f"btn_{idx}"):
                @st.dialog(f"Thông tin: {row['Họ và tên']}")
                def detail(r):
                    st.write(f"**Số thứ tự:** {r['STT']}")
                    st.write(f"**Quê quán:** {r['Quê quán']}")
                    st.write(f"**Chức vụ hiện nay:** {r['Chức vụ hiện nay']}")
                    st.divider()
                    st.write("*Dữ liệu đang tiếp tục được cập nhật...*")
                detail(row)

# --- CHỨC NĂNG CẬP NHẬT (ADMIN) ---
if st.session_state.admin:
    st.markdown("---")
    st.subheader("🛠️ Cập nhật dữ liệu")
    with st.form("edit_form"):
        # Các trường nhập liệu để sửa hoặc thêm mới
        st.write("Nhập thông tin để thêm/sửa nhân sự")
        # (Bạn có thể thêm các input tương tự như các bản trước tại đây)

        st.form_submit_button("Lưu thay đổi")
