from app import create_app

app = create_app()
print('Run: Create App')
 
if __name__ == '__main__':
    app.run(port=8080, debug=False)