#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Streamlit UI for PDF file upload and document management.
"""

import streamlit as st
import requests
import datetime
import pandas as pd
from typing import List, Dict, Any

# Configuration
API_BASE_URL = "http://localhost:8000/documents/"
UPLOAD_ENDPOINT = API_BASE_URL + "upload"
LIST_ENDPOINT = API_BASE_URL
DEFAULT_EXPIRE_DAYS = 7
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


# Upload file function
def upload_file(uploaded_file, expire_date):
    """Upload a file to the server."""
    files = {
        "file": (
            uploaded_file.name,
            uploaded_file.getvalue(),
            "application/pdf",
        )
    }
    data = {
        "expire_at": expire_date.strftime("%Y-%m-%d"),
    }
    try:
        response = requests.post(UPLOAD_ENDPOINT, files=files, data=data)
        response.raise_for_status()
        return True, response.json()
    except Exception as e:
        return False, str(e)


# File listing functions
def load_file_list():
    """Load the list of documents from the server."""
    try:
        response = requests.get(LIST_ENDPOINT)
        response.raise_for_status()
        files = response.json()
        return files
    except Exception as e:
        st.error(f"파일 목록을 불러오지 못했습니다: {e}")
        return []


def display_files(files: List[Dict[str, Any]]):
    """Display files in a nice table format."""
    if not files:
        st.warning("업로드된 파일이 없습니다.")
        return

    # Prepare data for display
    display_data = []
    for file in files:
        row = {
            "file_name": file.get("file_name", "-"),
            "file_size": f"{file.get('file_size', 0):,} bytes",
            "uploaded_by": file.get("uploaded_by", "-"),
            "uploaded_at": format_datetime(file.get("uploaded_at")),
            "expire_at": format_datetime(file.get("expire_at")),
            "status": file.get("status", "-"),
        }
        display_data.append(row)

    # Show table
    st.dataframe(display_data, use_container_width=True)

    # Show additional info
    st.info(f"총 {len(files)}개의 파일이 있습니다.")


def format_datetime(dt_str):
    """Format datetime string for display."""
    if not dt_str:
        return "-"
    try:
        dt = datetime.datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M")
    except Exception:
        return dt_str


# Streamlit UI
st.title("📄 PDF 문서 관리")

# Sidebar: File upload
with st.sidebar:
    st.header("📤 파일 업로드")
    uploaded_file = st.file_uploader("파일 업로드", type=["pdf", "docx"])
    expire_date = st.date_input(
        "파일 만료일",
        value=datetime.date.today()
        + datetime.timedelta(days=DEFAULT_EXPIRE_DAYS),  # 기본 내일
        min_value=datetime.date.today(),
    )
    upload_button = st.button("🚀 업로드")

if upload_button:
    if not uploaded_file:
        st.warning("⚠️ 파일을 먼저 선택해주세요.")
    else:
        if uploaded_file.size > MAX_FILE_SIZE:
            st.warning(
                f"⚠️ 파일 크기가 {MAX_FILE_SIZE / (1024*1024):.1f}MB를 초과했습니다."
            )
        else:
            with st.spinner("파일 업로드 중..."):
                success, result = upload_file(uploaded_file, expire_date)
                if success:
                    st.success("✅ 업로드 성공!")
                    st.toast("업로드 완료 🎉")
                    st.json(result)
                else:
                    st.error("❌ 업로드 실패")
                    st.text(result)

# Main area: File listing
st.header("📋 파일 목록")

# Load files from server
files = load_file_list()

# Display files
if files:
    display_files(files)
else:
    st.warning("업로드된 파일이 없습니다.")
