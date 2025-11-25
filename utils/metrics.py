import tiktoken
from config import Config


class RAGMetrics:
    """Calculate RAG-specific quality metrics for search results"""

    def __init__(self):
        # Using cl100k_base encoding (used by GPT-4 and GPT-3.5-turbo)
        self.encoding = tiktoken.get_encoding("cl100k_base")

    def count_tokens(self, text):
        """Count tokens in text using tiktoken"""
        if not text:
            return 0
        return len(self.encoding.encode(text))

    def calculate_exa_metrics(self, exa_results):
        """
        Calculate metrics for Exa search results

        Exa provides extracted, clean content ready for RAG
        """
        metrics = {
            'total_results': len(exa_results.get('results', [])),
            'has_answer': bool(exa_results.get('answer')),
            'answer_tokens': self.count_tokens(exa_results.get('answer', '')),
            'results': []
        }

        total_content_tokens = 0
        total_content_chars = 0

        for idx, result in enumerate(exa_results.get('results', []), 1):
            content = result.get('content', '')
            content_tokens = self.count_tokens(content)
            total_content_tokens += content_tokens
            total_content_chars += len(content)

            # Count highlights tokens
            highlights = result.get('highlights', [])
            highlights_text = ' '.join(highlights) if highlights else ''
            highlights_tokens = self.count_tokens(highlights_text)

            metrics['results'].append({
                'index': idx,
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'content_length': len(content),
                'content_tokens': content_tokens,
                'highlights_count': len(highlights),
                'highlights_tokens': highlights_tokens,
                'published_date': result.get('published_date', ''),
                'author': result.get('author', ''),
                'has_extracted_content': len(content) > 0
            })

        metrics['total_content_tokens'] = total_content_tokens
        metrics['total_content_chars'] = total_content_chars
        metrics['avg_tokens_per_result'] = (
            total_content_tokens / metrics['total_results']
            if metrics['total_results'] > 0 else 0
        )

        # Calculate how many results fit in different context windows
        metrics['context_window_fit'] = self._calculate_context_fit(
            exa_results.get('results', [])
        )

        return metrics

    def calculate_traditional_metrics(self, traditional_results):
        """
        Calculate metrics for traditional search results

        Traditional search only has snippets, no extracted content
        """
        metrics = {
            'total_results': len(traditional_results.get('results', [])),
            'has_answer': False,  # Traditional search doesn't provide answers
            'answer_tokens': 0,
            'results': []
        }

        total_snippet_tokens = 0
        total_snippet_chars = 0

        for idx, result in enumerate(traditional_results.get('results', []), 1):
            snippet = result.get('snippet', '')
            snippet_tokens = self.count_tokens(snippet)
            total_snippet_tokens += snippet_tokens
            total_snippet_chars += len(snippet)

            metrics['results'].append({
                'index': idx,
                'title': result.get('title', ''),
                'url': result.get('url', ''),
                'snippet_length': len(snippet),
                'snippet_tokens': snippet_tokens,
                'has_extracted_content': False,
                'requires_scraping': True
            })

        metrics['total_snippet_tokens'] = total_snippet_tokens
        metrics['total_snippet_chars'] = total_snippet_chars
        metrics['avg_tokens_per_result'] = (
            total_snippet_tokens / metrics['total_results']
            if metrics['total_results'] > 0 else 0
        )

        # Traditional search snippets are too short to be useful for RAG
        metrics['context_window_fit'] = {
            '4K': 0,
            '8K': 0,
            '16K': 0,
            '32K': 0
        }
        metrics['rag_ready'] = False

        return metrics

    def _calculate_context_fit(self, results):
        """
        Calculate how many results fit in different LLM context windows.

        This shows the practical value: how much information can you
        actually send to an LLM in one request?
        """
        context_windows = Config.CONTEXT_WINDOWS
        fit_counts = {}

        for window_name, window_size in context_windows.items():
            running_tokens = 0
            results_that_fit = 0

            for result in results:
                content_tokens = self.count_tokens(result.get('content', ''))
                if running_tokens + content_tokens <= window_size:
                    running_tokens += content_tokens
                    results_that_fit += 1
                else:
                    break

            fit_counts[window_name] = {
                'results_count': results_that_fit,
                'total_tokens': running_tokens,
                'window_size': window_size,
                'utilization_pct': round((running_tokens / window_size) * 100, 1)
            }

        return fit_counts

    def compare_metrics(self, exa_metrics, traditional_metrics):
        """
        Generate comparison insights between Exa and Traditional search

        This is the key value proposition demonstration
        """
        comparison = {
            'token_advantage': {
                'exa_tokens': exa_metrics['total_content_tokens'],
                'traditional_tokens': traditional_metrics['total_snippet_tokens'],
                'difference': (
                    exa_metrics['total_content_tokens'] -
                    traditional_metrics['total_snippet_tokens']
                ),
                'ratio': (
                    exa_metrics['total_content_tokens'] /
                    traditional_metrics['total_snippet_tokens']
                    if traditional_metrics['total_snippet_tokens'] > 0 else 0
                )
            },
            'rag_readiness': {
                'exa': 'Ready for RAG immediately',
                'traditional': 'Requires scraping, extraction, and cleaning',
                'exa_advantage': 'Single API call vs multiple steps'
            },
            'context_efficiency': {
                'exa_4k_results': (
                    exa_metrics['context_window_fit']['4K']['results_count']
                ),
                'traditional_4k_results': 0,
                'message': (
                    f"Exa fits {exa_metrics['context_window_fit']['4K']['results_count']} "
                    f"full articles in 4K context. Traditional search would need to scrape each URL."
                )
            },
            'has_answer': exa_metrics['has_answer'],
            'developer_burden': {
                'exa': '1 API call, ready to use',
                'traditional': 'API call + N scraping requests + error handling + content extraction'
            }
        }

        return comparison
