from app import app  # Import objek Flask
from app.routes import routes  # Import Blueprint routes

app.register_blueprint(routes)  # Daftarkan blueprint ke Flask

if __name__ == "__main__":
    app.run(debug=True)
