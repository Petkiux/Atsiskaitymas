import sys
import re
import requests
from PyQt6 import QtWidgets, QtCore
from design import Ui_MainWindow  

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.toolButton.clicked.connect(self.close)
        self.ui.toolButton_2.clicked.connect(self.check_address)

        self.list_model = QtCore.QStringListModel()
    # tikrinam adresa
    def check_address(self):
        address = self.ui.textEdit.toPlainText().strip()

        self.ui.listWidget_2.clear()

        if not address:
            self.ui.listWidget_2.addItem(" Įveskite adresą - laukas tuščias")
            return

        if not self.is_valid_url(address):
            self.ui.listWidget_2.addItem(" Neteisingas URL formatas")
            return

        if not address.startswith("https://elenta.lt"):
            self.ui.listWidget_2.addItem(" URL ne iš elenta.lt svetainės")
            return

        try:
            response = requests.head(address, timeout=5)
            if response.status_code == 200:
                self.ui.listWidget_2.addItem(" Galiojantis elenta.lt puslapis")
                #jei adresas tinka leidziam scrape
                self.scrape_category(address)
            else:
                self.ui.listWidget_2.addItem(f" Puslapis neegzistuoja (Kodas: {response.status_code})")
        except requests.RequestException as e:
            self.ui.listWidget_2.addItem(f" Klaida jungiantis: {str(e)}")
    # url sintakses tikrinimas
    def is_valid_url(self, url):
        regex = re.compile(
            r'^(https?://)?'                   
            r'([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}'  
            r'(:\d+)?'                         
            r'(/.*)?$',                        
            re.IGNORECASE
        )
        return re.match(regex, url) is not None
    #scrapinimo dalis
    def scrape_category(self, url):
    
        options = Options()
        options.add_argument('--headless')
        driver = webdriver.Chrome(options=options)

        try:
            driver.get(url)
            driver.maximize_window()
            time.sleep(2)  

            try:
                mygtukas = driver.find_element(By.CLASS_NAME, 'fc-button-label')
                mygtukas.click()
                time.sleep(1)
            except:
                pass  

            has_next = True
            ad_count = 0
            total_price = 0.0

            while has_next:
                time.sleep(2)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                leaflet_items = soup.select('[id^="unit-"]')

                for item in leaflet_items:

                    price_el = item.find('span', class_='price-box')
                    price = price_el.text.strip() if price_el else '0'
                    price = float(price.replace('€', '').replace(' ', '').replace(',', '.'))  
                    ad_count += 1
                    total_price += price  

                try:
                    next_btn = driver.find_element(By.CLASS_NAME, 'pagerNextPage')
                    next_btn.click()
                    time.sleep(2)
                except Exception as e:
                    has_next = False  

            driver.quit()
            
            self.ui.listWidget.clear()
            self.ui.listWidget.addItem(f"Iš viso skelbimu: {ad_count}")
            self.ui.listWidget.addItem(f"Bendra Suma: {total_price:.2f} €")
            self.ui.listWidget.addItem(f"Skelbimu kainos vidurkis: {total_price / ad_count if ad_count else 0:.2f} €")

        except Exception as e:
            self.ui.listWidget.clear()
            self.ui.listWidget.addItem(f"Error: {str(e)}")
            driver.quit()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
