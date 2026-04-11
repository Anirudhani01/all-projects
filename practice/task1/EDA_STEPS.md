### Numeric-only dataset

| Step | Action | Techniques/Notes | Visuals/Outputs |
|---|---|---|---|
| 1 | Load & inspect | Confirm all dtypes numeric; review shape/columns; remove duplicate rows | Head/summary printouts |
| 2 | Basic wrangling | Handle NaN/inf; standardize units if applicable | None |
| 3 | Distributions | Histograms; boxplots; summary stats (mean/median/std/IQR/skew); check zero-inflation | Histograms, boxplots, stats table |
| 4 | Correlations | Pearson and Spearman matrices; flag high correlations; optional VIF | Correlation heatmap; high-corr list |
| 5 | Missing values | Missing rate per column/row; pattern/co-missingness | Missingness matrix/heatmap; ranked list |
| 6 | Outliers | IQR rule; robust z (MAD); per-column counts; optional multivariate (Isolation Forest/LOF) | Outlier counts, flagged indices |
| 7 | Typical analysis | Ranges vs domain bounds; constant/near-constant features; temporal coverage if time-like numeric exists | Range summaries; stability checks |
| 8 | Data readiness | Note scaling needs; remove/merge highly collinear features | Readiness checklist |
| 9 | Summarize | Key findings, issues, proposed next steps | Plots bundle + issues list |

Detailed guidance for numeric-only datasets

- Step 1: Load & inspect
  - Verify file integrity (encoding, delimiter) and confirm every column is numeric. Ensure that the unit of analysis (row meaning) is understood.
  - Remove exact duplicate rows and assess whether there are implicit keys or identifiers embedded as numeric fields.
- Step 2: Basic wrangling
  - Convert non-finite values (inf, -inf) to NaN or clip to reasonable bounds; unify units (e.g., convert cents to dollars consistently).
  - Align scales where appropriate to avoid misleading comparisons in later plots.
- Step 3: Distributions
  - Plot histograms and boxplots for each feature to understand central tendency, dispersion, skewness, and presence of heavy tails or zero-inflation.
  - Use log or other variance-stabilizing transforms for highly skewed variables solely for visualization and understanding.
- Step 4: Correlations
  - Compute Pearson for linear relations and Spearman for monotonic, non-linear tendencies. Visualize with a heatmap and rank pairs by absolute correlation.
  - Diagnose multicollinearity using VIF; mark redundant features for potential removal or consolidation.
- Step 5: Missing values
  - Quantify missingness per column and row; inspect patterns of co-missingness to detect structural issues (e.g., fields missing together).
  - Identify columns with high missingness that may require special handling downstream.
- Step 6: Outliers
  - Apply IQR fences and robust z-scores (MAD-based) to flag potential outliers for each feature; count affected rows per feature.
  - Optionally run multivariate anomaly detectors (Isolation Forest/LOF) to spot joint anomalies not visible univariately.
- Step 7: Typical analysis
  - Compare observed ranges to domain-credible bounds; flag constant or near-constant features that add little information.
  - If a numeric time index exists, review temporal coverage for gaps/spikes that might bias summaries.
- Step 8: Data readiness
  - Note scaling or normalization needs depending on intended downstream methods; prepare a list of highly correlated features to remove or combine.
- Step 9: Summarize
  - Consolidate key plots, a short issues list (missingness, outliers, multicollinearity, unit inconsistencies), and proposed next steps.


### Mixed dataset (numbers + text)

| Step | Action | Techniques/Notes | Visuals/Outputs |
|---|---|---|---|
| 1 | Load & inspect | Identify numeric vs text columns; remove duplicates; normalize text encoding/case; trim whitespace | Head/summary printouts |
| 2 | Type fixes | Parse numeric strings; keep true text; detect high- vs low-cardinality text | Dtype report |
| 3 | Numeric EDA | As numeric-only: histograms, boxplots, stats; Pearson/Spearman; multicollinearity flags | Histograms, boxplots, heatmap |
| 4 | Text EDA | Missing/empty rates; length distribution (chars/words); top tokens/phrases; exact-duplicate rate | Length hist/box; frequency bars |
| 5 | Relationships | Numeric↔text: group numeric stats by top categories; for free text, bucket by length/keywords; Text↔text: cross-tabs if categorical-like | Grouped boxplots/bars; cross-tabs |
| 6 | Missing values | Numeric: as above; Text: treat empty/"N/A" as missing; co-missingness with numeric fields | Missingness matrix; ranked list |
| 7 | Outliers | Numeric: IQR/MAD; optional multivariate on numeric subset; Text: extreme lengths, rare categories, odd patterns | Outlier and anomaly summaries |
| 8 | Typical analysis | Cardinality review; mark text too high-cardinality for one-hot; note candidates for hashing/embeddings | Cardinality table |
| 9 | Summarize | Consolidate numeric plots, text summaries, missingness, outliers; key issues and next actions | Plots bundle + issues list |

