import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import random
import string

BASE_URL = "http://localhost:5000"


def make_username():
    suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"tuser_{suffix}"


@pytest.fixture(scope="function")
def driver():
    opts = Options()
    opts.add_argument("--headless")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--window-size=1920,1080")
    drv = webdriver.Chrome(options=opts)
    drv.implicitly_wait(10)
    yield drv
    drv.quit()


def wait_for_page(driver, text, timeout=15):
    """Wait until text appears in page source."""
    WebDriverWait(driver, timeout).until(
        lambda d: text in d.page_source
    )


def register_and_login(driver, password="TestPass@123"):
    username = make_username()
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "email").send_keys(f"{username}@example.com")
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "confirm").send_keys(password)
    driver.find_element(By.ID, "register-btn").click()
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(username)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.ID, "login-btn").click()
    wait_for_page(driver, "Welcome back")
    return username


def add_snippet(driver, title="Test Snippet", lang="Python",
                desc="Test desc", code="print('hello')"):
    driver.get(f"{BASE_URL}/add")
    driver.find_element(By.ID, "title").send_keys(title)
    # Use send_keys on select — works with Selenium 3.x reliably
    lang_select = driver.find_element(By.ID, "language")
    lang_select.send_keys(lang)
    driver.find_element(By.ID, "description").send_keys(desc)
    driver.find_element(By.ID, "code").send_keys(code)
    driver.find_element(By.ID, "save-btn").click()
    wait_for_page(driver, "Snippet saved")


# ── Tests ─────────────────────────────────────────────────────────────────────

def test_01_homepage_loads(driver):
    driver.get(BASE_URL)
    assert "CODEVAULT" in driver.page_source or "SNIPPET VAULT" in driver.page_source

def test_02_register_page_has_all_fields(driver):
    driver.get(f"{BASE_URL}/register")
    assert driver.find_element(By.ID, "username")
    assert driver.find_element(By.ID, "email")
    assert driver.find_element(By.ID, "password")
    assert driver.find_element(By.ID, "confirm")

def test_03_successful_registration(driver):
    u = make_username()
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys(f"{u}@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    assert "Account created" in driver.page_source

def test_04_password_mismatch_error(driver):
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(make_username())
    driver.find_element(By.ID, "email").send_keys("x@x.com")
    driver.find_element(By.ID, "password").send_keys("Pass1234")
    driver.find_element(By.ID, "confirm").send_keys("Different99")
    driver.find_element(By.ID, "register-btn").click()
    assert "Passwords do not match" in driver.page_source

def test_05_short_password_rejected(driver):
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(make_username())
    driver.find_element(By.ID, "email").send_keys("short@x.com")
    driver.find_element(By.ID, "password").send_keys("abc")
    driver.find_element(By.ID, "confirm").send_keys("abc")
    driver.find_element(By.ID, "register-btn").click()
    assert "at least 6 characters" in driver.page_source

def test_06_duplicate_username_rejected(driver):
    u = make_username()
    for email in [f"{u}@a.com", "other@b.com"]:
        driver.get(f"{BASE_URL}/register")
        driver.find_element(By.ID, "username").send_keys(u)
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "password").send_keys("TestPass@123")
        driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
        driver.find_element(By.ID, "register-btn").click()
    assert "already exists" in driver.page_source

def test_07_login_page_loads(driver):
    driver.get(f"{BASE_URL}/login")
    assert driver.find_element(By.ID, "username")
    assert driver.find_element(By.ID, "password")

def test_08_successful_login(driver):
    u = make_username()
    driver.get(f"{BASE_URL}/register")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "email").send_keys(f"{u}@example.com")
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "confirm").send_keys("TestPass@123")
    driver.find_element(By.ID, "register-btn").click()
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys(u)
    driver.find_element(By.ID, "password").send_keys("TestPass@123")
    driver.find_element(By.ID, "login-btn").click()
    assert "Welcome back" in driver.page_source

def test_09_invalid_login_rejected(driver):
    driver.get(f"{BASE_URL}/login")
    driver.find_element(By.ID, "username").send_keys("no_such_user_xyz999")
    driver.find_element(By.ID, "password").send_keys("wrongpass")
    driver.find_element(By.ID, "login-btn").click()
    assert "Invalid username or password" in driver.page_source

