"""
Unit and integration tests for Medical Literature Auto Search engine.
"""

import unittest
from src.core.models import Article, SearchResult
from src.core.query_builder import QueryBuilder
from src.filters.journal_filter import JournalFilter
from src.exporters.markdown_exporter import MarkdownExporter
from src.exporters.bibtex_exporter import BibTeXExporter
from src.exporters.csv_exporter import CSVExporter
from src.utils.config_loader import load_yaml_config


class TestMedicalSearch(unittest.TestCase):
    def setUp(self):
        self.journals_cfg = load_yaml_config("./config/journals.yaml")

    def test_query_builder(self):
        builder = QueryBuilder(self.journals_cfg)
        query = builder.build_pubmed_query(
            topic="Heart failure",
            years_back=5,
            top_tier_only=True,
            article_types=["guidelines", "meta_analyses"]
        )
        self.assertIn("Heart failure", query)
        self.assertIn("N Engl J Med", query)
        self.assertIn("Practice Guideline", query)
        self.assertIn("Date - Publication", query)

    def test_journal_filter(self):
        j_filter = JournalFilter(self.journals_cfg)

        # Test NEJM
        art1 = Article(pmid="1", title="Test NEJM", journal="The New England journal of medicine", journal_iso="N Engl J Med")
        j_filter.enrich_article(art1)
        self.assertTrue(art1.is_top_tier)
        self.assertEqual(art1.journal_tier, 1)

        # Test Lancet
        art2 = Article(pmid="2", title="Test Lancet", journal="The Lancet", journal_iso="Lancet")
        j_filter.enrich_article(art2)
        self.assertTrue(art2.is_top_tier)

        # Test AHA Circulation
        art3 = Article(pmid="3", title="Test Circulation", journal="Circulation", journal_iso="Circulation")
        j_filter.enrich_article(art3)
        self.assertTrue(art3.is_top_tier)
        self.assertEqual(art3.journal_group, "cardiology_aha")

        # Test ASH Blood
        art4 = Article(pmid="4", title="Test Blood", journal="Blood", journal_iso="Blood")
        j_filter.enrich_article(art4)
        self.assertTrue(art4.is_top_tier)
        self.assertEqual(art4.journal_group, "hematology_ash")

        # Test unknown journal
        art5 = Article(pmid="5", title="Test Local", journal="Random Local Journal", journal_iso="Rand Loc J")
        j_filter.enrich_article(art5)
        self.assertFalse(art5.is_top_tier)
        self.assertEqual(art5.journal_tier, 3)

    def test_exporters(self):
        art = Article(
            pmid="12345678",
            title="Sample Clinical Trial on SGLT2 Inhibitors",
            journal="The New England Journal of Medicine",
            journal_iso="N Engl J Med",
            pub_year=2024,
            pub_date="2024 Jan 15",
            authors=["Smith John", "Doe Jane"],
            abstract="BACKGROUND: Testing drug. METHODS: RCT. RESULTS: Significant reduction in mortality. CONCLUSION: Highly effective.",
            doi="10.1056/NEJMoa123456",
            article_types=["Randomized Controlled Trial", "Clinical Trial"],
            is_top_tier=True,
            free_fulltext_url="https://europepmc.org/article/MED/12345678",
            pdf_url="https://europepmc.org/articles/PMC12345/pdf/main.pdf"
        )
        res = SearchResult(
            topic="SGLT2 inhibitors",
            query_executed="test query",
            total_found_in_pubmed=1,
            articles=[art],
            ai_synthesis="Bằng chứng lâm sàng tích cực từ thử nghiệm RCT."
        )

        md = MarkdownExporter.export(res)
        self.assertIn("SGLT2 INHIBITORS", md)
        self.assertIn("12345678", md)
        self.assertIn("NEJM", md)

        bib = BibTeXExporter.export(res)
        self.assertIn("@article{Smith_2024_12345678", bib)
        self.assertIn("10.1056/NEJMoa123456", bib)


if __name__ == "__main__":
    unittest.main()
