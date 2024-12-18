import json
import random
from datetime import datetime
from pathlib import Path

class ContentStrategyManager:
    def __init__(self, strategy_file='config/content_strategy.json'):
        self.strategy_file = strategy_file
        self.load_strategy()

    def load_strategy(self):
        """Load content strategy from JSON file"""
        with open(self.strategy_file, 'r') as f:
            self.strategy = json.load(f)

    def save_strategy(self):
        """Save current strategy to JSON file"""
        with open(self.strategy_file, 'w') as f:
            json.dump(self.strategy, f, indent=4)

    def get_content_prompt(self, platform='twitter'):
        """Generate a content prompt based on current time and strategy"""
        current_time = datetime.now()
        day_of_week = current_time.strftime('%A').lower()
        hour = current_time.hour

        # Get daily themes
        daily_themes = self.strategy['content_calendar']['themes'].get(day_of_week, [])
        
        # Select content type based on frequency
        content_types = self.strategy['content_strategy']['content_types']
        content_type = random.choices(
            list(content_types.keys()),
            weights=[float(t['frequency'].strip('%')) for t in content_types.values()]
        )[0]
        
        # Get target audience info
        audience = self.strategy['target_audience']
        
        # Build prompt
        prompt = f"""Create a {platform} post for {audience['demographics']['occupation']} about {random.choice(daily_themes)}.
Content type: {content_type}
Tone: {self.strategy['content_strategy']['tone_of_voice']['primary']}
Target audience interests: {', '.join(audience['demographics']['interests'])}
Pain points to address: {random.choice(audience['demographics']['pain_points'])}
Format: {content_types[content_type]['format']}
Post length: {self.strategy['content_guidelines']['post_length'][platform]['optimal']} characters
Include a call to action from: {', '.join(self.strategy['content_guidelines']['call_to_action']['types'])}
"""
        return prompt

    def get_hashtags(self, count=None):
        """Get relevant hashtags for the post"""
        if count is None:
            count = self.strategy['content_strategy']['hashtag_strategy']['max_tags_per_post']
        
        primary = self.strategy['content_strategy']['hashtag_strategy']['primary_tags']
        secondary = self.strategy['content_strategy']['hashtag_strategy']['secondary_tags']
        
        # Prioritize primary tags
        selected = random.sample(primary, min(count, len(primary)))
        if len(selected) < count:
            selected.extend(random.sample(secondary, min(count - len(selected), len(secondary))))
        
        return selected

    def evaluate_content(self, content, platform='twitter'):
        """Evaluate if content meets guidelines"""
        guidelines = self.strategy['content_guidelines']
        length_rules = guidelines['post_length'][platform]
        
        evaluation = {
            'meets_length': length_rules['min'] <= len(content) <= length_rules['max'],
            'is_optimal_length': abs(len(content) - length_rules['optimal']) <= 20,
            'has_call_to_action': any(cta.lower() in content.lower() 
                                    for cta in guidelines['call_to_action']['types']),
            'matches_tone': all(tone not in content.lower() 
                              for tone in self.strategy['content_strategy']['tone_of_voice']['avoid'])
        }
        
        return evaluation

    def update_performance_metrics(self, metrics):
        """Update performance metrics and adjust strategy if needed"""
        current_metrics = self.strategy['performance_metrics']['key_indicators']
        triggers = self.strategy['performance_metrics']['adjustment_triggers']
        
        # Check if adjustments are needed
        if metrics['engagement_rate'] < float(triggers['low_engagement'].split('%')[0]) / 100:
            # Adjust strategy for low engagement
            self._adjust_strategy_for_low_engagement()
        elif metrics['engagement_rate'] > float(triggers['high_engagement'].split('%')[0]) / 100:
            # Reinforce successful patterns
            self._adjust_strategy_for_high_engagement()
        
        # Update metrics
        self.strategy['performance_metrics']['key_indicators'].update(metrics)
        self.save_strategy()

    def _adjust_strategy_for_low_engagement(self):
        """Adjust strategy when engagement is low"""
        # Increase engagement_questions frequency
        content_types = self.strategy['content_strategy']['content_types']
        content_types['engagement_questions']['frequency'] = '20%'
        content_types['tips_and_tricks']['frequency'] = '30%'
        
        # Update posting times
        for content_type in content_types.values():
            content_type['best_times'] = ['09:00', '12:00', '17:00']

    def _adjust_strategy_for_high_engagement(self):
        """Reinforce successful patterns when engagement is high"""
        # Maintain current content mix but optimize timing
        pass  # Implement based on specific requirements

    def get_best_posting_time(self, content_type):
        """Get the best posting time for specific content type"""
        return self.strategy['content_strategy']['content_types'][content_type]['best_times']
