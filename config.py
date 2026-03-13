# ============================================
# AMAZON SCRAPER CONFIGURATION
# ============================================

# Browser display mode
# True = Invisible browser (headless)
# False = Visible browser (window is shown)
HEADLESS_MODE = True

# Minimum delay between requests (seconds)
REQUEST_DELAY_MIN = 2

# Maximum delay between requests (seconds)
REQUEST_DELAY_MAX = 5

# Wait timeout for elements (seconds)
WAIT_TIMEOUT = 5

# WebDriverWait timeout for product detail pages (seconds)
PRODUCT_DETAILS_TIMEOUT = 3

# Browser window size (even in headless mode)
WINDOW_WIDTH = 1920
WINDOW_HEIGHT = 1080

# Realistic User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# ============================================
# SCRAPING OPTIONS
# ============================================

# Maximum number of retries on error
MAX_RETRIES = 3

# Wait time before retrying (seconds)
RETRY_DELAY = 5

