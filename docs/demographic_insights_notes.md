# Demographic Reporting Ideas

This note captures Grok’s suggestions for future demographic dashboards built on the DV/RMS datasets. Revisit when planning analytics or visualization sprints.

## Data Preparation

- Always run the redaction pipeline described in `docs/pii_policy.md` before loading or exporting data.
- Use a shared helper (`load_and_clean`) to enforce column presence: `VictimAge`, `VictimSex`, `VictimRace`, `IncidentDate`, `Relationship`, `IncidentTime`, `Longitude`, `Latitude`, `VictimID`.
- Handle nulls by filling with `Unknown`, clip age outliers via IQR, and drop invalid coordinates (use z-score filtering).
- Create `AgeBand`, `Hour`, `Day` as reusable columns for charts.

## Suggested Analyses (pandas + seaborn/matplotlib)

- **Gender distribution**  
  ```python
  gender_counts = df.groupby('VictimSex').size()
  gender_counts.plot(kind='bar', title='Victim Gender Distribution')
  ```
- **Race/Ethnicity heatmap**  
  ```python
  race_eth = pd.crosstab(df['VictimRace'], df['VictimEthnicity'], normalize='index')
  sns.heatmap(race_eth, annot=True, fmt='.1%', cmap='Blues')
  ```
- **Age bands**  
  ```python
  df['AgeBand'] = pd.cut(df['VictimAge'], bins=[0,17,24,34,44,54,100], labels=['<18','18-24','25-34','35-44','45-54','55+'])
  df.groupby('AgeBand').size()
  ```
- **Age vs. Relationship**  
  ```python
  pd.crosstab(df['AgeBand'], df['Relationship'], normalize='index').plot(kind='bar', stacked=True, colormap='viridis')
  ```
- **Temporal patterns** (hour-by-day heatmap)  
  ```python
  pivot = df.pivot_table(index='Day', columns='Hour', values='CaseNumber', aggfunc='count')
  sns.heatmap(pivot.reindex(['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']), cmap='Reds')
  ```
- **Geographic density**  
  ```python
  sns.kdeplot(x=df['Longitude'], y=df['Latitude'], cmap='plasma', shade=True, bw_adjust=0.5)
  ```
- **Repeat victims**  
  ```python
  repeats = df[df['VictimID'].duplicated(keep=False)].sort_values(['VictimID','IncidentDate'])
  sns.lineplot(data=repeats, x='IncidentDate', y='VictimID', hue='VictimID', legend=False, alpha=0.6)
  ```

## Reporting Considerations

- Export figures with `fig.savefig(..., dpi=300, bbox_inches='tight')` for supervisor-ready decks.
- Aggregate results (e.g., percentages per zone) before sharing to maintain anonymity.
- Target platforms: Tableau, Power BI, or ArcGIS Pro dashboards that display clustering/hotspots alongside demographic breakdowns.
- Include contextual notes about cultural sensitivity and limitations when presenting statistics.

## Automation Backlog

- Add a CLI command (e.g., `python etl.py report --src ...`) that produces the above charts once redaction passes.
- Integrate automated redaction helpers (`presidio`, `faker`) in reporting workflows.
- Add pytest fixtures that simulate PII leaks in reports and fail builds if redaction is skipped.
- Consider caching heavy plotting dependencies and data extracts for faster CI/notebook execution.

