from website import create_app

app = create_app()

# run webserver, not import
if __name__ == "__main__":
    app.run(debug=True)