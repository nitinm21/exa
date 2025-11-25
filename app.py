from flask import Flask, render_template, request, jsonify
from config import Config
from utils.exa_client import ExaSearchWrapper
from utils.traditional_search import TraditionalSearchMock, TraditionalSearchNote
from utils.metrics import RAGMetrics

app = Flask(__name__)


@app.route('/')
def index():
    """Render the main search page"""
    return render_template('index.html')


@app.route('/compare', methods=['POST'])
def compare():
    """
    Execute search comparison between Exa and traditional search.
    Returns metrics, results, and insights comparing both approaches.
    """
    query = request.form.get('query', '').strip()
    max_results = int(request.form.get('max_results', Config.DEFAULT_MAX_RESULTS))

    if not query:
        return jsonify({'error': 'Query is required'}), 400

    # Initialize clients
    exa_client = ExaSearchWrapper()
    traditional_client = TraditionalSearchMock()
    metrics_calculator = RAGMetrics()

    # Execute searches
    exa_results = exa_client.search(query, max_results)

    # Check for Exa API errors
    if 'error' in exa_results and not exa_results.get('results'):
        return jsonify({
            'error': f'Exa API error: {exa_results["error"]}'
        }), 500

    # Get AI-generated answer using Exa's Answer API
    exa_answer = exa_client.get_answer(query)

    traditional_results = traditional_client.search(query, max_results)

    # Calculate metrics
    exa_metrics = metrics_calculator.calculate_exa_metrics(exa_results)
    traditional_metrics = metrics_calculator.calculate_traditional_metrics(traditional_results)

    # Generate comparison insights
    comparison = metrics_calculator.compare_metrics(exa_metrics, traditional_metrics)

    # Get workflow explanation for traditional search
    workflow_steps = TraditionalSearchNote.get_workflow_steps()
    traditional_problems = TraditionalSearchNote.get_problems()

    return jsonify({
        'query': query,
        'exa': {
            'results': exa_results,
            'metrics': exa_metrics,
            'ai_answer': exa_answer
        },
        'traditional': {
            'results': traditional_results,
            'metrics': traditional_metrics,
            'workflow_steps': workflow_steps,
            'problems': traditional_problems
        },
        'comparison': comparison
    })


@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'exa_api_configured': bool(Config.EXA_API_KEY)
    })


if __name__ == '__main__':
    app.run(debug=Config.FLASK_DEBUG, port=5000)
