import streamlit as pd
import streamlit as st
import math
import pandas as pd

# ==============================================================================
# 1. CO-STIRPAT 게임 코어 로직 클래스
# ==============================================================================
class CoStirpatGame:
    def __init__(self):
        self.turn = 1
        self.max_turns = 5
        self.game_over = False
        self.game_result_message = ""
       
        # CO-STIRPAT 핵심 변수
        self.P = 100.0   # Population
        self.A = 50.0    # Affluence
        self.T = 1.0     # Technology
        self.CO = 1.0    # Cooperation/Offset
       
        # 모델 고유 계수
        self.a = 0.01
        self.b = 1.2
        self.c = 1.5
        self.d = 1.0
        self.e = -0.8
       
        # 게임 목표 지표
        self.accumulated_carbon = 0.0
        self.carbon_budget = 1200.0
        self.budget = 1000          
       
        # 시각화를 위한 이력 추적용 리스트
        self.history = []
        self.save_history(0, "게임 시작")

    def calculate_impact(self):
        try:
            ln_I = (math.log(self.a) +
                    self.b * math.log(self.P) +
                    self.c * math.log(self.A) +
                    self.d * math.log(self.T) +
                    self.e * math.log(self.CO))
            current_impact = math.exp(ln_I)
        except (ValueError, OverflowError):
            current_impact = 0.0
        return round(current_impact, 2)

    def save_history(self, current_emission, action_title):
        """매 턴의 데이터를 시각화를 위해 저장"""
        self.history.append({
            "Turn": f"Turn {self.turn}" if self.turn > 0 else "Start",
            "Action": action_title,
            "Emission": current_emission,
            "Accumulated Carbon": round(self.accumulated_carbon, 1),
            "Population (P)": round(self.P, 1),
            "Affluence (A)": round(self.A, 1),
            "Tech (T)": round(self.T, 2),
            "Cooperation (CO)": round(self.CO, 2),
            "Budget": self.budget
        })

    def get_policy_options(self):
        return {
            1: {
                "title": "🏭 구형 공업단지 대규모 증설",
                "cost": -200,
                "effect": {"P": 1.05, "A": 1.30, "T": 1.05, "CO": 1.0},
                "desc": "경제를 급격히 성장(A↑)시키지만, 구형 기술 혼용으로 탄소 집약도(T↑)가 가속화됩니다."
            },
            2: {
                "title": "🔋 분산에너지 특구 및 dMRV 인프라 도입",
                "cost": -400,
                "effect": {"P": 1.0, "A": 1.05, "T": 0.72, "CO": 1.2},
                "desc": "큰 예산이 들지만 기술 효율을 대폭 개선(T↓↓)하고 신뢰성 높은 상쇄 기반을 마련합니다."
            },
            3: {
                "title": "🌐 글로벌 기후 다자간 협약 체결",
                "cost": -100,
                "effect": {"P": 1.0, "A": 0.95, "T": 1.0, "CO": 1.6},
                "desc": "국제 공조(CO↑↑)를 강화하여 배출 계수를 억제하지만, 규제로 인해 일시적으로 경제가 위축됩니다."
            }
        }

    def play_turn(self, choice_id):
        if self.game_over:
            return
           
        options = self.get_policy_options()
        policy = options[choice_id]
       
        # 1. 비용 및 계수 변화 반영
        self.budget += policy["cost"]
        self.P *= policy["effect"]["P"]
        self.A *= policy["effect"]["A"]
        self.T *= policy["effect"]["T"]
        self.CO *= policy["effect"]["CO"]
       
        # 2. 자연적인 인구 성장 턴 제어
        self.P *= 1.02
       
        # 3. 배출량 계산 및 누적
        current_impact = self.calculate_impact()
        self.accumulated_carbon += current_impact
       
        # 4. 이력 저장
        self.save_history(current_impact, policy["title"])
       
        # 5. 게임 종료 조건 체크
        if self.accumulated_carbon > self.carbon_budget:
            self.game_over = True
            self.game_result_message = f"❌ 기후 재앙 엔딩: 임계 탄소 예산({self.carbon_budget})을 초과했습니다! 지구가 가열되었습니다."
        elif self.budget < 0:
            self.game_over = True
            self.game_result_message = "❌ 국가 부도 엔딩: 예산이 마이너스가 되어 친환경 정책을 펼칠 동력을 상실했습니다."
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.game_result_message = f"🎉 기후 방어 성공 엔딩: {self.max_turns}턴 동안 성공적으로 탄소 예산을 방어하며 지속 가능한 문명을 안착시켰습니다!"
        else:
            self.turn += 1

