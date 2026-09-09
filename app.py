from flask import Flask
from flask_login import LoginManager
from config import Config
from models import db, User
import os

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Ensure directories exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs('static/images', exist_ok=True)

# Initialize database
db.init_app(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please login to access this page.'
login_manager.login_message_category = 'warning'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Create tables and admin user
with app.app_context():
    db.create_all()
    
    # Create admin if not exists
    admin = User.query.filter_by(mobile=Config.ADMIN_MOBILE).first()
    if not admin:
        admin = User(
            name='VyahMandap Admin',
            mobile=Config.ADMIN_MOBILE,
            email='admin@vyahmandap.com',
            role='admin'
        )
        admin.set_password(Config.ADMIN_PASSWORD)
        db.session.add(admin)
        db.session.commit()
        print('✅ Admin user created successfully!')
    
    # Create demo customer if not exists
    demo = User.query.filter_by(mobile='9876543210').first()
    if not demo:
        demo = User(
            name='Demo Customer',
            mobile='9876543210',
            email='demo@vyahmandap.com',
            role='customer'
        )
        demo.set_password('123456')
        db.session.add(demo)
        db.session.commit()
        print('✅ Demo customer created successfully!')

# Register blueprints
from routes import auth, main, admin

app.register_blueprint(auth.bp)
app.register_blueprint(main.bp)
app.register_blueprint(admin.bp)

# Context processors
@app.context_processor
def utility_processor():
    from config import Config
    from utils import format_currency, get_category_icon, get_category_label
    return dict(
        app_name=Config.APP_NAME,
        app_tagline=Config.APP_TAGLINE,
        business_phone=Config.BUSINESS_PHONE,
        business_phone_alt=Config.BUSINESS_PHONE_ALT,
        business_location=Config.BUSINESS_LOCATION,
        categories=Config.CATEGORIES,
        format_currency=format_currency,
        get_category_icon=get_category_icon,
        get_category_label=get_category_label,
        Config=Config
    )

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
