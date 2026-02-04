from unittest import TestCase

from scielo_classic_website.utils.files_utils import sanitize_filename_surrogates


class TestSanitizeFilenameSurrogates(TestCase):
    def test_sanitize_normal_filename(self):
        """Test that normal filenames are not affected"""
        filename = "document.pdf"
        result = sanitize_filename_surrogates(filename)
        self.assertEqual(filename, result)

    def test_sanitize_filename_with_unicode(self):
        """Test that valid unicode characters are preserved"""
        filename = "Sumário.pdf"
        result = sanitize_filename_surrogates(filename)
        # Should preserve valid unicode
        self.assertEqual(filename, result)

    def test_sanitize_filename_with_surrogates(self):
        """Test that surrogate characters are replaced"""
        # Create a string with a surrogate character
        # This simulates what happens when filenames are read with encoding issues
        filename_with_surrogate = "Sum\udce1rio.pdf"
        result = sanitize_filename_surrogates(filename_with_surrogate)
        
        # The surrogate should be replaced with the replacement character
        # The exact result depends on the replacement strategy
        # but it should not raise an error and should be valid UTF-8
        self.assertIsInstance(result, str)
        # Verify it can be encoded to UTF-8 without errors
        result.encode("utf-8")

    def test_sanitize_empty_filename(self):
        """Test that empty string is handled correctly"""
        result = sanitize_filename_surrogates("")
        self.assertEqual("", result)

    def test_sanitize_none_filename(self):
        """Test that None is handled correctly"""
        result = sanitize_filename_surrogates(None)
        self.assertIsNone(result)

    def test_sanitize_filename_with_accents(self):
        """Test that accented characters are preserved"""
        filename = "café.pdf"
        result = sanitize_filename_surrogates(filename)
        self.assertEqual(filename, result)

    def test_sanitize_filename_with_multiple_surrogates(self):
        """Test that multiple surrogate characters are all replaced"""
        filename_with_surrogates = "\udce1\udce2\udce3.pdf"
        result = sanitize_filename_surrogates(filename_with_surrogates)
        
        # Should not raise an error and should be valid UTF-8
        self.assertIsInstance(result, str)
        result.encode("utf-8")
