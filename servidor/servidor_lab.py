from lab_v5.server import app

if __name__ == "__main__":
    import os
    app.run(host=os.environ.get("LAB_HOST", "127.0.0.1"), port=int(os.environ.get("LAB_PORT", "5000")), debug=False)
