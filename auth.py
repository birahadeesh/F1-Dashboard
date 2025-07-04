from flask_login import LoginManager
from models import User, db
from supabase import create_client
from config import Config
import uuid

login_manager = LoginManager()
login_manager.login_view = 'login'

# Initialize Supabase client
try:
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
except Exception as e:
    print(f"Error initializing Supabase client: {e}")
    supabase = None

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID."""
    return User.query.get(user_id)

def register_user(email, password, username):
    """Register a new user with Supabase and store in local database."""
    try:
        # Register user with Supabase
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        
        # Check if registration was successful
        if response.user and response.user.id:
            # Create local user record
            user = User(
                id=response.user.id,
                email=email,
                username=username
            )
            db.session.add(user)
            db.session.commit()
            return user, None
        else:
            return None, "Registration failed. Please try again."
    except Exception as e:
        return None, str(e)

def login_user_with_supabase(email, password):
    """Sign in a user with Supabase and retrieve from local database."""
    try:
        # Sign in with Supabase
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Check if login was successful
        if response.user and response.user.id:
            # Get the user from local database
            user = User.query.get(response.user.id)
            
            # If user doesn't exist in local database yet, create it
            if not user:
                user = User(
                    id=response.user.id,
                    email=email,
                    username=email.split('@')[0]  # Default username from email
                )
                db.session.add(user)
                db.session.commit()
                
            return user, None
        else:
            return None, "Login failed. Please check your credentials."
    except Exception as e:
        return None, str(e)

def logout_from_supabase():
    """Sign out the user from Supabase."""
    try:
        supabase.auth.sign_out()
        return True, None
    except Exception as e:
        return False, str(e)

def reset_password(email):
    """Send password reset email to user."""
    try:
        response = supabase.auth.reset_password_for_email(email)
        return True, "Password reset instructions have been sent to your email."
    except Exception as e:
        return False, str(e) 