#!/usr/bin/env python3
"""
Flask-based annotation UI for golden candidates.

Serves a web interface for annotating 250 conversations with:
- Primary intent
- Secondary intent (optional)
- Escalation required (yes/no/maybe)
- Ambiguity flag
- Annotator notes
"""

import sys
from pathlib import Path
import json
from flask import Flask, render_template, jsonify, request
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Load candidates and annotations
CANDIDATES_FILE = "data/evaluation/golden_candidates_reduced.jsonl"
ANNOTATIONS_FILE = "data/evaluation/golden_annotations.jsonl"

# Load intent taxonomy
INTENTS = {}
with open("reports/intent_discovery.json") as f:
    discovery = json.load(f)
    for intent, data in discovery['intent_categories'].items():
        INTENTS[intent] = {
            'definition': data['definition'],
            'count': data['count'],
            'pct': data['percentage']
        }

# Load candidates
candidates_map = {}
candidates_list = []

with open(CANDIDATES_FILE) as f:
    for line in f:
        record = json.loads(line)
        conv_id = record['conversation_id']
        candidates_map[conv_id] = record
        candidates_list.append(conv_id)

# Load existing annotations if any
annotations = {}
if Path(ANNOTATIONS_FILE).exists():
    with open(ANNOTATIONS_FILE) as f:
        for line in f:
            record = json.loads(line)
            annotations[record['conversation_id']] = record

print(f"Loaded {len(candidates_list)} candidates")
print(f"Found {len(annotations)} existing annotations")


@app.route('/')
def index():
    """Main annotation interface."""
    progress = {
        'total': len(candidates_list),
        'annotated': len(annotations),
        'remaining': len(candidates_list) - len(annotations),
        'pct': round(100.0 * len(annotations) / len(candidates_list), 1)
    }
    return render_template('annotator.html', progress=progress, intents=INTENTS)


@app.route('/api/candidate')
def get_candidate():
    """Get next candidate to annotate."""
    # Find first unannotated
    for conv_id in candidates_list:
        if conv_id not in annotations:
            candidate = candidates_map[conv_id]
            return jsonify({
                'conversation_id': candidate['conversation_id'],
                'messages': candidate['messages'],
                'metadata': candidate['metadata'],
                'existing_annotation': annotations.get(conv_id)
            })

    # All done
    return jsonify({'all_annotated': True})


@app.route('/api/candidate/<conv_id>')
def get_candidate_by_id(conv_id):
    """Get specific candidate."""
    if conv_id not in candidates_map:
        return jsonify({'error': 'Not found'}), 404

    candidate = candidates_map[conv_id]
    return jsonify({
        'conversation_id': candidate['conversation_id'],
        'messages': candidate['messages'],
        'metadata': candidate['metadata'],
        'existing_annotation': annotations.get(conv_id)
    })


@app.route('/api/annotate', methods=['POST'])
def save_annotation():
    """Save annotation for a conversation."""
    data = request.json
    conv_id = data['conversation_id']

    if conv_id not in candidates_map:
        return jsonify({'error': 'Invalid conversation'}), 400

    annotation = {
        'conversation_id': conv_id,
        'primary_intent': data.get('primary_intent'),
        'secondary_intent': data.get('secondary_intent'),
        'is_ambiguous': data.get('is_ambiguous', False),
        'escalation_required': data.get('escalation_required'),
        'annotator_notes': data.get('annotator_notes', ''),
        'timestamp': datetime.utcnow().isoformat()
    }

    # Save to annotations dict
    annotations[conv_id] = annotation

    # Append to file
    with open(ANNOTATIONS_FILE, 'a') as f:
        f.write(json.dumps(annotation) + '\n')

    progress = {
        'total': len(candidates_list),
        'annotated': len(annotations),
        'remaining': len(candidates_list) - len(annotations),
        'pct': round(100.0 * len(annotations) / len(candidates_list), 1)
    }

    return jsonify({
        'success': True,
        'progress': progress
    })


@app.route('/api/progress')
def get_progress():
    """Get annotation progress."""
    progress = {
        'total': len(candidates_list),
        'annotated': len(annotations),
        'remaining': len(candidates_list) - len(annotations),
        'pct': round(100.0 * len(annotations) / len(candidates_list), 1),
        'estimated_time_remaining_minutes': round((len(candidates_list) - len(annotations)) * 2.5)
    }
    return jsonify(progress)


@app.route('/api/export')
def export_annotations():
    """Export all annotations as JSON."""
    export = {
        'export_date': datetime.utcnow().isoformat(),
        'total_annotated': len(annotations),
        'total_candidates': len(candidates_list),
        'completion_pct': round(100.0 * len(annotations) / len(candidates_list), 1),
        'annotations': list(annotations.values())
    }
    return jsonify(export)


@app.route('/api/stats')
def get_stats():
    """Get annotation statistics."""
    intent_counts = {}
    escalation_counts = {'yes': 0, 'no': 0, 'maybe': 0}
    ambiguous_count = 0

    for annotation in annotations.values():
        intent = annotation.get('primary_intent')
        if intent:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1

        escalation = annotation.get('escalation_required')
        if escalation in escalation_counts:
            escalation_counts[escalation] += 1

        if annotation.get('is_ambiguous'):
            ambiguous_count += 1

    return jsonify({
        'total_annotated': len(annotations),
        'intent_distribution': intent_counts,
        'escalation_distribution': escalation_counts,
        'ambiguous_count': ambiguous_count,
        'completion_pct': round(100.0 * len(annotations) / len(candidates_list), 1)
    })


if __name__ == '__main__':
    print(f"Starting annotation UI on http://localhost:5000")
    print(f"Candidates: {CANDIDATES_FILE}")
    print(f"Annotations: {ANNOTATIONS_FILE}")
    app.run(debug=True, port=5000)