Detailed guidance for mixed datasets

- Step 1: Load & inspect
  - Separate columns into numeric vs text. Remove duplicates. Normalize text encoding (e.g., UTF-8), case (lowercase for analysis), and trim whitespace.
  - Identify potential ID-like text fields that should be treated as identifiers, not features.
- Step 2: Type fixes
  - Parse numeric strings and handle thousand separators or currency symbols. Keep true free text as text. Classify text columns by cardinality (low: categorical-like; high: free text).
  - Standardize placeholders (e.g., "N/A", "-", blanks) to consistent missing values.
- Step 3: Numeric EDA
  - Perform the same numeric analyses as the numeric-only workflow: distributions, correlations, multicollinearity checks, and basic range sanity.
- Step 4: Text EDA
  - Measure completeness (missing/empty rate). Analyze length distributions (characters/words) to find extremely short or long entries.
  - For quick semantic overview, compute top tokens or phrases (light cleanup only) and, for low-cardinality text, compute category frequency tables.
- Step 5: Relationships
  - Numeric ↔ text: group numeric summaries by top text categories; for free text, create simple buckets (e.g., length deciles or keyword flags) and compare numeric distributions across buckets.
  - Text ↔ text: where text behaves categorically, produce cross-tabs to identify co-occurrence patterns.
- Step 6: Missing values
  - Numeric missingness as standard. For text, treat empty/whitespace-only as missing and normalize placeholders. Inspect co-missingness across numeric and text features to spot systematic collection gaps.
- Step 7: Outliers
  - Numeric: IQR/MAD plus optional multivariate detectors on numeric subset. Text: flag extreme lengths, rare categories, and suspicious patterns (e.g., repeated characters).
- Step 8: Typical analysis
  - Conduct a cardinality review to determine feasibility of one-hot encoding; mark columns requiring hashing, embeddings, or dimensionality reduction if used later.
  - Record any label-like text columns that could cause leakage in future modeling.
- Step 9: Summarize
  - Combine numeric plots, text summaries, missingness visuals, and outlier/anomaly findings into a concise issues list with clear next actions.


### Differences between approaches

| Dimension | Numeric-only | Mixed (numbers + text) |
|---|---|---|
| Data typing | All columns numeric; simpler casting | Split numeric vs text; parse numeric strings; normalize text encoding/case |
| Wrangling focus | Handle NaN/inf, units, duplicates | Plus trim whitespace, handle placeholders ("N/A"), detect high/low-cardinality text |
| Distribution visuals | Histograms, boxplots, stats | Same for numeric + text length distributions and top tokens/categories |
| Correlations | Pearson/Spearman; heatmap; multicollinearity (VIF) | Same for numeric; for text use grouped summaries or categorical cross-tabs |
| Missing values | Per-column/row rates; pattern/co-missingness | Numeric missingness + text-specific (empty/whitespace, placeholders); co-missingness across types |
| Outliers | IQR, robust z (MAD), optional multivariate (IF/LOF) | Numeric outliers as above + text anomalies (extreme lengths, rare categories, odd patterns) |
| Relationships | Numeric↔numeric scatter/heatmap | Numeric↔text via grouped stats by categories or length/keyword buckets; text↔text via cross-tabs if categorical-like |
| Typical analysis | Zero-inflation; constant/near-constant features | Cardinality review; identify fields unsuitable for one-hot; candidates for hashing/embeddings |
| Readiness outputs | Scaling needs; drop/merge highly correlated features | Numeric readiness + text encoding strategy notes and anomaly flags |
