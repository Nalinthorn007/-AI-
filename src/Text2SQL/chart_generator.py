import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List

class ChartGenerator:
    def __init__(self):
        """
        Initialize Chart Generator for creating visualizations
        """
        pass
    
    def create_chart(self, df: pd.DataFrame) -> go.Figure:
        """
        Automatically create the best chart based on data characteristics
        """
        if df.empty:
            return self._create_empty_chart("No data to visualize")
        
        try:
            # Get column types
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
            datetime_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
            
            # Determine best chart type
            if len(datetime_cols) > 0 and len(numeric_cols) > 0:
                # Time series chart
                return self._create_time_series_chart(df, datetime_cols[0], numeric_cols[0])
            elif len(categorical_cols) > 0 and len(numeric_cols) > 0:
                # Bar chart for categorical vs numeric
                return self._create_bar_chart(df, categorical_cols[0], numeric_cols[0])
            elif len(numeric_cols) >= 2:
                # Scatter plot for numeric correlations
                return self._create_scatter_chart(df, numeric_cols[0], numeric_cols[1])
            elif len(categorical_cols) > 0:
                # Pie chart for categorical distribution
                return self._create_pie_chart(df, categorical_cols[0])
            elif len(numeric_cols) > 0:
                # Histogram for numeric distribution
                return self._create_histogram_chart(df, numeric_cols[0])
            else:
                # Default table view
                return self._create_table_chart(df)
                
        except Exception as e:
            return self._create_empty_chart(f"Error creating chart: {str(e)}")
    
    def _create_time_series_chart(self, df: pd.DataFrame, time_col: str, value_col: str) -> go.Figure:
        """Create time series chart"""
        fig = px.line(df, x=time_col, y=value_col, title=f"{value_col} over time")
        fig.update_layout(height=500, xaxis_title=time_col, yaxis_title=value_col)
        return fig
    
    def _create_bar_chart(self, df: pd.DataFrame, cat_col: str, value_col: str) -> go.Figure:
        """Create bar chart"""
        # Group by categorical column and aggregate numeric column
        if value_col in df.columns:
            grouped = df.groupby(cat_col)[value_col].sum().reset_index()
            fig = px.bar(grouped, x=cat_col, y=value_col, title=f"{value_col} by {cat_col}")
        else:
            # Count categorical values
            value_counts = df[cat_col].value_counts().head(20)
            fig = px.bar(x=value_counts.index, y=value_counts.values, title=f"Distribution of {cat_col}")
        
        fig.update_layout(height=500, xaxis_title=cat_col, yaxis_title="Count/Value")
        return fig
    
    def _create_scatter_chart(self, df: pd.DataFrame, x_col: str, y_col: str) -> go.Figure:
        """Create scatter plot"""
        fig = px.scatter(df, x=x_col, y=y_col, title=f"{x_col} vs {y_col}")
        fig.update_layout(height=500, xaxis_title=x_col, yaxis_title=y_col)
        return fig
    
    def _create_pie_chart(self, df: pd.DataFrame, cat_col: str) -> go.Figure:
        """Create pie chart"""
        value_counts = df[cat_col].value_counts().head(10)  # Limit to top 10
        fig = px.pie(values=value_counts.values, names=value_counts.index, title=f"Distribution of {cat_col}")
        fig.update_layout(height=500)
        return fig
    
    def _create_histogram_chart(self, df: pd.DataFrame, num_col: str) -> go.Figure:
        """Create histogram"""
        fig = px.histogram(df, x=num_col, title=f"Distribution of {num_col}")
        fig.update_layout(height=500, xaxis_title=num_col, yaxis_title="Frequency")
        return fig
    
    def _create_table_chart(self, df: pd.DataFrame) -> go.Figure:
        """Create table visualization"""
        fig = go.Figure(data=[go.Table(
            header=dict(values=list(df.columns), fill_color='paleturquoise', align='left'),
            cells=dict(values=[df[col] for col in df.columns], fill_color='lavender', align='left'))
        ])
        fig.update_layout(height=400, title="Data Table")
        return fig
    
    def _create_empty_chart(self, message: str) -> go.Figure:
        """Create empty chart with message"""
        fig = go.Figure()
        fig.add_annotation(
            text=message,
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16, color="gray")
        )
        fig.update_layout(height=400)
        return fig 