"""
Plots the Relative Brand Momentum Index (2015=100) for five brands
sourced from Perfume_Brand_Landscape_2026.pdf, Figure 1.
"""
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

years = [2015, 2016, 2018, 2020, 2022, 2024, 2026]

brands = {
    "Christian Dior": [100, 105, 118, 135, 155, 175, 195],
    "CHANEL":         [100, 108, 130, 160, 190, 220, 245],
    "YSL":            [100, 106, 120, 140, 165, 190, 210],
    "Marc Jacobs":    [100, 103, 110, 118, 128, 138, 148],
    "Tom Ford":       [100, 107, 125, 150, 175, 205, 230],
}

colors = {
    "Christian Dior": "#1a1a2e",
    "CHANEL":         "#c9a84c",
    "YSL":            "#8b0000",
    "Marc Jacobs":    "#4a90d9",
    "Tom Ford":       "#2d6a4f",
}

markers = {
    "Christian Dior": "o",
    "CHANEL":         "s",
    "YSL":            "^",
    "Marc Jacobs":    "D",
    "Tom Ford":       "P",
}

fig, ax = plt.subplots(figsize=(11, 6))
fig.patch.set_facecolor("#fafafa")
ax.set_facecolor("#fafafa")

for brand, values in brands.items():
    ax.plot(years, values, color=colors[brand], marker=markers[brand],
            linewidth=2.2, markersize=7, label=brand)
    ax.annotate(f"{values[-1]}",
                xy=(2026, values[-1]),
                xytext=(4, 0), textcoords="offset points",
                va="center", fontsize=9, color=colors[brand], fontweight="bold")

ax.axhline(100, color="#aaaaaa", linewidth=0.8, linestyle="--")
ax.set_xlim(2014.5, 2027.5)
ax.set_ylim(85, 265)
ax.set_xticks(years)
ax.yaxis.set_minor_locator(ticker.MultipleLocator(10))
ax.grid(axis="y", which="major", linestyle="--", linewidth=0.5, alpha=0.6)
ax.grid(axis="y", which="minor", linestyle=":", linewidth=0.3, alpha=0.4)

ax.set_title("Relative Brand Momentum Index — Perfume (2015 = 100)",
             fontsize=14, fontweight="bold", pad=14)
ax.set_xlabel("Year", fontsize=11)
ax.set_ylabel("Brand Momentum Index (2015 = 100)", fontsize=11)
ax.legend(loc="upper left", framealpha=0.9, fontsize=10)

note = ("Source: Perfume_Brand_Landscape_2026.pdf, Fig. 1  |  "
        "Index measures brand buzz/positioning, NOT revenue.  |  Values are illustrative.")
fig.text(0.5, -0.02, note, ha="center", fontsize=8, color="#666666")

plt.tight_layout()
plt.savefig("brand_momentum_index.png", dpi=150, bbox_inches="tight")
print("Saved: brand_momentum_index.png")
