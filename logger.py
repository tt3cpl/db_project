import logging
import os

<<<<<<< HEAD
log_file = os.path.join(os.path.dirname(__file__), "app.log")
=======
log_file = os.path.join(os.path.dirname(__file__), 'app.log')
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
<<<<<<< HEAD
    format="%(asctime)s - %(levelname)s - %(message)s",
=======
    format='%(asctime)s - %(levelname)s - %(message)s'
>>>>>>> d8d353c4260bb55e6728d0a2be9f2b8092c1954a
)

logger = logging.getLogger(__name__)
