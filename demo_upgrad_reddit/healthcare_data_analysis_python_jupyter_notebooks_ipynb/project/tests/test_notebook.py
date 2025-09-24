import pytest
import pandas as pd
from unittest import mock
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import Markdown, display, HTML


# Test Suite for notebook.ipynb's Chained Healthcare AI Workflow
# Pytest-based, with mocking and data simulation where necessary.

@pytest.fixture
def health_df():
    # Return a synthetic health dataframe with 'age', categorical, and numeric fields
    data = {
        'age': [25, 33, 50, 60, 40],
        'sex': ['M', 'F', 'M', 'F', 'M'],
        'lab_result': [1.5, 2.1, 1.8, 2.2, 1.7],
    }
    return pd.DataFrame(data)

@pytest.fixture
def clinical_notes_df():
    # Return a DataFrame with example clinical notes and simple entity extraction results
    data = [
        {'note': 'Patient with hypertension and diabetes.', 'entities': [
            {'entity_group': 'DISEASE', 'word': 'hypertension', 'score': 0.97},
            {'entity_group': 'DISEASE', 'word': 'diabetes', 'score': 0.95},
        ]},
        {'note': 'No history of cancer.', 'entities': [
            {'entity_group': 'NEG_CONDITION', 'word': 'cancer', 'score': 0.92},
        ]},
        {'note': 'Routine checkup. No complaints.', 'entities': []}
    ]
    return pd.DataFrame(data)

@pytest.fixture
def synthetic_df():
    # Mimics output from a synthetic data generator; same schema as health_df
    data = {
        'age': [27, 35, 52, 58, 44],
        'sex': ['M', 'F', 'M', 'F', 'F'],
        'lab_result': [1.6, 2.0, 1.9, 2.1, 1.8],
    }
    return pd.DataFrame(data)


@mock.patch('IPython.display.display')
def test_step1_eda_display_called(mock_display, health_df):
    # Arrange: health_df fixture, mock display
    # Act: Simulate EDA preview
    try:
        display(Markdown('## \U0001f6a9 Step 1: EDA – Real Healthcare Data Preview'))
        display(health_df.head(5))
        display(health_df.describe(include='all'))
    except Exception:
        display(Markdown('_(Structured health_df not found; please rerun EDA cell above if needed.)_'))
    # Assert: display called at least 3 times for EDA preview
    assert mock_display.call_count >= 3, 'EDA preview should display head and describe.'


def test_step1_eda_edgecase_missing_health_df(monkeypatch):
    # Test workflow when health_df is not defined
    # Arrange: Remove health_df from globals
    if 'health_df' in globals():
        monkeypatch.delitem(globals(), 'health_df', raising=False)
    # Mock display to capture markdown
    with mock.patch('IPython.display.display') as mock_display:
        with mock.patch('IPython.display.Markdown', side_effect=Markdown) as md:
            # Act: Simulate EDA cell error fallback
            try:
                display(Markdown('## \U0001f6a9 Step 1: EDA – Real Healthcare Data Preview'))
                display(health_df.head(5))
                display(health_df.describe(include='all'))
            except Exception:
                display(Markdown('_(Structured health_df not found; please rerun EDA cell above if needed.)_'))
    # Assert error message markdown triggered
    last_call_args = mock_display.call_args_list[-1][0][0]
    assert 'health_df not found' in str(last_call_args), 'Should show fallback markdown if health_df missing.'


@mock.patch('IPython.display.display')
def test_step2_nlp_display(mock_display, clinical_notes_df):
    # Arrange: clinical_notes_df fixture
    # Act: NLP block displays entities for first 3 notes
    try:
        display(Markdown('## \U0001f6a9 Step 2: NLP – Information Extraction from Clinical Notes'))
        display(clinical_notes_df.head(3))
        display(Markdown('Named entities (first 3 clinical notes):'))
        for idx, row in clinical_notes_df.head(3).iterrows():
            ent_list = row['entities'] if 'entities' in row else []
            ents_md = []
            for ent in ent_list:
                label = ent.get('entity_group', ent.get('entity',''))
                word = ent.get('word', '\u2013')
                score = ent.get('score', 0.0)
                ents_md.append(f"- <b>{label}</b>: '{word}' <span style=\"color:grey\">({score:.2f})</span>")
            if not ents_md:
                ents_md = ['_No entities extracted._']
            display(HTML('<br/>'.join(ents_md)))
    except Exception:
        display(Markdown('_(clinical_notes_df not found; please rerun NLP cell above if needed.)_'))
    # Assert display used for every note (entities or fallback)
    assert mock_display.call_count >= 4, 'NLP section should display notes and their entities.'


