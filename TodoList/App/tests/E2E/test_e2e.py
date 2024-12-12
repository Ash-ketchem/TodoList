import time
from django.test import LiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.auth.models import User
from selenium.webdriver.firefox.options import Options
from App.models import Task


class UserLoginTest(LiveServerTestCase):

    def setUp(self):
        # Create a superuser
        User.objects.create_superuser(
            username="admin", email="admin@example.com", password="admin"
        )
        t1 = Task.objects.create(title="demo", description="demo")
        t1.save()

        """Set up the test environment with Firefox WebDriver"""
        options = Options()
        options.add_argument("--headless")  # Run tests in headless mode (no UI)
        self.browser = webdriver.Firefox(options=options)
        self.url = self.live_server_url  # URL to the app

    def tearDown(self):
        """Clean up after each test"""
        self.browser.quit()

    def wait_for_element(self, by, value, timeout=10):
        """Helper function to wait for an element to appear"""
        return WebDriverWait(self.browser, timeout).until(
            EC.presence_of_element_located((by, value))
        )

    def wait_for_element_to_be_clickable(self, by, value, timeout=10):
        """Helper function to wait for an element to be clickable"""
        return WebDriverWait(self.browser, timeout).until(
            EC.element_to_be_clickable((by, value))
        )

    def test_admin_login_and_task_management(self):
        """Test admin login, view, create, update, and delete tasks"""
        self.login_as_admin()
        self.verify_task_view()
        self.create_task("Task 1", "Task Description")
        self.update_task("Task 1", "Task 1 changed")
        self.delete_task("Task 1 changed")

    def login_as_admin(self):
        """Log in as admin user"""
        self.browser.get(self.url + "/admin/")
        self.wait_for_element(By.NAME, "username")
        self.browser.find_element(By.NAME, "username").send_keys("admin")
        self.browser.find_element(By.NAME, "password").send_keys("admin")
        self.browser.find_element(By.NAME, "password").send_keys(Keys.RETURN)

        self.wait_for_element(By.ID, "logout-form")
        logout_form = self.browser.find_element(By.ID, "logout-form")
        self.assertEqual(logout_form.get_attribute("id"), "logout-form")
        time.sleep(2)

    def verify_task_view(self):
        """Verify admin can view all tasks"""
        self.browser.get(self.url + "/admin/App/task/")
        add_task = self.wait_for_element(By.CLASS_NAME, "addlink")
        self.assertTrue(add_task.is_displayed(), "The add task is not visible")
        time.sleep(2)

    def create_task(self, title, description):
        """Create a new task"""
        self.browser.get(self.url + "/admin/App/task/add/")

        title_input = self.wait_for_element(By.NAME, "title")
        description_input = self.browser.find_element(By.NAME, "description")

        title_input.send_keys(title)
        description_input.send_keys(description)

        time.sleep(2)

        save_button = self.browser.find_element(By.NAME, "_save")
        save_button.click()

        self.wait_for_element(By.CLASS_NAME, "results")
        time.sleep(2)

        task_title = self.browser.find_element(By.LINK_TEXT, title)
        self.assertEqual(task_title.text, title)

    def update_task(self, old_title, new_title):
        """Update an existing task"""
        task_title = self.browser.find_element(By.LINK_TEXT, old_title)
        task_title.click()

        title_input = self.wait_for_element(By.NAME, "title")
        title_input.clear()
        title_input.send_keys(new_title)

        time.sleep(2)

        save_button = self.browser.find_element(By.NAME, "_save")
        save_button.click()

        self.wait_for_element(By.CLASS_NAME, "results")
        time.sleep(2)

        task_title = self.browser.find_element(By.LINK_TEXT, new_title)
        self.assertEqual(task_title.text, new_title)

    def delete_task(self, title):
        """Delete a task"""
        task_title = self.browser.find_element(By.LINK_TEXT, title)
        task_title.click()

        delete_button = self.browser.find_element(By.CLASS_NAME, "deletelink")
        delete_button.click()

        confirm_button = self.wait_for_element_to_be_clickable(
            By.XPATH, '//input[@type="submit"]'
        )
        confirm_button.click()

        self.wait_for_element(By.CLASS_NAME, "results")
        time.sleep(2)

        task_titles = self.browser.find_elements(By.LINK_TEXT, title)
        self.assertEqual(len(task_titles), 0)
