"""
Telecom Customer Churn Analysis
Author: Himanshu Kothari
Dataset: IBM Watson Telco Customer Churn (Kaggle)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# ── 1. LOAD & CLEAN ───────────────────────────────────────
df = pd.read_csv('WA_Fn-UseC_-Telco-Customer-Churn.csv')
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'].fillna(df['TotalCharges'].median(), inplace=True)
df['Churn_Binary'] = (df['Churn'] == 'Yes').astype(int)

print("=" * 58)
print("  TELECOM CUSTOMER CHURN ANALYSIS")
print("=" * 58)
print(f"\n  Total Customers : {len(df):,}")
print(f"  Churned         : {df['Churn_Binary'].sum():,} ({df['Churn_Binary'].mean():.1%})")
print(f"  Retained        : {(df['Churn_Binary']==0).sum():,}")
print(f"  Avg Tenure      : {df['tenure'].mean():.1f} months")
print(f"  Avg Monthly Bill: ₹{df['MonthlyCharges'].mean():.2f}")

# ── 2. BUSINESS INSIGHTS ──────────────────────────────────
print("\n  CHURN RATE BY CONTRACT TYPE:")
ct = df.groupby('Contract')['Churn_Binary'].mean().sort_values(ascending=False)
for k,v in ct.items(): print(f"    {k:20s} → {v:.1%}")

print("\n  CHURN RATE BY INTERNET SERVICE:")
it = df.groupby('InternetService')['Churn_Binary'].mean().sort_values(ascending=False)
for k,v in it.items(): print(f"    {k:20s} → {v:.1%}")

churn_monthly = df.groupby('Churn')['MonthlyCharges'].mean()
print(f"\n  Avg Monthly Charges — Churned: ${churn_monthly['Yes']:.2f} | Retained: ${churn_monthly['No']:.2f}")

# ── 3. MODEL ──────────────────────────────────────────────
encode_cols = ['gender','Partner','Dependents','PhoneService','MultipleLines',
               'InternetService','OnlineSecurity','OnlineBackup','DeviceProtection',
               'TechSupport','StreamingTV','StreamingMovies','Contract',
               'PaperlessBilling','PaymentMethod']

df_model = df.copy()
le = LabelEncoder()
for col in encode_cols:
    df_model[col] = le.fit_transform(df_model[col])

features = ['tenure','MonthlyCharges','TotalCharges','Contract','InternetService',
            'OnlineSecurity','TechSupport','PaymentMethod','PaperlessBilling',
            'SeniorCitizen','Partner','Dependents','MultipleLines']
X = df_model[features]
y = df_model['Churn_Binary']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
model = RandomForestClassifier(n_estimators=100, random_state=42, class_weight='balanced')
model.fit(X_train, y_train)
y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)[:,1]

print(f"\n  MODEL PERFORMANCE:")
print(f"    ROC-AUC Score : {roc_auc_score(y_test, y_prob):.3f}")
rpt = classification_report(y_test, y_pred, output_dict=True)
print(f"    Precision (Churn): {rpt['1']['precision']:.2f}")
print(f"    Recall (Churn)   : {rpt['1']['recall']:.2f}")
print(f"    F1-Score (Churn) : {rpt['1']['f1-score']:.2f}")

feat_imp = pd.Series(model.feature_importances_, index=features).sort_values(ascending=False)

# ── 4. DASHBOARD ──────────────────────────────────────────
plt.style.use('seaborn-v0_8-whitegrid')
BLUE = '#1a56db'; RED = '#e02424'; GRAY = '#6b7280'
BG = '#f9fafb'

fig = plt.figure(figsize=(20, 15))
fig.patch.set_facecolor(BG)
gs = gridspec.GridSpec(3, 3, figure=fig, hspace=0.45, wspace=0.35)

# Plot 1: Churn distribution donut
ax1 = fig.add_subplot(gs[0, 0])
sizes = [df['Churn_Binary'].sum(), (df['Churn_Binary']==0).sum()]
wedge_props = {'width': 0.5, 'edgecolor': 'white', 'linewidth': 3}
ax1.pie(sizes, labels=['Churned','Retained'], colors=[RED, BLUE],
        autopct='%1.1f%%', startangle=90, wedgeprops=wedge_props,
        textprops={'fontsize':11})
ax1.set_title('Overall Churn Rate', fontsize=13, fontweight='bold', pad=12)

# Plot 2: Churn by Contract
ax2 = fig.add_subplot(gs[0, 1])
contract_churn = df.groupby('Contract')['Churn_Binary'].mean() * 100
bars = ax2.bar(contract_churn.index, contract_churn.values,
               color=[RED if v > 30 else BLUE for v in contract_churn.values],
               edgecolor='white', linewidth=1.5, width=0.6)
ax2.bar_label(bars, fmt='%.1f%%', padding=3, fontsize=10)
ax2.set_title('Churn Rate by Contract Type', fontsize=13, fontweight='bold', pad=12)
ax2.set_ylabel('Churn Rate (%)')
ax2.tick_params(axis='x', rotation=15)
ax2.set_ylim(0, contract_churn.max() * 1.25)

# Plot 3: Churn by Internet Service
ax3 = fig.add_subplot(gs[0, 2])
int_churn = df.groupby('InternetService')['Churn_Binary'].mean() * 100
bars3 = ax3.bar(int_churn.index, int_churn.values,
                color=[RED if v > 30 else BLUE for v in int_churn.values],
                edgecolor='white', linewidth=1.5, width=0.6)
ax3.bar_label(bars3, fmt='%.1f%%', padding=3, fontsize=10)
ax3.set_title('Churn Rate by Internet Service', fontsize=13, fontweight='bold', pad=12)
ax3.set_ylabel('Churn Rate (%)')
ax3.set_ylim(0, int_churn.max() * 1.25)

# Plot 4: Tenure distribution churn vs retained
ax4 = fig.add_subplot(gs[1, :2])
churned = df[df['Churn']=='Yes']['tenure']
retained = df[df['Churn']=='No']['tenure']
ax4.hist(retained, bins=30, alpha=0.7, color=BLUE, label='Retained', edgecolor='white')
ax4.hist(churned, bins=30, alpha=0.7, color=RED, label='Churned', edgecolor='white')
ax4.axvline(churned.mean(), color=RED, linestyle='--', linewidth=2, label=f'Churned Avg: {churned.mean():.0f}mo')
ax4.axvline(retained.mean(), color=BLUE, linestyle='--', linewidth=2, label=f'Retained Avg: {retained.mean():.0f}mo')
ax4.set_title('Tenure Distribution: Churned vs Retained', fontsize=13, fontweight='bold', pad=12)
ax4.set_xlabel('Tenure (months)')
ax4.set_ylabel('Number of Customers')
ax4.legend(fontsize=9)

# Plot 5: Monthly charges boxplot
ax5 = fig.add_subplot(gs[1, 2])
churn_groups = [df[df['Churn']=='No']['MonthlyCharges'], df[df['Churn']=='Yes']['MonthlyCharges']]
bp = ax5.boxplot(churn_groups, patch_artist=True, labels=['Retained','Churned'],
                 medianprops={'color':'white','linewidth':2.5})
bp['boxes'][0].set_facecolor(BLUE)
bp['boxes'][1].set_facecolor(RED)
ax5.set_title('Monthly Charges\nRetained vs Churned', fontsize=13, fontweight='bold', pad=12)
ax5.set_ylabel('Monthly Charges ($)')

# Plot 6: Feature importance
ax6 = fig.add_subplot(gs[2, :2])
top_feat = feat_imp.head(10)
colors_fi = [RED if i < 3 else BLUE for i in range(len(top_feat))]
top_feat.sort_values().plot(kind='barh', ax=ax6, color=colors_fi[::-1], edgecolor='white')
ax6.set_title('Top 10 Churn Predictors (Random Forest Feature Importance)', fontsize=13, fontweight='bold', pad=12)
ax6.set_xlabel('Importance Score')

# Plot 7: Confusion matrix
ax7 = fig.add_subplot(gs[2, 2])
cm = confusion_matrix(y_test, y_pred)
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', ax=ax7,
            xticklabels=['Retained','Churned'], yticklabels=['Retained','Churned'],
            linewidths=2, linecolor='white', cbar=False,
            annot_kws={'size':13, 'weight':'bold'})
ax7.set_title(f'Confusion Matrix\n(ROC-AUC: {roc_auc_score(y_test, y_prob):.3f})', fontsize=13, fontweight='bold', pad=12)
ax7.set_ylabel('Actual')
ax7.set_xlabel('Predicted')

fig.suptitle('Telecom Customer Churn Analysis Dashboard\nHimanshu Kothari | IBM Watson Dataset | 7,043 Customers',
             fontsize=16, fontweight='bold', y=0.99, color='#111827')

plt.savefig('churn_dashboard.png', dpi=150, bbox_inches='tight', facecolor=BG)
print("\n  Dashboard saved.")
