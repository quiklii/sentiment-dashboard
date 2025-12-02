# Sentience - Sentiment Analysis Dashboard

## The Vision

With the exponential rise and popularization of AI-powered tools, they have come to be perceived either as something too advanced and unreachable, or as a neat gadget with no real use in real-world problems.

*Sentience* was created to challenge that perception.  
Its purpose is to bring practical, meaningful AI capabilities to the businesses that need them most - especially small and medium-sized companies that rarely have access to data teams, analytics departments, or expensive software.

Sentience brings clarity to customer feedback, transforming raw data into practical, actionable insights.

## How it works?
Sentience is a tool build to make sense and gain meaningful insights  of the countless opinions hidden in everyday costumer reviews. It processes each review through a structured analytical pipeline, systematically transforming feedback into a consistent and interpretable representation.
### Pipeline
1. **Data acquisition** The analysis begins with obtaining data in a structured format. At the current development stage, this is done by placing a `.csv` file inside the `/src/data` directory. In future releases, this step will be replaced with direct integration through the Google Reviews API.
2. **Preprocessing and labeling**
   The raw text is then organized, cleaned, and normalized. After preprocessing, each review is evaluated by the sentiment model and assigned an appropriate label.
3. **Aggregation and exploration**
   Once processed, the data can be aggregated according to the user's settings in the sidebar (Location, Timeframe, Timescale). All visualizations, metrics, and KPI summaries across the dashboard update dynamically based on these selections.

### Dashboard structure
Sentience is designed to include (in the MVP version) **three subpages**, each representing a distinct piece of the insight-driven story told by your data:
- **Main Page** - *Do customers like or dislike your service?*
- **Content Analysis** - *Why do they feel this way? What drives their opinions?*
- **Strategy Navigator** - *What can you do to improve customer perception and strengthen satisfaction?*

## Application Preview

![Main Page](main_page.PNG)


