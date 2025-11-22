from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException

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

WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

search_str = "Apple iPhone 15 128GB Black"

# input search box and submit
driver.execute_script(f"""
                      document.querySelector('input.quick-search-input').value = '{search_str}';
                      document.querySelector('input.quick-search-input').dispatchEvent(new Event('input'));
                      document.querySelector('input[type="submit"]').click();
                      """)


time.sleep(2)

qrid_elements = WebDriverWait(driver, 30).until(
    EC.presence_of_all_elements_located(
        (By.CSS_SELECTOR, ".view-grid .br-pp-img-grid a")))

time.sleep(2)

first_product = qrid_elements[0]
first_product.click()

WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

time.sleep(2)

#get product full name
try:
    product["full_name"] = driver.execute_script("""
        return document.querySelector('h1.main-title').innerText;
    """).strip()
    
except Exception as e:
    print("Error getting full name:", e)
    product["full_name"] = None

#get product color
try:
    product["color"] = driver.find_element(By.CSS_SELECTOR, 'a[title^="Колір"]').get_attribute("title").replace("Колір", "").strip()
except Exception as e:
    print("Error getting color:", e)
    product["color"] = None

# get memory volume
try:
    product["memory_volume"] = driver.find_element(By.CSS_SELECTOR, 'a[title^="Вбудована пам\'ять"]').get_attribute("title").replace("Вбудована пам\'ять", "").strip()
except Exception as e:
    print("Error getting memory volume:", e)
    product["memory_volume"] = None

# get price use
try:
    product["price_use"] = driver.find_element(By.CSS_SELECTOR, '.price-wrapper span').text.strip()
except Exception as e:
    print("Error getting price use:", e)
    product["price_use"] = None    

# get price action

product["price_action"] = None


# get pictures URLs
try:
    picture_elements = driver.find_elements(By.CSS_SELECTOR, 'img.br-main-img')
    product["picture_urls"] = [elem.get_attribute("src") for elem in picture_elements]
except Exception as e:
    print("Error getting picture URLs:", e)
    product["picture_urls"] = []


#get product code
try:    
    product["product_code"] = driver.execute_script("""
        return document.querySelector('span.br-pr-code-val').innerText;
    """).strip()
except Exception as e:
    print("Error getting product code:", e)
    product["product_code"] = None


#get review count
try:

   product["review_count"] = driver.execute_script("""
        return document.querySelector('a.forbid-click span').textContent.trim();
    """).strip()
except NoSuchElementException:
    product["review_count"] = None
    print("Review count element not found.")  
except Exception as e:
    print("Error getting review count:", e)
    product["review_count"] = None

 
# get series
try:
    series_blocks = driver.find_elements(By.CSS_SELECTOR, 'div.br-pr-chr-item')
    print("Found series blocks:", len(series_blocks))
       
    for block in series_blocks:
        try:
            spans = block.find_elements(By.TAG_NAME, 'span')
            for i in range(len(spans) - 1):
                span = spans[i].get_attribute("textContent").strip()
                if span == "Модель":
                    product["series"] = spans[i+1].get_attribute("textContent").strip()
                    break
        except Exception as e:
            print("Error inside block:", e)
            product["series"] = None

    
except Exception as e:
    print("Error getting series:", e)
    series = None


#get display size
try:
    product["display_size"] = driver.find_element(By.CSS_SELECTOR, 'a[title^="Діагональ екрану"]').get_attribute("title").replace("Діагональ екрану", "").strip()
except Exception as e:
    print("Error getting display size:", e)
    product["display_size"] = None


#get resolution
try:
    product["resolution"] = driver.find_element(By.CSS_SELECTOR, 'a[title^="Роздільна здатність екрану"]').get_attribute("title").replace("Роздільна здатність екрану", "").strip()
except Exception as e:
    print("Error getting resolution:", e)
    product["resolution"] = None

#get specifications
specific_s = {}
try:
    all_spec_blocks = driver.find_elements(By.CSS_SELECTOR, '.br-pr-chr-item')
    i = 0
    for block in all_spec_blocks:
        try:
            # Title of the block (e.g. "Процесор", "Пам'ять")
            spec_name = block.find_element(By.TAG_NAME, 'h3').get_attribute('textContent').strip()
            try:
                specific_s[spec_name] = {}
                divs = block.find_element(By.TAG_NAME, 'div').find_elements(By.TAG_NAME, 'div')
                for div in divs:
                    spans = div.find_elements(By.TAG_NAME, 'span')
                    print(len(spans), " spans")

                    try:
                        key = spans[0].get_attribute('textContent').strip()
                    except Exception as e:
                        print("Error getting key: ", e)
                        key = None
                        
                    value = None

                    # Try value as link first
                    try:
                        value = spans[1].find_element(By.TAG_NAME, 'a').get_attribute('textContent').strip()
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







