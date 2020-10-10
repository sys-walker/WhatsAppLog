#!/usr/bin/env python3

import argparse, os, psutil, signal, sys, threading
from time import strftime, sleep
from PIL import Image
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

xpath_field_find_contact = "/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/div/div[2]"
xpath_found_contact = "/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div/div[3]/div/div/div[2]/div[1]/div[" \
                       "1]/span/span "
contact_status_tmp = "/html/body/div[1]/div/div/div[4]/div/header/div[2]/div[2]"


def signal_handler(signal, frame):
    if wa_options.filename != "":
        f.close()

    driver.quit()
    sys.exit(0)


def close():
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()


def open_webdriver():
    global f
    if wa_options.filename != "":
        f = open(wa_options.filename, "a+")
    options = Options()
    options.headless = wa_options.debug
    driver = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver', options=options)
    driver.get("https://web.whatsapp.com")
    return driver


def login_whatsapp():
    if not wa_options.debug:
        input("Please Login via web browser and press [Enter]")
        return
    print("QR Code Generating")
    sleep(5)
    driver.save_screenshot("screenshot.png")
    print("Sucessfully QR code genereted")
    image = Image.open('screenshot.png')
    image.show()
    sleep(5)
    input("Scan QR and press [Enter] to continue...")
    print("Wait...")
    close()
    sleep(5)


def keep_alive():
    try:
        while True:
            s = driver.find_element_by_xpath(xpath_field_find_contact)
            s.click()
            name2 = "Jobba"
            s.send_keys(name2)
            sleep(1)
            s.clear()
            sleep(10)
    except Exception as e:
        print("Connection Closed", e)
        os.kill(os.getpid(), signal.SIGINT)


def find_contact():
    while True:
        contact_finder = driver.find_element_by_xpath(xpath_field_find_contact)
        contact_finder.click()

        contact_finder.clear()
        name = input("contact:")
        if name != "":
            contact_finder.send_keys(name)
            print("Finding ", name)
            sleep(5)
            chat_divs_array = driver.find_elements_by_class_name("_210SC")
            for chat_div in chat_divs_array:
                if chat_div.find_elements_by_class_name("_3CneP"):
                    if name.lower() in chat_div.find_element_by_class_name("_3CneP").text.lower():
                        return chat_div.find_element_by_class_name("_3CneP")
        print("Couldn't Find make you sure that contact exists!")
        sleep(2)


def argsparser():
    global wa_options
    parser = argparse.ArgumentParser(description='WhatsApp Logging')
    parser.add_argument('-f', '--filename',
                        dest="filename",
                        default="", help="Set outputfile")
    parser.add_argument('-d', '--debug',
                        dest="debug",
                        action='store_false', default=True, help="Enables debug via webbroser visible")
    wa_options = parser.parse_args()
    print(wa_options)


def save_log(*args):
    for p in args:
        if wa_options.filename != "":
            print(p, file=f)
        print(p)


def track(driver, name):
    sleep(2)
    os.system('clear')
    print("Now tracking is live\n")
    fst_on = False
    fst_of = False
    t = strftime("%Y-%m-%d %H:%M:%S")

    header = "============= " + str(name) + " ============="
    session = "Session Started at " + str(t) + "\n"
    save_log(header, session)

    threading.Thread(target=keep_alive, daemon=True).start()
    while True:
        statusList = driver.find_elements_by_xpath(contact_status_tmp)
        sys.stdout.flush()
        if len(statusList) != 0:
            if statusList[0].text == 'en línea':
                fst_of = False
                if not fst_on:
                    save_log(name + " " + statusList[0].text + " " + str(t[11:]))

                fst_on = True
            elif statusList[0].text == 'escribiendo...':
                fst_on = False
                if not fst_of:
                    save_log(name + " " + "escribiendo..." + str(t[11:]))
                fst_of = True
            else:
                fst_on = False
                if not fst_of:
                    save_log(name + " " + statusList[0].text + " " + str(t[11:]))
                fst_of = True
        else:
            fst_on = False
            if not fst_of:
                save_log(name + " " + "[HIDDEN] disconnected/tipying" + " " + str(t[11:]))
            fst_of = True


if __name__ == '__main__':
    global wa_options
    global driver
    driver = None
    signal.signal(signal.SIGINT, signal_handler)
    argsparser()
    print("Please Wait Starting whatsapp-logging")

    try:
        driver = open_webdriver()
        login_whatsapp()
        whatsapp_contact = find_contact()
        whatsapp_contact.click()
        track(driver, whatsapp_contact.text)
    except Exception as e:
        print("Panic exit! ", e)
        if driver is not None:
            driver.quit()
        exit(1)