def test_10_logout_works(driver):
    register_and_login(driver)
    driver.find_element(By.LINK_TEXT, "[ LOGOUT ]").click()
    assert "logged out" in driver.page_source

def test_11_add_page_requires_login(driver):
    driver.get(f"{BASE_URL}/add")
    assert "login" in driver.current_url.lower()

def test_12_dashboard_requires_login(driver):
    driver.get(f"{BASE_URL}/dashboard")
    assert "login" in driver.current_url.lower()

def test_13_add_snippet_successfully(driver):
    register_and_login(driver)
    add_snippet(driver, title="Bubble Sort", code="def bubble(): pass")
    assert "Snippet saved" in driver.page_source

def test_14_snippet_appears_on_homepage(driver):
    register_and_login(driver)
    title = f"UniqueSnippet_{make_username()}"
    add_snippet(driver, title=title, code="x = 42")
    driver.get(BASE_URL)
    assert title in driver.page_source

def test_15_view_snippet_detail_page(driver):
    register_and_login(driver)
    title = f"ViewTest_{make_username()}"
    add_snippet(driver, title=title, code="def view_me(): pass")
    driver.get(BASE_URL)
    # Wait for snippet card and click
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".snippet-card"))
    )
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
    # Wait for detail page to load
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "snippet-code"))
    )
    assert title in driver.page_source

def test_16_search_finds_snippet(driver):
    register_and_login(driver)
    add_snippet(driver, title="QuickSort Algorithm", code="def quick(): pass")
    driver.get(BASE_URL)
    driver.find_element(By.ID, "search-input").send_keys("QuickSort")
    driver.find_element(By.ID, "search-btn").click()
    assert "QuickSort Algorithm" in driver.page_source

def test_17_search_no_results(driver):
    driver.get(BASE_URL)
    driver.find_element(By.ID, "search-input").send_keys("zzzNonExistentXYZ999")
    driver.find_element(By.ID, "search-btn").click()
    assert ("VAULT IS EMPTY" in driver.page_source
            or "0 snippet" in driver.page_source
            or "No snippets" in driver.page_source)

def test_18_filter_by_language(driver):
    register_and_login(driver)
    # Add a Python snippet so Python appears in filter
    add_snippet(driver, title="Filter Test Python", lang="Python",
                code="x = 'filter test'")
    driver.get(BASE_URL)
    # Wait for lang-filter to be present
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "lang-filter"))
    )
    # Select Python (guaranteed to exist since we just added one)
    Select(driver.find_element(By.ID, "lang-filter")).select_by_visible_text("Python")
    driver.find_element(By.ID, "search-btn").click()
    assert "Python" in driver.page_source

def test_19_dashboard_shows_snippets(driver):
    register_and_login(driver)
    add_snippet(driver, title="Dashboard Test Snippet", code="x = 1")
    driver.get(f"{BASE_URL}/dashboard")
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "dashboard-table"))
    )
    assert "Dashboard Test Snippet" in driver.page_source

def test_20_edit_snippet(driver):
    register_and_login(driver)
    title = f"EditTest_{make_username()}"
    add_snippet(driver, title=title, code="pass")
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".snippet-card"))
    )
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "edit-btn"))
    )
    driver.find_element(By.ID, "edit-btn").click()
    f = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "title"))
    )
    f.clear()
    f.send_keys("Updated Title")
    driver.find_element(By.ID, "update-btn").click()
    assert "Updated Title" in driver.page_source

def test_21_delete_snippet(driver):
    register_and_login(driver)
    add_snippet(driver, title="To Be Deleted", code="pass")
    driver.get(BASE_URL)
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".snippet-card"))
    )
    driver.find_element(By.CSS_SELECTOR, ".snippet-card").click()
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "delete-btn"))
    )
    driver.execute_script("window.confirm = function(){ return true; }")
    driver.find_element(By.ID, "delete-btn").click()
    assert "deleted" in driver.page_source.lower()
