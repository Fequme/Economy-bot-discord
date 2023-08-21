import logging
import asyncio

#create logger
logger = logging.getLogger('logger')
logger.setLevel(logging.INFO)

# Create handlers
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('log.log', 'w', 'utf-8')
c_handler.setLevel(logging.DEBUG)
f_handler.setLevel(logging.DEBUG)

#create log formatter
c_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]: %(message)s', datefmt='%d-%m-%y %H:%M:%S')
f_formatter = logging.Formatter('%(asctime)s %(levelname)s [%(filename)s:%(lineno)d]: %(message)s', datefmt='%d-%m-%y %H:%M:%S')
c_handler.setFormatter(c_formatter)
f_handler.setFormatter(f_formatter)

# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)