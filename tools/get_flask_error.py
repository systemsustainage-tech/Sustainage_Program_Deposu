import sys
import os
import logging

# Suppress logging
logging.getLogger().setLevel(logging.ERROR)

from flask import Flask, render_template, g, session

# Add project root
sys.path.append('/var/www/sustainage')

from web_app import app, MANAGERS

# Mock session and g
def test_render():
    with app.test_request_context('/social'):
        # Mock login
        with app.test_client() as client:
            with client.session_transaction() as sess:
                sess['user'] = {'id': 1, 'username': 'test'}
                sess['role'] = 'admin'
            
            # Set g.company_id
            g.company_id = 1
            
            # Get data
            manager = MANAGERS.get('social')
            stats = manager.get_stats(1)
            recent_data = manager.get_recent_data(1)
            trends = manager.get_satisfaction_trends(1)
            
            print("Rendering template...")
            try:
                # Render
                rendered = render_template('social.html', 
                                         title='Sosyal Etki', 
                                         stats=stats, 
                                         recent_data=recent_data, 
                                         trends=trends)
                print("Render Success!")
            except Exception as e:
                print("Render Failed!")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_render()
