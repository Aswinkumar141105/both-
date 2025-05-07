import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "home"
    st.session_state.phenol_data = pd.DataFrame(columns=[
        "Phenol (ml)", "Water (ml)", "% Phenol", 
        "Disappear Temp (°C)", "Reappear Temp (°C)", "Mean Temp (°C)"
    ])
    st.session_state.water_vol = 3.0
    st.session_state.cond_data = pd.DataFrame(columns=["NaOH (ml)", "Conductance (mS)"])
    st.session_state.naoh_normality = 0.1
    st.session_state.current_naoh = 0.0

# --------------------------
# PHENOL-WATER EXPERIMENT
# --------------------------

def phenol_intro():
    st.title("Phenol-Water CST Determination")
    st.markdown("""
    **Aim:** Determine the Critical Solution Temperature (CST) of phenol-water system
    
    **Theory:** 
    - Phenol and water show partial miscibility below CST (≈68°C)
    - At CST, the two phases become completely miscible
    - This experiment maps the phase boundary by observing turbidity changes
    """)
    if st.button("Start Experiment"):
        st.session_state.phenol_data = pd.DataFrame(columns=[
            "Phenol (ml)", "Water (ml)", "% Phenol", 
            "Disappear Temp (°C)", "Reappear Temp (°C)", "Mean Temp (°C)"
        ])
        st.session_state.water_vol = 3.0
        st.session_state.page = "phenol_exp1"

def phenol_exp1():
    st.title("Prepare Mixture")
    
    col1, col2 = st.columns(2)
    with col1:
        water = st.number_input(
            "Water volume (ml)", 
            min_value=3.0,
            max_value=36.0,
            value=st.session_state.water_vol,
            step=0.1,
            key="water_input_phenol"
        )
    
    with col2:
        phenol = st.number_input(
            "Phenol volume (ml)",
            min_value=5.0,
            max_value=10.0,
            value=5.0,
            step=0.1,
            key="phenol_input"
        )
    
    if st.button("Heat Mixture"):
        st.session_state.phenol_vol = phenol
        st.session_state.water_vol = water
        st.session_state.page = "phenol_exp2"

def phenol_exp2():
    st.title("Observe Phase Transition")
    
    total = st.session_state.phenol_vol + st.session_state.water_vol
    percent_phenol = (st.session_state.phenol_vol / total) * 100
    
    def calculate_temps(percent_phenol):
        if percent_phenol < 10:
            disappear = 32 + percent_phenol * 3.5
        elif percent_phenol < 30:
            disappear = 65 + (percent_phenol - 10) * 0.25
        elif percent_phenol < 70:
            disappear = 70 - (percent_phenol - 30) * 0.1
        else:
            disappear = 66 - (percent_phenol - 70) * 0.3
        
        reappear = disappear - (2 + percent_phenol * 0.05)
        return disappear, reappear
    
    disappear, reappear = calculate_temps(percent_phenol)
    
    st.markdown(f"""
    **Observations:**
    - Turbidity disappears at: **{disappear:.1f}°C**
    - Upon cooling, turbidity reappears at: **{reappear:.1f}°C**
    """)
    
    if st.button("Record Temperatures"):
        st.session_state.disappear = disappear
        st.session_state.reappear = reappear
        st.session_state.total = total
        st.session_state.page = "phenol_exp3"

def phenol_exp3():
    st.title("Record Data")
    
    percent_phenol = (st.session_state.phenol_vol / st.session_state.total) * 100
    mean_temp = (st.session_state.disappear + st.session_state.reappear) / 2
    
    existing = st.session_state.phenol_data[
        (st.session_state.phenol_data["Phenol (ml)"] == st.session_state.phenol_vol) &
        (st.session_state.phenol_data["Water (ml)"] == st.session_state.water_vol)
    ].empty
    
    if existing:
        new_row = {
            "Phenol (ml)": st.session_state.phenol_vol,
            "Water (ml)": st.session_state.water_vol,
            "% Phenol": percent_phenol,
            "Disappear Temp (°C)": st.session_state.disappear,
            "Reappear Temp (°C)": st.session_state.reappear,
            "Mean Temp (°C)": mean_temp
        }
        st.session_state.phenol_data = pd.concat([
            st.session_state.phenol_data,
            pd.DataFrame([new_row])
        ], ignore_index=True)
    
    st.dataframe(st.session_state.phenol_data.sort_values("% Phenol").style.format("{:.2f}"))
    
    if st.session_state.water_vol < 36:
        if st.button("Add More Water (+2ml)") :
            st.session_state.water_vol = min(st.session_state.water_vol + 2, 36.0)
            st.session_state.page = "phenol_exp1"
    else:
        if st.button("Plot Phase Diagram"):
            st.session_state.page = "phenol_graph"

