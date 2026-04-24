from pathlib import Path
import json

import streamlit as st


st.set_page_config(page_title="여행 성향 퀴즈", page_icon="✈️")

STUDENT_ID = "2023204072"
STUDENT_NAME = "전주용"
DATA_FILE = Path(__file__).with_name("quiz_data.json")
IMG_DIR = Path(__file__).with_name("img")
SUBMITTER_CHARACTER = IMG_DIR / "trip.jpg"

# 테스트용 유저 아이디 비밀번호 설정
USERS = {
    "student": "1234",
    "guest": "1111",
}

# 캐싱을 활용하여 퀴즈 json파일 읽기
@st.cache_data
def load_quiz_data(file_path, modified_time):
    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)

# 상태 초기화 부분
def init_state():
    #session_state에 로그인 상태와 결과 저장
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "login_user" not in st.session_state:
        st.session_state.login_user = ""
    if "login_error" not in st.session_state:
        st.session_state.login_error = False
    if "result_text" not in st.session_state:
        st.session_state.result_text = ""
    if "quiz_error" not in st.session_state:
        st.session_state.quiz_error = ""

# 로그인 함수
def login(username, password):
    # 입력한 값이 USERS와 일치하면 로그인 성공으로 처리
    if username in USERS and USERS[username] == password:
        st.session_state.logged_in = True
        st.session_state.login_user = username
        st.session_state.login_error = False
        st.rerun()
    else:
        st.session_state.login_error = True

# 로그아웃 함수
def logout():
    st.session_state.logged_in = False
    st.session_state.login_user = ""
    st.session_state.result_text = ""
    st.session_state.quiz_error = ""
    st.rerun()

# 퀴즈 결과 계산 함수
def calculate_result(quiz_data):
    # 각 문항의 첫 번째 선택지는 계획형, 두 번째 선택지는 즉흥형으로 계산
    plan_count = 0 # 계획형
    free_count = 0 # 즉흥형

    for question in quiz_data["questions"]:
        answer = st.session_state[question["id"]]
        if answer == question["choices"][0]:
            plan_count += 1
        else:
            free_count += 1

    if plan_count > free_count:
        return quiz_data["results"]["plan"]
    if free_count > plan_count:
        return quiz_data["results"]["free"]
    return quiz_data["results"]["balanced"]

# 초기 정보 화면
def show_submitter_info():
    info_col, image_col = st.columns([2, 1])

    # 학번 이름 
    with info_col:
        st.write(f"학번 : {STUDENT_ID}")
        st.write(f"이름 : {STUDENT_NAME}")

    # 이미지 부분
    with image_col:
        if SUBMITTER_CHARACTER.exists():
            st.image(str(SUBMITTER_CHARACTER), use_container_width=True)
            st.write('이미지 출처 : https://kr.pinterest.com')

# main 함수
def main():
    init_state()
    quiz_data = load_quiz_data(str(DATA_FILE), DATA_FILE.stat().st_mtime)

    st.title("여행 성향 퀴즈")
    st.write("간단한 질문에 답하고 나의 여행 스타일을 확인해보세요.")
    show_submitter_info()

    if st.session_state.logged_in:
        st.write(f"로그인 상태 : 로그인됨 ({st.session_state.login_user})")
        if st.button("로그아웃"):
            logout()
    else:
        st.write("로그인 상태: 로그아웃")

        username = st.text_input("아이디")
        password = st.text_input("비밀번호", type="password")

        if st.button("로그인"):
            login(username, password)

        if st.session_state.login_error:
            st.error("로그인 실패: 아이디 또는 비밀번호가 틀렸습니다.")

        st.caption("테스트 계정: student / 1234")
        return

    st.subheader("퀴즈")

    for number, question in enumerate(quiz_data["questions"], start=1):
        st.radio(
            f"{number}. {question['question']}",
            question["choices"],
            key=question["id"],
            index=None,
        )

    if st.button("결과 확인"):
        unanswered = []

        # 비어 있는 문항이 있으면 결과를 계산하지 않고 안내 메시지를 보여줌
        for number, question in enumerate(quiz_data["questions"], start=1):
            if st.session_state.get(question["id"]) is None:
                unanswered.append(str(number))

        if unanswered:
            st.session_state.result_text = ""
            st.session_state.quiz_error = (
                f"아직 답하지 않은 문항이 있습니다: {', '.join(unanswered)}번"
            )
        else:
            st.session_state.quiz_error = ""
            st.session_state.result_text = calculate_result(quiz_data)

    if st.session_state.quiz_error:
        st.warning(st.session_state.quiz_error)

    if st.session_state.result_text:
        st.subheader("최종 결과")
        st.success(st.session_state.result_text)


if __name__ == "__main__":
    main()
