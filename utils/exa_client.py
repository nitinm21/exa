import re
from exa_py import Exa
from config import Config


def clean_markdown_text(text):
    """
    Clean markdown formatting from text to get plain readable content.

    Removes:
    - Markdown links [text](url) -> text
    - Markdown images ![alt](url) -> alt
    - Markdown tables (| ... |)
    - Markdown headers (# symbols)
    - Bold/italic markers
    - Extra whitespace and newlines
    """
    if not text:
        return ''

    # Remove markdown images ![alt](url)
    text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)

    # Remove markdown links [text](url) -> text
    text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)

    # Remove markdown headers (# at start of line)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)

    # Remove bold markers **text** or __text__
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)
    text = re.sub(r'__([^_]+)__', r'\1', text)

    # Remove italic markers *text* or _text_
    text = re.sub(r'\*([^*]+)\*', r'\1', text)
    text = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', text)

    # Remove inline code backticks
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove markdown table formatting (lines with | characters)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Skip table separator lines (|---|---|)
        if re.match(r'^\s*\|[\s\-:|]+\|\s*$', line):
            continue
        # Clean table row lines - extract content between pipes
        if '|' in line and line.strip().startswith('|'):
            # Extract cell contents
            cells = [cell.strip() for cell in line.split('|') if cell.strip()]
            if cells:
                cleaned_lines.append(' - '.join(cells))
        else:
            cleaned_lines.append(line)

    text = '\n'.join(cleaned_lines)

    # Remove excessive newlines (more than 2 consecutive)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Clean up whitespace
    text = re.sub(r'[ \t]+', ' ', text)

    return text.strip()


class ExaSearchWrapper:
    """Wrapper for Exa Search API"""

    def __init__(self):
        self.client = Exa(api_key=Config.EXA_API_KEY)

    def search(self, query, max_results=5):
        """
        Execute a search using Exa API

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            Dictionary containing search results and metadata
        """
        try:
            # Use search_and_contents to get full text in one call
            # Set include_html_tags=False for clean text without HTML artifacts
            response = self.client.search_and_contents(
                query=query,
                num_results=max_results,
                type="auto",
                text={
                    "max_characters": 10000,
                    "include_html_tags": False
                }
            )

            formatted_results = {
                'query': query,
                'answer': '',  # Exa doesn't provide direct answers like Tavily
                'results': [],
                'raw_response': response
            }

            # Process results from Exa response
            for result in response.results:
                # Get raw text and clean markdown formatting
                raw_text = getattr(result, 'text', '')
                clean_text = clean_markdown_text(raw_text)

                formatted_results['results'].append({
                    'title': getattr(result, 'title', 'No title'),
                    'url': getattr(result, 'url', ''),
                    'content': clean_text,
                    'score': getattr(result, 'score', 0) if hasattr(result, 'score') else 0,
                    'highlights': getattr(result, 'highlights', []),
                    'published_date': getattr(result, 'published_date', ''),
                    'author': getattr(result, 'author', '')
                })

            # Generate a summary from highlights if available
            all_highlights = []
            for result in formatted_results['results']:
                if result.get('highlights'):
                    all_highlights.extend(result['highlights'])

            if all_highlights:
                formatted_results['answer'] = ' '.join(all_highlights[:5])

            return formatted_results

        except Exception as e:
            return {
                'error': str(e),
                'query': query,
                'results': []
            }

    def get_extracted_content_length(self, results):
        """Get total length of extracted content"""
        total = 0
        for result in results.get('results', []):
            total += len(result.get('content', ''))
        return total

    def get_result_urls(self, results):
        """Extract URLs from results"""
        return [r.get('url', '') for r in results.get('results', [])]

    def get_answer(self, query):
        """
        Get an AI-generated answer for the query using Exa's Answer API.

        Args:
            query: The question or query to answer

        Returns:
            Dictionary containing the answer (without inline citations)
        """
        try:
            response = self.client.answer(
                query=query,
                text=True
            )

            raw_answer = getattr(response, 'answer', '')
            # Remove inline markdown citations like ([text](url)), [text](url), and grouped citations
            # Handle patterns like: ([Source1](url1), [Source2](url2))
            clean_answer = re.sub(r'\s*\([^()]*\[[^\]]*\]\([^)]+\)[^()]*\)', '', raw_answer)
            clean_answer = re.sub(r'\s*\[[^\]]*\]\([^)]+\)', '', clean_answer)
            # Clean up any leftover artifacts
            clean_answer = re.sub(r'\s*,\s*\)', ')', clean_answer)
            clean_answer = re.sub(r'\(\s*,?\s*\)', '', clean_answer)
            clean_answer = re.sub(r'\s+\)', ')', clean_answer)  # Remove space before )
            clean_answer = re.sub(r'([.!?])\s*\)', r'\1', clean_answer)  # Remove ) after punctuation
            clean_answer = re.sub(r'\)\s*([.!?])', r'\1', clean_answer)  # Remove ) before punctuation
            # Remove markdown formatting
            clean_answer = re.sub(r'\*\*([^*]+)\*\*', r'\1', clean_answer)  # Bold **text**
            clean_answer = re.sub(r'\*([^*]+)\*', r'\1', clean_answer)  # Italic *text*
            clean_answer = re.sub(r'^[\s]*\*\s+', '', clean_answer, flags=re.MULTILINE)  # Bullet points
            clean_answer = re.sub(r'#{1,6}\s*', '', clean_answer)  # Headers
            clean_answer = re.sub(r'`([^`]+)`', r'\1', clean_answer)  # Inline code
            # Final cleanup
            clean_answer = re.sub(r'\s+([.,!?])', r'\1', clean_answer)  # Fix spacing before punctuation
            clean_answer = re.sub(r'\s{2,}', ' ', clean_answer)  # Collapse multiple spaces
            clean_answer = re.sub(r'\n{2,}', '\n\n', clean_answer)  # Collapse multiple newlines
            clean_answer = clean_answer.strip()

            # Extract citation URLs for source counting
            citation_urls = [
                getattr(c, 'url', '')
                for c in getattr(response, 'citations', [])
            ]

            return {
                'answer': clean_answer,
                'citation_urls': citation_urls,
                'error': None
            }

        except Exception as e:
            return {
                'answer': '',
                'citation_urls': [],
                'error': str(e)
            }
