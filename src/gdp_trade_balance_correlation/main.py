import importlib.resources

import pandas as pd
import plotly.express as px
import plotly.io as pio
import statsmodels.api as sm
import streamlit as st
from dbnomics import fetch_series
from streamlit_option_menu import option_menu


def main() -> None:
    # Set plot theme
    pio.templates.default = "plotly_dark"

    # GDP growth rate series
    gdp_series = {
        "USA": "IMF/WEO:2024-04/USA.NGDP_RPCH.pcent_change",
        "China": "IMF/WEO:2024-04/CHN.NGDP_RPCH.pcent_change",
        "Japan": "IMF/WEO:2024-04/JPN.NGDP_RPCH.pcent_change",
        "UK": "IMF/WEO:2024-04/GBR.NGDP_RPCH.pcent_change",
        "France": "IMF/WEO:2024-04/FRA.NGDP_RPCH.pcent_change",
        "Germany": "IMF/WEO:2024-04/DEU.NGDP_RPCH.pcent_change",
    }

    # Trade balance series
    tb_series = {
        "USA": "CEPII/CHELEM-TRADE-INDIC/USA.BALGDP.TOTAL.TTGS",
        "China": "CEPII/CHELEM-TRADE-INDIC/CHN.BALGDP.TOTAL.TTGS",
        "Japan": "CEPII/CHELEM-TRADE-INDIC/JPN.BALGDP.TOTAL.TTGS",
        "UK": "CEPII/CHELEM-TRADE-INDIC/GBR.BALGDP.TOTAL.TTGS",
        "France": "CEPII/CHELEM-TRADE-INDIC/FRA.BALGDP.TOTAL.TTGS",
        "Germany": "CEPII/CHELEM-TRADE-INDIC/DEU.BALGDP.TOTAL.TTGS",
    }

    # Function to fetch and prepare data for a specific series
    def fetch_and_prepare_data(series_dict, col_name):
        dfs = []
        for country, series_code in series_dict.items():
            df = fetch_series(series_code)
            if not df.empty:
                df = df.rename(
                    columns={"original_period": "Date", "original_value": col_name}
                )
                df["Country"] = country
                dfs.append(df)
        return pd.concat(dfs)

    # Streamlit interface
    package_dir = importlib.resources.files("gdp_trade_balance_correlation")
    st.set_page_config(
        page_title="GDP Trade Balance Correlation",
        page_icon=str(package_dir / "images/favicon.png"),
    )
    st.image(str(package_dir / "images/dbnomics.svg"), width=300)
    st.title(":blue[GDP Trade Balance Correlation]")

    def local_css(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    local_css(package_dir / "assets/styles.css")

    st.markdown(
        """
        <style>
        hr {
            height: 1px;
            border: none;
            color: #333;
            background-color: #333;
            margin-top: 3px;
            margin-bottom: 3px;
        }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    with st.sidebar:
        selected = option_menu(
            menu_title="Menu",
            options=[
                "GDP Growth Rate & Trade Balance",
                "Regression Analysis",
                "Sources",
            ],
            icons=["bar-chart", "book", "search"],
            menu_icon=":",
            default_index=0,
        )

    # Select countries for analysis
    if selected == "GDP Growth Rate & Trade Balance":
        selected_countries = st.multiselect(
            "Select countries to analyze",
            list(gdp_series.keys()),
            default=list(gdp_series.keys()),
        )

        # Fetch and prepare GDP data
        df_gdp_all = fetch_and_prepare_data(
            {country: gdp_series[country] for country in selected_countries},
            "GDP Growth Rate (%)",
        )

        # Fetch and prepare Trade Balance data
        df_tb_all = fetch_and_prepare_data(
            {country: tb_series[country] for country in selected_countries},
            "Trade Balance (% of GDP)",
        )

        # Display charts
        if df_gdp_all.empty or df_tb_all.empty:
            st.warning("No data available for the selected countries.")
        else:
            st.subheader("GDP Growth Rate (%)")
            st.link_button(
                ":blue[*GDP definition*]",
                "https://en.wikipedia.org/wiki/Gross_domestic_product",
            )
            fig_gdp = px.line(
                df_gdp_all,
                x="Date",
                y="GDP Growth Rate (%)",
                color="Country",
                labels={
                    "Date": "Date",
                    "GDP Growth Rate (%)": "GDP Growth Rate (%)",
                    "Country": "Country",
                },
                title="GDP Growth Rate Over Time",
                template="plotly_dark",
                hover_data={"GDP Growth Rate (%)": ":,.2f", "Date": False},
            )

            fig_gdp.update_traces(
                mode="lines+markers", line=dict(width=2), marker=dict(size=6)
            )

            fig_gdp.update_layout(
                xaxis=dict(title="Date", showgrid=True, title_standoff=15),
                yaxis=dict(
                    title="GDP Growth Rate (%)", showgrid=True, title_standoff=15
                ),
                legend=dict(
                    title=None,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                margin=dict(l=50, r=20, t=70, b=50),
            )

            st.plotly_chart(fig_gdp)

            st.subheader("Trade Balance (% of GDP)")
            st.link_button(
                ":blue[*Trade Balance definition*]",
                "https://en.wikipedia.org/wiki/Balance_of_trade",
            )
            fig_tb = px.line(
                df_tb_all,
                x="Date",
                y="Trade Balance (% of GDP)",
                color="Country",
                labels={
                    "Date": "Date",
                    "Trade Balance (% of GDP)": "Trade Balance (% of GDP)",
                    "Country": "Country",
                },
                title="Trade Balance Over Time",
                template="plotly_dark",
                hover_data={"Trade Balance (% of GDP)": ":,.2f", "Date": False},
            )

            fig_tb.update_traces(
                mode="lines+markers", line=dict(width=2), marker=dict(size=6)
            )

            fig_tb.update_layout(
                xaxis=dict(title="Date", showgrid=True, title_standoff=15),
                yaxis=dict(
                    title="Trade Balance (% of GDP)", showgrid=True, title_standoff=15
                ),
                legend=dict(
                    title=None,
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                ),
                margin=dict(l=50, r=20, t=70, b=50),
            )

            st.plotly_chart(fig_tb)
    if selected == "Regression Analysis":
        selected_countries = st.multiselect(
            "Select countries to analyze",
            list(gdp_series.keys()),
            default=list(gdp_series.keys()),
        )
        tab1, tab2, tab3 = st.tabs(
            ["Correlation Analysis", "Regressions Results", "Explanations"]
        )
        with tab1:
            df_gdp_all = fetch_and_prepare_data(
                {country: gdp_series[country] for country in selected_countries},
                "GDP Growth Rate (%)",
            )
            # Fetch and prepare Trade Balance data
            df_tb_all = fetch_and_prepare_data(
                {country: tb_series[country] for country in selected_countries},
                "Trade Balance (% of GDP)",
            )
            # Calculate correlation between GDP Growth Rate and Trade Balance
            correlation_df = pd.merge(
                df_gdp_all, df_tb_all, on=["Country", "Date"], suffixes=("_gdp", "_tb")
            )
            correlations = (
                correlation_df.groupby("Country")[
                    ["GDP Growth Rate (%)", "Trade Balance (% of GDP)"]
                ]
                .corr()
                .iloc[0::2]["Trade Balance (% of GDP)"]
            )

            st.subheader("Correlation Analysis")
            st.write(
                "The correlation between two variables, GDP growth rate (X) and trade balance (% of GDP) (Y), is measured "
                "using Pearson's correlation coefficient :"
            )
            for country in selected_countries:
                corr_value = correlations.loc[country].iloc[
                    0
                ]  # Access the numeric value
                st.write(f"{country}: {corr_value:.2f}")
            st.link_button(
                ":blue[*Pearson's coefficient definition*]",
                "https://en.wikipedia.org/wiki/Pearson_correlation_coefficient",
            )
            st.markdown(
                "\n"
                "                ### Interpretation of Correlation Coefficients:\n"
                "- **Positive Correlation (0.5 to 1.0)**: Indicates that higher GDP growth rate tends to be "
                "associated with a larger trade surplus relative to GDP. This suggests that economic expansion may "
                "lead to increased exports relative to imports.\n"
                "- **Negative Correlation (-0.5 to -1.0)**: Indicates that higher GDP growth rate tends to be "
                "associated with a larger trade deficit relative to GDP. This could imply that economic growth drives "
                "up imports faster than exports.\n"
                "- **Weak or No Correlation (around 0)**: Indicates that GDP growth rate and trade balance do not "
                "have a strong linear relationship."
            )

            # Regression Analysis
        with tab2:
            st.subheader(
                "Regression Analysis: GDP Growth Rate vs. Trade Balance (% of GDP)"
            )
            st.write(
                "Linear regression is used to model the linear relationship between a dependent variable (Y, trade balance % "
                "of GDP) and one or more independent variables (X, GDP growth rate)."
            )
            st.link_button(
                ":blue[*Regression analysis definition*]",
                "https://en.wikipedia.org/wiki/Regression_analysis",
            )
            for country in selected_countries:
                df_country = correlation_df[correlation_df["Country"] == country]
                X = df_country["GDP Growth Rate (%)"]
                y = df_country["Trade Balance (% of GDP)"]

                X = sm.add_constant(X)  # Add intercept term
                model = sm.OLS(y, X).fit()

                # Display results
                st.write(f"**{country}**")
                st.write(model.summary())
        with tab3:
            st.markdown(
                "\n"
                "    ### Interpretation of Regression Results:\n"
                "- **Coefficient (coef)**: This represents the slope of the regression line. A positive coefficient "
                "indicates "
                "that as the GDP growth rate increases, the trade balance (% of GDP) tends to increase as well. "
                "Conversely "
                "a negative coefficient would indicate an inverse relationship, where an increase in GDP growth rate "
                "corresponds to a decrease in trade balance (% of GDP).\n"
                "- **Intercept (const)**: This is the value of the trade balance (% of GDP) when the GDP growth rate "
                "is zero. "
                "It provides a baseline level of trade balance, giving an idea of the trade balance independent of "
                "GDP growth fluctuations.\n"
                "- **R-squared**: This value represents the proportion of the variance in the trade balance (% of "
                "GDP) that can "
                "be explained by the GDP growth rate. An R-squared closer to 1 indicates a strong relationship, "
                "where most of "
                "the variance in trade balance is accounted for by GDP growth rate, while a value closer to 0 "
                "suggests a weak relationship.\n"
                "- **P-value (P>|t|)**: This value assesses the statistical significance of each coefficient. A "
                "P-value less than "
                "0.05 typically indicates that the coefficient is significantly different from zero, implying that "
                "there is a "
                "statistically significant relationship between GDP growth rate and trade balance (% of GDP).\n"
                "\n"
                "### Economic Dynamics:\n"
                "The correlation between GDP and the trade balance reflects complex economic dynamics influenced by "
                "multiple factors. As observed in the analysis based on data from several countries including the "
                "United States, China, Japan, the United Kingdom, France, and Germany, GDP growth rates are generally "
                "positively associated with trade balances. This relationship underscores the significant role of "
                "exports in economic growth, as higher GDP growth rates often coincide with increased export "
                "performance, thereby positively impacting the trade balance. Moreover, economic policies and "
                "structures play crucial roles: favorable exchange rates and robust domestic demand can stimulate "
                "exports, reinforcing both GDP and the trade balance. The intricate interaction of these factors "
                "highlights how national economic policies and global economic conditions collectively shape the "
                "correlation between GDP and the trade balance, illustrating the complex nature of international "
                "trade dynamics and economic growth.\n"
                "    \n"
                "Regarding the lagged impact on the trade balance compared to GDP, contractual clauses play a pivotal "
                "role by often introducing delays in international transactions. For instance, long-term contracts in "
                "sectors such as manufacturing or agricultural products may include payment terms spread over months "
                "or years. Therefore, even if a country's GDP growth increases and is followed by higher exports, "
                "the effects on the trade balance may be delayed due to the time required for export revenues to be "
                "fully realized and recorded. Additionally, fluctuations in exchange rates and variations in "
                "commodity prices can also influence export values and thus the trade balance, adding a temporal "
                "dimension of volatility to the observed correlation between GDP and the trade balance."
            )

    # Data sources
    if selected == "Sources":
    st.subheader(":blue[Data]")
    st.write(
        "[GDP data](https://db.nomics.world/IMF/WEO:2024-04?tab=list)\n"
        "\n"
        "[Trade Balance data](https://db.nomics.world/CEPII/CHELEM-TRADE-INDIC?tab=list)\n"
    )
    st.markdown("---")
    st.write(
        "[DBnomics](https://db.nomics.world)\n"
        "[Source Code](https://github.com/dbnomics/gdp-trade-balance-correlation-dashboard)"
    )
if __name__ == "__main__":
    main()
