from __future__ import annotations
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

FONT_FAMILY = "Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, Helvetica Neue, Arial, Noto Sans, sans-serif"
FONT_CONFIG = {"family": FONT_FAMILY, "size": 13, "color": "#0f172a"}


def _apply_font(fig):
    fig.update_layout(font=FONT_CONFIG)
    fig.update_xaxes(title_font=FONT_CONFIG, tickfont=FONT_CONFIG)
    fig.update_yaxes(title_font=FONT_CONFIG, tickfont=FONT_CONFIG)
    return fig


def grouped_bar(df, x, y, color, title, height=420):
    fig = px.bar(df, x=x, y=y, color=color, barmode="group", title=title, template="plotly_white", height=height)
    fig.update_layout(legend_title_text="", margin=dict(l=20, r=20, t=60, b=20))
    return _apply_font(fig)


def histogram_compare(baseline_values, compare_values, column, height=420, title=None, y_title="Density"):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=baseline_values, name="Version 1", opacity=0.65, histnorm="probability density"))
    fig.add_trace(go.Histogram(x=compare_values, name="Version 2", opacity=0.65, histnorm="probability density"))
    fig.update_layout(barmode="overlay", template="plotly_white", title=title or f"Distribution of {column}", xaxis_title=column, yaxis_title=y_title, height=height, margin=dict(l=20, r=20, t=60, b=20))
    return _apply_font(fig)


def box_compare(df, value_column, version_column, column, height=420, title=None):
    fig = px.box(df, x=version_column, y=value_column, title=title or f"Comparative boxplot of {column}", template="plotly_white", points="outliers", height=height)
    fig.update_layout(margin=dict(l=20, r=20, t=60, b=20))
    return _apply_font(fig)


def categorical_compare(df, value_column, share_column, version_column, column, height=420, title=None, y_title="Relative share", x_title="Category"):
    fig = px.bar(df, x=value_column, y=share_column, color=version_column, barmode="group", title=title or f"Categorical breakdown of {column}", template="plotly_white", height=height)
    fig.update_layout(yaxis_title=y_title, xaxis_title=x_title, legend_title_text="", margin=dict(l=20, r=20, t=60, b=20))
    return _apply_font(fig)
