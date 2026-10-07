# =============================================================================
# HR Analytics - Employee Attrition EDA
# Dataset : IBM HR Analytics Employee Attrition (Kaggle)
# Author  : Sidhanth Tyagi
# =============================================================================

import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import seaborn as sns

warnings.filterwarnings("ignore")
os.makedirs("plots", exist_ok=True)

# ─── Dark Theme ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.facecolor": "#0f1117",
    "axes.facecolor":   "#1a1d2e",
    "axes.edgecolor":   "#3a3d5c",
    "axes.labelcolor":  "#c9d1d9",
    "xtick.color":      "#8b949e",
    "ytick.color":      "#8b949e",
    "text.color":       "#c9d1d9",
    "grid.color":       "#21262d",
    "grid.linewidth":   0.6,
    "font.family":      "DejaVu Sans",
    "axes.titlesize":   13,
    "axes.labelsize":   11,
    "figure.dpi":       130,
})

PALETTE = {"Yes": "#ff6b6b", "No": "#4ecca3"}
GRAD    = ["#4ecca3", "#45aaf2", "#7c5cbf", "#ff6b6b", "#ffa726", "#26c6da"]

# =============================================================================
# 1. LOAD DATA
# =============================================================================
print("=" * 65)
print("   HR ANALYTICS — EMPLOYEE ATTRITION EDA")
print("=" * 65)

df = pd.read_csv("data/HR_Analytics_Clean.csv")
print(f"\n[OK] Dataset loaded | {df.shape[0]:,} rows × {df.shape[1]} columns")

# =============================================================================
# 2. DATA CLEANING
# =============================================================================
# Drop constant/zero-variance columns if still present in raw file
for col in ["EmployeeCount", "Over18", "StandardHours"]:
    if col in df.columns:
        df.drop(columns=[col], inplace=True)

# Binary target
if "Attrition_Flag" not in df.columns:
    df["Attrition_Flag"] = (df["Attrition"] == "Yes").astype(int)

# Ordinal label mappings (if not already present)
edu_map = {1: "Below College", 2: "College", 3: "Bachelor", 4: "Master", 5: "Doctor"}
sat_map = {1: "Low", 2: "Medium", 3: "High", 4: "Very High"}
wlb_map = {1: "Bad", 2: "Good", 3: "Better", 4: "Best"}

if "EducationLabel" not in df.columns:
    df["EducationLabel"] = df["Education"].map(edu_map)
if "JobSatisfaction_Label" not in df.columns:
    df["JobSatisfaction_Label"] = df["JobSatisfaction"].map(sat_map)
if "EnvironmentSatisfaction_Label" not in df.columns:
    df["EnvironmentSatisfaction_Label"] = df["EnvironmentSatisfaction"].map(sat_map)
if "WorkLifeBalance_Label" not in df.columns:
    df["WorkLifeBalance_Label"] = df["WorkLifeBalance"].map(wlb_map)
if "AgeBand" not in df.columns:
    df["AgeBand"] = pd.cut(
        df["Age"], bins=[17, 25, 35, 45, 55, 65],
        labels=["18-25", "26-35", "36-45", "46-55", "56-65"]
    )
if "IncomeBand" not in df.columns:
    df["IncomeBand"] = pd.cut(
        df["MonthlyIncome"], bins=[0, 3000, 6000, 10000, 20000],
        labels=["Low(<3K)", "Mid(3-6K)", "High(6-10K)", "VHigh(>10K)"]
    )

print(f"[OK] Cleaned  | {df.shape[0]:,} rows × {df.shape[1]} columns\n")

# =============================================================================
# 3. DESCRIPTIVE STATISTICS
# =============================================================================
attr_rate = df["Attrition_Flag"].mean() * 100
print(f"  Overall Attrition Rate : {attr_rate:.2f}%")
print(f"  Total Employees        : {len(df):,}")
print(f"  Employees Who Left     : {df['Attrition_Flag'].sum():,}")
print(f"  Avg Monthly Income     : ${df['MonthlyIncome'].mean():,.0f}")
print(f"  Avg Age                : {df['Age'].mean():.1f} yrs")
print(f"  Avg Tenure             : {df['YearsAtCompany'].mean():.1f} yrs")
print(f"  Overtime Workers       : {(df['OverTime']=='Yes').sum():,} "
      f"({(df['OverTime']=='Yes').mean()*100:.1f}%)\n")

