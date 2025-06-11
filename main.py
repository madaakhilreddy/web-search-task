import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse

class WebCrawler:
    def __init__(self):
        self.index = defaultdict(str)
        self.visited = set()

    def crawl(self, url, base_url=None):
        if url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    full_url = urljoin(base_url or url, href)
                    if full_url.startswith(base_url or url):
                        self.crawl(full_url, base_url=base_url or url)
        except Exception as e:
            print(f"Error crawling {url}: {e}")

    def search(self, keyword):
        results = []
        for url, text in self.index.items():
            if keyword.lower() in text.lower():
                results.append(url)
        return results

    def print_results(self, results):
        if results:
            print("Search results:")
            for result in results:
                print(f"- {result}")
        else:
            print("No results found.")

# ------------------- MAIN FUNCTION -------------------

def main():
    crawler = WebCrawler()
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "test"
    results = crawler.search(keyword)
    crawler.print_results(results)

# ------------------- UNIT TESTS -------------------

import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

class ExtendedWebCrawlerTests(unittest.TestCase):

    @patch('requests.get')
    def test_crawl_skips_visited(self, mock_get):
        crawler = WebCrawler()
        crawler.visited.add("https://example.com")
        crawler.crawl("https://example.com")
        mock_get.assert_not_called()

    @patch('requests.get')
    def test_crawl_handles_invalid_href(self, mock_get):
        html_with_invalid_href = """
        <html><body>
            <a href="#">Home</a>
            <a href="">Empty</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = html_with_invalid_href
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")
        self.assertEqual(len(crawler.visited), 1)
        self.assertIn("https://example.com", crawler.index)

    def test_search_case_insensitive(self):
        crawler = WebCrawler()
        crawler.index["/test"] = "This Page Contains TeSt Content"
        results = crawler.search("test")
        self.assertEqual(results, ["/test"])  # ✅ FIXED

    def test_search_returns_unmatched(self):
        crawler = WebCrawler()
        crawler.index["/a"] = "Nothing relevant"
        crawler.index["/b"] = "Another thing"
        results = crawler.search("notfound")
        self.assertEqual(set(results), set())  # ✅ FIXED

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results_outputs_expected_format(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/page"])
        output = mock_stdout.getvalue()
        self.assertIn("Search results:", output)
        self.assertIn("- https://test.com/page", output)

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results_empty(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results([])
        output = mock_stdout.getvalue()
        self.assertIn("No results found", output)

    def test_error_handling_invalid_url(self):
        crawler = WebCrawler()
        with patch('requests.get', side_effect=Exception("boom")):
            crawler.crawl("https://invalid.com")
            self.assertIn("https://invalid.com", crawler.visited)
            self.assertNotIn("https://invalid.com", crawler.index)

    def test_index_text_extraction(self):
        crawler = WebCrawler()
        html = "<html><body><p>Hello</p><div>World</div></body></html>"
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = html
            mock_get.return_value = mock_response
            crawler.crawl("https://example.com")

            self.assertIn("Hello", crawler.index["https://example.com"])
            self.assertIn("World", crawler.index["https://example.com"])

    def test_url_normalization_with_base(self):
        html = """
        <html><body>
            <a href="/relative">Relative Link</a>
        </body></html>
        """
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.text = html
            mock_get.return_value = mock_response

            crawler = WebCrawler()
            crawler.crawl("https://example.com")

            self.assertIn("https://example.com/relative", crawler.visited)

# ------------------- RUNNING -------------------

if __name__ == "__main__":
    unittest.main()  # To run tests
    # main()         # To run actual crawler