def test_step2_nlp_missing_notes(monkeypatch):
    # Arrange: Remove clinical_notes_df
    if 'clinical_notes_df' in globals():
        monkeypatch.delitem(globals(), 'clinical_notes_df', raising=False)
    # Mock display to intercept markdown
    with mock.patch('IPython.display.display') as mock_display:
        # Act: Trigger nlp block, expect error fallback
        try:
            display(Markdown('## \U0001f6a9 Step 2: NLP – Information Extraction from Clinical Notes'))
            display(clinical_notes_df.head(3))
        except Exception:
            display(Markdown('_(clinical_notes_df not found; please rerun NLP cell above if needed.)_'))
    # Assert fallback markdown shown
    last_call_args = mock_display.call_args_list[-1][0][0]
    assert 'clinical_notes_df not found' in str(last_call_args), 'Should show fallback markdown if clinical_notes_df missing.'


@mock.patch('IPython.display.display')
def test_step3_synthetic_data_display_plot(mock_display, synthetic_df, health_df):
    # Arrange: real and synthetic dataframes with 'age' column
    # Patch matplotlib.pyplot.show to prevent plot GUI popup
    with mock.patch('matplotlib.pyplot.show') as mock_show:
        try:
            display(Markdown('#### Synthetic Patient Records (preview)'))
            display(synthetic_df.head(5))
            plt.figure(figsize=(6,4))
            sns.histplot(health_df['age'], color='skyblue', label='Real', kde=True, stat='density', bins=20, alpha=0.4)
            sns.histplot(synthetic_df['age'], color='r', label='Synthetic', kde=True, stat='density', bins=20, alpha=0.4)
            plt.title('Age: Synthetic vs Real Distributions')
            plt.xlabel('Age')
            plt.ylabel('Density')
            plt.legend()
            plt.tight_layout()
            plt.show()
        except Exception:
            display(Markdown('_Synthetic tabular data not found. To reproduce, rerun the synthetic notebook cells above._'))
    # Assert display called for markdown and data, and plot show was attempted
    assert mock_display.call_count >= 2, 'Synthetic data section should display markdown and data preview.'
    assert mock_show.call_count == 1, 'Plot should be generated for synthetic vs real distribution comparison.'


def test_step3_synthetic_missing(monkeypatch):
    # Arrange: remove synthetic_df if present
    if 'synthetic_df' in globals():
        monkeypatch.delitem(globals(), 'synthetic_df', raising=False)
    # Mock display
    with mock.patch('IPython.display.display') as mock_display:
        # Act: Try running synthetic section, expect fallback
        try:
            display(Markdown('#### Synthetic Patient Records (preview)'))
            display(synthetic_df.head(5))
        except Exception:
            display(Markdown('_Synthetic tabular data not found. To reproduce, rerun the synthetic notebook cells above._'))
    # Assert error markdown shown
    last_call_args = mock_display.call_args_list[-1][0][0]
    assert 'Synthetic tabular data not found' in str(last_call_args), 'Should report missing synthetic data.'


def test_workflow_summary_markdown():
    # Arrange: Markdown string from notebook summary cell
    summary_md = '''
    ## \U0001f4dd Workflow Summary: Rapid AI Healthcare Experimentation
    This notebook chains **EDA \u2192 Clinical NLP \u2192 Synthetic Data Generation** in modular, reusable steps:
    - **Exploratory Data Analysis:**
        - Key dataset properties and plausible statistical distributions are surveyed first, identifying data issues and likely modeling features.
    - **NLP Pipeline:**
        - Transformer-based entity recognition extracts clinical terms from de-identified text; model swaps and tuning are rapid for improved accuracy.
    - **Synthetic Data Generation:**
        - Privacy-compliant, structurally-matched synthetic records are quickly produced and compared distributionally to the original data.
    '''
    # Act: Attempt to render summary using Markdown
    try:
        md = Markdown(summary_md)
    except Exception as e:
        pytest.fail(f'Markdown summary rendering failed: {e}')
    # Assert: The markdown renders (returns a Markdown object)
    assert hasattr(md, 'data'), 'Summary markdown should construct without error.'

# Advanced case: Check that entity extraction logic robustly handles empty/malformed input
@pytest.mark.parametrize('ent_list,expected', [
    ([{'entity_group': 'DRUG', 'word': 'Aspirin', 'score': 0.91}], True),
    ([], False),
    (None, False),
    ([{'word': 'Unknown'}], True),
])
def test_entity_extraction_rendering(ent_list, expected):
    # Given a list of entities (possibly malformed), the logic produces either
    # a non-empty or a fallback markdown list
    ents_md = []
    if ent_list:
        for ent in ent_list:
            label = ent.get('entity_group', ent.get('entity',''))
            word = ent.get('word', '\u2013')
            score = ent.get('score', 0.0)
            ents_md.append(f"- <b>{label}</b>: '{word}' <span style=\"color:grey\">({score:.2f})</span>")
    if not ents_md:
        ents_md = ['_No entities extracted._']
    # Assert logic: if input is empty or None, fallback fires
    assert (ents_md == ['_No entities extracted._']) is not expected