# =============================================================================
# 4. VISUALISATIONS
# =============================================================================

def save(name):
    plt.savefig(f"plots/{name}", bbox_inches="tight", dpi=130, facecolor="#0f1117")
    plt.close()
    print(f"  [OK] plots/{name}")


# ── Plot 1: Attrition Overview ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
fig.suptitle("Attrition Overview", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
counts = df["Attrition"].value_counts()
axes[0].pie(counts, labels=counts.index, autopct="%1.1f%%",
            colors=[PALETTE[k] for k in counts.index], startangle=90,
            wedgeprops={"width": 0.55, "edgecolor": "#0f1117", "linewidth": 2},
            textprops={"color": "#e6edf3", "fontsize": 12})
axes[0].set_title("Attrition Distribution")
dept_attr = (df.groupby("Department")["Attrition_Flag"].mean() * 100).sort_values()
dept_attr.plot(kind="barh", ax=axes[1], color=GRAD[:3], edgecolor="#0f1117")
axes[1].set_title("Attrition Rate by Department (%)")
axes[1].xaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(axes[1].containers[0], fmt="%.1f%%", padding=4, color="#e6edf3")
plt.tight_layout()
save("01_attrition_overview.png")

# ── Plot 2: Demographics ──────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))
fig.suptitle("Demographic Analysis", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
for lbl, grp in df.groupby("Attrition"):
    axes[0].hist(grp["Age"], bins=20, alpha=0.7, label=lbl,
                 color=PALETTE[lbl], edgecolor="#0f1117")
axes[0].set_title("Age Distribution by Attrition")
axes[0].legend()
gender_attr = df.groupby("Gender")["Attrition_Flag"].mean() * 100
bars = axes[1].bar(gender_attr.index, gender_attr.values,
                   color=["#ff8fab", "#74b9ff"], edgecolor="#0f1117")
axes[1].set_title("Attrition Rate by Gender (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(bars, fmt="%.1f%%", padding=4, color="#e6edf3")
ms_attr = (df.groupby("MaritalStatus")["Attrition_Flag"].mean() * 100) \
            .sort_values(ascending=False)
bars2 = axes[2].bar(ms_attr.index, ms_attr.values, color=GRAD, edgecolor="#0f1117")
axes[2].set_title("Attrition Rate by Marital Status (%)")
axes[2].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[2].bar_label(bars2, fmt="%.1f%%", padding=4, color="#e6edf3")
plt.tight_layout()
save("02_demographic_analysis.png")

# ── Plot 3: Job Role & Level ──────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(16, 6))
fig.suptitle("Job Role & Level Analysis", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
role_attr = (df.groupby("JobRole")["Attrition_Flag"].mean() * 100).sort_values()
role_attr.plot(kind="barh", ax=axes[0], color=GRAD, edgecolor="#0f1117")
axes[0].set_title("Attrition Rate by Job Role (%)")
axes[0].xaxis.set_major_formatter(mtick.PercentFormatter())
axes[0].bar_label(axes[0].containers[0], fmt="%.1f%%", padding=4, color="#e6edf3")
level_attr = df.groupby("JobLevel")["Attrition_Flag"].mean() * 100
bars3 = axes[1].bar(level_attr.index.astype(str), level_attr.values,
                    color=GRAD, edgecolor="#0f1117")
axes[1].set_title("Attrition Rate by Job Level (1=Entry → 5=Executive)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(bars3, fmt="%.1f%%", padding=4, color="#e6edf3")
plt.tight_layout()
save("03_job_role_analysis.png")

# ── Plot 4: Compensation ──────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Compensation Analysis", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
for lbl, grp in df.groupby("Attrition"):
    axes[0].hist(grp["MonthlyIncome"], bins=30, alpha=0.7, label=lbl,
                 color=PALETTE[lbl], edgecolor="#0f1117")
axes[0].set_title("Monthly Income Distribution by Attrition")
axes[0].legend()
axes[0].xaxis.set_major_formatter(
    mtick.FuncFormatter(lambda x, _: f"${x:,.0f}"))
inc_attr = df.groupby("IncomeBand")["Attrition_Flag"].mean() * 100
inc_attr.plot(kind="bar", ax=axes[1], color=GRAD, edgecolor="#0f1117", rot=0)
axes[1].set_title("Attrition Rate by Income Band (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(axes[1].containers[0], fmt="%.1f%%", padding=4, color="#e6edf3")
plt.tight_layout()
save("04_compensation_analysis.png")

# ── Plot 5: Satisfaction & WLB ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Satisfaction & Work-Life Balance", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
pivot1 = (df.pivot_table(values="Attrition_Flag", index="JobSatisfaction",
                         columns="OverTime", aggfunc="mean") * 100)
sns.heatmap(pivot1, annot=True, fmt=".1f", cmap="RdYlGn_r",
            ax=axes[0], linewidths=0.5, cbar_kws={"label": "Attrition %"})
axes[0].set_title("Attrition %: Job Satisfaction × OverTime")
wlb = df.groupby("WorkLifeBalance_Label")["Attrition_Flag"].mean() * 100
wlb = wlb.reindex([x for x in ["Bad", "Good", "Better", "Best"] if x in wlb.index])
bars4 = axes[1].bar(wlb.index, wlb.values, color=GRAD, edgecolor="#0f1117")
axes[1].set_title("Attrition Rate by Work-Life Balance")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(bars4, fmt="%.1f%%", padding=4, color="#e6edf3")
plt.tight_layout()
save("05_satisfaction_worklife.png")

# ── Plot 6: OverTime & Travel ─────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))
fig.suptitle("OverTime & Business Travel Impact", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
ot_attr = df.groupby(["OverTime", "Attrition"]).size().unstack()
ot_attr.plot(kind="bar", ax=axes[0], color=list(PALETTE.values()),
             edgecolor="#0f1117", rot=0, width=0.6)
axes[0].set_title("Employee Count: OverTime × Attrition")
axes[0].legend(title="Attrition")
travel_attr = (df.groupby("BusinessTravel")["Attrition_Flag"].mean() * 100) \
               .sort_values(ascending=False)
bars5 = axes[1].bar(travel_attr.index, travel_attr.values,
                    color=GRAD, edgecolor="#0f1117")
axes[1].set_title("Attrition Rate by Business Travel (%)")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
axes[1].bar_label(bars5, fmt="%.1f%%", padding=4, color="#e6edf3")
axes[1].tick_params(axis="x", labelrotation=10)
plt.tight_layout()
save("06_overtime_travel.png")

# ── Plot 7: Tenure ────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(15, 5))
fig.suptitle("Tenure & Experience", fontsize=15, fontweight="bold",
             color="#e6edf3", y=1.02)
for lbl, grp in df.groupby("Attrition"):
    axes[0].hist(grp["YearsAtCompany"], bins=20, alpha=0.7, label=lbl,
                 color=PALETTE[lbl], edgecolor="#0f1117")
axes[0].set_title("Years at Company by Attrition")
axes[0].legend()
ten_attr = df.groupby("YearsAtCompany")["Attrition_Flag"].mean() * 100
axes[1].plot(ten_attr.index, ten_attr.values,
             color="#ff6b6b", linewidth=2, marker="o", markersize=5)
axes[1].fill_between(ten_attr.index, ten_attr.values, alpha=0.2, color="#ff6b6b")
axes[1].set_title("Attrition Rate vs Years at Company")
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter())
plt.tight_layout()
save("07_tenure_experience.png")

# ── Plot 8: Correlation Heatmap ───────────────────────────────────────────────
num_features = [
    "Age", "DailyRate", "DistanceFromHome", "Education",
    "EnvironmentSatisfaction", "HourlyRate", "JobInvolvement", "JobLevel",
    "JobSatisfaction", "MonthlyIncome", "MonthlyRate", "NumCompaniesWorked",
    "PercentSalaryHike", "RelationshipSatisfaction", "StockOptionLevel",
    "TotalWorkingYears", "TrainingTimesLastYear", "WorkLifeBalance",
    "YearsAtCompany", "YearsInCurrentRole", "YearsSinceLastPromotion",
    "YearsWithCurrManager", "Attrition_Flag"
]
corr = df[num_features].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
fig, ax = plt.subplots(figsize=(14, 10))
fig.suptitle("Feature Correlation Matrix", fontsize=15, fontweight="bold",
             color="#e6edf3")
sns.heatmap(corr, mask=mask, annot=False, cmap="coolwarm", center=0,
            ax=ax, linewidths=0.3, vmin=-1, vmax=1)
plt.tight_layout()
save("08_correlation_heatmap.png")

# ── Plot 9: Attrition Risk Factors ───────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 7))
fig.suptitle("Top Factors Correlated with Attrition", fontsize=15,
             fontweight="bold", color="#e6edf3")
attr_corr = corr["Attrition_Flag"].drop("Attrition_Flag").sort_values()
colors_bar = ["#ff6b6b" if v > 0 else "#4ecca3" for v in attr_corr]
attr_corr.plot(kind="barh", ax=ax, color=colors_bar, edgecolor="#0f1117")
ax.axvline(0, color="#8b949e", linewidth=1, linestyle="--")
ax.set_title("Correlation with Attrition  (Red = Risk Driver)")
ax.set_xlabel("Pearson Correlation Coefficient")
plt.tight_layout()
save("09_attrition_risk_factors.png")

# ── Plot 10: Age × Income Heatmap ────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 5))
fig.suptitle("Attrition % — Age Band × Income Band", fontsize=15,
             fontweight="bold", color="#e6edf3")
pivot2 = (df.pivot_table(values="Attrition_Flag", index="AgeBand",
                         columns="IncomeBand", aggfunc="mean") * 100)
sns.heatmap(pivot2, annot=True, fmt=".1f", cmap="YlOrRd",
            ax=ax, linewidths=0.5, cbar_kws={"label": "Attrition %"})
plt.tight_layout()
save("10_age_income_heatmap.png")

# =============================================================================
# 5. KEY INSIGHTS
# =============================================================================
print("\n" + "=" * 65)
print("   KEY BUSINESS INSIGHTS")
print("=" * 65)
ot_yes  = df[df["OverTime"] == "Yes"]["Attrition_Flag"].mean() * 100
ot_no   = df[df["OverTime"] == "No"]["Attrition_Flag"].mean() * 100
q1_inc  = df["MonthlyIncome"].quantile(0.25)

rows = [
    ("Overall Attrition Rate",          f"{attr_rate:.1f}%",
     "Above 15% industry avg — action needed"),
    ("Overtime Attrition",              f"{ot_yes:.1f}%",
     f"vs {ot_no:.1f}% non-OT  →  3× higher risk"),
    ("Single Employee Attrition",
     f"{df[df['MaritalStatus']=='Single']['Attrition_Flag'].mean()*100:.1f}%",
     "Singles leave more — fewer personal commitments"),
    ("Low Income (<Q1) Attrition",
     f"{df[df['MonthlyIncome']<=q1_inc]['Attrition_Flag'].mean()*100:.1f}%",
     f"Salary < ${q1_inc:,.0f}/mo is a retention risk"),
    ("New Hire Attrition (≤ 1 yr)",
     f"{df[df['YearsAtCompany']<=1]['Attrition_Flag'].mean()*100:.1f}%",
     "Onboarding & early engagement critical"),
    ("Sales Executive Attrition",
     f"{df[df['JobRole']=='Sales Executive']['Attrition_Flag'].mean()*100:.1f}%",
     "Highest role-level attrition"),
    ("Frequent Traveller Attrition",
     f"{df[df['BusinessTravel']=='Travel_Frequently']['Attrition_Flag'].mean()*100:.1f}%",
     "Travel fatigue — work-life imbalance"),
]

print(f"\n  {'INSIGHT':<38} {'VALUE':<12} COMMENT")
print("  " + "-" * 85)
for name, val, comment in rows:
    print(f"  {name:<38} {val:<12} {comment}")

print("\n\n[DONE] All 10 plots saved in /plots  |  EDA complete!\n")
