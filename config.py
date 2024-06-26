# Statement for enabling the development environment
DEBUG = True

# Define the application directory
import os
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Define the database - we are working with
# SQLite for this example
DATABASE_CONNECT_OPTIONS = {"database":'flujo_dev',
  "host":'api.fintechile.cl',
   "port":'5432',
   "user":'flujo',
   "password":'123456'
}

# Application threads. A common general assumption is
# using 2 per available processor cores - to handle
# incoming requests using one and performing background
# operations using the other.
THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED = True

# Use a secure, unique and absolutely secret key for
# signing the data.
CSRF_SESSION_KEY = "asdwerweafazxcdqcaf"

# Secret key for signing cookies
SECRET_KEY = "123sdwrfdqwvr623em"