"""Tests that the manuscript data is properly retrieved from the database.
"""

import unittest

from .. import test_client


class TestRetrieveManuscript(unittest.TestCase):
    """Mock test of manuscript retrieval.
    """

    def test_retrieve_manuscript(self):
        """Tests that the manuscript data is properly returned.
        """
        with test_client as client:
            response = client.get("/manuscript/4Q157")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(),
                             {"4Q157": "[--]\n[-- עלו]הי עננא\n[-- ביו]מ֯י שנה\n[-- ]־־־\n[-- מדנ]ח\nאנ֯[כיר? --]\nהאנש מא[לה --]\nובמלאכו֯[הי --]\nד֯בעפרא [--]\nומן בלי מני[ח --]\nימותון ולא ב֯[חכ]מ֯[ה --]\nת֯בקה _____ הלא סכל יק֯[טל --]\nואנה חזי֯ת ד֯ר֯ש֯ע מ֯[ו]עה ולטת ל־[ --]\n[מפ]ר֯ק[ן?] והת־־[ ]־־־[ --]\n[-- ]ל֯[ --]\n"})

    def test_retrieve_manuscript_column(self):
        """Tests that the manuscript data is properly returned with column option.
        """
        with test_client as client:
            response = client.get("/manuscript/4Q157?column=frg.%201%20i")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(),
                             {
                "4Q157": {
                    "frg. 1 i": "[--]\n[-- עלו]הי עננא\n[-- ביו]מ֯י שנה\n[-- ]־־־\n[-- מדנ]ח\n"
                }
            })

    def test_retrieve_manuscript_line(self):
        """
        Tests that the manuscript data is properly returned with line option.
        """
        with test_client as client:
            response = client.get(
                "/manuscript/4Q157?column=frg.%201%20i&line=1")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(),
                             {
                "4Q157": {
                    "frg. 1 i": {
                        "1": "[--]\n"
                    }
                }
            }
            )

    def test_retrieve_manuscript_missing(self):
        """Tests that a missing manuscript is properly handled.
        """
        with test_client as client:
            response = client.get("/manuscript/unknown")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.text, "Manuscript unknown not found.")

    def test_retrieve_manuscript_missing_column(self):
        """Tests that a missing manuscript is properly handled.
        """
        with test_client as client:
            response = client.get("/manuscript/unknown")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.text, "Manuscript unknown not found.")

    def test_retrieve_attribute(self):
        """Tests that attributes of a manuscript are properly retrieved.
        """
        with test_client as client:
            response = client.get("/manuscript/4Q157/attributes/column")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {'4Q157':{"column": ["frg. 1 i", "frg. 1 ii"]}})

    def test_retrieve_attribute_missing(self):
        """Tests that a missing manuscript is properly handled when requesting attributes.
        """
        with test_client as client:
            response = client.get("/manuscript/unknown/attributes/column")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.text, "Manuscript unknown not found.")

    def test_retrieve_manuscript_display(self):
        """Tests that the manuscript data is properly returned in HTML format.
        """
        with test_client as client:
            response = client.get("/manuscript/4Q157/display")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.text,
                             "<body dir='rtl'><br><b>4Q157</b><br/><b></b><br/><b></b><br/>[--]<br>[-- עלו]הי עננא<br>[-- ביו]מ֯י שנה<br>[-- ]־־־<br>[-- מדנ]ח<br>אנ֯[כיר? --]<br>האנש מא[לה --]<br>ובמלאכו֯[הי --]<br>ד֯בעפרא [--]<br>ומן בלי מני[ח --]<br>ימותון ולא ב֯[חכ]מ֯[ה --]<br>ת֯בקה _____ הלא סכל יק֯[טל --]<br>ואנה חזי֯ת ד֯ר֯ש֯ע מ֯[ו]עה ולטת ל־[ --]<br>[מפ]ר֯ק[ן?] והת־־[ ]־־־[ --]<br>[-- ]ל֯[ --]<br></body>")

    def test_retrieve_manuscript_display_missing(self):
        """Tests that a missing manuscript is properly handled in display mode."""
        with test_client as client:
            response = client.get("/manuscript/unknown/display")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.text, "Manuscript unknown not found.")
