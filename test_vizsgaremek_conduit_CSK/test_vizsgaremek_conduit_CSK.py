from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time
import csv

from adatok import user, article, update_article, delete_article
from functions import login, new_article


# Böngésző és az adott oldal megnyitása, bezárása:
class TestConduit(object):
    def setup_method(self):
        service = Service(executable_path=ChromeDriverManager().install())
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        self.browser = webdriver.Chrome(service=service, options=options)
        URL = "http://localhost:1667/#/"
        self.browser.get(URL)
        self.browser.maximize_window()

    def teardown_method(self):
        self.browser.quit()

    # 1. Adatkezelési nyilatkozat elfogadásának ellenőrzése:
    def test_cookies(self):

        # gombok megkeresése, ellenőrzése:

        time.sleep(2)
        decline_btn = self.browser.find_element(By.XPATH,
                                                '//button[@class="cookie__bar__buttons__button cookie__bar__buttons__button--decline"]')
        accept_btn = self.browser.find_element(By.XPATH,
                                               '//button[@class="cookie__bar__buttons__button cookie__bar__buttons__button--accept"]')
        cookie_panel = self.browser.find_element(By.XPATH,
                                                 '//div[@class="cookie cookie__bar cookie__bar--bottom-left"]')

        assert cookie_panel.is_displayed()
        assert decline_btn.is_enabled()
        assert accept_btn.is_enabled()
        assert accept_btn.text == 'I accept!'

        # kattintás után a panel eltűnésének ellenőrzése:

        accept_btn.click()
        time.sleep(2)

        assert len(self.browser.find_elements(By.ID, 'cookie-policy-panel')) == 0

    # 2. Regisztráció folyamata helyes adatokkal:
    def test_registration(self):

        # gombok, mezők, üzenetek megkeresése, mezők kitöltése:

        time.sleep(2)
        sign_up_btn = self.browser.find_element(By.LINK_TEXT, 'Sign up')
        sign_up_btn.click()
        time.sleep(2)

        # annak ellenőrzése, hogy az URL megváltozik azaz új oldalra visz kattintásra:

        assert self.browser.current_url != "http://localhost:1667/#/"
        time.sleep(2)

        username_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Username"]')
        email_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Email"]')
        password_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Password"]')
        sign_up_reg_btn = self.browser.find_element(By.XPATH, '//button[@class="btn btn-lg btn-primary pull-xs-right"]')
        time.sleep(2)

        username_input.send_keys(user['name'])
        email_input.send_keys(user['email'])
        password_input.send_keys(user['password'])

        sign_up_reg_btn.click()
        time.sleep(2)

        reg_message_big = WebDriverWait(self.browser, 5).until(
            EC.presence_of_element_located((By.XPATH, '//div[@class="swal-title"]')))
        reg_message_small = self.browser.find_element(By.XPATH, '//div[@class="swal-text"]')

        # annak ellenőrzése, hogy sikeres a regisztráció, az üzenetek szövege megfelelő:

        assert reg_message_big.text == 'Welcome!'
        assert reg_message_small.text == 'Your registration was successful!'

        reg_ok_btn = self.browser.find_element(By.XPATH, '//button[@class="swal-button swal-button--confirm"]')
        reg_ok_btn.click()
        time.sleep(2)

        # akkor sikeres a belépés, ha a kijelentkezés gombja elérhető lesz:

        logut_btn = self.browser.find_element(By.XPATH, '//a[@class="nav-link"]')

        assert logut_btn.is_enabled()
        logut_btn.click()

    # 3. Bejelentkezés ellenőrzése helyes adatokkal:
    def test_login(self):

        # gombok, mezők megkeresése, mezők kitöltése:

        time.sleep(2)
        sign_in_btn = self.browser.find_element(By.LINK_TEXT, 'Sign in')
        sign_in_btn.click()
        time.sleep(2)

        email_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Email"]')
        password_input = self.browser.find_element(By.XPATH, '//input[@placeholder="Password"]')

        email_input.send_keys(user['email'])
        password_input.send_keys(user['password'])

        sign_in_btn2 = self.browser.find_element(By.XPATH, '//button[@class="btn btn-lg btn-primary pull-xs-right"]')
        sign_in_btn2.click()
        time.sleep(2)

        # sikeres a bejelentkezés ha a felhasználónév gombja és a kijelentkezés gombja megjelenik:

        profile_name_btn = self.browser.find_elements(By.XPATH, '//a[@class="nav-link"]')[4]
        assert profile_name_btn.is_displayed()

        logut_btn = self.browser.find_element(By.XPATH, '//a[@class="nav-link"]')
        assert logut_btn.is_enabled()

    # 4. Adatok listázásának ellenőrzése:
    def test_tagfilter(self):

        login(self.browser)

        # bejelentkezés után egy tag kiválasztása a Popular Tags listából:

        mitast_tag = self.browser.find_element(By.XPATH, '//a[@href="#/tag/mitast"]')
        mitast_tag.click()
        time.sleep(2)

        # kiválasztott filter megjelenik a Feed-ben:

        mitast_filter = self.browser.find_element(By.XPATH, '//a[@class="nav-link router-link-exact-active active"]')
        assert mitast_filter.is_displayed()

    # 5. Több oldalas lista bejárásának ellenőrzése:
    def test_list_of_pages(self):

        login(self.browser)

        # gombok megkeresése, oldalak listába gyűjtése:

        pages = []
        page_number_btns = self.browser.find_elements(By.XPATH, '//a[@class="page-link"]')
        for page in page_number_btns:
            page.click()
            pages.append(page)

        time.sleep(2)

        # annak ellenőrzése, hogy az oldalak listája megegyezik az oldalszámokkal:

        assert len(pages) == len(page_number_btns)

    # 6. Új adatbevitel ellenőrzése:
    def test_new_data(self):

        login(self.browser)

        # gombok, mezők megkeresése, mezők kitöltése:

        new_article_btn = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, '//a[@href="#/editor"]')))
        time.sleep(4)
        new_article_btn.click()
        time.sleep(4)

        article_title = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Article Title"]')))
        article_about = self.browser.find_element(By.XPATH, '//input[@placeholder="What\'s this article about?"]')
        article_words = self.browser.find_element(By.XPATH,
                                                  '//textarea[@placeholder="Write your article (in markdown)"]')
        article_tags = self.browser.find_element(By.XPATH, '//input[@placeholder="Enter tags"]')


        time.sleep(4)
        article_title.send_keys(article["title"])
        time.sleep(4)
        article_about.send_keys(article["about"])
        time.sleep(4)
        article_words.send_keys(article["words"])
        time.sleep(4)
        article_tags.send_keys(article["tags"])

        time.sleep(4)
        publish_article_btn = self.browser.find_element(By.XPATH, '//button[@type="submit"]')
        time.sleep(4)
        publish_article_btn.click()
        time.sleep(4)

        # annak ellenőrzése, hogy a felvitt cikk adatai sikeresen elmentődtek - a cikk címe megegyezik a dictionary-ben szereplő címmel:

        new_title = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//h1')))
        time.sleep(4)
        assert new_title.text == article["title"]

    # 7. Ismételt és sorozatos adatbevitel ellenőrzése adatforrásból:
    def test_file_data(self):

        login(self.browser)

        # külső adatforrásból adatfeltöltés, csv file megnyitása, soronkénti beolvasása:

        with open('test_vizsgaremek_conduit_CSK/cimek.csv', 'r', encoding='UTF-8') as file:  # test_vizsgaremek_conduit_CSK/....
            csv_reader = csv.reader(file, delimiter=',')
            next(csv_reader)

            my_title_list = []

            for row in csv_reader:
                new_article(self.browser, row[0], row[1], row[2], row[3])
                time.sleep(1)
                my_title_list.append(row[0])  # címek kigyűjtése az ellenőrzéshez
                new_article_title = self.browser.find_element(By.XPATH, '//h1')
                assert new_article_title.text == row[0]

            assert new_article_title.text in my_title_list

    # 8. Meglévő adat módosításának ellenőrzése:
    def test_update_data(self):

        login(self.browser)

        # gombok, mezők megkeresése, cím módosítása:

        new_article(self.browser, article["title"], article["about"], article["words"],
                    article["tags"])  # adatok meghívása
        time.sleep(4)

        edit_btn = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="btn btn-sm btn-outline-secondary"]')))
        edit_btn.click()
        time.sleep(4)
        article_title = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, '//input[@placeholder="Article Title"]')))
        time.sleep(2)

        article_title.clear()
        time.sleep(4)
        article_title.send_keys(update_article["title"])
        time.sleep(4)
        publish_article_btn = self.browser.find_element(By.XPATH, '//button[@type="submit"]')

        time.sleep(4)
        publish_article_btn.click()
        time.sleep(6)

        # annak ellenőrzése, hogy a módosított cím megegyezik az adatokból felvitt eredeti címmel:

        new_title = WebDriverWait(self.browser, 2).until(EC.presence_of_element_located((By.XPATH, '//h1')))
        time.sleep(2)
        assert new_title.text == update_article["title"]

    # 9. Adat törlésének ellenőrzése:
    def test_delete_data(self):

        login(self.browser)

        # gombok, mezők megkeresése, cikk törlése:

        new_article(self.browser, delete_article['title'], delete_article['about'], delete_article['words'],
                    delete_article['tags'])  # adatok meghívása
        time.sleep(2)

        delete_btn = WebDriverWait(self.browser, 2).until(
            EC.presence_of_element_located((By.XPATH, '//button[@class="btn btn-outline-danger btn-sm"]')))
        delete_btn.click()
        time.sleep(2)

        profile_name_btn = self.browser.find_elements(By.XPATH, '//a[@class="nav-link"]')[4]
        profile_name_btn.click()
        time.sleep(2)

        article_list = self.browser.find_elements(By.XPATH, '//a/h1')
        new_article_list = []
        for i in article_list:
            new_article_list.append(i.text)

        # a saját cikkek listájában nem szerepel a törölt cím:

        assert not delete_article["title"] in new_article_list

    # 10. Adatok lementésének ellenőrzése - lementett tartalom megegyzik az oldalon lévő tartalommal:
    def test_save_data(self):

        login(self.browser)

        # gombok megkeresése, adat mentése, visszatöltése olvasásra:

        popular_tags = self.browser.find_elements(By.XPATH, '//a[@class="tag-pill tag-default"]')
        with open('test_vizsgaremek_conduit_CSK/mentett_adatok.csv', 'w', encoding="UTF-8") as file:
            for tag in popular_tags:
                file.write(tag.text)
                file.write("\n")

        tag_list = []
        with open('test_vizsgaremek_conduit_CSK/mentett_adatok.csv', 'r', encoding="UTF-8") as file_read:
            csv_reader = csv.reader(file_read, delimiter=',')
            for tag in csv_reader:
                tag_list.append(tag)

        assert len(tag_list) > 0
        assert len(tag_list) == len(popular_tags)

    # 11. Kijelentkezés folyamatának ellenőrzése:
    def test_sign_out(self):

        login(self.browser)

        # gombok megkeresése:

        logout_btn = self.browser.find_element(By.XPATH, '//a[@active-class="active"]')
        assert logout_btn.is_enabled()  # A 'Kijelentkezés' gomb elérhető, azaz be vagyunk jelentkezve.
        logout_btn.click()

        sign_in_btn = self.browser.find_element(By.LINK_TEXT, 'Sign in')
        assert sign_in_btn.is_enabled()  # A 'Bejelentkezés' gomb elérhető azaz ki vagyunk jelentkezve.
