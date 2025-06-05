# chart_utils.py
import matplotlib.pyplot as plt
import numpy as np
import base64
from io import BytesIO
from collections import defaultdict

from results.models import Teacher, Student
def is_teacher(user):
    return Teacher.objects.filter(user=user).exists()
def is_student(user):
    return Student.objects.filter(user=user).exists()



def process_quiz_data(results):
    """Process quiz results to calculate accuracy by topic"""
    topic_stats = defaultdict(lambda: {'correct': 0, 'total': 0})

    for result in results:
        # Extract clean topic name (remove path and .json)
        topic = result['topic'].split('/')[-1].replace('.json', '')
        topic_stats[topic]['total'] += 1
        if result['is_correct']:
            topic_stats[topic]['correct'] += 1

    topics = list(topic_stats.keys())
    accuracy = [(stats['correct'] / stats['total']) * 100 for stats in topic_stats.values()]

    return topics, accuracy

def create_radar_chart(topics, accuracy):
    """Create a radar chart and return as base64 encoded image"""
    num_vars = len(topics)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]
    accuracy += accuracy[:1]

    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))

    # Plot styling
    ax.plot(angles, accuracy, color='#1f77b4', linewidth=2, linestyle='solid', marker='o', markersize=8)
    ax.fill(angles, accuracy, color='#1f77b4', alpha=0.25)
    plt.xticks(angles[:-1], topics, color='grey', size=12)
    ax.set_rlabel_position(30)
    plt.yticks([20, 40, 60, 80, 100], ["20%", "40%", "60%", "80%", "100%"], color="grey", size=10)
    plt.ylim(0, 100)
    plt.title('Quiz Performance by Topic', size=15, y=1.1)

    # Add grid
    ax.grid(color='grey', linestyle='-', linewidth=0.5, alpha=0.5)

    # Save plot to a BytesIO object
    buffer = BytesIO()
    plt.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
    plt.close(fig)  # Important to close the figure to free memory
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()

    return base64.b64encode(image_png).decode('utf-8')

def generate_quiz_report(results):
    """Generate complete report with processed data and chart"""
    topics, accuracy = process_quiz_data(results)
    chart_image = create_radar_chart(topics, accuracy)

    return {
        'topics': topics,
        'accuracy': accuracy,
        'chart_image': chart_image,
        'total_questions': len(results),
        'correct_answers': sum(1 for r in results if r['is_correct']),
    }
