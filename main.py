import telebot
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.expected_conditions import element_to_be_clickable
from flask import Flask, request
import os
import time
server = Flask(__name__)
TOKEN = 'TOKEN'
bot = telebot.TeleBot(token=TOKEN)
print("STARTED")
@bot.message_handler(func=lambda message: message.text.startswith('/'))
def scrape(message):
    print("Started scraping for "+message.text[1:]+"....")
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.38')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument("window-size=1240,516")
    chrome_options.binary_location = os.environ.get('GOOGLE_CHROME_BIN')
    movie=message.text[1:]
    browser = webdriver.Chrome(executable_path=os.environ.get("CHROMEDRIVER_PATH"),options=chrome_options)
    print(type(browser))
    browser.get('https://pahe.ph')
    browser.implicitly_wait(10)
    browser.find_element_by_class_name('search-live').send_keys(movie + Keys.RETURN)
    if(len(browser.find_elements_by_class_name('post-box-title'))==0):
        bot.reply_to(message,"Not found")
        browser.quit()
        return
    browser.find_element_by_xpath("//h2[@class='post-box-title']/a").click()
    switchwind(browser)
    # browser.find_elements_by_xpath('//*/text()[.="some specific word"]/following-sibling::div[@class="something"]')
    seasons=browser.find_elements_by_xpath("//ul[@class='tabs-nav']/li")
    print("Not yet entered")
    if(len(seasons)!=0):
        print("enter in if else")
        sname=""
        sindex=0
        for season in seasons:
            sname=sname+str(sindex)+". "+season.get_attribute('innerHTML')+"\n"
            sindex+=1
        msg = bot.reply_to(message,"Choose:\n"+sname)
        bot.register_next_step_handler(msg,process_season,browser,seasons)
    else:
        print("in else part")
        process_quality(message, browser)

def process_season(message,browser,seasons):
    print("in process_seasons part")
    nelem=seasons[int(message.text)]
    print(type(nelem))
    nelem.click()
    print("Clicked season button")
    switchwind(browser)
    process_quality(message,browser)
    
def process_quality(message,browser):
    print("inside process_quality")
    megabuttons=browser.find_elements_by_css_selector(".shortc-button.small.red")
    # megabuttons=browser.find_elements_by_css_selector("//ffebdeabfabcbcbd[contains(@class, 'shortc-button') and contains(@class, 'red')]")
    # //div[contains(@class, 'class1') and contains(@class, 'class2')]
    print("*******")
    print(megabuttons)
    qualitylabels=browser.find_elements_by_xpath("//div[@class='box-inner-block']/b")
    print(qualitylabels)
    megachoose=""
    index=0
    for megabutton in megabuttons:
        print(index)
        megachoose=megachoose+str(index)+" "
        index+=1
    megachoose=megachoose+"\n"
    for ql in qualitylabels:
        print(ql)
        megachoose=megachoose+ql.get_attribute('innerHTML')+" / "
    msg=bot.reply_to(message,"Choose quality: "+megachoose)
    bot.register_next_step_handler(msg,process_rest,browser,megabuttons)
    
def process_rest(message,browser,megabuttons):
    print("process_rest")
    print(message.text)
    mega_to_click=megabuttons[int(message.text)]
    print(mega_to_click)
    mega_to_click.click()
    print("clicked mega button")
    switchwind(browser)
    count=0
    consent=True
    while(not browser.find_elements_by_class_name('qc-cmp2-consent-info')):
        count=count+1
        print("inside consent box")
        browser.back()
        browser.find_element_by_css_selector('.shortc-button.small.red').click()
        switchwind(browser)
        WebDriverWait(browser, 4).until(
        presence_of_element_located((By.CLASS_NAME, 'qc-cmp2-consent-info')))
        if(count==3):
            consent=False
            break
    if(consent==True):
        print("consent is false")
        browser.find_elements_by_tag_name('button')[2].click()
        browser.find_elements_by_tag_name('button')[9].click()
    print("waiting for generate link button")
    WebDriverWait(browser,3).until(
        presence_of_element_located((By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_im-not-a-robot.png']"))
    )
    browser.find_element(By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_im-not-a-robot.png']").click()
    WebDriverWait(browser,10).until(
        presence_of_element_located((By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_generate-link.png']"))
    )
    browser.find_element(By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_generate-link.png']").click()
    WebDriverWait(browser,10).until(
        presence_of_element_located((By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_download.png']"))
    )
    browser.find_element(By.XPATH,"//img[@src='https://intercelestial.com/wp-content/uploads/2019/09/button_download.png']").click()
    time.sleep(2)
    browser.switch_to.window(browser.window_handles[1])
    WebDriverWait(browser,30).until(
        presence_of_element_located((By.CSS_SELECTOR,"a.btn.btn-primary.btn-xs"))
    )
    button = browser.find_element(By.CSS_SELECTOR,"a.btn.btn-primary.btn-xs")
    browser.execute_script("arguments[0].click();", button)
    time.sleep(1)
    megalink=browser.current_url
    print(browser.current_url)
    browser.quit()
    bot.reply_to(message, megalink)

def switchwind(browser):
    if(len(browser.window_handles)>1):
        browser.switch_to.window(browser.window_handles[1])
        browser.close()
        browser.switch_to.window(browser.window_handles[0])

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='WEBHOOK URL' + TOKEN)
    return "!", 200


if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
