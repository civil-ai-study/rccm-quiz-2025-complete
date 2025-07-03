#!/usr/bin/env python3
"""
🌐 Browser Automation - Selenium-based UI Testing
Provides browser automation for comprehensive UI testing
"""

import os
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import json

# Import Selenium components with graceful fallback
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.chrome.options import Options as ChromeOptions
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
    from selenium.common.exceptions import (
        TimeoutException, NoSuchElementException, WebDriverException,
        ElementNotInteractableException, StaleElementReferenceException
    )
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
    # Create dummy classes for graceful degradation
    class DummyWebDriver:
        pass
    
    webdriver = DummyWebDriver()
    TimeoutException = Exception
    NoSuchElementException = Exception
    WebDriverException = Exception

class BrowserAutomation:
    """Browser automation for UI testing with Selenium"""
    
    def __init__(self, browser: str = "chrome", headless: bool = True, base_url: str = "http://localhost:5000"):
        self.browser = browser.lower()
        self.headless = headless
        self.base_url = base_url.rstrip('/')
        self.driver = None
        self.logger = logging.getLogger(__name__)
        
        # Screenshots directory
        self.screenshots_dir = Path(__file__).parent.parent.parent / "results" / "screenshots"
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        # Wait configuration
        self.implicit_wait = 10
        self.explicit_wait = 20
        
        # Test configuration
        self.page_load_timeout = 30
        self.script_timeout = 30
        
        if not SELENIUM_AVAILABLE:
            self.logger.warning("⚠️ Selenium not available. Browser automation features will be disabled.")

    def start_browser(self) -> bool:
        """Start browser with appropriate configuration"""
        if not SELENIUM_AVAILABLE:
            self.logger.error("❌ Selenium not installed. Cannot start browser automation.")
            return False
        
        try:
            if self.browser == "chrome":
                self.driver = self._create_chrome_driver()
            elif self.browser == "firefox":
                self.driver = self._create_firefox_driver()
            else:
                self.logger.error(f"❌ Unsupported browser: {self.browser}")
                return False
            
            # Configure timeouts
            self.driver.implicitly_wait(self.implicit_wait)
            self.driver.set_page_load_timeout(self.page_load_timeout)
            self.driver.set_script_timeout(self.script_timeout)
            
            self.logger.info(f"✅ Browser started: {self.browser} (headless: {self.headless})")
            return True
            
        except WebDriverException as e:
            self.logger.error(f"❌ Failed to start browser: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unexpected error starting browser: {e}")
            return False

    def _create_chrome_driver(self):
        """Create Chrome WebDriver with options"""
        options = ChromeOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Add performance and stability options
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-images')  # Faster loading
        options.add_argument('--disable-javascript')  # For basic HTML testing
        
        # Set user agent
        options.add_argument('--user-agent=RCCM-Test-Framework/1.0 (Selenium)')
        
        return webdriver.Chrome(options=options)

    def _create_firefox_driver(self):
        """Create Firefox WebDriver with options"""
        options = FirefoxOptions()
        
        if self.headless:
            options.add_argument('--headless')
        
        # Add performance options
        options.add_argument('--width=1920')
        options.add_argument('--height=1080')
        
        # Set preferences for faster testing
        profile = webdriver.FirefoxProfile()
        profile.set_preference('permissions.default.image', 2)  # Don't load images
        profile.set_preference('javascript.enabled', False)     # Disable JS for basic testing
        
        return webdriver.Firefox(options=options, firefox_profile=profile)

    def navigate_to_quiz(self, department: str, question_count: int) -> Dict[str, Any]:
        """Navigate to quiz with specific department and question count"""
        if not self.driver:
            return {'success': False, 'error': 'Browser not started'}
        
        try:
            # Map department to URL parameter
            department_mapping = {
                '基礎科目': 'basic',
                '道路部門': 'road',
                '河川・砂防部門': 'civil_planning',
                '都市計画部門': 'urban_planning',
                '造園部門': 'landscape',
                '建設環境部門': 'construction_env',
                '鋼構造・コンクリート部門': 'steel_concrete',
                '土質・基礎部門': 'soil_foundation',
                '施工計画部門': 'construction_planning',
                '上下水道部門': 'water_supply',
                '森林土木部門': 'forestry',
                '農業土木部門': 'agriculture',
                'トンネル部門': 'tunnel'
            }
            
            dept_param = department_mapping.get(department, 'basic')
            quiz_url = f"{self.base_url}/quiz?department={dept_param}&count={question_count}"
            
            self.logger.info(f"🔄 Navigating to quiz: {department} - {question_count} questions")
            self.driver.get(quiz_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Take screenshot
            screenshot_path = self.take_screenshot(f"quiz_navigation_{department}_{question_count}q")
            
            # Validate quiz page loaded
            validation_result = self._validate_quiz_page_loaded(department, question_count)
            
            return {
                'success': True,
                'url': self.driver.current_url,
                'title': self.driver.title,
                'screenshot': screenshot_path,
                'validation': validation_result
            }
            
        except TimeoutException:
            return {'success': False, 'error': 'Page load timeout'}
        except WebDriverException as e:
            return {'success': False, 'error': f'WebDriver error: {e}'}
        except Exception as e:
            return {'success': False, 'error': f'Navigation error: {e}'}

    def answer_question(self, answer: str, current_question: int) -> Dict[str, Any]:
        """Answer a quiz question"""
        if not self.driver:
            return {'success': False, 'error': 'Browser not started'}
        
        try:
            self.logger.debug(f"🔄 Answering question {current_question} with answer: {answer}")
            
            # Find answer option
            answer_option = self._find_answer_option(answer)
            if not answer_option:
                return {'success': False, 'error': f'Answer option {answer} not found'}
            
            # Click answer option
            answer_option.click()
            time.sleep(0.5)  # Brief pause for UI update
            
            # Find and click submit button
            submit_button = self._find_submit_button()
            if not submit_button:
                return {'success': False, 'error': 'Submit button not found'}
            
            submit_button.click()
            
            # Wait for page transition
            WebDriverWait(self.driver, self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Take screenshot after submission
            screenshot_path = self.take_screenshot(f"after_answer_q{current_question}")
            
            # Check if we're on feedback or results page
            page_type = self._determine_page_type()
            
            return {
                'success': True,
                'answer_submitted': answer,
                'question_number': current_question,
                'page_type': page_type,
                'url': self.driver.current_url,
                'screenshot': screenshot_path
            }
            
        except TimeoutException:
            return {'success': False, 'error': 'Answer submission timeout'}
        except ElementNotInteractableException:
            return {'success': False, 'error': 'Cannot interact with answer element'}
        except Exception as e:
            return {'success': False, 'error': f'Answer submission error: {e}'}

    def navigate_to_next_question(self) -> Dict[str, Any]:
        """Navigate to next question from feedback page"""
        if not self.driver:
            return {'success': False, 'error': 'Browser not started'}
        
        try:
            # Find next question button
            next_button = self._find_next_button()
            if not next_button:
                return {'success': False, 'error': 'Next button not found'}
            
            next_button.click()
            
            # Wait for page transition
            WebDriverWait(self.driver, self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Take screenshot
            screenshot_path = self.take_screenshot("next_question_navigation")
            
            return {
                'success': True,
                'url': self.driver.current_url,
                'screenshot': screenshot_path
            }
            
        except TimeoutException:
            return {'success': False, 'error': 'Next question navigation timeout'}
        except Exception as e:
            return {'success': False, 'error': f'Next question navigation error: {e}'}

    def navigate_to_results(self) -> Dict[str, Any]:
        """Navigate to results page"""
        if not self.driver:
            return {'success': False, 'error': 'Browser not started'}
        
        try:
            # Find results button
            results_button = self._find_results_button()
            if not results_button:
                return {'success': False, 'error': 'Results button not found'}
            
            results_button.click()
            
            # Wait for results page to load
            WebDriverWait(self.driver, self.explicit_wait).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete"
            )
            
            # Take screenshot
            screenshot_path = self.take_screenshot("results_page")
            
            # Extract results information
            results_info = self._extract_results_information()
            
            return {
                'success': True,
                'url': self.driver.current_url,
                'screenshot': screenshot_path,
                'results_info': results_info
            }
            
        except TimeoutException:
            return {'success': False, 'error': 'Results page load timeout'}
        except Exception as e:
            return {'success': False, 'error': f'Results navigation error: {e}'}

    def take_screenshot(self, name: str) -> str:
        """Take screenshot and return path"""
        if not self.driver:
            return ""
        
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{name}.png"
            screenshot_path = self.screenshots_dir / filename
            
            self.driver.save_screenshot(str(screenshot_path))
            self.logger.debug(f"📸 Screenshot saved: {screenshot_path}")
            
            return str(screenshot_path)
            
        except Exception as e:
            self.logger.error(f"❌ Screenshot failed: {e}")
            return ""

    def get_page_source(self) -> str:
        """Get current page source"""
        if not self.driver:
            return ""
        
        return self.driver.page_source

    def get_current_url(self) -> str:
        """Get current URL"""
        if not self.driver:
            return ""
        
        return self.driver.current_url

    def close_browser(self):
        """Close browser and cleanup"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("✅ Browser closed successfully")
            except Exception as e:
                self.logger.error(f"❌ Error closing browser: {e}")
            finally:
                self.driver = None

    def _validate_quiz_page_loaded(self, department: str, question_count: int) -> Dict[str, Any]:
        """Validate that quiz page loaded correctly"""
        validation = {
            'has_question': False,
            'has_answer_options': False,
            'has_progress_indicator': False,
            'correct_question_count': False
        }
        
        try:
            # Check for question text
            question_elements = self.driver.find_elements(By.CLASS_NAME, "question-text")
            validation['has_question'] = len(question_elements) > 0
            
            # Check for answer options
            answer_elements = self.driver.find_elements(By.NAME, "answer")
            validation['has_answer_options'] = len(answer_elements) >= 4
            
            # Check for progress indicator
            progress_elements = self.driver.find_elements(By.CLASS_NAME, "progress")
            if not progress_elements:
                # Alternative progress indicators
                progress_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '/')]")
            validation['has_progress_indicator'] = len(progress_elements) > 0
            
            # Check for correct question count in page
            page_source = self.driver.page_source
            validation['correct_question_count'] = f"/{question_count}" in page_source
            
        except Exception as e:
            self.logger.error(f"❌ Quiz page validation error: {e}")
        
        return validation

    def _find_answer_option(self, answer: str):
        """Find answer option element"""
        try:
            # Try by value attribute
            answer_element = self.driver.find_element(By.CSS_SELECTOR, f"input[name='answer'][value='{answer.lower()}']")
            return answer_element
        except NoSuchElementException:
            # Try by ID
            try:
                answer_element = self.driver.find_element(By.ID, f"answer_{answer.lower()}")
                return answer_element
            except NoSuchElementException:
                return None

    def _find_submit_button(self):
        """Find submit button element"""
        try:
            # Try multiple selectors
            selectors = [
                "input[type='submit']",
                "button[type='submit']",
                ".submit-btn",
                "#submit-btn",
                "*[contains(text(), '回答')]",
                "*[contains(text(), 'Submit')]"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("*[contains"):
                        element = self.driver.find_element(By.XPATH, f"//{selector}")
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception:
            return None

    def _find_next_button(self):
        """Find next question button"""
        try:
            selectors = [
                "*[contains(text(), '次の問題')]",
                "*[contains(text(), 'Next')]",
                ".next-btn",
                "#next-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("*[contains"):
                        element = self.driver.find_element(By.XPATH, f"//{selector}")
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception:
            return None

    def _find_results_button(self):
        """Find results button"""
        try:
            selectors = [
                "*[contains(text(), '結果')]",
                "*[contains(text(), 'Results')]",
                ".results-btn",
                "#results-btn"
            ]
            
            for selector in selectors:
                try:
                    if selector.startswith("*[contains"):
                        element = self.driver.find_element(By.XPATH, f"//{selector}")
                    else:
                        element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    return element
                except NoSuchElementException:
                    continue
            
            return None
            
        except Exception:
            return None

    def _determine_page_type(self) -> str:
        """Determine current page type"""
        page_source = self.driver.page_source.lower()
        
        if any(keyword in page_source for keyword in ['feedback', 'correct', '正解', '不正解']):
            return 'feedback'
        elif any(keyword in page_source for keyword in ['results', 'score', '結果', '点数']):
            return 'results'
        elif any(keyword in page_source for keyword in ['question', '問題']):
            return 'question'
        else:
            return 'unknown'

    def _extract_results_information(self) -> Dict[str, Any]:
        """Extract results information from results page"""
        results_info = {
            'score_found': False,
            'score_text': '',
            'correct_answers': 0,
            'total_questions': 0,
            'percentage': 0
        }
        
        try:
            page_source = self.driver.page_source
            
            # Look for score patterns
            import re
            score_match = re.search(r'(\d+)/(\d+)', page_source)
            if score_match:
                results_info['score_found'] = True
                results_info['correct_answers'] = int(score_match.group(1))
                results_info['total_questions'] = int(score_match.group(2))
                results_info['score_text'] = score_match.group(0)
                
                if results_info['total_questions'] > 0:
                    results_info['percentage'] = (results_info['correct_answers'] / results_info['total_questions']) * 100
            
        except Exception as e:
            self.logger.error(f"❌ Results extraction error: {e}")
        
        return results_info

    def __enter__(self):
        """Context manager entry"""
        if self.start_browser():
            return self
        else:
            raise Exception("Failed to start browser")

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close_browser()

if __name__ == "__main__":
    # Test browser automation
    import logging
    
    logging.basicConfig(level=logging.INFO)
    
    if SELENIUM_AVAILABLE:
        try:
            with BrowserAutomation(headless=True) as browser:
                # Test navigation
                result = browser.navigate_to_quiz('基礎科目', 10)
                if result['success']:
                    print("✅ Browser navigation test passed")
                    print(f"URL: {result['url']}")
                    print(f"Validation: {result['validation']}")
                else:
                    print(f"❌ Browser navigation test failed: {result['error']}")
        except Exception as e:
            print(f"❌ Browser automation test failed: {e}")
    else:
        print("❌ Selenium not available. Install selenium package for browser automation.")
    
    print("Browser automation test completed.")