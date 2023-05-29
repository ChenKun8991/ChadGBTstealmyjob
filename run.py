from app import create_app
from app.models import populate_data, drop_all_tables
app = create_app()

if __name__ == '__main__':
    with app.app_context():
        print("pass")
        drop_all_tables()
        populate_data()
    app.run()