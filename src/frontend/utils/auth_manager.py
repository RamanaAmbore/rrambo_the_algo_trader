import requests
from dash import callback, Input, Output, State, ctx, no_update
from datetime import datetime, timedelta

from dash.exceptions import PreventUpdate
from flask import session, request

from src.helpers.logger import get_logger

logger = get_logger(__name__)

class AuthManager:
    """
    Manages all authentication-related functionality for the frontend
    """
    def __init__(self, app, api_base_url):
        self.app = app
        self.api_base_url = api_base_url
        self.register_callbacks()
    
    def is_authenticated(self):
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

    def set_user_session(self, token, user_data, remember=False):
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

    def clear_user_session(self):
        """Clear user session"""
        if 'token' in session:
            session.pop('token')
        if 'user' in session:
            session.pop('user')
        if 'expiry' in session:
            session.pop('expiry')
        logger.info("User session cleared")
    
    def register_callbacks(self):
        """Register all authentication-related callbacks"""
    
        # For all auth actions, we'll use separate callbacks with pattern-matching
    
        # Sign-in callback
        @callback(
            Output('auth-store', 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
            Input('signin-submit', 'n_clicks'),
            [State('username-input', 'value'),
             State('password-input', 'value'),
             State('remember-me', 'value')],
            prevent_initial_call=True
        )
        def handle_signin(signin_clicks, username, password, remember):
            """Handle sign-in action"""
            if not signin_clicks:
                raise PreventUpdate
            
            # Your existing sign-in logic here
            trigger_id = 'signin-submit'
            auth_data = {}
            pathname = no_update
        
            if not username or not password:
                auth_data = {'success': False, 'message': 'Please enter both username and password'}
            else:
                try:
                    # API call to sign in
                    response = requests.post(
                        f"{self.api_base_url}/auth/signin", 
                        json={'username': username, 'password': password},
                        headers={'X-Requested-With': 'XMLHttpRequest'}
                    )
                
                    if response.status_code == 200:
                        data = response.json()
                        # Set cookie and session
                        self.set_user_session(data['token'], data['user'], remember)
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
                
            return auth_data, pathname
    
        # Sign-up callback
        @callback(
            Output('auth-store', 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
            Input('signup-submit', 'n_clicks'),
            [State('username-input', 'value'),
             State('email-input', 'value'),
             State('password-input', 'value'),
             State('confirm-password-input', 'value'),
             State('terms-checkbox', 'value'),
             State('remember-me', 'value')],
            prevent_initial_call=True
        )
        def handle_signup(signup_clicks, username, email, password, confirm_password, terms, remember):
            """Handle sign-up action"""
            if not signup_clicks:
                raise PreventUpdate
            
            # Your existing sign-up logic here
            auth_data = {}
            pathname = no_update
        
            if not username or not email or not password or not confirm_password:
                auth_data = {'success': False, 'message': 'Please fill all fields'}
            elif password != confirm_password:
                auth_data = {'success': False, 'message': 'Passwords do not match'}
            else:
                try:
                    # API call to sign up
                    response = requests.post(
                        f"{self.api_base_url}/auth/signup", 
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
                        self.set_user_session(data['token'], data['user'], remember)
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
                
            return auth_data, pathname
    
        # Sign-out callback
        @callback(
            Output('auth-store', 'data', allow_duplicate=True),
            Output('url', 'pathname', allow_duplicate=True),
            Input('signout-btn', 'n_clicks'),
            prevent_initial_call=True
        )
        def handle_signout(signout_clicks):
            """Handle sign-out action"""
            if not signout_clicks:
                raise PreventUpdate
            
            # Clear session
            self.clear_user_session()
            auth_data = {
                'success': True, 
                'message': 'Signed out successfully',
                'authenticated': False
            }
            pathname = '/sign_in'  # Redirect to sign-in
        
            return auth_data, pathname
    
        # Keep your existing authentication status middleware and message callbacks
        # ...

        # Authentication status middleware
        @callback(
            [Output('auth-status', 'children'),
             Output('url', 'pathname', allow_duplicate=True)],
            Input('url', 'pathname'),
            State('auth-store', 'data'),
            prevent_initial_call=True
        )
        def authenticate_user(pathname, auth_data):
            """
            Check if user is authenticated and redirect if necessary
            """
            # List of paths that require authentication
            protected_routes = ['/dashboard', '/profile', '/settings', '/orders', '/trades']
            # List of paths that should redirect to dashboard if user is already authenticated
            auth_routes = ['/sign_in', '/sign_up']
            
            # Current authentication status
            is_authenticated = auth_data and auth_data.get('authenticated', False)
            
            # Check if current path requires authentication
            if pathname in protected_routes and not is_authenticated:
                # User is not authenticated but trying to access protected route
                return None, '/sign_in'
            
            # Check if user is already authenticated and trying to access auth routes
            elif pathname in auth_routes and is_authenticated:
                # User is authenticated but trying to access auth routes like sign in
                return None, '/dashboard'
            
            # Regular access, no redirection needed
            return None, no_update

        # Initialize auth store from session or API
        @callback(
            Output('auth-store', 'data', allow_duplicate=True),
            Input('url', 'pathname'),
            State('auth-store', 'data'),
            prevent_initial_call=True
        )
        def initialize_auth_store(pathname, current_data):
            """
            Initialize the auth store with session data if available
            """
            # Only run on initial page load if data is not set
            if current_data is None:
                try:
                    # Check session with backend
                    response = requests.get(
                        f"{self.api_base_url}/auth/check_session", 
                        cookies=request.cookies,
                        headers={'X-Requested-With': 'XMLHttpRequest'}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        return {
                            'authenticated': True,
                            'user_id': data.get('user_id'),
                            'username': data.get('username'),
                        }
                except Exception as e:
                    logger.error(f"Error checking session: {str(e)}")
            
            # Otherwise, do not update
            return no_update
            
        # Callback to update sign-in form feedback
        @callback(
            Output('signin-message', 'children'),
            Output('signin-message', 'className'),
            Input('auth-store', 'data')
        )
        def update_signin_message(auth_data):
            if not auth_data:
                return '', 'auth-message'
            
            if auth_data.get('success'):
                return auth_data.get('message', 'Success'), 'auth-message success-message'
            else:
                return auth_data.get('message', 'Error occurred'), 'auth-message error-message'
                
        # Callback to update sign-up form feedback
        @callback(
            Output('signup-message', 'children'),
            Output('signup-message', 'className'),
            Input('auth-store', 'data')
        )
        def update_signup_message(auth_data):
            if not auth_data:
                return '', 'auth-message'
            
            if auth_data.get('success'):
                return auth_data.get('message', 'Success'), 'auth-message success-message'
            else:
                return auth_data.get('message', 'Error occurred'), 'auth-message error-message'