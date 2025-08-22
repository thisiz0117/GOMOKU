import streamlit as st
import numpy as np

# --- 게임 설정 ---
BOARD_SIZE = 15
EMPTY, BLACK, WHITE = 0, 1, 2

# --- 페이지 설정 ---
st.set_page_config(page_title="AI 대전 오목", page_icon="⚫")

st.title("AI와 대결하는 오목 게임 🎮")
st.write("**당신은 흑돌(⚫)이고, AI는 백돌(⚪)입니다.**")

# --- 게임 상태 초기화 ---
def init_game():
    st.session_state.board = np.full((BOARD_SIZE, BOARD_SIZE), EMPTY, dtype=int)
    st.session_state.turn = BLACK
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.message = "게임 시작! 당신의 차례입니다."

if 'board' not in st.session_state:
    init_game()

# --- 게임/AI 로직 (변경 없음) ---
def check_win(board, player):
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if c <= BOARD_SIZE - 5 and np.all(board[r, c:c+5] == player): return True
            if r <= BOARD_SIZE - 5 and np.all(board[r:r+5, c] == player): return True
            if r <= BOARD_SIZE - 5 and c <= BOARD_SIZE - 5 and np.all([board[r+i, c+i] for i in range(5)] == player): return True
            if r <= BOARD_SIZE - 5 and c >= 4 and np.all([board[r+i, c-i] for i in range(5)] == player): return True
    return False

def find_best_move(board):
    empty_cells = list(zip(*np.where(board == EMPTY)))
    for r, c in empty_cells:
        board[r, c] = WHITE;
        if check_win(board, WHITE): board[r, c] = EMPTY; return r, c
        board[r, c] = EMPTY
    for r, c in empty_cells:
        board[r, c] = BLACK;
        if check_win(board, BLACK): board[r, c] = EMPTY; return r, c
        board[r, c] = EMPTY
    best_offensive_score, best_defensive_score = -1, -1
    best_offensive_move, best_defensive_move = None, None
    for r, c in empty_cells:
        board[r, c] = WHITE
        offensive_score = calculate_line_score(board, r, c, WHITE)
        if offensive_score > best_offensive_score: best_offensive_score, best_offensive_move = offensive_score, (r, c)
        board[r, c] = EMPTY
        board[r, c] = BLACK
        defensive_score = calculate_line_score(board, r, c, BLACK)
        if defensive_score > best_defensive_score: best_defensive_score, best_defensive_move = defensive_score, (r, c)
        board[r, c] = EMPTY
    return best_offensive_move if best_offensive_score >= best_defensive_score else best_defensive_move

def calculate_line_score(board, r, c, player):
    max_score = 0
    for dr, dc in [(1, 0), (0, 1), (1, 1), (1, -1)]:
        line_len = 1
        for i in range(1, 5):
            nr, nc = r + dr * i, c + dc * i
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr, nc] == player: line_len += 1
            else: break
        for i in range(1, 5):
            nr, nc = r - dr * i, c - dc * i
            if 0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE and board[nr, nc] == player: line_len += 1
            else: break
        max_score = max(max_score, line_len)
    return max_score

# --- UI 렌더링 ---

# 시인성을 위한 단순하고 안정적인 CSS
st.markdown("""
<style>
/* Streamlit의 컬럼(칸) 사이의 가로 간격을 없앱니다 */
div[data-testid="column"] {
    width: 42px !important; /* 칸 너비를 고정하여 줄이 틀어지는 것을 방지 */
    flex: 0 0 42px !important;
}
/* 버튼 스타일 */
.stButton>button {
    width: 40px;
    height: 40px;
    font-size: 26px;
    border: 1px solid #B0B0B0; /* 선명한 회색 테두리 */
    background-color: #68687D; /* 밝은 회색 배경 */
    border-radius: 0 !important; /* 완벽한 사각형 */
}
.stButton>button:hover {
    border-color: #FF4B4B; /* 마우스를 올리면 붉은색 테두리 */
}
.stButton>button:disabled {
    background-color: #F0F2F6;
    color: black;
    border-color: #B0B0B0;
}
</style>
""", unsafe_allow_html=True)

# 게임 상태 메시지
if st.session_state.winner:
    if st.session_state.winner == BLACK: st.success("🎉 축하합니다! 당신이 이겼습니다!"); st.balloons()
    elif st.session_state.winner == WHITE: st.error("🤖 AI가 승리했습니다. 다시 도전해보세요!")
    else: st.warning("무승부입니다!")
else:
    st.info(st.session_state.message)

# 오목판을 담을 컨테이너
board_container = st.container()

with board_container:
    board = st.session_state.board
    for r in range(BOARD_SIZE):
        cols = st.columns(BOARD_SIZE, gap="small")
        for c in range(BOARD_SIZE):
            stone = board[r, c]
            symbol = " "
            if stone == BLACK: symbol = "⚫"
            elif stone == WHITE: symbol = "⚪️"
            
            is_disabled = st.session_state.game_over or stone != EMPTY
            if cols[c].button(symbol, key=f"btn_{r}_{c}", disabled=is_disabled):
                if not st.session_state.game_over and st.session_state.turn == BLACK:
                    st.session_state.board[r, c] = BLACK
                    if check_win(st.session_state.board, st.session_state.turn):
                        st.session_state.game_over, st.session_state.winner = True, st.session_state.turn
                    elif not np.any(st.session_state.board == EMPTY):
                        st.session_state.game_over, st.session_state.winner = True, "Draw"
                    else: st.session_state.turn = WHITE; st.session_state.message = "AI가 생각 중입니다..."
                    st.rerun()

st.markdown("---") # 구분선

# '새 게임 시작' 버튼
if st.button("새 게임 시작" if not st.session_state.game_over else "다시 하기", key="new_game"):
    init_game()
    st.rerun()

# --- AI 턴 처리 로직 ---
if not st.session_state.game_over and st.session_state.turn == WHITE:
    with st.spinner("AI가 최적의 수를 찾고 있습니다... 🤔"):
        ai_r, ai_c = find_best_move(st.session_state.board)
        st.session_state.board[ai_r, ai_c] = WHITE
        if check_win(st.session_state.board, st.session_state.turn):
            st.session_state.game_over, st.session_state.winner = True, st.session_state.turn
        elif not np.any(st.session_state.board == EMPTY):
            st.session_state.game_over, st.session_state.winner = True, "Draw"
        else: st.session_state.turn = BLACK; st.session_state.message = "당신의 차례입니다. 돌을 놓아주세요."
    st.rerun()