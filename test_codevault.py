import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time
import random

class TestCodeVault:
    
    @pytest.fixture
    def driver(self):
        """Setup headless Chrome driver for Jenkins"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Headless mode for Jenkins
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        
        # Auto-manage ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.implicitly_wait(10)
        yield driver
        driver.quit()
    
    def generate_unique_username(self):
        """Generate unique username for tests"""
        return f"testuser_{int(time.time())}_{random.randint(1000, 9999)}"
    
    # ========== TEST CASES (15+ tests) ==========
    
    def test_01_homepage_loads(self, driver):
        """Test 1: Verify homepage loads successfully"""
        driver.get("http://localhost:5000")
        assert "CODEVAULT" in driver.page_source or "SNIPPET VAULT" in driver.page_source
        print("✓ Test 1 passed: Homepage loads")
    
    def test_02_register_page_loads(self, driver):
        """Test 2: Verify registration page loads"""
        driver.get("http://localhost:5000/register")
        assert driver.find_element(By.ID, "username")
        assert driver.find_element(By.ID, "email")
        assert driver.find_element(By.ID, "password")
        assert driver.find_element(By.ID, "confirm")
        print("✓ Test 2 passed: Registration page loads")
    
    def test_03_successful_registration(self, driver):
        """Test 3: Register a new user successfully"""
        driver.get("http://localhost:5000/register")
        
        username = self.generate_unique_username()
        email = f"{username}@example.com"
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        assert "Account created" in driver.page_source
        print(f"✓ Test 3 passed: User {username} registered")
    
    def test_04_registration_password_mismatch(self, driver):
        """Test 4: Registration fails when passwords don't match"""
        driver.get("http://localhost:5000/register")
        
        driver.find_element(By.ID, "username").send_keys("testuser")
        driver.find_element(By.ID, "email").send_keys("test@example.com")
        driver.find_element(By.ID, "password").send_keys("password123")
        driver.find_element(By.ID, "confirm").send_keys("different123")
        driver.find_element(By.ID, "register-btn").click()
        
        assert "Passwords do not match" in driver.page_source
        print("✓ Test 4 passed: Password mismatch handled")
    
    def test_05_registration_duplicate_user(self, driver):
        """Test 5: Registration fails with existing username"""
        driver.get("http://localhost:5000/register")
        
        username = "duplicate_test_user"
        
        # First registration
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        # Try to register again
        driver.get("http://localhost:5000/register")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys("different@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        assert "Username or email already exists" in driver.page_source
        print("✓ Test 5 passed: Duplicate user prevented")
    
    def test_06_login_page_loads(self, driver):
        """Test 6: Verify login page loads"""
        driver.get("http://localhost:5000/login")
        assert driver.find_element(By.ID, "username")
        assert driver.find_element(By.ID, "password")
        assert "AUTHENTICATE" in driver.page_source
        print("✓ Test 6 passed: Login page loads")
    
    def test_07_successful_login(self, driver):
        """Test 7: Login with valid credentials"""
        # Register first
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        # Login
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        
        assert f"Welcome back, {username}" in driver.page_source
        print(f"✓ Test 7 passed: User {username} logged in")
    
    def test_08_login_invalid_credentials(self, driver):
        """Test 8: Login fails with invalid credentials"""
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys("nonexistent_user")
        driver.find_element(By.ID, "password").send_keys("wrongpassword")
        driver.find_element(By.ID, "login-btn").click()
        
        assert "Invalid username or password" in driver.page_source
        print("✓ Test 8 passed: Invalid login handled")
    
    def test_09_logout_functionality(self, driver):
        """Test 9: User can logout successfully"""
        # Register and login
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        
        # Click logout
        logout_link = driver.find_element(By.LINK_TEXT, "[ LOGOUT ]")
        logout_link.click()
        
        assert "You have been logged out" in driver.page_source
        assert "LOGIN" in driver.page_source
        print("✓ Test 9 passed: Logout works")
    
    def test_10_add_snippet_requires_login(self, driver):
        """Test 10: Adding snippet redirects to login when not authenticated"""
        driver.get("http://localhost:5000/add")
        assert "login" in driver.current_url
        assert "Please log in" in driver.page_source
        print("✓ Test 10 passed: Add snippet requires login")
    
    def test_11_add_snippet_successfully(self, driver):
        """Test 11: Authenticated user can add a snippet"""
        # Register and login
        driver.get("http://localhost:5000/register")
        username = self.generate_unique_username()
        
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass123")
        driver.find_element(By.ID, "register-btn").click()
        
        driver.get("http://localhost:5000/login")
        driver.find_element(By.ID, "username").send_keys(username)
        driver.find_element(By.ID, "password").send_keys("TestPass123")
        driver.find_element(By.ID, "login-btn").click()
        
        # Add snippet
        driver.get("http://localhost:5000/add")
        driver.find_element(By.ID, "title").send_keys("Binary Search in Python")
        driver.find_element(By.ID, "language").send_keys("Python")
        driver.find_element(By.ID, "description").send_keys("Efficient binary search algorithm")
        driver.find_element(By.ID, "code").send_keys("def binary_search(arr, target):\n    left, right = 0, len(arr)-1\n    while left <= right:\n        mid = (left+right)//2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            left = mid+1\n        else:\n            right = mid-1\n    return -1")
        driver.find_element(By.ID, "save-btn").click()
        
        assert "Snippet saved to the vault" in driver.page_source
        print("✓ Test 11 passed: Snippet added successfully")
    
    def test_12_view_snippet_details(self, driver):
        """Test 12: User can view snippet details"""
        # First add a snippet
        self.test_11_add_snippet_successfully(driver)
        
        # Find and click on the snippet card
        driver.get("http://localhost:5000")
        snippet_card = driver.find_element(By.CSS_SELECTOR, ".snippet-card")
        snippet_card.click()
        
        assert "Binary Search in Python" in driver.page_source
        assert "def binary_search" in driver.page_source
        print("✓ Test 12 passed: Snippet details viewed")
    
    def test_13_search_snippets(self, driver):
        """Test 13: Search functionality works"""
        # Add a snippet first
        self.test_11_add_snippet_successfully(driver)
        
        driver.get("http://localhost:5000")
        search_input = driver.find_element(By.ID, "search-input")
        search_input.send_keys("Binary Search")
        search_input.send_keys(Keys.RETURN)
        
        assert "Binary Search in Python" in driver.page_source
        print("✓ Test 13 passed: Search works")
    
    def test_14_filter_by_language(self, driver):
        """Test 14: Filter snippets by language"""
        self.test_11_add_snippet_successfully(driver)
        
        driver.get("http://localhost:5000")
        lang_filter = driver.find_element(By.ID, "lang-filter")
        lang_filter.send_keys("Python")
        driver.find_element(By.ID, "search-btn").click()
        
        assert "Python" in driver.page_source or "PYTHON" in driver.page_source.upper()
        print("✓ Test 14 passed: Language filter works")
    
    def test_15_empty_search_shows_message(self, driver):
        """Test 15: Empty search shows appropriate message"""
        driver.get("http://localhost:5000")
        search_input = driver.find_element(By.ID, "search-input")
        search_input.send_keys("xyz_nonexistent_snippet_12345")
        search_input.send_keys(Keys.RETURN)
        
        page_text = driver.page_source
        assert "No snippets match" in page_text or "VAULT IS EMPTY" in page_text
        print("✓ Test 15 passed: Empty search handled")
    
    def test_16_dashboard_requires_login(self, driver):
        """Test 16: Dashboard requires authentication"""
        driver.get("http://localhost:5000/dashboard")
        assert "login" in driver.current_url
        print("✓ Test 16 passed: Dashboard requires login")
    
    def test_17_dashboard_shows_user_snippets(self, driver):
        """Test 17: Dashboard shows user's snippets"""
        self.test_11_add_snippet_successfully(driver)
        
        # Navigate to dashboard
        dashboard_link = driver.find_element(By.LINK_TEXT, "[ DASHBOARD ]")
        dashboard_link.click()
        
        assert "Binary Search in Python" in driver.page_source
        print("✓ Test 17 passed: Dashboard shows snippets")
    
    def test_18_edit_snippet(self, driver):
        """Test 18: User can edit their snippet"""
        self.test_11_add_snippet_successfully(driver)
        
        # View the snippet
        driver.get("http://localhost:5000")
        snippet_card = driver.find_element(By.CSS_SELECTOR, ".snippet-card")
        snippet_card.click()
        
        # Click edit button
        driver.find_element(By.ID, "edit-btn").click()
        
        # Update title
        title_field = driver.find_element(By.ID, "title")
        title_field.clear()
        title_field.send_keys("Updated: Binary Search with Comments")
        
        driver.find_element(By.ID, "update-btn").click()
        
        assert "Updated: Binary Search with Comments" in driver.page_source
        print("✓ Test 18 passed: Snippet edited successfully")
    
    def test_19_delete_snippet(self, driver):
        """Test 19: User can delete their snippet"""
        self.test_11_add_snippet_successfully(driver)
        
        # View the snippet
        driver.get("http://localhost:5000")
        snippet_card = driver.find_element(By.CSS_SELECTOR, ".snippet-card")
        snippet_card.click()
        
        # Click delete button and confirm
        driver.find_element(By.ID, "delete-btn").click()
        driver.switch_to.alert.accept()
        
        assert "Snippet deleted" in driver.page_source
        print("✓ Test 19 passed: Snippet deleted successfully")

# Run with: pytest test_codevault.py -v