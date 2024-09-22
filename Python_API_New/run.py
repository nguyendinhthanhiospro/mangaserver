from api_manga import *
from api_get_home import *
from api_account_management import *

# with app.app_context():
#     db.create_all()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7979)