def phenol_graph():
    import matplotlib.pyplot as plt

    st.title("Phase Diagram: Mean Temperature vs % Phenol")

    df = st.session_state.phenol_data.drop_duplicates().sort_values("% Phenol")

    fig, ax = plt.subplots(figsize=(8, 6))

    # Plot Mean CST Curve
    ax.plot(df["% Phenol"], df["Mean Temp (°C)"], color='black', linewidth=2.5, label="Mean Temperature")

    # Mark CST
    max_temp_idx = df["Mean Temp (°C)"].idxmax()
    cst_temp = df.loc[max_temp_idx, "Mean Temp (°C)"]
    cst_conc = df.loc[max_temp_idx, "% Phenol"]

    ax.plot(cst_conc, cst_temp, 'ro', markersize=8, label="CST Point")
    ax.annotate(
        f"CST = {cst_temp:.1f}°C\nat {cst_conc:.1f}% phenol",
        xy=(cst_conc, cst_temp),
        xytext=(cst_conc + 3, cst_temp + 2),
        arrowprops=dict(arrowstyle='->', color='gray'),
        fontsize=10
    )

    ax.set_xlabel("Phenol Concentration (%)", fontsize=12)
    ax.set_ylabel("Mean Temperature (°C)", fontsize=12)
    ax.set_title("Critical Solution Temperature Determination", fontsize=14)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.legend()

    st.pyplot(fig)

    st.markdown(f"""
    **Results:**
    - Critical Solution Temperature (CST): **{cst_temp:.1f}°C**
    - Phenol Concentration at CST: **{cst_conc:.1f}%**
    """)

    if st.button("Return Home"):
        st.session_state.page = "home"

# --------------------------
# CONDUCTOMETRIC TITRATION
# --------------------------

def cond_intro():
    st.title("Conductometric Titration")
    st.write("**Aim:** Determine strength of HCl and CH₃COOH in mixture")
    if st.button("Start Experiment"):
        st.session_state.cond_data = pd.DataFrame(columns=["NaOH (ml)", "Conductance (mS)"])
        st.session_state.current_naoh = 0.0
        st.session_state.page = "cond_standardize"

def cond_standardize():
    st.title("Standardize NaOH Solution")
    
    naoh_used = st.number_input(
        "Volume of NaOH used (ml)", 
        min_value=0.1, 
        max_value=50.0, 
        value=18.5, 
        step=0.1,
        key="naoh_standardize"
    )
    
    if st.button("Calculate NaOH Normality"):
        oxalic_normality = 0.05
        oxalic_vol = 25.0
        st.session_state.naoh_normality = (oxalic_vol * oxalic_normality) / naoh_used
        st.success(f"NaOH Normality: {st.session_state.naoh_normality:.4f} N")
        
    if st.button("Proceed to Titration"):
        st.session_state.page = "cond_titration"

def cond_titration():
    st.title("Conductometric Titration")
    
    naoh_added = st.number_input(
        "Add NaOH (ml)", 
        min_value=0.0, 
        max_value=8.0, 
        value=float(st.session_state.current_naoh), 
        step=0.2,
        key="naoh_titration"
    )
    
    if naoh_added <= 4.0:
        conductance = 0.8 - 0.02 * (naoh_added / 0.2)
    else:
        conductance = 0.6 + 0.03 * ((naoh_added - 4.0) / 0.2)
    
    if st.button("Record Measurement"):
        if naoh_added not in st.session_state.cond_data["NaOH (ml)"].values:
            new_row = {"NaOH (ml)": naoh_added, "Conductance (mS)": conductance}
            st.session_state.cond_data = pd.concat([st.session_state