# ==============================================================================
# 2. Streamlit UI 대시보드 구성
# ==============================================================================
st.set_page_config(page_title="CO-STIRPAT 기후 시뮬레이터", layout="wide")

st.title("🌱 CO-STIRPAT 기반 기후 거버넌스 보드게임")
st.caption("인구(P), 부(A), 기술(T), 협력(CO)의 고차 방정식을 제어하여 탄소 예산 초과를 막으세요.")

# 세션 상태(session_state)에 게임 인스턴스가 없으면 새로 생성하여 주입
if 'game' not in st.session_state:
    st.session_state['game'] = CoStirpatGame()

game = st.session_state['game']

# 좌측 레이아웃: 대시보드 현황판
col1, col2 = st.columns([1, 2])

with col1:
    st.header(f"⏳ 현재 진행: {game.turn} / {game.max_turns} 턴")
   
    # 주요 지표 시각적 매트릭스 표시
    st.metric(label="💰 국가 재정 예산", value=f"${game.budget}", delta=f"{game.budget - 1000} (초기비비교)")
   
    # 탄소 진척도 바 프로그레스 바 구현
    carbon_ratio = min(game.accumulated_carbon / game.carbon_budget, 1.0)
    st.write(f"💨 누적 탄소 배출량: **{game.accumulated_carbon:.1f}** / 한계치: {game.carbon_budget}")
    st.progress(carbon_ratio)
   
    st.markdown("---")
    st.subheader("📊 핵심 STIRPAT 상태 지표")
    st.write(f"- 👥 인구 지수 (P): `{game.P:.1f}`")
    st.write(f"- 📈 경제 풍요도 (A): `{game.A:.1f}`")
    st.write(f"- ⚡ 기술 탄소집약도 (T): `{game.T:.2f}` *(낮을수록 우수)*")
    st.write(f"- 🤝 글로벌 협력 지수 (CO): `{game.CO:.2f}` *(높을수록 우수)*")

# 우측 레이아웃: 유저 행동 및 차트 데이터 시각화
with col2:
    if not game.game_over:
        st.subheader("🃏 이번 턴에 발령할 정책 카드를 선택하세요")
        options = game.get_policy_options()
       
        # 라디오 버튼이나 셀렉트박스로 정책 선택 인터페이스 구현
        choice_title = st.radio(
            "정책 리스트",
            options=[options[k]["title"] for k in options],
            help="정책에 따라 경제 지표와 CO-STIRPAT 계수들이 유기적으로 변동합니다."
        )
       
        # 선택한 타이틀에 매핑되는 ID 찾기
        choice_id = [k for k in options if options[k]["title"] == choice_title][0]
        st.info(f"**효과:** {options[choice_id]['desc']}")
       
        # [턴 진행 버튼] 클릭 시 해당 ID로 play_turn 메소드 실행
        if st.button("선택한 정책 집행 및 턴 종료 ➡️", type="primary"):
            game.play_turn(choice_id)
            st.rerun() # UI 상태 즉시 새로고침
           
    else:
        # 게임이 종료되었을 때 출력되는 엔딩 화면
        st.error("### 🛑 게임 종료")
        st.warning(game.game_result_message)
       
        if st.button("🔄 게임 처음부터 다시 시작하기"):
            del st.session_state['game']
            st.rerun()

    # 데이터 시각화 탭 분리 (플레이 이력 추적용)
    st.markdown("---")
    st.subheader("📈 실시간 기후 경제 시계열 트렌드")
    if len(game.history) > 1:
        df_history = pd.DataFrame(game.history)
       
        # 탄소 배출 추이 라인 차트
        st.write("**누적 탄소 배출량 변화 추이**")
        st.line_chart(df_history, x="Turn", y="Accumulated Carbon")
       
        # 지표별 상세 변동 데이터 테이블 제공
        with st.expander("📝 세부 정량 데이터 이력 보기"):
            st.dataframe(df_history)
