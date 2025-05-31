import requests
from bs4 import BeautifulSoup
from collections import defaultdict
from urllib.parse import urljoin, urlparse
import unittest
from unittest.mock import patch, MagicMock
from io import StringIO


class WebCrawler:
    def __init__(self, max_depth=2):
        self.index = defaultdict(str)
        self.visited = set()
        self.max_depth = max_depth

    def crawl(self, url, base_url=None, depth=0):
        if depth > self.max_depth or url in self.visited:
            return
        self.visited.add(url)

        try:
            response = requests.get(url, timeout=5)
            soup = BeautifulSoup(response.text, 'html.parser')
            self.index[url] = soup.get_text()

            parsed_base = urlparse(base_url or url).netloc

            for link in soup.find_all('a'):
                href = link.get('href')
                if href:
                    href = urljoin(base_url or url, href)
                    if urlparse(href).scheme in ('http', 'https') and urlparse(href).netloc == parsed_base:
                        self.crawl(href, base_url=base_url or url, depth=depth + 1)

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


def main():
    crawler = WebCrawler(max_depth=2)
    start_url = "https://example.com"
    crawler.crawl(start_url)

    keyword = "Domain"
    results = crawler.search(keyword)
    crawler.print_results(results)


# Unit tests
class WebCrawlerTests(unittest.TestCase):
    @patch('requests.get')
    def test_crawl_success(self, mock_get):
        sample_html = """
        <html><body>
            <h1>Welcome!</h1>
            <a href="/about">About Us</a>
            <a href="https://example.com">Home Again</a>
        </body></html>
        """
        mock_response = MagicMock()
        mock_response.text = sample_html
        mock_get.return_value = mock_response

        crawler = WebCrawler()
        crawler.crawl("https://example.com")

        self.assertIn("https://example.com/about", crawler.visited)
        self.assertIn("https://example.com", crawler.index)

    @patch('requests.get')
    def test_crawl_error(self, mock_get):
        mock_get.side_effect = requests.exceptions.RequestException("Test Error")

        crawler = WebCrawler()

        with patch('sys.stdout', new_callable=StringIO) as mock_stdout:
            crawler.crawl("https://example.com")
            self.assertIn("Error crawling https://example.com", mock_stdout.getvalue())

    def test_search(self):
        crawler = WebCrawler()
        crawler.index["page1"] = "This has the keyword"
        crawler.index["page2"] = "No match here"

        results = crawler.search("keyword")
        self.assertEqual(results, ["page1"])

    @patch('sys.stdout', new_callable=StringIO)
    def test_print_results(self, mock_stdout):
        crawler = WebCrawler()
        crawler.print_results(["https://test.com/result"])
        output = mock_stdout.getvalue()
        self.assertIn("Search results:", output)
        self.assertIn("- https://test.com/result", output)


if __name__ == "__main__":
    print("Running tests...\n")
    unittest.main(exit=False)
    print("\nRunning main crawler...\n")
    main()