import json
import openai


def get_ai_recommendation(context):
    prompt = f"""
    Based on the following employee data:
    - Employee Code: {context['employee_code']}
    - Department: {context['department']}
    - Position: {context['position']}
    - Country: {context['country']}
    - Strategic Goal: {context['strategic_goal']}
    - KPI: {context['kpi']}
    - Deliverable: {context['deliverable']}
    - Self Score: {context['self_score'] or 'N/A'}
    - Assessor Score: {context['assessor_score'] or 'N/A'}
    
    Provide recommendations in three categories:
    1. Performance: Suggestions to improve job performance based on strategic goals, KPIs, and scores.
    2. Upskilling: Courses or certifications to enhance skills relevant to the department and position.
    3. Engagement: Activities or events to boost engagement and networking, considering the employee's country.
    
    Return a JSON object with keys 'performance', 'upskilling', and 'engagement', each containing a concise recommendation.
    """
    
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.7,
        )
        
        # Parse the response as JSON
        recommendation_text = response.choices[0].message.content
        try:
            recommendation = json.loads(recommendation_text)
            # Validate required keys
            if not all(key in recommendation for key in ['performance', 'upskilling', 'engagement']):
                raise ValueError("AI response missing required keys")
            return recommendation
        except json.JSONDecodeError:
            # Fallback: parse text manually if not valid JSON
            return {
                "performance": "Improve job performance based on available data.",
                "upskilling": "Consider relevant certifications for your role.",
                "engagement": "Participate in local industry events."
            }
    except Exception as e:
        raise Exception(f"OpenAI API error: {str(e)}")
    





