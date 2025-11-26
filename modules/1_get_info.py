from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementNotInteractableException

from load_django import *
from parser_app.models import MobileGadget
import json

product = {}

options = Options()
options.add_argument("--maximize-window")


options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=options)
driver.get("https://brain.com.ua")
time.sleep(2)

WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "html/body")))

search_str = "Apple iPhone 15 128GB Black"

search_boxes = driver.find_elements(By.XPATH, "//input[@class='quick-search-input']")

for box in search_boxes:
    try:
        box.send_keys("Apple iPhone 15 128GB Black")
        box.send_keys(Keys.ENTER)
        break
    except ElementNotInteractableException:
        print("ElementNotInteractableException")
        continue


time.sleep(2)

try:
    qrid_elements = driver.find_elements(By.XPATH, "//div[contains(@class,'br-pp-img-grid')]")
    first_product = qrid_elements[0]
    first_product.click()
except Exception as e:
    print(e)

time.sleep(2)


body = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.XPATH, "html/body")))

time.sleep(2)


#get product full name
try:
    product["full_name"]= driver.find_element(By.XPATH, "//h1[contains(@class, 'main-title')]").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting full name:", e)
    product["full_name"] = None

#get product color
try:
    product["color"] = driver.find_element(By.XPATH, "//a[contains(@title, 'Колір')]").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting color:", e)
    product["color"] = None

# get memory volume
try:
    product["memory_volume"] = driver.find_element(By.XPATH, "//a[contains(@title, 'Вбудована пам')]").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting memory volume:", e)
    product["memory_volume"] = None


# get price use
try:
    product["price_use"] = driver.find_element(By.XPATH, "//div[contains(@class, 'main-price-block')]").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting price use:", e)
    product["price_use"] = None    

# get price action
product["price_action"] = None


# get pictures URLs
try:
    picture_elements = driver.find_elements(By.XPATH, "//img[contains(@class, 'br-main-img')]")
    product["picture_urls"] = [elem.get_attribute("src") for elem in picture_elements]
except Exception as e:
    print("Error getting picture URLs:", e)
    product["picture_urls"] = []


#get product code
try:    
    product["product_code"] = driver.find_element(By.XPATH, "//span[contains(@class, 'br-pr-code-val')]").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting product code:", e)
    product["product_code"] = None


#get review count
try:
   product["review_count"] = driver.find_element(By.XPATH, "//a[contains(@class, 'forbid-click')]/span").get_attribute("textContent").strip()
except NoSuchElementException:
    product["review_count"] = None
    print("Review count element not found.")  
except Exception as e:
    print("Error getting review count:", e)
    product["review_count"] = None

 
# get series
try:
    product['series'] = driver.find_element(By.XPATH, "//span[text() = 'Модель']/following-sibling::span").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting series:", e)
    series = None


#get display size
try:
    product["display_size"] = driver.find_element(By.XPATH, "//span[text() = 'Діагональ екрану']/following-sibling::span").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting display size:", e)
    product["display_size"] = None


#get resolution
try:
    product["resolution"] = driver.find_element(By.XPATH, "//span[text() = 'Роздільна здатність екрану']/following-sibling::span").get_attribute("textContent").strip()
except Exception as e:
    print("Error getting resolution:", e)
    product["resolution"] = None

#get specifications
specific_s = {}
try:
    all_spec_blocks = driver.find_elements(By.XPATH, "//div[contains(@class, 'br-pr-chr-item')]")
    for block in all_spec_blocks:
        try:
            # Title of the block (e.g. "Процесор", "Пам'ять")
            spec_name = block.find_element(By.XPATH, './/h3').get_attribute('textContent').strip()
            try:
                specific_s[spec_name] = {}
                divs = block.find_element(By.XPATH, './/div').find_elements(By.XPATH, './/div')
                for div in divs:
                    spans = div.find_elements(By.XPATH, './/span')
                    try:
                        key = spans[0].get_attribute('textContent').strip()
                    except Exception as e:
                        print("Error getting key: ", e)
                        key = None
                        
                    value = None

                    # Try value as link first
                    try:
                        value = spans[1].find_element(By.XPATH, './/a').get_attribute('textContent').strip()
                    except:
                        try:
                            value = spans[1].get_attribute('textContent').strip()
                        except Exception as e:
                            print("Error getting value: ", e)
                    specific_s[spec_name][key] = value

            except Exception as e:
                print("Error getting div:", e)

        except Exception as e:
            print("Error inside block:", e)

except Exception as e:
    print("Error getting specification blocks:", e)
    specific_s = {}

product['specifications'] = json.dumps(specific_s, indent=4, ensure_ascii=False)

time.sleep(1)
driver.quit()
print("Driver closed.")

# Print collected data
print("full_name: ", product['full_name']) 
print("color: ", product['color'])
print("memory_volume: ", product['memory_volume']) 
print("price_use: ", product['price_use'])
print("price_action: ", product['price_action'])
print("picture_urls: ", product['picture_urls'])
print("product_code: ", product['product_code'])
print("review_count: ", product['review_count'])
print("series: ", product['series'])
print("display_size: ", product['display_size'])
print("resolution: ", product['resolution'])
print("specifications: ", product['specifications'])



# save to db
try:
    gadget, created = MobileGadget.objects.get_or_create(
        full_name = product['full_name'],
        color = product['color'],
        memory_volume = product['memory_volume'],
        price_use = product['price_use'],
        price_action = product['price_action'],
        pic_links = product['picture_urls'],
        product_code = product["product_code"],
        review_count = product['review_count'],
        series = product['series'],
        display_size = product['display_size'],
        resolution = product['resolution'],
        specifications = product['specifications']
    )
    print("New gadget saved to database." if created else "Gadget already exists in database.")
except Exception as e:
    print(f"Database error: {e}")







