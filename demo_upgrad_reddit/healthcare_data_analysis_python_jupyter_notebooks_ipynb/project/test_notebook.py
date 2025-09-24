import unittest
import numpy as np
import pandas as pd
from unittest import mock
from types import SimpleNamespace
import matplotlib
matplotlib.use('Agg')  # Prevent GUI for tests
import matplotlib.pyplot as plt
import seaborn as sns

from notebook import generate_synthetic_tabular, generate_synthetic_notes, plot_distribution_compare, plot_categorical_compare

class TestSyntheticDataNotebook(unittest.TestCase):
    def test_generate_synthetic_tabular_structure_and_types(self):
        # Arrange
        n_samples = 150
        # Act
        df = generate_synthetic_tabular(n_samples=n_samples, random_seed=99)
        # Assert
        self.assertEqual(len(df), n_samples, "Generated tabular data row count mismatch")
        expected_cols = {'patient_id', 'age', 'sex', 'admission_type', 'systolic_bp', 'diastolic_bp', 'glucose', 'length_of_stay', 'discharge_status'}
        self.assertSetEqual(set(df.columns), expected_cols, "Tabular data columns mismatch")
        self.assertTrue(df['age'].between(0, 100).all(), "Age out of realistic range (0-100)")
        self.assertTrue(df['sex'].isin(['Male', 'Female']).all(), "Sex contains invalid values")
        self.assertTrue(df['admission_type'].isin(['Emergency', 'Elective', 'Urgent']).all(), "Admission type contains invalid")
        self.assertTrue(df['discharge_status'].isin(['Home', 'Transferred', 'Deceased']).all(), "Discharge status contains invalid")
        # Check for no NaN values
        self.assertFalse(df.isna().any().any(), "Tabular synthetic data contains missing values")

    def test_generate_synthetic_tabular_edge_cases(self):
        # Test zero and one row cases
        df_zero = generate_synthetic_tabular(n_samples=0)
        self.assertEqual(len(df_zero), 0, "Tabular: Expected 0 rows for n_samples=0")
        df_one = generate_synthetic_tabular(n_samples=1)
        self.assertEqual(len(df_one), 1, "Tabular: Expected 1 row for n_samples=1")
        # Test negative number raises exception or gets handled
        with self.assertRaises(ValueError):
            generate_synthetic_tabular(n_samples=-5)

    def test_generate_synthetic_notes_structure_and_types(self):
        # Arrange
        n_samples = 7
        # Act
        df = generate_synthetic_notes(n_samples=n_samples, random_seed=7)
        # Assert
        self.assertEqual(len(df), n_samples)
        self.assertSetEqual(set(df.columns), {'note_id', 'note_text'})
        self.assertTrue((df['note_id'] == np.arange(1, n_samples+1)).all(), "Note IDs are not consecutive and starting from 1")
        self.assertTrue(df['note_text'].apply(lambda x: isinstance(x, str)).all(), "Some notes are not strings")
        self.assertTrue(df['note_text'].apply(lambda x: len(x.strip()) > 0).all(), "Empty clinical note found")

    def test_generate_synthetic_notes_diversity_and_reproducibility(self):
        n_samples = 15
        df1 = generate_synthetic_notes(n_samples=n_samples, random_seed=22)
        df2 = generate_synthetic_notes(n_samples=n_samples, random_seed=22)
        # Same random seed yields identical data
        self.assertTrue(df1.equals(df2), "Notes with same random seed should be equal")
        # With different seed, should be different (probabilistic; high chance for short samples)
        df3 = generate_synthetic_notes(n_samples=n_samples, random_seed=23)
        self.assertFalse(df1.equals(df3), "Notes with different seeds likely differ")
        # Check for high enough vocabulary diversity (no single word dominates too much)
        words = ' '.join(df1['note_text']).split()
        unique_word_ratio = len(set(words))/len(words)
        self.assertGreater(unique_word_ratio, 0.15, "Vocabulary diversity too low in generated notes")

    def test_plot_distribution_compare_and_categorical_compare(self):
        # Arrange: generate tabular real and synthetic data with different seeds
        real_df = generate_synthetic_tabular(n_samples=40, random_seed=123)
        syn_df = generate_synthetic_tabular(n_samples=40, random_seed=321)
        # Act+Assert: Test that plots run without error even for small samples
        # Mock plt.show to avoid actually displaying
        with mock.patch('matplotlib.pyplot.show'):
            for col in ['age', 'systolic_bp', 'diastolic_bp', 'glucose', 'length_of_stay']:
                plot_distribution_compare(syn_df, real_df, col, bins=8)
            for cat in ['sex', 'admission_type', 'discharge_status']:
                plot_categorical_compare(syn_df, real_df, cat)

    def test_textual_basic_statistics(self):
        # Arrange
        df = generate_synthetic_notes(n_samples=8, random_seed=55)
        # Act
        df['num_words'] = df['note_text'].apply(lambda s: len(s.split()))
        df['num_chars'] = df['note_text'].apply(len)
        # Assert: Word and char counts are positive and sensible
        self.assertTrue((df['num_words'] > 3).all(), "All notes should have more than three words")
        self.assertTrue((df['num_chars'] > 10).all(), "All notes have more than 10 chars")
        # Check statistics consistency
        stats = df[['num_words','num_chars']].describe()
        self.assertIn('mean', stats.columns or stats.index, "Stats describe did not run properly")

    def test_invalid_plot_distribution_column(self):
        # Arrange
        real_df = generate_synthetic_tabular(n_samples=10)
        syn_df = generate_synthetic_tabular(n_samples=10, random_seed=5)
        with mock.patch('matplotlib.pyplot.show'):
            # Invalid feature; should raise KeyError
            with self.assertRaises(KeyError):
                plot_distribution_compare(syn_df, real_df, column='nonexistent_col')

    def test_invalid_plot_categorical_column(self):
        real_df = generate_synthetic_tabular(n_samples=10)
        syn_df = generate_synthetic_tabular(n_samples=10, random_seed=5)
        with mock.patch('matplotlib.pyplot.show'):
            with self.assertRaises(KeyError):
                plot_categorical_compare(syn_df, real_df, column='bad_category')

    def test_notes_zero_and_negative(self):
        df = generate_synthetic_notes(n_samples=0)
        self.assertEqual(len(df), 0, "Should return empty DataFrame for zero samples")
        with self.assertRaises(ValueError):
            generate_synthetic_notes(n_samples=-3)

if __name__ == '__main__':
    unittest.main()