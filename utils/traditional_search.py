"""
Mock traditional search API (like Google, Bing, SerpAPI)

This simulates what traditional search APIs return:
- URLs
- Short snippets (meta descriptions)
- NO extracted full content

To get the full content, you'd need to:
1. Scrape each URL
2. Extract main content
3. Clean HTML
4. Handle errors
"""


class TraditionalSearchMock:
    """
    Simulates traditional search API behavior.
    In a real scenario, this would call Google Custom Search API or similar.
    """

    def __init__(self):
        pass

    def search(self, query, max_results=5):
        """
        Simulate a traditional search API response

        Returns only URLs and short snippets (like meta descriptions),
        NOT full extracted content - that's the key difference from Exa.
        """

        mock_results = self._generate_mock_results(query, max_results)

        return {
            'query': query,
            'results': mock_results,
            'total_results': len(mock_results)
        }

    def _generate_mock_results(self, query, max_results):
        """
        Generate mock results that simulate traditional search API behavior.

        Traditional APIs return:
        - Title
        - URL
        - Short snippet/description (typically meta description, ~160 chars)
        - NO full content extraction
        """

        mock_templates = [
            {
                'title': f'{query.title()} - Comprehensive Guide',
                'url': f'https://example.com/guide/{query.replace(" ", "-")}',
                'snippet': f'Learn about {query} in this comprehensive guide. Discover the best practices, tips, and techniques for understanding {query}...'
            },
            {
                'title': f'Understanding {query.title()}: A Complete Overview',
                'url': f'https://docs.example.org/{query.replace(" ", "-")}',
                'snippet': f'Everything you need to know about {query}. This article covers the fundamentals, advanced concepts, and practical applications...'
            },
            {
                'title': f'{query.title()} Explained - Tutorial',
                'url': f'https://tutorial.site/{query.replace(" ", "/")}',
                'snippet': f'A step-by-step tutorial on {query}. Perfect for beginners and advanced users alike. Includes examples and best practices...'
            },
            {
                'title': f'Latest News and Updates on {query.title()}',
                'url': f'https://news.example.com/topics/{query.replace(" ", "-")}',
                'snippet': f'Stay up to date with the latest developments in {query}. Recent articles, announcements, and industry insights...'
            },
            {
                'title': f'{query.title()} - Wikipedia',
                'url': f'https://wikipedia.org/wiki/{query.replace(" ", "_")}',
                'snippet': f'{query.title()} refers to... From Wikipedia, the free encyclopedia. This article needs additional citations for verification...'
            },
            {
                'title': f'{query.title()} Best Practices and Tips',
                'url': f'https://medium.com/@author/{query.replace(" ", "-")}-best-practices',
                'snippet': f'In this article, we explore the best practices for {query}. Learn from industry experts and improve your understanding...'
            },
            {
                'title': f'The Ultimate {query.title()} Resource',
                'url': f'https://resources.dev/{query.replace(" ", "-")}',
                'snippet': f'Your one-stop resource for everything related to {query}. Curated links, tutorials, and documentation...'
            },
            {
                'title': f'{query.title()} FAQ - Frequently Asked Questions',
                'url': f'https://faq.example.com/{query.replace(" ", "-")}',
                'snippet': f'Find answers to the most common questions about {query}. Our FAQ covers basics to advanced topics...'
            },
            {
                'title': f'Getting Started with {query.title()}',
                'url': f'https://quickstart.io/{query.replace(" ", "-")}',
                'snippet': f'New to {query}? This getting started guide will help you understand the fundamentals quickly and efficiently...'
            },
            {
                'title': f'{query.title()} Documentation - Official',
                'url': f'https://docs.official.com/{query.replace(" ", "-")}',
                'snippet': f'Official documentation for {query}. Complete API reference, guides, and examples for developers...'
            }
        ]

        return mock_templates[:max_results]

    def get_snippet_length(self, results):
        """Get total length of all snippets"""
        total = 0
        for result in results.get('results', []):
            total += len(result.get('snippet', ''))
        return total

    def get_result_urls(self, results):
        """Extract URLs from results"""
        return [r.get('url', '') for r in results.get('results', [])]


class TraditionalSearchNote:
    """
    Helper class to explain the traditional search workflow
    """

    @staticmethod
    def get_workflow_steps():
        return [
            "Call search API (Google, Bing, SerpAPI)",
            "Get URLs and short snippets",
            "For each URL, you need to scrape the page (requests, selenium), parse HTML (BeautifulSoup, lxml), extract main content (custom logic), clean and format text and handle errors (404s, timeouts, paywalls)",
            "Filter and rank extracted content",
            "Optimize for LLM context window",
            "Finally get RAG-ready content"
        ]

    @staticmethod
    def get_problems():
        return [
            "Multiple API calls required",
            "Complex scraping logic needed",
            "Error handling for each website",
            "Content extraction varies by site",
            "High latency (serial scraping)",
            "Maintenance burden (site changes)",
            "Rate limiting concerns",
            "Extra infrastructure needed"
        ]
