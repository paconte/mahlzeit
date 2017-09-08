# -*- coding: utf-8 -*-

# Scrapy settings for mahlzeit project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'mahlzeit'

SPIDER_MODULES = ['mahlzeit.spiders']
NEWSPIDER_MODULE = 'mahlzeit.spiders'
LOG_LEVEL = 'WARNING'
DATA_FILES = 'data/'
EXPORT_FILES = DATA_FILES + 'export/'
BACKUP_FILES = DATA_FILES + 'backup/'
IMPORT_FILES = DATA_FILES + 'import/'
FRONTEND_FILES = DATA_FILES + 'frontend/'
LOG_FILE = DATA_FILES + "log/log-mahlzeit.log"
COMMANDS_MODULE = 'mahlzeit.commands'
MONGODB_SERVER = "localhost"
MONGODB_PORT = 27017
MONGODB_DB = "coolinarius"
#MONGODB_COLLECTION = "lunch"
MONGODB_COLLECTION = "lunch_test1"
MONGODB_COLLECTION_BACKUP = BACKUP_FILES + "lunch_backup.json"
FRONTEND_FILE = FRONTEND_FILES + "lunches.json"
VUEJS_PATH = "/home/frevilla/devel/culinarius/"
VUEJS_LUNCH_FILE = VUEJS_PATH + "src/test.js"
VUEJS_DEPLOY_SCRIPT = VUEJS_PATH + "prepare_deploy_script.sh"
CSV_ITEM_NAMES = ['Jouis Nour', 'FOOD']

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'mahlzeit (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'mahlzeit.middlewares.TutorialSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'mahlzeit.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'mahlzeit.pipelines.JsonExportPipeline': 300,
    'mahlzeit.pipelines.CsvExportPipeline': 400,
    'mahlzeit.pipelines.MongoDBPipeline': 500,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 60*60*24
HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
