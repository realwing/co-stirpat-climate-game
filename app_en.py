import streamlit as st
import math
import pandas as pd

# ==============================================================================
# 1. CO-STIRPAT Game Core Logic Class
# ==============================================================================
class CoStirpatGame:
    def __init__(self):
        self.turn = 1
        self.max_turns = 5
        self.game_over = False
        self.game_result_message = ""
       
        # CO-STIRPAT Core Variables
        self.P = 100.0   # Population
        self.A = 50.0    # Affluence (GDP per capita)
        self.T = 1.0     # Technology (Carbon Intensity - lower is better)
        self.CO = 1.0    # Cooperation/Offset (higher is better)
       
        # Model Coefficients (Sensitivity variables)
        self.a = 0.01
        self.b = 1.2     # Population scaling
        self.c = 1.5     # Affluence scaling
        self.d = 1.0     # Technology scaling
        self.e = -0.8    # Cooperation scaling (negative means reduction)
       
        # Game Target Metrics
        self.accumulated_carbon = 0.0
        self.carbon_budget = 1200.0
        self.budget = 1000          
       
        # History Tracking for Visualization
        self.history = []
        self.save_history(0, "Game Start")

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
        """Saves telemetry data per turn for real-time visualization"""
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
                "title": "🏭 Expand Legacy Industrial Complex",
                "cost": -200,
                "effect": {"P": 1.05, "A": 1.30, "T": 1.05, "CO": 1.0},
                "desc": "Boosts economic growth (A↑) rapidly, but accelerates carbon intensity (T↑) due to legacy infrastructure integration."
            },
            2: {
                "title": "🔋 Deploy Distributed Energy Zone & dMRV",
                "cost": -400,
                "effect": {"P": 1.0, "A": 1.05, "T": 0.72, "CO": 1.2},
                "desc": "Requires high capital expenditure but radically optimizes technical efficiency (T↓↓) and builds verifiable offset mechanisms."
            },
            3: {
                "title": "🌐 Sign Multilateral Climate Accord",
                "cost": -100,
                "effect": {"P": 1.0, "A": 0.95, "T": 1.0, "CO": 1.6},
                "desc": "Strengthens global framework cooperation (CO↑↑) to suppress systemic scaling, though strict regulations temporarily cool down domestic growth."
            }
        }

    def play_turn(self, choice_id):
        if self.game_over:
            return
           
        options = self.get_policy_options()
        policy = options[choice_id]
       
        # 1. Apply cost and multipliers
        self.budget += policy["cost"]
        self.P *= policy["effect"]["P"]
        self.A *= policy["effect"]["A"]
        self.T *= policy["effect"]["T"]
        self.CO *= policy["effect"]["CO"]
       
        # 2. Natural population growth scaling
        self.P *= 1.02
       
        # 3. Calculate and accumulate impact
        current_impact = self.calculate_impact()
        self.accumulated_carbon += current_impact
       
        # 4. Save history
        self.save_history(current_impact, policy["title"])
       
        # 5. Evaluate Game Over conditions
        if self.accumulated_carbon > self.carbon_budget:
            self.game_over = True
            self.game_result_message = f"❌ Climate Catastrophe: Carbon budget limit ({self.carbon_budget}) breached! Extreme warming triggered."
        elif self.budget < 0:
            self.game_over = True
            self.game_result_message = "❌ Sovereign Default: Fiscal budget depleted. Capital required to deploy sustainable policy has collapsed."
        elif self.turn >= self.max_turns:
            self.game_over = True
            self.game_result_message = f"🎉 Climate Mitigation Success: You defended the carbon budget for {self.max_turns} turns and stabilized a sustainable civilization!"
        else:
            self.turn += 1

# ==============================================================================
# 2. Streamlit UI Dashboard Layout
# ==============================================================================
st.set_page_config(page_title="CO-STIRPAT Climate Simulator", layout="wide")

st.title("🌱 JIN: CO-STIRPAT Climate Governance")
st.caption("Control the non-linear dynamics of Population(P), Affluence(A), Technology(T), and Cooperation(CO) to prevent climate tipping points.")

# Initialize game instance within Streamlit session state if not existing
if 'game' not in st.session_state:
    st.session_state['game'] = CoStirpatGame()

game = st.session_state['game']

# Layout: Split dashboard status and user actions
col1, col2 = st.columns([1, 2])

with col1:
    st.header(f"⏳ Progress: Turn {game.turn} / {game.max_turns}")
   
    # Financial telemetry display
    st.metric(label="💰 Fiscal Budget Status", value=f"${game.budget}", delta=f"{game.budget - 1000} (vs Initial)")
   
    # Carbon footprint tracker and progress indicator bar
    carbon_ratio = min(game.accumulated_carbon / game.carbon_budget, 1.0)
    st.write(f"💨 Accumulated Carbon Emissions: **{game.accumulated_carbon:.1f}** / Threshold: {game.carbon_budget}")
    st.progress(carbon_ratio)
   
    st.markdown("---")
    st.subheader("📊 Core STIRPAT Diagnostics")
    st.write(f"- 👥 Population Index (P): `{game.P:.1f}`")
    st.write(f"- 📈 Affluence Level (A): `{game.A:.1f}`")
    st.write(f"- ⚡ Tech Carbon Intensity (T): `{game.T:.2f}` *(Lower is Better)*")
    st.write(f"- 🤝 Global Cooperation Index (CO): `{game.CO:.2f}` *(Higher is Better)*")

with col2:
    if not game.game_over:
        st.subheader("🃏 Select a Policy Card to Deploy This Turn")
        options = game.get_policy_options()
       
        # Policy Selection Interface
        choice_title = st.radio(
            "Available Policy Instruments",
            options=[options[k]["title"] for k in options],
            help="Each macro-policy shifts your economic baseline and structural CO-STIRPAT coefficients dynamically."
        )
       
        # Mapping selected title to numeric ID
        choice_id = [k for k in options if options[k]["title"] == choice_title][0]
        st.info(f"**Impact Vector:** {options[choice_id]['desc']}")
       
        # Execution flow button trigger
        if st.button("Deploy Policy & End Turn ➡️", type="primary"):
            game.play_turn(choice_id)
            st.rerun() # Refresh state machine immediately
           
    else:
        # Game over screen presentation layer
        st.error("### 🛑 Simulation Concluded")
        st.warning(game.game_result_message)
       
        if st.button("🔄 Restart New Simulation"):
            del st.session_state['game']
            st.rerun()

    # Time series diagnostics tabs
    st.markdown("---")
    st.subheader("📈 Real-Time Climate-Economic Telemetry")
    if len(game.history) > 1:
        df_history = pd.DataFrame(game.history)
       
        # Time-series line chart for carbon projection tracking
        st.write("**Carbon Accumulation Trajectory**")
        st.line_chart(df_history, x="Turn", y="Accumulated Carbon")
       
        # Detailed quantitative table lookup
        with st.expander("📝 View Raw Telemetry History"):
            st.dataframe(df_history)
