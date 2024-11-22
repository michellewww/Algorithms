import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load CSV data into a DataFrame
df = pd.read_csv("households.csv")

# Visualization 1: Distribution of Household Types
def plot_household_types(data):
    household_type_counts = data.groupby("Household ID")["Household Type"].first().value_counts()
    household_type_counts.plot(kind="bar", color="skyblue", figsize=(10, 6))
    plt.title("Distribution of Household Types", fontsize=16)
    plt.xlabel("Household Type", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

# Visualization 2: Distribution of Household Sizes
def plot_household_sizes(data):
    household_sizes = data.groupby("Household ID").size()
    household_sizes.value_counts().sort_index().plot(kind="bar", color="lightcoral", figsize=(10, 6))
    plt.title("Distribution of Household Sizes", fontsize=16)
    plt.xlabel("Number of People in Household", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

# Visualization 3: Age Distribution by Role
def plot_age_by_role(data):
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=data, x="Position in Household", y="Age", palette="Set2")
    plt.title("Age Distribution by Role in Household", fontsize=16)
    plt.xlabel("Position in Household", fontsize=14)
    plt.ylabel("Age", fontsize=14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

# Visualization 4: Gender Distribution by Role
def plot_gender_by_role(data):
    gender_role_distribution = data.groupby(["Position in Household", "Sex"]).size().unstack(fill_value=0)
    gender_role_distribution.plot(kind="bar", stacked=True, figsize=(12, 6), colormap="coolwarm")
    plt.title("Gender Distribution by Role in Household", fontsize=16)
    plt.xlabel("Position in Household", fontsize=14)
    plt.ylabel("Count", fontsize=14)
    plt.xticks(rotation=0, fontsize=12)
    plt.yticks(fontsize=12)
    plt.legend(["Male", "Female"], title="Sex", fontsize=12)
    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.show()

# Generate Plots
plot_household_types(df)
plot_household_sizes(df)
plot_age_by_role(df)
plot_gender_by_role(df)
