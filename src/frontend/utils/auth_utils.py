import time
import json
import requests
from dash import callback, Input, Output, State, ctx, no_update
from datetime import datetime, timedelta
from flask import session, request

from src.helpers.logger import get_logger

logger = get_logger(__name__)

def is_authenticated():
    """Check if user is authenticated and token is still valid"""
    try:
        # Get the session expiry time
        expiry = session.get('expiry')
        if not expiry:
            return False
            
        # Check if token is expired
        if datetime.now().timestamp() > expiry:
            return False
            
        # If token exists and is not expired, user is authenticated
        return 'token' in session and session['token']
    except Exception as e:
        logger.error(f"Error checking authentication status: {str(e)}")
        return False

def set_user_session(token, user_data, remember=False):
    """Set user session with token and expiry"""
    # Set token in session
    session['token'] = token
    session['user'] = user_data
    
    # Calculate expiry (7 days from now if remember me, else 24 hours)
    if remember:
        expiry = datetime.now() + timedelta(days=7)
    else:
        expiry = datetime.now() + timedelta(days=1)
        
    session['expiry'] = expiry.timestamp()
    logger.info(f"User session set for {user_data.get('username')} with expiry on {expiry}")

def clear_user_session():
    """Clear user session"""
    if 'token' in session:
        session.pop('token')
    if 'user' in session:
        session.pop('user')
    if 'expiry' in session:
        session.pop('expiry')
    logger.info("User session cleared")

def register_auth_callbacks(app, api_base_url):
    """Register authentication callbacks for the app"""
    
    @callback(
        Output('auth-store', 'data'),
        Output('url', 'pathname', allow_duplicate=True),
        [Input('signin-submit', 'n_clicks'),
         Input('signup-submit', 'n_clicks'),
         Input('signout-btn', 'n_clicks')],
        [State('username-input', 'value'),
         State('password-input', 'value'),
         State('email-input', 'value'), 
         State('confirm-password-input', 'value'),
         State('remember-me', 'checked')],
        prevent_initial_call=True
    )
    def handle_auth_action(signin_clicks, signup_clicks, signout_clicks, 
                         username, password, email, confirm_password, remember):
        """Handle authentication actions (sign in, sign up, sign out)"""
        trigger_id = ctx.triggered_id
        
        # Default values
        auth_data = {}
        pathname = no_update
        
        # Handle sign-in
        if trigger_id == 'signin-submit' and signin_clicks:
            if not username or not password:
                auth_data = {'success': False, 'message': 'Please enter both username and password'}
            else:
                try:
                    # API call to sign in
                    response = requests.post(
                        f"{api_base_url}/auth/signin", 
                        json={'username': username, 'password': password},
                        headers={'X-Requested-With': 'XMLHttpRequest'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        # Set cookie and session
                        set_user_session(data['token'], data['user'], remember)
                        auth_data = {
                            'success': True, 
                            'message': 'Sign in successful',
                            'authenticated': True,
                            'user_id': data['user'].get('id'),
                            'username': data['user'].get('username')
                        }
                        pathname = '/dashboard'  # Redirect to dashboard
                    else:
                        error_data = response.json()
                        auth_data = {'success': False, 'message': error_data.get('message', 'Invalid credentials')}
                except Exception as e:
                    logger.error(f"Sign-in error: {str(e)}")
                    auth_data = {'success': False, 'message': f'Connection error: Could not reach authentication service'}
        
        # Handle sign-up
        elif trigger_id == 'signup-submit' and signup_clicks:
            if not username or not email or not password or not confirm_password:
                auth_data = {'success': False, 'message': 'Please fill all fields'}
            elif password != confirm_password:
                auth_data = {'success': False, 'message': 'Passwords do not match'}
            else:
                try:
                    # API call to sign up
                    response = requests.post(
                        f"{api_base_url}/auth/signup", 
                        json={
                            'username': username, 
                            'email': email, 
                            'password': password
                        },
                        headers={'X-Requested-With': 'XMLHttpRequest'}
                    )
                    
                    if response.status_code == 201:
                        data = response.json()
                        # Set cookie and session
                        set_user_session(data['token'], data['user'], remember)
                        auth_data = {
                            'success': True, 
                            'message': 'Account created successfully',
                            'authenticated': True,
                            'user_id': data['user'].get('id'),
                            'username': data['user'].get('username')
                        }
                        pathname = '/dashboard'  # Redirect to dashboard
                    else:
                        error_data = response.json()
                        auth_data = {
                            'success': False, 
                            'message': error_data.get('message', 'Registration failed')
                        }
                except Exception as e:
                    logger.error(f"Sign-up error: {str(e)}")
                    auth_data = {'success': False, 'message': f'Connection error: Could not reach registration service'}
        
        # Handle sign-out
        elif trigger_id == 'signout-btn' and signout_clicks:
            # Clear session
            clear_user_session()
            auth_data = {
                'success': True, 
                'message': 'Signed out successfully',
                'authenticated': False
            }
            pathname = '/sign_in'  # Redirect to sign-in
            
        return auth_data, pathname