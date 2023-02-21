from unittest import TestCase

from scielo_classic_website.models.reference import Reference


class ReferenceTest(TestCase):

    def setUp(self):
        data = {
            "v237": [
                {
                    "_": "10.1108/cpoib.2010.29006baa.001"
                }
            ],
            "v701": [
                {
                    "_": "1"
                }
            ],
            "v032": [
                {
                    "_": "2/3"
                }
            ],
            "v004": [
                {
                    "_": "v61n3"
                }
            ],
            "v012": [
                {
                    "_": "Critical international management and international critical management: Perspectives from Latin America"
                }
            ],
            "v700": [
                {
                    "_": "5"
                }
            ],
            "v065": [
                {
                    "_": "20100000"
                }
            ],
            "collection": "scl",
            "v705": [
                {
                    "_": "S"
                }
            ],
            "v880": [
                {
                    "_": "S0034-7590202100030030000001"
                }
            ],
            "v064": [
                {
                    "_": "2010"
                }
            ],
            "v003": [
                {
                    "_": "0034-7590-rae-61-03-e0000-0010.xml"
                }
            ],
            "v865": [
                {
                    "_": "20210000"
                }
            ],
            "code": "S0034-7590202100030030000001",
            "v882": [
                {
                    "v": "61",
                    "n": "3",
                    "_": ""
                }
            ],
            "v936": [
                {
                    "o": "3",
                    "i": "0034-7590",
                    "y": "2021",
                    "_": ""
                }
            ],
            "v708": [
                {
                    "_": "51"
                }
            ],
            "v706": [
                {
                    "_": "c"
                }
            ],
            "v002": [
                {
                    "_": "S0034-7590(21)06100300300"
                }
            ],
            "v992": [
                {
                    "_": "scl"
                }
            ],
            "v071": [
                {
                    "_": "journal"
                }
            ],
            "v702": [
                {
                    "_": "rae/v61n3/0034-7590-rae-61-03-e0000-0010.xml"
                }
            ],
            "v031": [
                {
                    "_": "6"
                }
            ],
            "v010": [
                {
                    "r": "ND",
                    "s": "Alcadipani",
                    "n": "R.",
                    "_": ""
                }
            ],
            "v030": [
                {
                    "_": "Critical Perspectives on International Business"
                }
            ],
            "v999": [
                {
                    "_": "../bases-work/rae/rae"
                }
            ],
            "processing_date": "2022-08-02"
        }
        self.reference = Reference(data)

    def test_source(self):
        result = self.reference.source
        self.assertEqual("Critical Perspectives on International Business", result)
