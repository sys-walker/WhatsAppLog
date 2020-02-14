#!/usr/bin/env python3

# inspiration https://github.com/rizwansoaib/whatsapp-monitor/
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
import psutil, os, sys
from PIL import Image
from time import strftime, sleep


def close():
    for proc in psutil.process_iter():
        if proc.name() == "display":
            proc.kill()


def open_webdriver():
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(executable_path=os.getcwd() + '/geckodriver', options=options)
    driver.get("https://web.whatsapp.com")
    return driver


def login_whatsapp(driver):
    print("QR Code Generating")
    sleep(5)
    driver.save_screenshot("screenshot.png")
    print("Sucessfully QR code genereted")
    image = Image.open('screenshot.png')
    image.show()
    sleep(5)
    input("Scan QR and press anykey to continue...")
    close()


def find_Contact(driver):
    s = driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/input")
    s.click()
    name = input("Please enter Contact:>>>     ")
    s.send_keys(name)
    sleep(1)
    open_chat = driver.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div/div[2]/div[1]/div/div/div[2]')
    open_chat.click()
    driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/input").clear()
    return name


def track(driver,file):
    while True:
        # loop whatsapp conactos
        try:
            print("Sucessfully QR Code Scanned")
            # buscar contacto
            name = find_Contact(driver)
            #
            sleep(2)
            os.system('clear')
            print("Now tracking is live\n")
            fst_on = False
            fst_of = False
            check = 0
            t = strftime("%Y-%m-%d %H:%M:%S")

            header = "============= " + str(name) + " ============="
            session = "Session Started at " + str(t) + "\n"
            print(header)
            print(session)
            print(header, file=file)
            print(session,file=file)
            while True:
                if check == 0:
                    s = driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/input")
                    s.click()
                    name2 = "Jobba"
                    s.send_keys(name2)
                    sleep(1)
                    driver.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div/div[1]/div/label/input").clear()
                else:
                    sleep(1)

                sys.stdout.write('\r' + "working ... " + str(check))
                sys.stdout.flush()

                statusList= list(driver.find_elements_by_class_name("_315-i"))
                status = "Undefined" if len(statusList)==0 else statusList[0].text
                
                sys.stdout.flush()
                if len(statusList)!=0:
                    if status == 'en línea':
                        fst_of = False
                        if fst_on == False:
                            print("\n", name, status, t[11:])
                            print("\n"+name+" "+status+" "+ str(t[11:]),file=file)
                        fst_on = True
                        check = (check + 1) % 10
                    if status != 'en línea':
                        fst_on = False
                        if fst_of == False:
                            print("\n", name, "disconnected", t[11:])  # ,file=f
                            print("\n"+name+" "+status+" "+ str(t[11:]),file=file)
                        fst_of = True
                        check = (check + 1) % 10
                else:
                    fst_on = False
                    if fst_of == False:
                        print("\n", name, "[HIDDEN] disconnected/tipying", t[11:])  # ,file=f
                        print("\n"+name+" "+"[HIDDEN] disconnected/tipying"+" "+ str(t[11:]),file=file)
                    fst_of = True
                    check = (check + 1) % 10
        # aturar el programa
        except KeyboardInterrupt as ki:
            print(ki)
            print("[Ctrl+C] Program Stopped")
            file.close()
            driver.quit()
            break


if __name__ == '__main__':
    print("Please Wait Starting whatsapp-logging")

    driver = open_webdriver()
    login_whatsapp(driver)
    try:
        f = open("Whatsapp_log.txt", "a+")
        track(driver,f)
    except Exception as e:
        print("Panic exit",e)
        driver.quit()
