# COVID-19 Data Analysis Insights\n\n
## 🌍 Global COVID-19 Overview (as of 2023-10-24)

### Key Metrics:
*   **Total Cases Worldwide**: 3,268,621,333
*   **Total Deaths Worldwide**: 29,129,997
*   **Total Vaccinations Administered**: 55.2 billion
*   **Global Mortality Rate**: 0.89%
*   **Average Global Vaccination Rate**: 63.3%
\n\n
## 📉 Most Affected Countries (by Total Cases, Excluding Aggregates)

| Country | Total Cases | Total Deaths | Mortality Rate (%) |
|---|---|---|---|
| High income | 425,988,398 | 2,914,272 | 0.68 |
| Upper middle income | 244,463,792 | 2,666,760 | 1.09 |
| European Union | 184,210,531 | 1,245,398 | 0.68 |
| United States | 103,436,829 | 1,136,920 | 1.10 |
| China | 99,315,684 | 121,742 | 0.12 |\n\n
## 💉 Vaccination Leaders (Countries with >1M Population, Excluding Aggregates)

| Country | At Least One Dose (%) | Fully Vaccinated (%) |
|---|---|---|
| Qatar | 105.8 | 105.8 |
| United Arab Emirates | 105.8 | 103.7 |
| Singapore | 91.5 | 90.8 |
| Hong Kong | 92.4 | 90.8 |
| Chile | 92.3 | 90.3 |\n\n
## 🔗 Key Correlations

Correlation between different metrics (Pearson correlation coefficient):

|                    |   mortality_rate |   vaccination_rate |   gdp_per_capita |   population_density |   life_expectancy |
|:-------------------|-----------------:|-------------------:|-----------------:|---------------------:|------------------:|
| mortality_rate     |             1    |              -0.37 |             0.01 |                -0    |              0.01 |
| vaccination_rate   |            -0.37 |               1    |             0.44 |                 0.14 |              0.52 |
| gdp_per_capita     |             0.01 |               0.44 |             1    |                 0.37 |              0.68 |
| population_density |            -0    |               0.14 |             0.37 |                 1    |              0.22 |
| life_expectancy    |             0.01 |               0.52 |             0.68 |                 0.22 |              1    |\n\n
## 📈 Recent Trends (2023-10-17 to 2023-10-24, Excluding Aggregates)

### Highest Average Daily Cases:

| Country | Avg. Daily Cases |
|---|---|
| Italy | 6,874 |
| Iran | 1,254 |
| United Kingdom | 1,170 |
| Finland | 503 |
| China | 387 |\n\n
### Fastest Growing Outbreaks:
(Comparing most recent day (according to the file data)to 7 days prior, based on new cases and excluding aggregates)

| Country | Increase Factor |
|---|---|
| Armenia | 1.0 |
| China | 1.0 |
| Finland | 1.0 |\n\n
## 💉 Vaccination Impact (Excluding Aggregates)

- **Average Mortality in Highly Vaccinated Countries (>50% fully vaccinated)**: 0.92%
- **Average Mortality in Less Vaccinated Countries (<20% fully vaccinated)**: 2.72%
\n\n
## 🇰🇪 Kenya - Specific Insights (as of 2023-10-18)

*   **Total Cases**: 343,999
*   **New Cases (Latest Day)**: 0
*   **Total Deaths**: 5,689
*   **New Deaths (Latest Day)**: 0
*   **Mortality Rate**: 1.65%
*   **Total Vaccinations**: 23,750,431
*   **Vaccination Rate (At Least One Dose)**: 26.8%
