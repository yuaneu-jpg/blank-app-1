import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(
    page_title="Antibiotic Effectiveness Dashboard",
    layout="wide"
)

st.title("The Importance of Factoring in MIC when Prescribing Broad-Spec Antibiotics")

st.markdown(
    """
    This dashboard explores the minimum inhibitory concentration (MIC) of three broad-spectrum antibiotics: 
    Penicillin, Streptomycin, and Neomycin across multiple species of bacterium. A lower MIC means an antibiotic is more effective because 
    it takes less concentration to inihibit bacterial growth. Hence knowing and visualizing which antibiotic would be
    most effective (lowest MIC) is an imperative factor in every patient case.
    """
)

url = "https://cdn.jsdelivr.net/npm/vega-datasets@1/data/burtin.json"
df = pd.read_json(url)

df_long = df.melt(
    id_vars=["Bacteria", "Gram_Staining", "Genus"],
    value_vars=["Penicillin", "Streptomycin", "Neomycin"],
    var_name="Antibiotic",
    value_name="MIC"
)

df_avg = df_long.groupby("Antibiotic", as_index=False)["MIC"].mean()
df_avg = df_avg.sort_values("MIC", ascending=False)

st.subheader("Average MIC Summary")

cols = st.columns(3)

for i, row in enumerate(df_avg.itertuples()):
    cols[i].metric(
        label=row.Antibiotic,
        value=f"{row.MIC:.2f}"
    )

st.markdown(
    """
    Penicillin has the highest average MIC in this dataset, meaning it often requires a much higher 
    concentration to inhibit bacterial growth. However, this does not necessarily mean Penicillin is useless, but it does show 
    that its effectiveness is unevenly distibuted across bacterial species, especially when compared with Neomycin and 
    Streptomycin.

    As doctors facing an ever-relevant issue of antibiotic-resistant super bugs, we might have to take into consideration which antibiotic should be
    prescribed to minimize the dosage used. The more contact realized inside the body of a patient, the higher
    the likelihood of antibiotic resistance. This visualization explores the unique intersections of the 3 most
    popular broad-spec antibiotics and the most commonly met bacterial diseases.

    This interactive narrative begins with a broad summary: a bar chart with average MIC by antibiotic. Then it narrows into the full heatmap, 
    where each bacterial species can be compared across all three antibiotics. Click a bar or a heatmap cell 
    to highlight one antibiotic across the visualization. Hover over the heatmap to inspect individual MIC values.
    """
)

antibiotic_click = alt.selection_point(
    fields=["Antibiotic"],
    empty=True
)


cell_hover = alt.selection_point(
    fields=["Bacteria", "Antibiotic"],
    on="mouseover",
    clear="mouseout",
    empty=False
)

bar_chart = alt.Chart(df_avg).mark_bar(size=90).encode(
    x=alt.X(
        "Antibiotic:N",
        title="Click an antibiotic to highlight",
        sort="-y",
        scale=alt.Scale(padding=0.35)
    ),
    y=alt.Y(
        "MIC:Q",
        title="Average MIC"
    ),
    color=alt.condition(
        antibiotic_click,
        alt.Color("Antibiotic:N", legend=None),
        alt.value("lightgray")
    ),
    opacity=alt.condition(
        antibiotic_click,
        alt.value(1),
        alt.value(0.35)
    ),
    tooltip=[
        "Antibiotic:N",
        alt.Tooltip("MIC:Q", title="Average MIC", format=".2f")
    ]
).add_params(
    antibiotic_click
).properties(
    width=700,
    height=280,
    title="Penicillin has the Highest MIC across the most Common Bacterial Diseases"
)

heatmap_base = alt.Chart(df_long).mark_rect(
    stroke="white",
    strokeWidth=1
).encode(
    x=alt.X("Antibiotic:N", title="Antibiotic"),
    y=alt.Y(
        "Bacteria:N",
        title="Bacterial Species",
        sort=alt.EncodingSortField(field="MIC", op="mean", order="descending")
    ),
    color=alt.Color(
        "MIC:Q",
        scale=alt.Scale(type="log", scheme="orangered"),
        title="MIC Lower = More Effective"
    ),
    opacity=alt.condition(
        antibiotic_click,
        alt.value(1),
        alt.value(0.2)
    ),
    tooltip=[
        "Bacteria:N",
        "Gram_Staining:N",
        "Antibiotic:N",
        alt.Tooltip("MIC:Q", title="MIC")
    ]
)

hover_outline = alt.Chart(df_long).mark_rect(
    fill=None,
    stroke="black",
    strokeWidth=3
).encode(
    x="Antibiotic:N",
    y=alt.Y(
        "Bacteria:N",
        sort=alt.EncodingSortField(field="MIC", op="mean", order="descending")
    ),
    opacity=alt.condition(
        cell_hover,
        alt.value(1),
        alt.value(0)
    )
)

heatmap = (
    heatmap_base + hover_outline
).add_params(
    antibiotic_click,
    cell_hover
).properties(
    width=700,
    height=520,
    title="But the Story is Actually Much More Complicated"
)

final_chart = alt.vconcat(
    bar_chart,
    heatmap
).resolve_scale(
    color="independent"
)

st.altair_chart(final_chart, use_container_width=False)
